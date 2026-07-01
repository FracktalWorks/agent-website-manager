---
name: performance_optimization
description: >
  Analyze page speed (Google PageSpeed Insights), configure LiteSpeed Cache
  (LSCache) on Hostinger, enable browser/object caching, minify CSS/JS,
  optimize critical rendering path, manage CDN, clean database, and measure
  Core Web Vitals — all to improve WordPress loading speeds.
when_to_use: "User asks to improve page speed, optimize performance, set up caching, minify assets, or analyze Core Web Vitals"
authority: write
cost_tier: 2
version: 0.1.0
---

# Performance Optimization & Caching Skill

Comprehensive WordPress performance optimization for Hostinger-hosted sites.
Analyzes page speed, configures LiteSpeed Cache (LSCache), enables server-level
caching, optimizes assets (CSS/JS/images), manages CDN, and measures Core Web
Vitals (LCP, FID/INP, CLS).

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wp_performance.py` | Page speed analysis, Core Web Vitals measurement |
| `scripts/wp_cache_setup.py` | LSCache configuration, cache purging, optimization settings |

## Usage

```bash
# Analyze page speed (uses Google PageSpeed Insights)
python .github/skills/performance_optimization/scripts/wp_performance.py \
  --action analyze --url https://mysite.com

# Analyze all core pages
python .github/skills/performance_optimization/scripts/wp_performance.py \
  --action analyze-all

# Measure Core Web Vitals specifically
python .github/skills/performance_optimization/scripts/wp_performance.py \
  --action web-vitals --url https://mysite.com

# Test from multiple locations (mobile + desktop)
python .github/skills/performance_optimization/scripts/wp_performance.py \
  --action full-audit --url https://mysite.com

# Check current cache status
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action cache-status

# Enable LiteSpeed Cache with recommended settings
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action setup-lscache

# Configure page caching
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action enable-page-cache --ttl 604800

# Enable browser caching
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action enable-browser-cache --expires 31536000

# Enable CSS/JS minification and combination
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action enable-minify --css --js --html

# Enable image lazy loading
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action enable-lazy-load

# Purge all cache
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action purge-all

# Purge cache for a specific URL
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action purge-url --url https://mysite.com/shop

# Configure CDN (Hostinger CDN or Cloudflare)
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action setup-cdn --provider hostinger

# Database optimization (clean revisions, transients, spam)
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action optimize-db --dry-run

# Run complete performance optimization
python .github/skills/performance_optimization/scripts/wp_cache_setup.py \
  --action optimize-all --backup-first
```

## Performance Optimization Checklist

1. **Server-Level**: LiteSpeed Cache enabled, PHP 8.2+, OPcache, Redis object cache
2. **Page Caching**: LSCache page cache with smart purge
3. **Browser Caching**: Long expiry for static assets (images, CSS, JS, fonts)
4. **CSS Optimization**: Minify, combine, inline critical CSS, remove unused CSS
5. **JS Optimization**: Minify, combine, defer non-critical JS, delay JS
6. **Image Optimization**: WebP conversion, lazy loading, responsive images, CDN
7. **Database**: Clean revisions, transients, spam, optimize tables
8. **CDN**: Hostinger CDN or Cloudflare for static assets
9. **Fonts**: Preload critical fonts, font-display: swap, host locally
10. **Third-Party**: Lazy load embeds, async third-party scripts

## Required Environment Variables

- `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`
- `HOSTINGER_API_TOKEN` — For server-level cache control
- `PAGESPEED_API_KEY` (optional) — Google PageSpeed Insights API key

## Outputs

Writes audit reports and optimization logs to `outputs/<project-slug>/perf_*.json`.
