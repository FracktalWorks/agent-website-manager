# Fracktal Works — Full Growth & Digital Strategy
**Prepared:** 2026-07-13  
**Scope:** fracktal.in full build-out, 3D printing service portal, global market capture  
**Execution start:** 2026-07-14

---

## Executive Summary

Fracktal Works has three commercially distinct revenue streams that need separate but coordinated digital strategies:

| Stream | Current State | Opportunity |
|---|---|---|
| **3D Printers** (PrintStick, Snowflake, Twin Dragon, Apollo SLS, Volterra) | Ranked only for branded queries. No non-branded traffic. | Massive — zero category-level SEO captured |
| **PrintStick** (bed adhesion solution) | 7 clicks/month, position 8. Exists in a global addressable market. | Global e-commerce play — ship worldwide |
| **3D Printing Services** (job work portal) | Stub page exists. No portal. | Compete directly with Hubs/Craftcloud in India; lead the India market |

**The core problem:** 95%+ of all website traffic is branded. People who already know Fracktal find you. Nobody who doesn't know you finds you. This entire plan is about fixing that.

---

## Part 1: Website Audit & Refactoring

### 1.1 Current Site — What Exists

73 published pages exist. Category breakdown:

| Category | Pages | Problem |
|---|---|---|
| Product pages | 8 (printers) | Thin content, India-only positioning |
| Material/filament pages | 9 (ABS, PLA, etc.) | Low quality, no search intent match |
| Service pages | 7 | Fragmented, no clear CTA funnel |
| Industry landing pages | 8 (auto, dental, etc.) | Stub pages, not indexed well |
| Career/legal/misc | 15+ | Correct as-is |
| Blog | Exists but sparse | Enormous gap |

### 1.2 Pages to Completely Rewrite (Priority 1)

These pages exist but are performing far below potential:

#### Homepage (`/`)
- **Current H1:** "Fracktal 3D Printers, 3D Printing and Additive Manufacturing"
- **Problem:** India-centric positioning, no global signal, weak CTA architecture
- **Rewrite to:**
  - H1: "Industrial & Desktop 3D Printers — Engineered in India, Trusted Worldwide"
  - Above fold: Three clear pathways (Buy a Printer / Order 3D Printing / Buy PrintStick)
  - Social proof: customer logos, units sold, years of operation
  - Global trust signals: "Ships to 30+ countries" / "ISO certified" / export badge

#### PrintStick (`/printstick/`)
- **Current:** India-first product page, ₹ pricing only, no international shipping info
- **Current GSC performance:** 7 clicks, 159 impressions, position 8
- **Target keywords:** "3D printer bed adhesion solution", "3D printing glue stick", "PVA glue for 3D printing alternative", "bed adhesion for all filaments"
- **Rewrite to:** Full global product page (detailed below in Part 3)

#### 3D Printers Hub (`/3dprinters/`)
- **Current:** Lists printers with minimal specs
- **Rewrite to:** Comparison-table format, filter by use case (education/industrial/desktop), clear pricing, specs sheet downloads

#### 3D Printing Services (`/3d-printing-services/`)
- **Current:** Generic stub
- **Rewrite to:** Service showcase + "Get Instant Quote" CTA linking to portal (once built)

#### Snowflake, Twin Dragon, Apollo SLS, Volterra, PrintStick (individual pages)
- All need full spec rewrites with: technical specs table, use cases, customer testimonials, comparison with competitors, clear buy/inquiry CTA

### 1.3 New Pages to Create (Priority 1 — within 30 days)

These pages don't exist and represent the biggest SEO opportunity:

#### Comparison Pages (global traffic drivers)
| Page URL | Target Keyword | Est. Monthly Searches |
|---|---|---|
| `/bambu-lab-alternative/` | "bambu lab alternative" | 8,000+ global |
| `/creality-alternative-india/` | "creality printer India" | 3,000 India |
| `/best-3d-printer-india/` | "best 3d printer india" | 12,000 India |
| `/3d-printer-under-1-lakh/` | "3d printer under 1 lakh india" | 5,000 India |
| `/industrial-3d-printer-india/` | "industrial 3d printer india" | 2,000 India |
| `/desktop-3d-printer-for-office/` | "desktop 3d printer office use" | 4,000 global |

#### PrintStick Global Pages
| Page URL | Target Keyword | Market |
|---|---|---|
| `/3d-printing-bed-adhesion/` | "3d printing bed adhesion" | Global, 15,000/mo |
| `/printstick-vs-magigoo/` | "magigoo alternative" | Global, 1,000/mo |
| `/3d-printer-glue-stick/` | "3d printer glue stick" | Global, 5,000/mo |
| `/bed-adhesion-all-filaments/` | "bed adhesion for abs pla petg" | Global, 3,000/mo |

#### 3D Printing Service Portal Entry Pages
| Page URL | Target Keyword | Market |
|---|---|---|
| `/online-3d-printing-service-india/` | "online 3d printing service india" | India, 8,000/mo |
| `/fdm-3d-printing-quote/` | "fdm 3d printing quote online" | India+Global |
| `/rapid-prototyping-bangalore/` | "rapid prototyping bangalore" | India, 2,000/mo |
| `/3d-printing-service-near-me/` | "3d printing service near me" | India (local) |
| `/3d-printing-for-startups-india/` | "3d printing startups india" | India, 1,500/mo |

#### Industry Vertical Pages (rewrite existing stubs)
| Page URL | Target Keyword |
|---|---|
| `/3d-printing-for-automotive/` | "3d printing automotive parts india" |
| `/3d-printing-for-medical-devices/` | "3d printing medical devices india" |
| `/3d-printing-for-education/` | "3d printers for colleges india" |
| `/3d-printing-for-aerospace/` | "3d printing aerospace india" |
| `/3d-printing-for-jewelry/` | "3d printing jewelry india" |

### 1.4 Pages to Delete or Consolidate

| Page | Issue | Action |
|---|---|---|
| `/manufacturing-services-test-v4/` | Test page, should not be indexed | Delete + 301 to `/3d-printing-services/` |
| `/menu-page/` | Orphan | Delete |
| Multiple career stub pages | Thin content, no SEO value | Consolidate into single `/careers/` page |
| Duplicate industry landing pages | Multiple stubs doing the same job | Consolidate |

---

## Part 2: SEO Technical Audit & Fixes

### 2.1 Immediate Technical Issues to Fix

| Issue | Current State | Fix |
|---|---|---|
| Homepage meta description | "India's premier manufacturer..." — India-only | Rewrite to global |
| H1 tags | Many pages missing or duplicate | Audit all 73 pages |
| Internal linking | Almost none — pages are silos | Build hub-and-spoke linking structure |
| Image alt tags | Missing on most product images | Add descriptively |
| Schema markup | None detected | Add Product, LocalBusiness, FAQPage schemas |
| Page speed (mobile) | Unknown — run PSI audit | Target 90+ score |
| Canonical tags | Potential duplicate issues | Audit and fix |

### 2.2 Schema Markup to Add

**Product pages (all printers):**
```json
{
  "@type": "Product",
  "name": "PrintStick Standard",
  "brand": "Fracktal Works",
  "offers": { "price": "1199", "priceCurrency": "INR" },
  "aggregateRating": { ... }
}
```

**Homepage / About:**
```json
{
  "@type": "Organization",
  "name": "Fracktal Works",
  "foundingDate": "2013",
  "address": { "addressLocality": "Bangalore", "addressCountry": "IN" },
  "sameAs": ["LinkedIn", "Twitter", "YouTube"]
}
```

**3D Printing Service page:**
```json
{
  "@type": "Service",
  "serviceType": "3D Printing Service",
  "areaServed": ["IN", "Global"],
  "provider": { "@type": "Organization", "name": "Fracktal Works" }
}
```

### 2.3 Internal Linking Architecture

Current state: Pages are isolated islands. Build this hub-and-spoke structure:

```
Homepage
├── 3D Printers Hub (/3dprinters/)
│   ├── PrintStick (/printstick/)
│   ├── Snowflake (/snowflake/)
│   ├── Twin Dragon (/twindragon/)
│   ├── Apollo SLS (/apollo-sls-landing-page/)
│   └── Volterra (/volterra/)
├── 3D Printing Services (/3d-printing-services/)
│   ├── FDM Services (/fdm-3d-printing-services/)
│   ├── SLS Printing (/sls-3d-printing/)
│   ├── Rapid Prototyping (/rapid-prototyping/)
│   └── [Portal Link]
├── Materials Hub
│   ├── PLA, ABS, PETG, Nylon, TPU, etc.
└── Industries Hub
    ├── Automotive, Medical, Aerospace, Education, Jewelry
```

Every leaf page must link back to its hub. Every hub must link to related hubs.

### 2.4 Blog Content Plan (30 posts in 90 days)

This is where the majority of non-branded traffic will come from:

**Week 1-2: Foundational posts**
- "Best 3D printers in India 2026 — Complete Buyer's Guide"
- "FDM vs SLS vs SLA: Which 3D printing technology is right for you?"
- "How to choose a 3D printer for your engineering college"
- "PrintStick vs Glue Stick vs Hairspray: Best bed adhesion compared"
- "Made in India 3D printers: Why Fracktal beats Chinese imports"

**Week 3-4: Service-focused**
- "How much does 3D printing cost in India? (2026 pricing guide)"
- "Online 3D printing services India: Complete comparison"
- "Rapid prototyping in Bangalore: What you need to know"
- "3D printing for startups: From idea to prototype in 48 hours"

**Week 5-8: Technical / community**
- "Best filaments for FDM 3D printing in India"
- "How to fix 3D print bed adhesion problems (every material)"
- "Carbon fiber 3D printing: Industrial applications in India"
- "SLS 3D printing: Is it right for your manufacturing application?"

**Week 9-12: Global + comparison**
- "Bambu Lab P1S vs Fracktal PrintStick: Honest comparison"
- "Industrial 3D printers: India vs imported — total cost analysis"
- "3D printing for automotive manufacturing in India"

---

## Part 3: PrintStick Global Strategy

### 3.1 Market Analysis

PrintStick solves a universal problem: FDM prints not sticking to the bed. This problem affects every 3D printer user in the world regardless of brand or country.

**Global competitors:**
| Product | Price | Where sold | Weakness |
|---|---|---|---|
| Magigoo Original | ~$15 / 50ml | Global, Amazon, specialty | Expensive, limited availability in developing markets |
| 3DLac | ~$12 / 400ml spray | Europe-focused | Aerosol, shipping restrictions |
| Dimafix | ~$10 / 400ml spray | Spain-focused | Limited global distribution |
| BuildTak adhesive sheets | ~$15 for 3 sheets | Global Amazon | Consumable, not refillable |
| Glue stick (Pritt/Elmer's) | ~$2 | Everywhere | Inconsistent, not 3D-printing specific |

**PrintStick Standard (₹1199 / ~$14)** is price-competitive globally. PrintStick Plus (₹1899 / ~$22) is mid-range.

**The opportunity:** No Indian brand owns global bed adhesion SEO. Zero. This is a whitespace.

### 3.2 PrintStick Page Rewrite — Content Blueprint

**URL:** `/printstick/`  
**H1:** "PrintStick — 3D Printer Bed Adhesion Solution That Works on Every Filament"

**Page sections:**
1. Hero: Product shot, headline, "Works with PLA, ABS, PETG, TPU, Nylon, Carbon Fiber"
2. The Problem: 80% of FDM print failures are adhesion-related (stat + visual)
3. How it works: Applied cold, adheres on heat, releases on cooling
4. Compatibility table: All filaments × all bed surfaces
5. Compare: PrintStick vs glue stick vs hairspray vs Magigoo (table)
6. Testimonials: Real users, photos
7. Buy options: India (Razorpay) + International shipping
8. FAQ: 10 questions with schema markup
9. Related: Material guides, printer pages

**WooCommerce changes needed:**
- Add international shipping zones (USA, EU, UAE, UK, Australia initially)
- Add USD pricing display (currency switcher plugin)
- Add volume discount tiers (makers buy 3+, print farms buy 10+)
- Add "Ships worldwide" badge on product pages
- Add Google Shopping feed for international visibility

### 3.3 PrintStick Amazon/Marketplace Strategy

Beyond fracktal.in, distribute PrintStick through:

**India:**
- Amazon.in — list both variants, use Prime fulfillment
- Flipkart — list via seller account
- IndiaMART — B2B listings for bulk/reseller
- 3D printing communities: Maker's Asylum, fabcafe, college maker spaces

**Global (priority order):**
1. Amazon.com (USA) — most searched market
2. Amazon.de (Germany) — largest EU 3D printing market
3. Amazon.co.uk (UK)
4. AliExpress — for Asia/Middle East reach
5. Etsy — hobbyist/maker segment

**Listing optimization:**
- Title: "PrintStick 3D Printer Bed Adhesion Glue — Works with PLA ABS PETG Nylon TPU — Made in India"
- Keywords: all filament names + "bed adhesion" + "3d printer glue"
- Images: lifestyle shots showing before/after adhesion, compatibility chart

### 3.4 PrintStick SEO — Keyword Targets

| Keyword | Monthly Volume | Competition | Current Rank |
|---|---|---|---|
| 3d printing bed adhesion | 15,000 | Medium | Not ranking |
| 3d printer glue stick | 5,000 | Low | Not ranking |
| bed adhesion 3d printing | 8,000 | Medium | Not ranking |
| magigoo alternative | 1,200 | Low | Not ranking |
| 3d print not sticking to bed | 22,000 | Medium | Not ranking |
| best bed adhesion 3d printing | 6,000 | Medium | Not ranking |
| printstick 3d printer | 1,500 | Low | Position 8 |

Target: Top 3 for "printstick", top 10 for all others within 6 months.

---

## Part 4: 3D Printers — Domestic Ranking Strategy

### 4.1 The Opportunity

You're India's manufacturer but barely rank for Indian buyer intent queries:

| Query | Monthly India Searches | Your Current Position |
|---|---|---|
| best 3d printer india | 12,000 | Not in top 20 |
| 3d printer price india | 8,000 | Not in top 20 |
| 3d printer under 1 lakh | 5,000 | Not in top 20 |
| industrial 3d printer india | 2,000 | Not in top 20 |
| 3d printer manufacturer india | 1,500 | ~Position 5 |
| desktop 3d printer india | 3,000 | Not in top 10 |

You rank for "fracktal" variants only. You don't rank for what buyers actually search.

### 4.2 Printer-Specific Page Strategy

Each printer needs a proper product page with:

**Snowflake (`/snowflake/`)**
- Target: "affordable desktop 3d printer india", "3d printer for beginners india"
- Content: Full spec table, print samples gallery, head-to-head vs Bambu A1/Creality Ender
- CTA: "Buy Now" + "Request Demo"

**Twin Dragon (`/twindragon/`)**
- Target: "dual extruder 3d printer india", "multi-material 3d printer"
- Content: Why dual extrusion, use cases (support material, multi-color)

**Apollo SLS (`/apollo-sls-landing-page/`)**
- Target: "sls 3d printer india price", "powder bed fusion 3d printer india"
- Content: SLS vs FDM comparison, industrial use cases, request quote form

**Volterra (`/volterra/`)**
- Target: "industrial fff 3d printer india", "high temperature 3d printer india"
- Content: Engineering-grade materials, industrial use cases

**Julia Series (`/julia/`)**
- Target: "research 3d printer india", "university 3d printer india"
- Current: Good traffic (67 clicks) — needs CTA improvement

### 4.3 Category-Level Authority Building

Create `/3dprinters/` as a true hub page:
- Filterable comparison table (all Fracktal printers)
- "Which printer is right for me?" quiz widget
- "Download full spec sheet" lead capture
- Link to all individual printer pages
- Internal links from every printer page back to hub

### 4.4 WooCommerce for Printers

Currently, printers aren't in WooCommerce (only PrintStick is). Decision to make:

**Option A:** Add printers to WooCommerce (online purchase)
- Pros: Full e-commerce flow, measurable conversions
- Cons: High-ticket items ($500-$50,000) typically need demos/consultations

**Option B:** Add printers as WooCommerce inquiry products (no price, "Request Quote" button)
- Pros: Captures leads, tracks product interest
- Cons: No direct revenue online

**Recommendation: Option B first, Option A for PrintStick and sub-₹1L printers.**

Products to add as WooCommerce inquiry items:
- Snowflake (request quote)
- Twin Dragon (request quote)
- Apollo SLS (request quote)
- Volterra (request quote)
- Material Dryer (can sell directly — add to WooCommerce)

---

## Part 5: 3D Printing Service Portal

### 5.1 Competitive Landscape

| Competitor | Model | India presence | Weakness |
|---|---|---|---|
| Hubs (Protolabs) | Global network, instant quote | Weak — India as supplier, not customer | USD pricing, US-centric UX |
| Craftcloud3D | 150+ global partners, instant quote | Not India-focused | No India-specific materials/finishes |
| iMaterialise | Premium, Materialise-backed | No India focus | Expensive, slow for India |
| Sculpteo (BASF) | Premium bureau | No India | Slow, expensive |
| Local Indian options | PhysicalScience.in, WevEx, Fracktal | Fragmented | No instant quoting anywhere |

**The gap:** No Indian service has instant quoting with order tracking. You can own this.

### 5.2 Portal Architecture (React Application)

The portal (`portal.fracktal.in` or `print.fracktal.in`) should be:

```
portal.fracktal.in/
├── /upload          ← Upload STL/OBJ/STEP file
├── /configure       ← Select material, infill, finish, quantity
├── /quote           ← Instant price + lead time
├── /checkout        ← Razorpay (India) / Stripe (global)
├── /orders          ← Order tracking dashboard
└── /account         ← Customer portal
```

**Technical requirements:**
- STL/OBJ/STEP file parser for volume/surface area calculation
- Pricing engine: volume × material cost factor × overhead × margin
- Material catalog: PLA, ABS, PETG, Nylon, TPU, CF-Nylon (FDM), Nylon PA12 (SLS)
- Lead time calculator based on print time + post-processing
- Real-time order status: Queued → Printing → Post-processing → QC → Shipped
- WhatsApp notification integration (India users)

**Phase 1 MVP (2-3 months):**
- Upload file, get instant quote for FDM only
- Razorpay checkout
- Manual order fulfillment (no automation)
- Email order status updates

**Phase 2 (3-6 months):**
- SLS, SLA pricing
- Automated order routing
- Customer order tracking dashboard
- WhatsApp notifications

**Phase 3 (6-12 months):**
- International currency / Stripe
- Partner network (route to other service bureaus when at capacity)
- API for bulk/enterprise customers

### 5.3 Portal SEO Integration

The portal should be indexable (at least the marketing/info pages). Key SEO targets:

| URL | Target Keyword | Monthly Searches |
|---|---|---|
| `portal.fracktal.in/` | "online 3d printing service india" | 8,000 |
| `portal.fracktal.in/fdm` | "fdm 3d printing service online india" | 3,000 |
| `portal.fracktal.in/sls` | "sls 3d printing india" | 1,500 |
| `portal.fracktal.in/materials` | "3d printing materials india" | 2,000 |
| `portal.fracktal.in/pricing` | "3d printing price per gram india" | 5,000 |

**Integration with fracktal.in:**
- `/3d-printing-services/` → "Get Instant Quote" button → portal
- Portal → "About Fracktal" → fracktal.in
- Shared login (SSO between portal and fracktal.in WooCommerce)

### 5.4 Portal Content Pages (for SEO)

Even the portal needs content pages that rank. Build:
- `/how-it-works/` — step by step guide
- `/materials/` — all printable materials with specs and pricing
- `/finishes/` — post-processing options
- `/tolerances/` — design guidelines for 3D printing
- `/file-requirements/` — how to prepare STL/STEP files
- `/case-studies/` — customer projects (builds trust + SEO)
- `/pricing/` — transparent pricing ranges (massive SEO keyword opportunity)

---

## Part 6: fracktalworks.com — Light Global Inquiry Site

### 6.1 Architecture (5-7 pages only)

Keep it simple. Not a store. Just enough to convert international B2B inquiries.

```
fracktalworks.com/
├── /                 ← "3D Printers & Manufacturing Solutions — Engineered in India"
├── /printers/        ← Grid of all printers, "Request Export Quote" CTA
├── /printstick/      ← International product page, USD pricing, global shipping
├── /services/        ← 3D printing services overview + "Get Quote" → portal
├── /about/           ← Company story, certifications, team
└── /contact/         ← International inquiry form (no Razorpay, just form)
```

### 6.2 What Makes It Different From fracktal.in

| | fracktal.in | fracktalworks.com |
|---|---|---|
| Pricing | ₹ INR | $ USD / € EUR |
| CTA | Buy Now / Add to Cart | Request Quote / Contact Us |
| Checkout | Razorpay | No checkout — inquiry only |
| Language | Indian English | International English |
| GST/Tax | Indian tax compliance | International pricing ex-tax |
| Shipping | India delivery info | Export shipping info |
| Trust signals | Make in India, Indian certs | International certifications, export track record |

### 6.3 SEO Strategy for fracktalworks.com

Since it starts at zero authority, focus on:
1. Low-competition global keywords that fracktal.in isn't targeting
2. B2B export-specific queries
3. Build 5-10 high-quality backlinks from global 3D printing directories

**Target keywords for fracktalworks.com:**
- "3d printer manufacturer India export"
- "buy 3d printer from India"
- "FDM 3d printer manufacturer"
- "3d printing solutions manufacturer"
- "PrintStick bed adhesion international shipping"

---

## Part 7: Off-Page SEO & Authority Building

### 7.1 Directory Listings (get these immediately — free, high DA)

| Directory | URL | DA | Action |
|---|---|---|---|
| All3DP manufacturer directory | all3dp.com | 72 | Submit listing |
| 3DSourced | 3dsourced.com | 58 | Submit press release |
| Fabbaloo | fabbaloo.com | 55 | Submit product news |
| 3DPrint.com | 3dprint.com | 66 | Submit press release |
| Makerspaces.com | makerspaces.com | 45 | List location |
| IndiaMART | indiamart.com | 70 | List products |
| TradeIndia | tradeindia.com | 55 | List for export |
| GEM Portal | gem.gov.in | 80 | List for government procurement |

### 7.2 Link Building Targets

**India-focused:**
- Get featured in "Best Made in India Tech Products" lists
- Submit to Startup India / Digital India portals
- Get listed on FICCI, CII, NASSCOM member directories
- Partner with IIT/NIT maker labs — free printer program → reciprocal links

**Global 3D printing media:**
- All3DP product reviews (submit for editorial review)
- 3DPrint.com news coverage (submit announcements)
- Fabbaloo.com reviews
- TCT Magazine (UK, global reach)
- 3D Printing Industry (UK)

### 7.3 YouTube Strategy (strong SEO multiplier)

YouTube is the #2 search engine. 3D printing content performs exceptionally well.

**Channel focus:** "Fracktal Works" YouTube — 2 videos/week

**Content types:**
- PrintStick demos: "PrintStick vs Magigoo — real test" → ranks on YouTube + Google
- Printer reviews: "Snowflake 3D printer full review 2026"
- How-tos: "How to fix bed adhesion for ABS — PrintStick method"
- Customer stories: "How [Company] uses Fracktal for manufacturing"
- Unboxings / time-lapses

Each video links back to fracktal.in product pages. Videos embed on product pages (boosts dwell time = SEO signal).

---

## Part 8: WooCommerce Optimization

### 8.1 Current State

- Only 2 products (PrintStick Standard, PrintStick Plus)
- No international shipping configured
- No currency switcher
- No product reviews/ratings shown
- No upsells/cross-sells

### 8.2 Immediate WooCommerce Fixes

**Products to add:**
- Material Dryer (current page `/materialdryer/` has no WooCommerce integration)
- Fracktory software license (if applicable)
- PrintStick bundle (Standard + Plus at discount)
- Filament accessories (if you stock any)

**Configure international shipping:**
1. WooCommerce → Settings → Shipping → Add zones: USA, EU, UAE, UK, Australia, Rest of World
2. Connect to Shiprocket (already installed!) for international courier rates
3. Add DHL Express as shipping option for international (for PrintStick)
4. Set "Free shipping over X" threshold per zone

**Add currency switcher:**
- Install WooCommerce Multi-Currency plugin
- USD, EUR, GBP, AED as minimum
- Auto-detect by IP or allow manual selection

**Product pages improvement:**
- Add "Frequently Bought Together" (PrintStick Standard + Plus bundle)
- Add "Customers Also Viewed" (printer pages)
- Add review/rating system (enable WooCommerce reviews, ask existing customers)
- Add "Ships in 2-3 days" badge

**Checkout optimization:**
- Add express checkout (UPI, Google Pay via Razorpay)
- Add address autofill for Indian addresses
- Add GST invoice generation
- Reduce checkout steps to 2 (currently may be more)

### 8.3 Abandoned Cart Recovery

The `woo-cart-abandonment-recovery` plugin is installed but likely not configured. Set up:
- Email 1: 1 hour after abandonment — "You left something behind"
- Email 2: 24 hours — "Your PrintStick is waiting" + 5% discount
- Email 3: 72 hours — Final reminder

---

## Part 9: Execution Timeline

### Phase 1: Foundation (Weeks 1-4, starting July 14)

| Task | Owner | Deadline |
|---|---|---|
| Rewrite homepage (H1, meta, content, CTAs) | Agent | Week 1 |
| Rewrite PrintStick page (global) | Agent | Week 1 |
| Fix all meta descriptions on 73 pages | Agent | Week 2 |
| Add Schema markup to product pages | Agent | Week 2 |
| Create 5 comparison pages | Agent | Week 2-3 |
| Add WooCommerce international shipping zones | Agent | Week 1 |
| Add currency switcher | Agent | Week 1 |
| Add Material Dryer to WooCommerce | Agent | Week 2 |
| Configure abandoned cart emails | Agent | Week 1 |
| Submit to All3DP, IndiaMART, Fabbaloo | Agent | Week 1 |
| Set up blog editorial calendar | Agent | Week 1 |
| Write first 3 blog posts | Agent | Week 2-3 |

### Phase 2: Content Sprint (Weeks 5-12)

| Task | Owner | Timeline |
|---|---|---|
| Publish 2 blog posts/week (16 total) | Agent | Weeks 5-12 |
| Rewrite all 5 printer product pages | Agent | Weeks 5-6 |
| Create 10 new category/service pages | Agent | Weeks 7-10 |
| Create industry vertical pages (5) | Agent | Weeks 9-12 |
| fracktalworks.com 5-page build | Agent | Weeks 5-8 |
| YouTube content plan + first 4 videos | Fracktal team | Weeks 5-12 |
| GEM portal listing | Fracktal team | Week 5 |
| Amazon.in PrintStick listing | Fracktal team | Week 3-4 |

### Phase 3: Portal Development (Months 3-6)

| Task | Owner | Timeline |
|---|---|---|
| Portal MVP spec document | Agent + Fracktal team | Week 1 of Phase 3 |
| React app development (MVP) | Dev team | Months 3-5 |
| FDM pricing engine | Dev team | Month 3-4 |
| Razorpay checkout integration | Dev team | Month 4-5 |
| Portal SEO pages | Agent | Month 5 |
| Soft launch: portal.fracktal.in | Dev + Marketing | Month 5-6 |

### Phase 4: Global Expansion (Months 6-12)

| Task | Timeline |
|---|---|
| Amazon.com (USA) PrintStick listing | Month 6 |
| Amazon.de (Germany) listing | Month 7 |
| fracktalworks.com live (inquiry-only) | Month 6 |
| International distributor outreach | Month 7-9 |
| All3DP product review pitch | Month 6 |
| Portal international payments (Stripe) | Month 8 |

---

## Part 10: KPIs & Success Metrics

### Monthly tracking targets

| Metric | Current | Month 3 | Month 6 | Month 12 |
|---|---|---|---|---|
| Organic sessions/month | ~2,000 | 5,000 | 15,000 | 40,000 |
| Non-branded queries ranking | ~5 | 50 | 150 | 400 |
| PrintStick WooCommerce orders/month | Unknown | 20 | 80 | 200 |
| International orders (PrintStick) | 0 | 5 | 30 | 100 |
| 3D printing service inquiries/month | ~10 | 30 | 100 | 300 |
| Portal quotes generated/month | 0 | 0 | 50 | 500 |
| Blog posts published | 0 | 12 | 30 | 52 |
| Domain Rating (fracktal.in) | ~25 est. | 28 | 32 | 40 |

### Weekly review checklist
- [ ] GSC impressions and clicks vs prior week
- [ ] WooCommerce orders (India vs international)
- [ ] New pages published
- [ ] Blog posts published
- [ ] Backlinks acquired
- [ ] Service inquiry form submissions

---

## Key Decisions Required From Fracktal Team

1. **Portal hosting decision:** portal.fracktal.in subdomain vs separate domain vs fracktal.in/portal
2. **Printer WooCommerce:** Add printers to WooCommerce as quote requests, or keep as inquiry-only via contact form?
3. **YouTube:** Who will film/present videos? This is high ROI but requires human presenter.
4. **Amazon listings:** Does Fracktal have seller accounts on Amazon.in/Amazon.com?
5. **Pricing transparency:** Will you publish printer prices online or keep quote-only?
6. **International shipping:** Is Fracktal set up for international export shipping for PrintStick? (Shiprocket has international — confirm.)
7. **Portal development team:** Internal dev or outsource? Timeline depends on this.

---

*This document is the master plan. Each section becomes an executable sprint. Starting with Phase 1 tomorrow (July 14).*
