---
name: website_analysis
description: >
  Produce decision-oriented website analysis reports for any brand/site —
  website health, SEO, internal-linking/orphans, information architecture,
  content audit, and brand-aware "what to build next" recommendations. Turns
  raw data from the analytical skills into polished, stakeholder-ready
  Artifacts, not JSON dumps.
when_to_use: >
  User asks for a site audit, SEO report, health check, internal-linking/orphan
  analysis, a sitemap/architecture map, "what's working / not working", "areas
  of improvement", or "what pages should we build".
authority: read
cost_tier: 2
version: 0.1.0
---

# Website Analysis & Reporting Skill

The **umbrella** skill for understanding a website end-to-end and delivering the
findings as a clear, decision-oriented report. It does two things the individual
analytical skills don't:

1. **Orchestrates** `content_auditor`, `site_health_monitor`,
   `performance_optimization`, and the SEO/GSC data into one coherent picture.
2. **Delivers** that picture as a polished, self-contained **Artifact** (see the
   design system below) — the format a site owner can read, act on, and share.

## The frame every report must answer

Whatever the report type, it exists to answer five questions about the site —
tailored to *this* brand, its audience, and its goals (rank on Google, be cited
by LLMs, convert sales, serve customers):

1. **What's working** — keep / build on it.
2. **What's not working** — the real problems, ranked by impact.
3. **Areas of improvement** — fixable gaps between current and ideal.
4. **Health** — is anything broken, decaying, or at risk right now.
5. **What to build** — the pages/content the brand is missing, with evidence.

Never hand back a raw metric dump. Lead with the summary and the verdict; put
detail behind it; encode severity in form (chips, color) so it's scannable.

## Report catalog

| Report | Answers | Primary data sources |
|--------|---------|----------------------|
| **Website Health Check** | Health · not-working | `site_inventory.py` (post-types, plugins, sitemaps, URL status) + `site_health_monitor` (PHP, DB, cron, SSL) + Hostinger MCP + DB via phpMyAdmin |
| **SEO Report** | Working · improve · build | Google Search Console (`.tmp/scripts/fetch_search_console.py`) + `onpage_seo_audit.py` + Yoast meta |
| **Internal Linking & Orphan Audit** | Not-working · improve | `link_audit.py` (full-site crawl → inbound-link/orphan/chrome map) |
| **Site Architecture / IA Map** | Working · build | `site_inventory.py` + `link_audit.py` + judgment (built vs. to-build) |
| **Content Audit** | Not-working · improve | `content_auditor` (dupes, thin, broken links) + `onpage_seo_audit.py` (schema, headings, alt) |
| **Page Opportunity Report** | Build | synthesis of SEO gaps + IA holes + brand/capability context |

Most real requests are a **blend** — e.g. "audit the site" = health + linking +
architecture. Run the relevant scripts, then synthesize into one report.

## Scripts (this skill)

| Script | Purpose |
|--------|---------|
| `scripts/wp_client.py` | Shared WP REST client (.env loader, `req()`, output dir). Imported by the others. |
| `scripts/site_inventory.py` | What exists + light health: sitemap inventory by type, post-type published counts, active/inactive plugins, key-URL status |
| `scripts/link_audit.py` | Full-site crawl → per-URL inbound-link count, split into orphan / thin / nav-footer |
| `scripts/onpage_seo_audit.py` | Live-page SEO signals: title, meta, canonical, OG, JSON-LD schema, headings, image-alt, word count, internal links, issue list |
| `scripts/seo_meta.py` | Read / update Yoast title, description, focus keyword (to *execute* fixes) |

```bash
python .github/skills/website_analysis/scripts/site_inventory.py
python .github/skills/website_analysis/scripts/link_audit.py            # full crawl
python .github/skills/website_analysis/scripts/onpage_seo_audit.py --sitemap page
python .github/skills/website_analysis/scripts/seo_meta.py read 31954
```
All scripts read `WORDPRESS_SITE_URL` / `_USERNAME` / `_APP_PASSWORD` from the
repo-root `.env` and write JSON to `outputs/<slug>/`. They are **site-agnostic** —
point `.env` at any WordPress site.

## Deeper DB-level health (bloat, stuck imports, stranded post types)

Some health signals only exist in the database. Get a phpMyAdmin sign-on link via
the Hostinger MCP and run **read-only** SQL:

1. `hosting_listWebsitesV1(domain=...)` → account `username`.
2. `hosting_listAccountDatabasesV1(username=...)` → the WordPress DB name.
3. `hosting_getPhpMyAdminLinkV1(username, name)` → an auto-signon URL.
4. Playwright: navigate the link, then POST SQL to `index.php?route=/sql` with the
   page's `token` and parse the result HTML. Useful queries:
   - `SELECT post_type, post_status, COUNT(*) FROM wp_posts GROUP BY 1,2` (stranded CPTs, drafts, stuck imports)
   - `SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE()` (table bloat)
   - `SELECT option_name, LENGTH(option_value) FROM wp_options WHERE autoload='yes' ORDER BY 2 DESC LIMIT 20` (autoload bloat)

Keep it SELECT-only. See the `kb-content-recovery` memory note for a worked example.

## Reporting workflow

1. **Scope** — decide which report(s) the request maps to; pick the scripts/skills.
2. **Gather** — run the scripts; pull GSC/analytics; DB probe if health is in scope.
3. **Synthesize** — apply judgment. Separate real problems from noise (e.g. nav/footer
   inflating link counts; sidebar images inflating "missing alt"). Rank by impact.
   Triage every finding into fix / improve / leave-or-noindex.
4. **Deliver** — write the report as an **Artifact** using the design system below.
   Lead with the verdict + a metric strip; then prioritized findings; end with the
   recommended next action and open decisions.
5. **Record** — save durable reports/links under `outputs/<slug>/` (or `outputs/seo/`
   for the master plan) and, if it's a reusable reference, a memory note.

## Report design system

All reports share one visual identity so they read as a series. The full token
set + a ready-to-fill skeleton live in:

- `reference/report_design_system.md` — palette, type, status-chip vocabulary,
  layout rules, both light/dark themes.
- `reference/report_template.html` — copy this, fill the content, publish via the
  Artifact tool. (Load the `artifact-design` skill first to calibrate effort.)

House style in brief: a picked warm-neutral ground, one brand accent (per brand —
Fracktal is coral `#d84332`), a **monospace face for URLs/counts/data**, severity
**status chips** (built/good · thin/warn · orphan/critical · to-build · consolidate),
summary-before-detail, and both themes styled via CSS custom properties.

## Composing the other skills

- **Health** → `site_health_monitor` (`wp_health_check.py`) for PHP/DB/cron/SSL.
- **Content quality** → `content_auditor` (`wp_content_audit.py`) for broken links,
  dupes, thin content.
- **Performance** → `performance_optimization` for PageSpeed / Core Web Vitals / LSCache.
- **Infra/DB** → `hostinger_management` / Hostinger MCP.
This skill sits on top and turns their output into the report.

## Required environment

- `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`
- `HOSTINGER_API_TOKEN` (for infra/DB health)
- Optional: `GOOGLE_SEARCH_CONSOLE_SITE`, `PAGESPEED_API_KEY` for SEO/performance depth

## Outputs

Raw data → `outputs/<slug>/*.json`. Finished reports → published Artifacts (record
the URL in the repo, e.g. `outputs/seo/website_overhaul_plan.md`, and in memory).
