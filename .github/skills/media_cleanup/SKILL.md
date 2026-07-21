---
name: media_cleanup
description: >
  Detect and remove unused images, organize WordPress media library, compress
  oversized images, convert to WebP format, regenerate thumbnails, and clean
  up orphaned files in wp-content/uploads. Keeps your media library lean.
when_to_use: "User asks to clean up images, remove unused media, organize media library, compress images, or convert to WebP"
authority: write
cost_tier: 2
version: 0.1.0
---

# Media Cleanup & Optimization Skill

Detect unused/orphaned images, remove them safely, compress oversized media,
convert images to next-gen formats (WebP/AVIF), regenerate thumbnails, and
organize the WordPress media library for better performance and storage.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wp_media_cleanup.py` | Detect unused images, safe delete, media audit |
| `scripts/wp_image_optimize.py` | Compress, convert to WebP, regenerate thumbnails |
| `scripts/wp_media_classify.py` | CLIP-based image classification, virtual folder (VMFO) organization |

## Usage

```bash
# Audit media library — find unused images
python .github/skills/media_cleanup/scripts/wp_media_cleanup.py --action audit

# Find truly unused images (not in posts, pages, products, Elementor, widgets)
python .github/skills/media_cleanup/scripts/wp_media_cleanup.py --action find-unused

# Dry-run delete (preview what would be removed)
python .github/skills/media_cleanup/scripts/wp_media_cleanup.py --action clean --dry-run

# Delete unused images permanently
python .github/skills/media_cleanup/scripts/wp_media_cleanup.py --action clean --confirm

# Find oversized images (>500KB)
python .github/skills/media_cleanup/scripts/wp_media_cleanup.py --action find-oversized --max-size 500

# List images by file size (largest first)
python .github/skills/media_cleanup/scripts/wp_media_cleanup.py --action list-by-size --sort desc

# Find images missing alt text
python .github/skills/media_cleanup/scripts/wp_media_cleanup.py --action missing-alt

# Organize — bulk update titles/alt text from filename
python .github/skills/media_cleanup/scripts/wp_media_cleanup.py --action organize --dry-run

# Compress images (lossless optimization)
python .github/skills/media_cleanup/scripts/wp_image_optimize.py --action compress \
  --quality 85 --max-width 1920

# Convert JPEG/PNG to WebP
python .github/skills/media_cleanup/scripts/wp_image_optimize.py --action convert-webp \
  --quality 80

# Regenerate thumbnails for all images
python .github/skills/media_cleanup/scripts/wp_image_optimize.py --action regenerate-thumbnails

# Full optimization: compress + webp + thumbnails
python .github/skills/media_cleanup/scripts/wp_image_optimize.py --action optimize-all

# Ensure virtual folders (VMFO taxonomy) exist for the target taxonomy
python .github/skills/media_cleanup/scripts/wp_media_classify.py --action ensure-folders

# Classify a random sample first to spot-check accuracy (no writes)
python .github/skills/media_cleanup/scripts/wp_media_classify.py --action classify --dry-run --sample 50

# Classify the full library (no writes, just a report)
python .github/skills/media_cleanup/scripts/wp_media_classify.py --action classify --dry-run

# Classify + assign images to virtual folders in WordPress
python .github/skills/media_cleanup/scripts/wp_media_classify.py --action classify --apply

# Classify a single category's images only, writing a named report
python .github/skills/media_cleanup/scripts/wp_media_classify.py --action classify --dry-run \
  --report-name banners_hero

# Apply only a pre-approved, hand-reviewed set of media IDs
python .github/skills/media_cleanup/scripts/wp_media_classify.py --action classify --apply \
  --ids-file outputs/_memory/banners_hero_ids.txt

# Classify images referenced in post/page content instead of by CLIP (for blog images)
python .github/skills/media_cleanup/scripts/wp_media_classify.py --action blog-images

# Sort by MIME type (SVG/font/video/etc.) instead of CLIP — no model load, near-instant
python .github/skills/media_cleanup/scripts/wp_media_classify.py --action sort-files
```

### The real workflow: classify → review → approve → apply

Never go straight from `--dry-run` to `--apply` on a category with real ambiguity (e.g.
"is this a banner or a hero image?"). The proven multi-pass loop, used for every category
cleanup so far:

1. **Classify** that category with a named report: `--action classify --dry-run
   --report-name <category>` → writes `outputs/_memory/media_classification_<category>.json`.
2. **Build a review HTML** from that JSON (thumbnail grid with predicted folder + confidence)
   so a human can eyeball misclassifications at a glance — save as
   `outputs/_memory/<category>_review.html`.
3. **Approve** — after review, write the accepted media IDs to
   `outputs/_memory/<category>_ids.txt` (one ID per line, or whatever the reviewer confirms).
4. **Apply** only those IDs: `--action classify --apply --ids-file
   outputs/_memory/<category>_ids.txt`. This scopes the write to reviewed items instead of
   trusting the raw model output for the whole library.

This is why `outputs/_memory/` accumulates `*_items.json` / `*_review.html` / `*_ids.txt`
triples per category (banners_hero, product_cleanup, product_images, blog_images, ...) —
that's expected, not clutter. Keep them; they're the audit trail for what was approved.

## Virtual Folder Classification (CLIP)

The site uses the **VMFO** (Media Folder) plugin, which exposes a real taxonomy
(`vmfo_folder`) readable/writable via the standard `wp/v2/media` endpoint
(`vmfo-folders` field, an array of folder term IDs) and manageable via
`/wp-json/vmfo/v1/folders`.

Media titles/alt text on this site are mostly blank or auto-generated
(`image-147.png`, "Misc – Image 96"), so classification is done by actually
looking at each image using local **CLIP zero-shot classification**
(`open_clip`, `ViT-B-32/openai`) against a fixed set of category prompts —
no API cost, no external vision calls. Low-confidence predictions
(similarity below the threshold in the script) fall into "Uncategorized"
for manual review rather than being force-assigned.

Always run `--action classify --dry-run` (optionally with `--sample N`)
first and review `outputs/_memory/media_classification.json` before
`--apply`.

## How Unused Image Detection Works

1. Fetches ALL media IDs from WordPress REST API
2. Searches for each media ID in:
   - Post/page content (`post_content` via REST API)
   - Featured images (`_thumbnail_id` post meta)
   - WooCommerce product images & galleries
   - Elementor page data (`_elementor_data` post meta)
   - Widget data and theme mods
   - Custom post types
3. Flags media NOT found anywhere as "unused"
4. Also checks `wp-content/uploads/` for files not in the media library (orphaned files)

## Safety Features

- **Dry-run mode**: Preview without deleting
- **Trash first**: Moves to trash before permanent deletion (unless `--force`)
- **Backup reminder**: Prompts to backup via Hostinger first
- **Size threshold**: Can target only images above a certain size
- **Age filter**: Can target only images older than X days

## Required Environment Variables

- `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`

## Outputs

Writes audit reports to `outputs/<project-slug>/media_*.json`.
