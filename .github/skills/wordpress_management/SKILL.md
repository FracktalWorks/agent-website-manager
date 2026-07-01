---
name: wordpress_management
description: >
  Manage WordPress content, plugins, themes, users, comments, media, and SEO
  via the WordPress REST API. Create/edit pages/posts, manage media library,
  configure plugins/themes, moderate comments, and optimize on-page SEO.
when_to_use: "User asks to manage WordPress content, pages, posts, plugins, themes, media, users, comments, or SEO"
authority: write
cost_tier: 2
version: 0.1.0
---

# WordPress Management Skill

Full WordPress site management via the REST API. Create, read, update, and delete
pages, posts, media, users, comments, plugins, themes, and SEO settings.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wp_rest_api.py` | Primary WordPress REST API client — all CRUD operations |
| `scripts/wp_seo_analyze.py` | Analyze on-page SEO and generate optimization recommendations |
| `scripts/wp_plugin_manager.py` | Install, activate, deactivate, update, and delete plugins |

## Usage

```bash
# Check connectivity
python .github/skills/wordpress_management/scripts/wp_rest_api.py --action ping

# List all pages
python .github/skills/wordpress_management/scripts/wp_rest_api.py --action list-pages

# Create a new page
python .github/skills/wordpress_management/scripts/wp_rest_api.py --action create-page \
  --title "About Us" --content "<h2>Our Story</h2><p>...</p>" --status draft

# Update a page
python .github/skills/wordpress_management/scripts/wp_rest_api.py --action update-page \
  --id 42 --title "Updated Title" --content "New content"

# Create a blog post
python .github/skills/wordpress_management/scripts/wp_rest_api.py --action create-post \
  --title "My Post" --content "..." --categories "News" --tags "update,wordpress"

# Upload media
python .github/skills/wordpress_management/scripts/wp_rest_api.py --action upload-media \
  --file ./image.jpg --alt-text "Description"

# SEO analysis
python .github/skills/wordpress_management/scripts/wp_seo_analyze.py --url https://mysite.com/page

# Plugin management
python .github/skills/wordpress_management/scripts/wp_plugin_manager.py --action list
python .github/skills/wordpress_management/scripts/wp_plugin_manager.py --action install --slug elementor
python .github/skills/wordpress_management/scripts/wp_plugin_manager.py --action update --slug yoast-seo
```

## Required Environment Variables

- `WORDPRESS_SITE_URL` — Your WordPress site URL
- `WORDPRESS_USERNAME` — WordPress admin username
- `WORDPRESS_APP_PASSWORD` — WordPress application password

## Outputs

Writes operation results to `outputs/<project-slug>/wp_*.json`.
