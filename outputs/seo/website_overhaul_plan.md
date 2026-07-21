# Fracktal Works — SEO & Website Overhaul Plan

**Goal:** Rank #1 in India for 3D printing-related searches, and capture the long tail of underserved queries currently invisible to the site.

**Data source:** Google Search Console, last 90 days (2026-04-03 to 2026-07-02), 250 top queries + 250 top pages by impressions. Non-branded query set analyzed (231 queries, excluding "fracktal"/"fractal works"/product-name searches).

**How to read this plan:** Ordered by effort-to-impact ratio — cheapest, fastest wins first, biggest structural bets last. Each item lists the evidence (real query data) behind it, not a guess.

---

## Phase 0 — Baseline facts

- The homepage gets 12,318 impressions/quarter but ranks at position **15.0 average** and converts at only 7.1% CTR — it is not yet a strong entry point for non-branded search.
- Across the top 25 highest-impression non-branded queries, **average CTR is under 1%** despite decent average position (many are top-10). This is a title/meta-description problem, not a content-does-not-exist problem, for most of these.
- 71 pages currently exist. Material pages (PLA, ABS, TPU, Nylon, PET-G, PC, PVA, Carbon Fiber Nylon), process pages (FDM, SLS, SLA, HPMJF, Vacuum Casting), and industry landing pages (Healthcare, Medical, Dental, Automobile, Entertainment, Jewelry, Engineering, Manufacturing) already exist — the gap is mostly **optimization**, not creation.
- Genuine content gaps are a small, well-defined list (Phase 3).

---

## Phase 1 — Lowest-hanging fruit: fix titles & meta descriptions on existing high-impression pages

**Effort: very low (no new content, just Yoast title/meta rewrites). Impact: highest ROI in this plan.**

These pages already rank on page 1 (or close) and get real impressions, but almost nobody clicks. Fixing the `<title>` and meta description to match actual search intent could 5-10x the click volume on traffic you're already earning.

| Page | Impressions/qtr | Position | CTR | Action |
|---|---:|---:|---:|---|
| `/carbon-fiber-nylon/` | 7,795 | 5.8 | 0.3% | Rewrite title to lead with "Carbon Fiber Nylon (CF-PA) Filament" + price/spec hook; rewrite meta description to answer the query directly |
| `/abs-acrylonitrile-butadiene-styrene/` | 1,878 | 10.8 | 0.2% | Same — target "ABS material" and "ABS filament" directly in title |
| `/pet-g-polyethylene-terephthalate-glycol/` | 1,638 | 6.7 | 0.1% | Same — target "PET-G" and "polyethylene terephthalate glycol filament" |
| `/tpu-thermoplastic-polyurethane/` | 1,546 | 5.3 | 0.1% | Same — target "TPU material" |
| `/kb/about-abs-a-brief-introduction/` | 607 | 24.6 | 0.2% | Merge/de-duplicate with the ABS material page or clearly differentiate (KB vs. commercial page competing for the same query hurts both) |
| `/nylon/` | 1,167 | 11.4 | 0.2% | Rewrite title/meta, target "nylon filament for 3d printing" |
| `/pva-polyvinyl-alcohol/` | 1,190 | 9.7 | 0.4% | Same |
| `/3d-printing-services/` | 2,515 | 11.8 | 0.7% | Rewrite title/meta; also needs Phase 2 content strengthening to break into top 10 |
| `/consulting-services/` | 1,229 | 18.9 | 0.1% | Rewrite title/meta; target "3d print consulting" (150 impr, 0% CTR) directly |
| `/materialdryer/` | 793 | 17.1 | 0.1% | Rewrite title to target "3d powder dryer" (273 impr) and "3d filament dryer" directly |
| `/vaccum-casting/` | 486 | 19.4 | 1.0% | Rewrite title/meta; target "vacuum casting services" (149 impr, 2.0% CTR at position 14.4 — close to breaking through) |

**How to execute:** Use the WordPress REST API / Yoast meta fields (`yoast_head_json` or `_yoast_wpseo_title` / `_yoast_wpseo_metadesc` post meta) to batch-update. I can draft all new titles/descriptions and apply them via script — recommend reviewing drafts before pushing live since these directly affect how the brand appears in search results.

---

## Phase 2 — Strengthen pages stuck on page 2-3 (positions 11-40)

**Effort: medium (content additions, internal linking, schema markup). Impact: high — these are "almost there" pages.**

| Page / Query cluster | Impressions/qtr | Position | Action |
|---|---:|---:|---|
| `/3d-printer-manufacturer-india/` — targets "3d printer manufacturers in india" (257), "indian 3d printers" (48), "3d additive manufacturing companies" (62), "3d manufacturing companies" (44) | ~450 combined | 20-38 | Expand into a comprehensive, comparison-style page (specs table, "why choose Fracktal" section, case studies); add FAQ schema; build internal links from every material/process page back to this page |
| `/3d-printing-services/` | 2,515 | 11.8 | Add detailed service breakdown, pricing tiers or "get a quote" flow, customer logos/case studies, FAQ schema targeting "3d printing service india", "3d printing company" |
| `/kb/about-carbon-fiber-nylon-cf-pa-a-brief-introduction/` vs `/carbon-fiber-nylon/` | 1,486 + 7,795 | 9.4 / 5.8 | Two pages competing for the same query — consolidate into one authoritative page or clearly differentiate intent (KB = technical deep-dive, product page = commercial) and cross-link |
| Docs/KB troubleshooting pages (SMPS not turning on: 2,241 impr pos 5.3; printer doesn't turn on: 1,872 impr pos 6.8; limit switch issues: 2,210 impr pos 5.2) | ~6,300 combined | 5-7 | Already ranking well — these need a **troubleshooting hub page** (see Phase 3) linking them together to capture "3d printing troubleshooting" (82 impr, position 73, currently invisible) |

---

## Phase 3 — New pages: genuine content gaps (zero matching page found)

**Effort: medium-high (net new content). Impact: currently zero traffic captured — any ranking is pure upside.**

| # | New page | Evidence | Notes |
|---|---|---|---|
| 1 | **HSN Code & GST on 3D Printing / 3D Printed Products in India** | "3d printing hsn code" (98 impr), "3d printed parts hsn code" (36), "gst on 3d printed products" (45), "3d printed products hsn code" (12) — **4 distinct queries, zero pages exist for any** | High commercial intent — B2B buyers researching this are usually finance/procurement doing due diligence before a purchase. Low competition expected for India-specific tax content. |
| 2 | **3D Printing Troubleshooting Hub** | "3d printing troubleshooting" (82 impr, pos 73), "3d print troubleshooting" (15 impr, pos 55) | You already have strong-ranking individual troubleshooting docs (Phase 2) — this page aggregates/links them and captures the umbrella query. |
| 3 | **Metal 3D Printing (service/page)** | "3d metal printer companies" (12 impr), "3d metal printing company" (1), "3d metal printing service" (1), "3d metal printer service" (1) | Currently zero presence. Confirm first whether Fracktal actually offers metal printing — only build this page if it's a real capability. |
| 4 | **3D Printing "Near Me" / Location pages** (e.g., Bangalore) | "3d filament near me" (3), "3d miniature near me" (2), "3d designer near me" (1), "3d print filament shop near me" (2), "3d printing machine manufacturers in bangalore" (11 impr, pos 7.4, 18.2% CTR — already converting well despite low volume), "3d print in bangalore" (1) | Local SEO play — a location/service-area page with Google Business Profile alignment. Bangalore-specific query already shows the best CTR in the entire non-branded set (18.2%) at a decent position — strong signal this pattern works. |
| 5 | **3D Printed Wearables / Fashion Accessories (dedicated page)** | "3d printed wearable devices" (56 impr, pos 18, 0% CTR), "3d printed wearable market" (13), "3d printed fashion accessories" (11), "3d printed clothing accessories" (2) | A blog post exists (`3d-printing-fashion-wearable-technology`, 1,211 impr, pos 11.5) but it's editorial, not a commercial/service page — consider a dedicated industry page similar to Jewelry/Automobile if this is a real service line. |
| 6 | **3D Printed Jigs & Fixtures (service query variant)** | "3d printed jigs and fixtures service" (3), "3d printed jigs and fixtures" (2) | Page exists at `/manufacturing-landing-page/jigs-fixtures/` but isn't appearing in top 250 queries — verify it's indexed and internally linked; may just need Phase 1-style optimization instead of a new page. |
| 7 | **3D Printing Adhesives / Bed Adhesion (consolidated page)** | Cluster: "3d printer glue" (86), "3d printing glue" (77), "3d print glue" (44), "print stick"/"printstick" (already has a product page — 2,220 impr, pos 6.9), "3d printing adhesive" (16), "3d print bed adhesive" (2), "3d bed adhesive" (1) | PrintStick product page exists but isn't capturing the generic "3d print glue"/"bed adhesion" search cluster — build a comparison/guide page ("Best 3D Print Bed Adhesion Solutions") that ranks for the generic terms and funnels to the PrintStick product page. |

---

## Phase 4 — Structural / technical SEO (site-wide, higher effort, compounding impact)

**Effort: high. Impact: multiplies the effect of everything above.**

1. **Fix the homepage.** 12,318 impressions/quarter at position 15 and 7.1% CTR is the single biggest average-position problem on the site relative to its traffic volume. Needs: clear H1 targeting "3D Printer Manufacturer India", trust signals above the fold, and internal links fanning out to every material/process/industry page.
2. **Internal linking pass.** Many high-performing pages (materials, KB docs) don't appear to link to the commercial pages that should benefit from their authority (e.g., material pages → 3D Printing Services page, troubleshooting docs → main product pages). A structured internal-linking sweep compounds every ranking gain above.
   > **See the [Internal Linking & Orphan Audit — 6 Jul 2026](https://claude.ai/code/artifact/9135b65f-e6f4-45d3-9f06-60857945da71)** for the current inbound-link map: which pages are well-linked vs. thin, and exactly where the sweep should add links.
3. **Schema markup audit.** Add/verify Product schema on material and printer pages, FAQ schema on service pages, Organization schema site-wide. Improves CTR even without ranking changes (rich snippets).
4. **Duplicate/competing content cleanup.** At least two clear cases found (ABS commercial page vs. KB intro page; Carbon Fiber Nylon commercial page vs. KB intro page) where two pages compete for the same query and likely cannibalize each other's ranking. Needs a full duplicate-title/duplicate-meta audit — the `content_auditor` skill already in this repo can run this (`wp_content_audit.py --action duplicate-titles`).
5. **Orphan page check.** Several docs-category and KB pages get meaningful impressions but may not be linked from anywhere prominent on the site (worth running `wp_content_audit.py --action orphans`).
   > **✅ Done — 6 Jul 2026 · [Internal Linking & Orphan Audit (interactive report)](https://claude.ai/code/artifact/9135b65f-e6f4-45d3-9f06-60857945da71).**
   > Full-site crawl of all 91 sitemap URLs: **23 orphans** (0 inbound links), **23 contextually linked** (12 of them "thin", ≤2 links), **45 well-linked** (in nav/footer). Root cause is a **fragmented service architecture** — the optimized `/manufacturing-landing-page/*` landing set is fully orphaned, and the `/3d-printing-services/` hub has only 2 inbound links. The report triages every orphan (fix / strengthen / noindex-or-delete) and recommends consolidating the three overlapping service-page sets as the single highest-leverage move. Also flags: `/privacy-policy/` appears orphaned while other legal pages are footer-linked (verify for compliance).

---

## Suggested execution order

1. Phase 1 (title/meta rewrites) — can start immediately, no content creation needed, highest ROI
2. Phase 4.4 (duplicate content cleanup) — should happen alongside Phase 1 since some Phase 1 targets are the duplicate-content pages
3. Phase 3, item 1 (HSN/GST page) — fastest net-new page to write, clear zero-competition opportunity
4. Phase 2 (strengthen near-miss pages) — homepage and services page first
5. Phase 3, remaining items — prioritize by whether the capability is real (metal printing, wearables) vs. speculative
6. Phase 4, remaining items (internal linking, schema) — ongoing, run after each new/updated page

---

## What I can execute directly vs. what needs your input

**I can execute directly (with your go-ahead each time, as we've been doing):**
- Rewrite and apply Yoast titles/meta descriptions (Phase 1)
- Run duplicate-title/orphan-page audits (Phase 4.4/4.5)
- Draft new page content and page structure for Phase 3 pages
- Add FAQ/Product schema where Yoast supports it

**Needs your input before I proceed:**
- Confirm whether metal 3D printing is a real service (Phase 3, item 3) — don't want to build a page for a capability that doesn't exist
- Confirm whether wearables/fashion is a service line or was a one-off blog topic (Phase 3, item 5)
- Priority call on Bangalore/location page — needs your Google Business Profile details if we want to align it properly
- Final review of all title/meta rewrites before they go live (brand voice, accuracy)
