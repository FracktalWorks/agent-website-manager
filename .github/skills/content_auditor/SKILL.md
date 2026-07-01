---
name: content_auditor
description: >
  Audit WordPress content quality — detect broken internal/external links,
  find orphan pages (no inbound links), analyze redirect chains, identify
  thin content pages, check for duplicate titles/meta descriptions, and
  generate a content health report with fix priorities.
when_to_use: "User asks to check broken links, find orphan pages, audit content quality, fix redirects, or analyze site structure"
authority: read
cost_tier: 1
version: 0.1.0
---

# Content Auditor Skill

Comprehensive content quality audit for WordPress sites. Finds broken links
(both internal and external), orphan pages with no navigation path, redirect
chains, thin content, duplicate meta data, and missing Open Graph tags.
Essential for SEO health and user experience.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wp_content_audit.py` | Full content audit — broken links, orphans, quality checks |

## Usage

```bash
# Full content audit (all checks)
python .github/skills/content_auditor/scripts/wp_content_audit.py --action full

# Find broken internal links
python .github/skills/content_auditor/scripts/wp_content_audit.py --action broken-links

# Find broken external (outbound) links
python .github/skills/content_auditor/scripts/wp_content_audit.py --action broken-external

# Find orphan pages (published pages with no inbound internal links)
python .github/skills/content_auditor/scripts/wp_content_audit.py --action orphans

# Check for thin content (< 300 words)
python .github/skills/content_auditor/scripts/wp_content_audit.py --action thin-content --min-words 300

# Find duplicate meta titles
python .github/skills/content_auditor/scripts/wp_content_audit.py --action duplicate-titles

# Find duplicate meta descriptions
python .github/skills/content_auditor/scripts/wp_content_audit.py --action duplicate-descriptions

# Check redirect chains (pages that redirect more than once)
python .github/skills/content_auditor/scripts/wp_content_audit.py --action redirect-chains

# Find pages missing Open Graph / meta tags
python .github/skills/content_auditor/scripts/wp_content_audit.py --action missing-meta

# Analyze internal link structure (most linked-to pages, dead-end pages)
python .github/skills/content_auditor/scripts/wp_content_audit.py --action link-structure

# Audit all content for a specific post type
python .github/skills/content_auditor/scripts/wp_content_audit.py --action audit --type post --limit 50

# Generate content health report with prioritized fixes
python .github/skills/content_auditor/scripts/wp_content_audit.py --action report
```

## What Gets Audited

| Check | What it finds | Severity |
|-------|--------------|----------|
| **Broken internal links** | Links to pages that return 404, 500, or redirect | HIGH |
| **Broken external links** | Outbound links to dead or unreachable sites | MEDIUM |
| **Orphan pages** | Published pages with zero inbound internal links | MEDIUM |
| **Thin content** | Pages with very low word count | MEDIUM |
| **Duplicate titles** | Multiple pages with the same title tag | HIGH |
| **Duplicate meta descriptions** | Multiple pages with identical meta descriptions | LOW |
| **Redirect chains** | Pages that redirect through multiple hops | MEDIUM |
| **Missing meta tags** | Pages without title, description, or OG tags | HIGH |
| **Dead-end pages** | Pages with no outbound internal links | LOW |

## Required Environment Variables

- `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`

## Outputs

Writes audit reports to `outputs/<project-slug>/content_audit_*.json`.
