"""Turn an uploaded file into a web-ready site asset.

Everything a clinic hands over arrives as a 4000px, 6 MB phone photograph with
EXIF attached. Shipping that unprocessed costs the visitor seconds of load time
and — for clinical photography — leaks metadata that must not be published. So
an upload is never just written to disk; it goes through here first.

What this does and why:

* **Applies EXIF orientation, then discards EXIF.** Phone cameras record the
  sensor's raw orientation plus a rotation flag. Saving without applying the
  flag rotates the picture sideways; keeping the tag republishes it. We bake the
  rotation into the pixels and drop the metadata block entirely — which also
  removes the GPS coordinates of the clinic and the patient's capture time. For
  patient photography that is not an optimisation, it is a requirement.
* **Caps the long edge.** Nothing on this site is displayed above ~1600px, so
  anything larger is bytes the visitor pays for and never sees.
* **Re-encodes to a sensible format.** Photographs become progressive JPEG at
  quality 82 (visually indistinguishable at these sizes, a fraction of the
  bytes). Images with transparency stay PNG. SVG is copied untouched — it is
  markup, not pixels, and re-encoding would destroy it.
* **Reports the stored dimensions** so the renderer can emit width/height and
  the browser reserves the right box before the file arrives.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).parent
IMG_DIR = ROOT / "assets" / "img"

MAX_EDGE = 1600          # nothing is displayed larger than this
JPEG_QUALITY = 82
MAX_UPLOAD = 25 * 1024 * 1024

# Accepted upload types. Deliberately short: these are the formats a browser
# renders everywhere, and every one of them is something Pillow can verify by
# decoding rather than by trusting the filename.
KINDS = {
    "image/jpeg": ".jpg", "image/png": ".png",
    "image/webp": ".webp", "image/svg+xml": ".svg",
}


class MediaError(Exception):
    """An upload we will not store, with the reason shown to the user."""


def slugify(text: str) -> str:
    """A filename that is safe, lowercase, and still recognisable."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return (text or "image")[:60]


def save(raw: bytes, mime: str, name_hint: str) -> dict:
    """Store an upload and return the image dict the page data will hold.

    Returns `{"src", "w", "h"}` — `alt`, `focus` and `consent` are the author's
    to supply, and `build.py` refuses the page until `alt` is there.
    """
    if len(raw) > MAX_UPLOAD:
        raise MediaError(f"That file is {len(raw) // 1024 // 1024} MB; the limit "
                         f"is {MAX_UPLOAD // 1024 // 1024} MB.")
    if mime not in KINDS:
        raise MediaError(f"{mime or 'That file type'} is not a web image format. "
                         "Use JPEG, PNG, WebP or SVG.")

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    stem = slugify(Path(name_hint).stem)

    if mime == "image/svg+xml":
        # Vector artwork: no re-encode. Reject scripting so a logo upload can
        # never introduce an inline <script> into every page that shows it.
        text = raw.decode("utf-8", "replace")
        if re.search(r"<script|onload=|onerror=|javascript:", text, re.I):
            raise MediaError("That SVG contains script. Export a plain vector "
                             "or convert it to PNG.")
        path = _unique(stem, ".svg")
        path.write_bytes(raw)
        return {"src": f"img/{path.name}"}

    try:
        from PIL import Image, ImageOps
    except ImportError as exc:                     # pragma: no cover
        raise MediaError("Pillow is not installed, so images cannot be "
                         "processed. Run: pip install Pillow") from exc

    import io
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()                                  # decode now: proves it is an
    except Exception as exc:                       # image, not a renamed file
        raise MediaError(f"That file is not a readable image ({exc}).") from exc

    im = ImageOps.exif_transpose(im)                # bake rotation into pixels
    if max(im.size) > MAX_EDGE:
        im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)

    transparent = im.mode in ("RGBA", "LA", "P") and _has_alpha(im)
    if transparent:
        im = im.convert("RGBA")
        path = _unique(stem, ".png")
        im.save(path, "PNG", optimize=True)        # save() writes no EXIF here
    else:
        im = im.convert("RGB")
        path = _unique(stem, ".jpg")
        im.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True,
                progressive=True)
    return {"src": f"img/{path.name}", "w": im.width, "h": im.height}


def _has_alpha(im) -> bool:
    if im.mode == "P":
        return "transparency" in im.info
    return im.getchannel("A").getextrema()[0] < 255


def _unique(stem: str, ext: str) -> Path:
    """A free filename. Never overwrite: an old file may still be referenced."""
    path = IMG_DIR / f"{stem}{ext}"
    n = 2
    while path.exists():
        path = IMG_DIR / f"{stem}-{n}{ext}"
        n += 1
    return path


def unused() -> list[str]:
    """Files in assets/img that no page references — safe to delete."""
    import build                                    # imports PAGES + text_of
    referenced = set()
    for page in build.PAGES:
        for m in re.finditer(r"img/[\w.-]+", build.text_of(page)):
            referenced.add(m.group(0))
    return sorted(f"img/{p.name}" for p in IMG_DIR.glob("*")
                  if f"img/{p.name}" not in referenced) if IMG_DIR.is_dir() else []
