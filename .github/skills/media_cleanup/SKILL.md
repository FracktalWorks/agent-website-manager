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
```

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
