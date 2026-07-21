#!/usr/bin/env python3
"""
WordPress Media Classifier & Virtual Folder Organizer

Classifies media library images with local CLIP zero-shot classification
and assigns them to VMFO (Media Folder plugin) virtual folders via the
`vmfo-folders` field on wp/v2/media.

Folders are a real WP taxonomy (vmfo_folder) exposed at:
  GET/POST /wp-json/vmfo/v1/folders          (list / create folders)
  POST     /wp-json/wp/v2/media/{id}         (assign via vmfo-folders: [id])

Usage:
    # Ensure target folders exist (idempotent, safe to re-run)
    python wp_media_classify.py --action ensure-folders

    # Classify all images, write a report, make no changes
    python wp_media_classify.py --action classify --dry-run

    # Classify + write vmfo-folders assignments back to WordPress
    python wp_media_classify.py --action classify --apply

    # Classify a random sample only (for spot-checking accuracy)
    python wp_media_classify.py --action classify --dry-run --sample 50

    # Move every image actually used in a blog post into "Blog Posts"
    python wp_media_classify.py --action blog-images --dry-run
    python wp_media_classify.py --action blog-images --apply
"""

import os, sys, json, argparse, base64, random, io, html, re
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
WP_USER = os.getenv("WORDPRESS_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "")
AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
API = f"{WP_URL}/wp-json/wp/v2"
VMFO_API = f"{WP_URL}/wp-json/vmfo/v1"

OUTPUT_DIR = Path(__file__).parent.parent.parent.parent.parent / "outputs" / "_memory"

# Category name -> CLIP zero-shot text prompts describing that category.
# Kept as short natural-language descriptions; CLIP compares each image
# against all prompts and picks the highest-similarity match.
CATEGORIES = {
    "Product Images": [
        "a photo of a 3D printer machine",
        "a product render of a 3D printing machine enclosure",
        "a photo of industrial machinery or manufacturing equipment",
        "a photo of an electronic hardware device or component such as a "
        "circuit board, motor, or tool",
        "a photo of a spool of 3D printing filament",
    ],
    "Printed Parts": [
        "a close-up photo of a small 3D printed plastic object, not a "
        "machine and not a spool of filament",
        "a product photo of a manufactured plastic or metal part on a "
        "plain background, without any printer, machine, or filament "
        "spool visible",
    ],
    "Logos and Branding": [
        "a company or brand wordmark logo on a plain or transparent "
        "background, no photographic scene",
        "a partner or client organization logo, an emblem or crest logo",
        "a small brand icon mark with no background scene",
    ],
    "People and Lifestyle": [
        "a photo of a person, with the person as the main subject",
        "a lifestyle stock photo of one or more people",
        "a portrait photo of a person's face",
        "a photo of people using or interacting with a product",
    ],
    "Team and Office": [
        "a photo of employees in an office",
        "a photo of a workplace or office interior",
    ],
    "Banners and Hero": [
        "a wide banner background graphic filling the whole frame, with "
        "no logo or text as the main subject",
        "an abstract hero background image with gradient, texture, or "
        "3D render, no logo",
    ],
    "Screenshots and UI": [
        "a screenshot of a software application or website",
        "a screenshot of a computer desktop or dashboard",
        "a screen capture showing a browser window with text and menus",
    ],
    "Blog and Editorial": [
        "an editorial illustration for a blog article",
        "a photo used to illustrate a news or blog post",
    ],
    "Icons and Illustrations": [
        "a small flat icon illustration",
        "a vector-style graphic illustration",
    ],
}
UNCATEGORIZED = "Uncategorized"
# Softmax probability over 9 categories; uniform/no-signal is ~0.11.
# Below this, route to Uncategorized for manual review instead of guessing.
CONFIDENCE_THRESHOLD = 0.35

# Media authored by this WP user goes straight to "Fracktal Care" (233 items,
# matches the existing folder count) without running CLIP on them.
FRACKTAL_CARE_AUTHOR_ID = 4144  # Kiran Kumar
FRACKTAL_CARE_FOLDER = "Fracktal Care"

# Images actually referenced in a blog post (post_content or featured_media)
# go into this folder. This is a content-reference check, not CLIP vision.
BLOG_POSTS_FOLDER = "Blog Posts"

# Non-raster / non-photo assets are sorted by mime type, not CLIP vision.
VECTOR_FOLDER = "Vector Images"
OTHER_FILES_FOLDER = "Other Files"
VECTOR_MIME_TYPES = {"image/svg+xml"}
OTHER_FILE_MIME_TYPES = {
    "application/x-font-ttf", "application/x-font-otf", "font/ttf", "font/otf",
    "video/mp4", "video/quicktime", "video/webm",
    "application/json", "application/pdf", "application/zip",
}

_model = None
_preprocess = None
_tokenizer = None
_text_features = None
_prompt_to_category = []


def _check():
    missing = [v for v, k in [("WP_URL", WP_URL), ("WP_USER", WP_USER),
                ("WP_APP_PASSWORD", WP_APP_PASSWORD)] if not k]
    if missing:
        print(json.dumps({"error": True, "message": f"Missing: {', '.join(missing)}"}))
        sys.exit(1)


def _get_all_pages(endpoint, params=None, per_page=100, base=API):
    params = (params or {}).copy()
    params["per_page"] = per_page
    params["page"] = 1
    all_data = []
    while True:
        url = f"{base}/{endpoint.lstrip('/')}"
        r = requests.get(url, headers=HEADERS, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        all_data.extend(data)
        total_pages = int(r.headers.get("X-WP-TotalPages", 1))
        if params["page"] >= total_pages:
            break
        params["page"] += 1
    return all_data


def _get_all_images():
    print("Fetching all image media items...", file=sys.stderr)
    return _get_all_pages("media", {
        "_fields": "id,title,source_url,media_type,alt_text,vmfo-folders,author",
        "media_type": "image",
    })


def _get_all_media_any_type():
    """Fetch every media item regardless of type (images, video, fonts,
    documents, archives). WP's media_type=image bucket also includes SVGs."""
    print("Fetching all media items (any type)...", file=sys.stderr)
    return _get_all_pages("media", {
        "_fields": "id,title,source_url,media_type,mime_type,vmfo-folders",
    })


def _load_clip():
    """Lazy-load CLIP model and precompute text embeddings for all category prompts."""
    global _model, _preprocess, _tokenizer, _text_features, _prompt_to_category
    if _model is not None:
        return
    import torch
    import open_clip

    print("Loading CLIP model (ViT-B-32-quickgelu/openai)...", file=sys.stderr)
    _model, _, _preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32-quickgelu", pretrained="openai")
    _tokenizer = open_clip.get_tokenizer("ViT-B-32")
    _model.eval()

    prompts, cat_map = [], []
    for cat, texts in CATEGORIES.items():
        for t in texts:
            prompts.append(t)
            cat_map.append(cat)
    _prompt_to_category = cat_map

    with torch.no_grad():
        tokens = _tokenizer(prompts)
        feats = _model.encode_text(tokens)
        feats /= feats.norm(dim=-1, keepdim=True)
        _text_features = feats


def _classify_image(url):
    """Download an image and return (category, confidence) via CLIP zero-shot."""
    import torch
    from PIL import Image

    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception as e:
        return UNCATEGORIZED, 0.0, str(e)

    image_input = _preprocess(img).unsqueeze(0)
    with torch.no_grad():
        image_features = _model.encode_image(image_input)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        # CLIP's own logit_scale (~100) sharpens cosine similarities into a
        # distribution where the winning category actually stands out,
        # instead of raw cosine sims which cluster tightly around 0.2-0.3.
        logit_scale = _model.logit_scale.exp()
        logits = (logit_scale * image_features @ _text_features.T).squeeze(0)

    # Aggregate per-category by max logit across that category's prompts,
    # then softmax across categories to get a real probability distribution.
    best_per_cat = {}
    for logit, cat in zip(logits.tolist(), _prompt_to_category):
        if cat not in best_per_cat or logit > best_per_cat[cat]:
            best_per_cat[cat] = logit

    cats = list(best_per_cat.keys())
    cat_logits = torch.tensor([best_per_cat[c] for c in cats])
    probs = torch.softmax(cat_logits, dim=0)

    best_idx = int(probs.argmax())
    best_cat = cats[best_idx]
    best_score = probs[best_idx].item()

    if best_score < CONFIDENCE_THRESHOLD:
        return UNCATEGORIZED, best_score, None
    return best_cat, best_score, None


def _get_or_create_folders():
    """Fetch existing VMFO folders; create any missing target categories. Returns {name: id}."""
    r = requests.get(f"{VMFO_API}/folders", headers=HEADERS, timeout=30)
    r.raise_for_status()
    # WP stores/returns folder names HTML-entity-encoded (e.g. "Team &amp; Office")
    existing = {html.unescape(f["name"]): f["id"] for f in r.json()}

    wanted = list(CATEGORIES.keys()) + [UNCATEGORIZED, BLOG_POSTS_FOLDER,
                                         VECTOR_FOLDER, OTHER_FILES_FOLDER]
    for name in wanted:
        if name in existing:
            continue
        resp = requests.post(f"{VMFO_API}/folders", headers=HEADERS,
                              json={"name": name, "parent": 0}, timeout=30)
        if resp.status_code in (200, 201):
            existing[name] = resp.json()["id"]
            print(f"Created folder: {name} (id={existing[name]})", file=sys.stderr)
        else:
            print(f"WARN: could not create folder {name}: "
                  f"{resp.status_code} {resp.text[:200]}", file=sys.stderr)
    return existing


def action_ensure_folders(args):
    folders = _get_or_create_folders()
    return {"folders": folders}


def _get_blog_referenced_media_ids():
    """Find every media ID actually used in a blog post (post type=post):
    featured image + inline <img class="wp-image-N"> references."""
    print("Fetching blog posts...", file=sys.stderr)
    posts = _get_all_pages("posts", {"_fields": "id,title,content,featured_media"})

    referenced = set()
    for post in posts:
        fm = post.get("featured_media", 0)
        if fm:
            referenced.add(fm)
        content = post.get("content", {}).get("rendered", "")
        for mid in re.findall(r"wp-image-(\d+)", content):
            referenced.add(int(mid))
    return referenced


def action_blog_images(args):
    """Move every image referenced in a blog post into the Blog Posts folder."""
    blog_media_ids = _get_blog_referenced_media_ids()
    all_images = _get_all_images()
    matched = [m for m in all_images if m["id"] in blog_media_ids]

    print(f"Found {len(matched)} media items referenced in blog posts "
          f"(of {len(blog_media_ids)} referenced IDs).", file=sys.stderr)

    result = {
        "referenced_ids": len(blog_media_ids),
        "matched_media_items": len(matched),
        "items": [{"id": m["id"], "title": m["title"]["rendered"],
                    "url": m.get("source_url", ""),
                    "current_folders": m.get("vmfo-folders", [])}
                   for m in matched],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "media_blog_images.json"
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    print(f"Report written to {report_path}", file=sys.stderr)

    if not args.apply:
        return {"dry_run": True, "matched_media_items": len(matched),
                "report": str(report_path)}

    folders = _get_or_create_folders()
    folder_id = folders.get(BLOG_POSTS_FOLDER)
    applied, failed = 0, 0
    for m in matched:
        try:
            resp = requests.post(f"{API}/media/{m['id']}", headers=HEADERS,
                                  json={"vmfo-folders": [folder_id]}, timeout=15)
            if resp.status_code in (200, 201):
                applied += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    return {"applied": applied, "failed": failed, "report": str(report_path)}


def action_sort_files(args):
    """Sort non-photo assets (SVGs, fonts, video, docs, archives) by mime
    type into Vector Images / Other Files, regardless of current folder.
    No CLIP needed -- mime type is a deterministic, reliable signal here."""
    all_media = _get_all_media_any_type()

    vectors = [m for m in all_media if m["mime_type"] in VECTOR_MIME_TYPES]
    others = [m for m in all_media if m["mime_type"] in OTHER_FILE_MIME_TYPES]

    print(f"Found {len(vectors)} vector files, {len(others)} other "
          f"non-photo files.", file=sys.stderr)

    def _summarize(items):
        return [{"id": m["id"], "title": m["title"]["rendered"],
                  "url": m.get("source_url", ""), "mime_type": m["mime_type"],
                  "current_folders": m.get("vmfo-folders", [])}
                 for m in items]

    result = {"vector_count": len(vectors), "other_count": len(others),
               "vectors": _summarize(vectors), "others": _summarize(others)}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "media_sort_files.json"
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    print(f"Report written to {report_path}", file=sys.stderr)

    if not args.apply:
        return {"dry_run": True, "vector_count": len(vectors),
                "other_count": len(others), "report": str(report_path)}

    folders = _get_or_create_folders()
    vector_folder_id = folders.get(VECTOR_FOLDER)
    other_folder_id = folders.get(OTHER_FILES_FOLDER)

    applied, failed = 0, 0
    for m, folder_id in [(m, vector_folder_id) for m in vectors] + \
                         [(m, other_folder_id) for m in others]:
        try:
            resp = requests.post(f"{API}/media/{m['id']}", headers=HEADERS,
                                  json={"vmfo-folders": [folder_id]}, timeout=15)
            if resp.status_code in (200, 201):
                applied += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    return {"applied": applied, "failed": failed, "report": str(report_path)}


def action_classify(args):
    all_images = _get_all_images()

    if args.ids_file:
        wanted_ids = {int(x) for x in
                      Path(args.ids_file).read_text().split()}
        all_images = [m for m in all_images if m["id"] in wanted_ids]

    # Split off Kiran Kumar's media -> Fracktal Care directly, no CLIP needed.
    fracktal_care_items = [m for m in all_images
                            if m.get("author") == FRACKTAL_CARE_AUTHOR_ID]
    images = [m for m in all_images
              if m.get("author") != FRACKTAL_CARE_AUTHOR_ID]

    if args.sample:
        random.seed(42)
        images = random.sample(images, min(args.sample, len(images)))

    print(f"{len(fracktal_care_items)} images assigned to "
          f"'{FRACKTAL_CARE_FOLDER}' by author (no CLIP needed).", file=sys.stderr)
    print(f"Classifying {len(images)} remaining images with CLIP...", file=sys.stderr)

    results = []
    counts = {}

    for m in fracktal_care_items:
        counts[FRACKTAL_CARE_FOLDER] = counts.get(FRACKTAL_CARE_FOLDER, 0) + 1
        results.append({
            "id": m["id"],
            "title": m["title"]["rendered"],
            "url": m.get("source_url", ""),
            "current_folders": m.get("vmfo-folders", []),
            "predicted_category": FRACKTAL_CARE_FOLDER,
            "confidence": None,
            "error": None,
        })

    if images:
        _load_clip()
    for i, m in enumerate(images, 1):
        url = m.get("source_url", "")
        cat, score, err = _classify_image(url)
        counts[cat] = counts.get(cat, 0) + 1
        results.append({
            "id": m["id"],
            "title": m["title"]["rendered"],
            "url": url,
            "current_folders": m.get("vmfo-folders", []),
            "predicted_category": cat,
            "confidence": round(score, 4),
            "error": err,
        })
        if i % 50 == 0:
            print(f"  ...{i}/{len(images)}", file=sys.stderr)

    report = {
        "generated": datetime.now().isoformat(),
        "total_classified": len(results),
        "counts_by_category": counts,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "items": results,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / (args.report_name or "media_classification.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report written to {report_path}", file=sys.stderr)

    if not args.apply:
        return {"dry_run": True, "counts_by_category": counts,
                "total_classified": len(results), "report": str(report_path)}

    folders = _get_or_create_folders()
    applied, failed = 0, 0
    for item in results:
        folder_id = folders.get(item["predicted_category"])
        if not folder_id:
            failed += 1
            continue
        try:
            resp = requests.post(f"{API}/media/{item['id']}", headers=HEADERS,
                                  json={"vmfo-folders": [folder_id]}, timeout=15)
            if resp.status_code in (200, 201):
                applied += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    return {"applied": applied, "failed": failed, "counts_by_category": counts,
            "report": str(report_path)}


def main():
    _check()
    parser = argparse.ArgumentParser(description="WordPress Media Classifier & Folder Organizer")
    parser.add_argument("--action", required=True,
                         choices=["ensure-folders", "classify", "blog-images",
                                  "sort-files"])
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true",
                         help="Write vmfo-folders assignments back to WordPress")
    parser.add_argument("--sample", type=int, default=0,
                         help="Classify only a random sample of N images")
    parser.add_argument("--ids-file", dest="ids_file", default=None,
                         help="Path to a text file of media IDs (one per "
                              "line) to restrict classification to")
    parser.add_argument("--report-name", dest="report_name", default=None,
                         help="Override output report filename "
                              "(default media_classification.json)")
    args = parser.parse_args()

    if args.action == "ensure-folders":
        result = action_ensure_folders(args)
    elif args.action == "classify":
        result = action_classify(args)
    elif args.action == "blog-images":
        result = action_blog_images(args)
    elif args.action == "sort-files":
        result = action_sort_files(args)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
