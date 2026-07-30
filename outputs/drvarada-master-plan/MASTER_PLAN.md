# Dr. Varada — Marketing & Website Development Master Plan

**Version 1.0 · 2026-07-26 · supersedes the initial market-research plan**
(Research data remains the evidence base: `outputs/drvarada-market-research/` + artifact
https://claude.ai/code/artifact/afa83797-ddfd-4312-8a29-8316da1c636b)

## 0 · Mission

Two war fronts, one website:

| Front | Goal | Definition of "dominate" |
|---|---|---|
| **A — Hyderabad** | Own every clinical service we offer, city-wide | Top-3 Google local pack (both locations) for service + "near me" queries; top-3 organic for every `{service} in hyderabad` query; more GBP actions/mo than any Ameerpet/Jubilee Hills competitor |
| **B — Pan-India** | #1 authority for **Vitiligo** and **Psoriasis** | Top-3 organic India-wide for vitiligo/psoriasis treatment head terms; the reference content hub patients and press cite; steady national teleconsult + travel-patient pipeline |

Model from research: 40–300 incremental patients/mo at 12 months; Front B raises the ceiling
(India has the world's highest vitiligo prevalence; patients travel and consult online).

## 1 · Prerequisite: one entity, one story (Weeks 1–2)

The brand is fragmented: Google = "BNR Skin & VITILIGO HOSPITAL" (Ameerpet) · Practo =
"Dr Varada's Ageless Aesthetics" (Jubilee Hills) + "Vardhan Healthcare" (West Marredpally) ·
site = "Dr Varada's Skin Center". Search engines see three unrelated businesses; reviews don't compound.

1. **drvarada.com becomes the umbrella entity**: "Dr. Varada's Skin & Hair Center".
2. `/locations/` page per active practice, NAP character-identical to Practo + GBP.
3. GBP transition keeps legacy equity: "Dr. Varada's Skin & Hair Center (BNR Skin & Vitiligo Hospital)" during transition; never a cold rename. **Open question: is Ameerpet/BNR still operating? (drives 1 vs 2 GBPs)**
4. Every external profile (Practo ×2, GBP, Justdial, Apollo247, Skedoc, ClinicSpots, IMA) links → drvarada.com.
5. `Physician` + `MedicalClinic` schema everywhere; sameAs → Practo/GBP profiles.

## 2 · Front A — Hyderabad domination

**Thesis:** "near me"/local intent dwarfs every condition term (Trends: dermatologist-near-me 81 vs
biggest condition 13). Local victory = GBP × location pages × reviews × service pillars.

1. **GBP engine**: correct categories (Dermatologist / Skin care clinic / Hair transplantation clinic),
   weekly posts, photo cadence, Q&A seeding, UTM-tagged links. Review flywheel: QR card at reception →
   GBP (primary) alternating Practo; target +15–20 reviews/mo; reply to all.
2. **Service pillar pages** (one per demand cluster, titles = autocomplete-verified queries):
   vitiligo, psoriasis, eczema/AD, acne, allergy/rashes, botox/anti-aging, skin boosters,
   RF tightening, chemical peels, hair loss, alopecia, dandruff, premature greying (+ laser hair
   reduction & dermatosurgery — Practo shows these are offered and they're commercial).
3. **Locality relevance**: Jubilee Hills page carries aesthetics; West Marredpally carries morning
   medical-derm; "near me" coverage for Banjara Hills, Madhapur, Gachibowli via locality mentions
   (NOT doorway pages — one page per real location only).
4. **Telugu layer**: `psoriasis treatment in telugu` is a real autocomplete with zero good clinic
   content. Telugu versions of the top-6 condition pages, proper `hreflang`.
5. **Citations**: align the aggregator profiles; local press/backlinks (Telangana Today health desk,
   local health bloggers, IMA Telangana).

## 3 · Front B — Pan-India vitiligo & psoriasis authority

**Thesis:** these are journey conditions (chronic, stigmatized, research-heavy). Whoever owns the
patient-education journey owns the patient. Competitors nationally (Maharshi, Kayakalp, chain
hospitals) have volume but thin, template content and weak physician bylines. We counter with a
41-year specialist's depth.

1. **Two national hubs**, separate from local pages:
   - `/vitiligo/` hub → types & stages, causes/autoimmunity, treatments (excimer laser, NB-UVB
     phototherapy, melanocyte transplant/grafting surgery, topicals/JAK creams), children's vitiligo,
     diet & myths, stability assessment, repigmentation gallery, cost guide, FAQ, **online consultation**.
   - `/psoriasis/` hub → plaque/scalp/guttate/nail/inverse types, triggers & flare management,
     treatments (topicals, phototherapy, methotrexate/biologics counselling), diet & lifestyle,
     psoriatic arthritis red flags, cost guide, FAQ, **online consultation**.
2. **E-E-A-T spine**: every page "Medically reviewed by Dr. (Lt Col) Khagendra Varada, MBBS,
   Dip. Practical Dermatology (Cardiff)" + dated review stamps; doctor profile page as the authority
   node; original photos, never stock; real case stories (with consent).
3. **National funnel**: WhatsApp photo triage → Practo **online consultation** (doctor already does
   video consults) → treatment plan → travel visit if procedural. Dedicated
   `/vitiligo/online-consultation` + `/psoriasis/online-consultation` landing pages.
4. **Authority building**: answers on the questions patients actually ask (People-Also-Ask mining);
   guest expertise in national health media; YouTube shorts (vitiligo myths, repigmentation
   time-lapses) feeding the hub; publish repigmentation outcome data (unique, linkable asset).
5. **Language phases**: EN (phase 1) → Telugu (phase 1, local overlap) → **Hindi hub pages (phase 3)** —
   vitiligo demand skews strongly Hindi-belt (autocomplete: "vitiligo treatment in hindi").

## 4 · Full sitemap (build order = phase column)

Legend: template T1 = service pillar · T2 = national hub article · T3 = utility/brand · T4 = blog. P = phase.

| # | URL | Primary query target | T | P |
|---|---|---|---|---|
| 1 | `/` | dr varada + brand, skin & hair specialists hyderabad | T3 | 1 |
| 2 | `/about/dr-khagendra-varada` | dr khagendra varada (E-E-A-T node) | T3 | 1 |
| 3 | `/locations/jubilee-hills` | dermatologist jubilee hills | T3 | 1 |
| 4 | `/locations/west-marredpally` | dermatologist west marredpally / secunderabad | T3 | 1 |
| 5 | `/contact` | (brand) | T3 | 1 |
| 6 | `/vitiligo-treatment-hyderabad` | vitiligo treatment in hyderabad (+leucoderma synonym) | T1 | 1 |
| 7 | `/psoriasis-treatment-hyderabad` | psoriasis treatment in hyderabad | T1 | 1 |
| 8 | `/vitiligo/` | vitiligo treatment (India) | T2 | 1 |
| 9 | `/psoriasis/` | psoriasis treatment (India) | T2 | 1 |
| 10 | `/vitiligo/online-consultation` | vitiligo doctor online consultation | T2 | 1 |
| 11 | `/psoriasis/online-consultation` | psoriasis doctor online consultation | T2 | 1 |
| 12 | `/results` | vitiligo before after, treatment results | T3 | 1 |
| 13 | `/patient-stories` | dr varada reviews (Practo social-proof sync) | T3 | 1 |
| 14 | `/hair-loss-treatment-hyderabad` | hair loss treatment hyderabad (men/women sections) | T1 | 2 |
| 15 | `/alopecia-treatment-hyderabad` | alopecia areata treatment hyderabad | T1 | 2 |
| 16 | `/acne-treatment-hyderabad` | acne treatment near me / hyderabad | T1 | 2 |
| 17 | `/skin-allergy-rashes-treatment` | skin allergy (biggest TG cluster) | T1 | 2 |
| 18 | `/eczema-atopic-dermatitis-treatment` | eczema / atopic dermatitis treatment | T1 | 2 |
| 19 | `/anti-aging-botox-hyderabad` | botox hyderabad | T1 | 2 |
| 20 | `/skin-boosters-hyderabad` | skin booster treatment (+86% TG momentum) | T1 | 2 |
| 21 | `/chemical-peels-hyderabad` | chemical peel hyderabad + cost | T1 | 2 |
| 22 | `/rf-skin-tightening-hyderabad` | skin tightening treatment hyderabad | T1 | 2 |
| 23 | `/laser-hair-reduction-hyderabad` | laser hair removal hyderabad (Practo top service) | T1 | 2 |
| 24 | `/dermatosurgery-hyderabad` | mole removal, skin tag removal, wart removal hyderabad | T1 | 2 |
| 25 | `/dandruff-treatment` | dandruff treatment (seborrheic dermatitis) | T1 | 3 |
| 26 | `/premature-greying-treatment` | premature greying of hair treatment | T1 | 3 |
| 27–33 | `/vitiligo/{types-stages, excimer-laser, phototherapy, surgery-grafting, children, diet-myths, cost}` | long-tail national vitiligo cluster | T2 | 2–3 |
| 34–39 | `/psoriasis/{types, scalp, triggers-diet, phototherapy, biologics, cost}` | long-tail national psoriasis cluster | T2 | 2–3 |
| 40 | `/te/` (Telugu: vitiligo, psoriasis, hair fall, allergy, acne, eczema) | {condition} treatment in telugu | T1 | 2 |
| 41 | `/blog/` + editorial calendar | informational long-tail | T4 | 2+ |
| 42 | `/hi/vitiligo/`, `/hi/psoriasis/` (Hindi hubs) | vitiligo treatment in hindi | T2 | 3 |

## 5 · Content system

- **Cadence**: Phase 1 = 13 cornerstone pages. Then 2 T2-cluster pages + 2 blog posts/week.
  Every blog post internal-links up to its pillar; every pillar links to booking + related cluster.
- **Page anatomy (T1)**: query-matched H1 → credibility line (41 yrs · 97% · locations) → sticky
  **Book on Practo** → protocol with named technology → before/after strip → doctor quote →
  FAQ (autocomplete + PAA questions, FAQPage schema) → Practo stories → related reading.
- **YMYL compliance**: no cure claims (esp. vitiligo — "repigmentation", "control", "stability");
  no fabricated statistics; consent-documented photos; disclaimers on outcome variability. This is
  also a ranking strategy — Google punishes medical over-claiming.
- **Social-proof sync**: scheduled script pulls own Practo profiles (rating, count, newest stories) →
  JSON → WP; site strips update automatically. (Build in `.github/skills/` as `practo_sync`.)

## 6 · Conversion architecture (Practo-first — team directive)

Primary CTA everywhere: **Book on Practo** (per-location deep link; aesthetics → Ageless Aesthetics,
medical → morning practice). Secondary: **WhatsApp your photos** (staff replies with Practo link).
Tertiary: tap-to-call. National pages lead with **Practo online consultation**. No parallel booking
forms. Re-evaluate direct-booking prominence at month 6 with data.

## 7 · Technical build spec (WordPress · Hostinger · this repo's tooling)

- **Stack**: WP on Hostinger (installation 24363459), Elementor installed, LiteSpeed cache, https ✔.
- **Build method**: design in Open Design → **deploy-canvas** (direct HTML, elementor_canvas) for
  speed/fidelity on templated marketing pages (repo default); Elementor-native only where clinic
  team needs self-editing. Shared header/footer as reusable components.
- **Templates**: T1 service pillar, T2 hub article, T3 brand/utility, T4 blog post — 4 templates,
  40+ pages, consistent blocks.
- **Performance**: LCP < 2.5s on 4G, image WebP + lazy-load, LiteSpeed page + object cache tuned,
  Core Web Vitals green before Phase 2 content push.
- **Schema**: Organization + Physician + MedicalClinic (per location) + MedicalWebPage +
  FAQPage + Review snippets where policy-compliant; `hreflang` en/te/hi.
- **Analytics**: GA4 + Search Console + click-tracking on Practo/WhatsApp/call CTAs (per-page lead
  attribution); rank tracking for the keyword map; monthly report artifact (repo reporting capability).
- **Housekeeping at build time**: WP core + plugin updates, delete duplicate AI-builder pages,
  proper permalinks, XML sitemap + robots, GSC verification.

## 8 · Roadmap

| Phase | When | Ships |
|---|---|---|
| **1 · Foundation & spearhead** | Wk 1–4 | Entity fix + GBP; templates; 13 cornerstone pages (incl. both national hubs + online-consult funnels); analytics; review flywheel starts |
| **2 · Hyderabad broadside** | Wk 5–10 | All remaining T1 service pillars; Telugu layer; national cluster pages begin; blog cadence; citations aligned; social-proof sync live |
| **3 · National authority** | Mo 3–6 | Complete vitiligo/psoriasis clusters; Hindi hubs; outcome-data asset; PR/backlinks; YouTube feed |
| **4 · Compound & defend** | Mo 6–12 | Content refresh cycle; paid support on winners (₹15–25K/mo test); direct-booking test; quarterly strategy review vs KPIs |

## 9 · KPIs (review monthly)

| Metric | 3 mo | 6 mo | 12 mo |
|---|---|---|---|
| `{service} in hyderabad` top-3 rankings | 3 queries | 8 | 15+ |
| Local pack (both locations) | visible | top-3 on 5 queries | top-3 on 10+ |
| India top-10: vitiligo/psoriasis head terms | tracked | 2–3 terms | top-3 on core terms |
| Organic sessions/mo | 1.5K | 5K | 12K+ |
| Leads (Practo clicks + WA + calls)/mo | 50 | 150 | 400+ |
| New patients/mo attributable | ~20 | ~80 | 150–300 |
| GBP reviews (cumulative new) | +40 | +100 | +200 |

## 10 · Risks & mitigations

- **GBP rename resets rank** → transition naming, never cold rename.
- **Ameerpet/BNR status unknown** → confirm before entity work (only open user question).
- **YMYL/medical-claim penalties & MCI/NMC ad ethics** → review-stamped, claim-free copy; physician byline.
- **Practo dependency** (owns relationship data, lead fees) → all CTAs swappable per page; direct test at mo 6.
- **Capacity ceiling** (300/mo ≈ 12/day extra) → phase paid spend to slot headroom; expand online consults.
