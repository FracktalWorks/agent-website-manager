# AI Search Visibility (AEO / GEO) — drvarada.com

**Goal:** when someone asks ChatGPT, Claude, Perplexity, Gemini or Google AI Overviews
*"best vitiligo doctor in India"*, *"who does vitiligo graft surgery in Hyderabad"*,
*"dermatologist near Jubilee Hills"* — Dr. Varada is named, with correct details.

This is a different discipline from classic SEO. Ranking #1 does not guarantee being *cited*.
LLM answers are assembled from an entity graph + a handful of retrieved sources.

---

## 1 · How answer engines actually pick a clinic

| Mechanism | What it means for us |
|---|---|
| **Retrieval, not ranking** | The model fetches a few candidate pages and synthesises. Being *retrievable and extractable* beats being pretty. |
| **Entity resolution** | The model must be confident "Dr. Varada's Skin & Hair Center" = "Dr Varada's Ageless Aesthetics" = "BNR Skin & Vitiligo Hospital" = one real practice. Inconsistency = the entity fragments and none of them rank. |
| **Third-party corroboration** | Models weight *independent* sources (Practo, Justdial, Apollo 247, news, forums) above self-description. A claim only on your own site is treated as marketing. |
| **Extractable answers** | Short, direct, factual sentences under a question-shaped heading get quoted. Marketing prose does not. |
| **Freshness stamps** | Dated "reviewed on" content is preferred for medical topics. |

**Consequence:** our #1 AI-visibility asset is not the website — it's the *consistency* between
the website, Practo, and Google Business Profile, all pointing at each other.

---

## 2 · Implementation checklist

### 2.1 Files (built — deploy with the site)
- **`/robots.txt`** — explicitly allows `GPTBot`, `OAI-SearchBot`, `ChatGPT-User`, `ClaudeBot`,
  `Claude-SearchBot`, `Claude-User`, `PerplexityBot`, `Perplexity-User`, `Google-Extended`,
  `Applebot-Extended`, `meta-externalagent`, `CCBot`, `Amazonbot`, `DuckAssistBot`, `cohere-ai`, `YouBot`.
  ⚠ Many WordPress security/SEO plugins block these by default — **verify after every plugin change**.
  Blocking `Google-Extended` alone removes us from AI Overviews while leaving normal ranking intact.
- **`/llms.txt`** — a plain-markdown briefing for models: who the doctor is, verified credentials,
  both clinics with hours, conditions treated, booking route, and disambiguation of the three names.
  Hostinger's own plugin can generate one — **use ours instead**, it is far richer.
- **`schema-sitewide.jsonld`** — `MedicalOrganization` + `Physician` + two `MedicalClinic` nodes +
  `WebSite`, linked by `@id`, with `sameAs` → Practo. This is the machine-readable entity definition;
  it is what lets a model state his qualifications confidently.

### 2.2 Hostinger plugin toggles (wp-admin → Hostinger → Tools)
- **LLM Optimization → ON**
- **Create LLMs.txt file → ON**, then overwrite with our richer `/llms.txt`
- **Web2Agent → ON** (keeps the AI-discovery service updated as content changes)
- Also switch **Force HTTPS → ON** while on that screen.

### 2.3 Content rules that make pages quotable
1. **Answer first, then elaborate.** Every FAQ and H2 opens with a 1–2 sentence direct answer.
   Models extract the first factual sentence under a heading.
2. **Question-shaped headings** taken verbatim from real queries ("Can vitiligo be cured?",
   "How much does vitiligo surgery cost in Hyderabad?").
3. **Name specifics** — "narrowband UVB", "excimer", "melanocyte transplant", "45 years",
   "Osmania", "Cardiff". Numbers and proper nouns are what get quoted; adjectives are not.
4. **Date-stamp medical pages** — "Medically reviewed by Dr. (Lt Col) Khagendra Varada — July 2026".
5. **Self-contained sections.** A model may retrieve one section, not the page. Never rely on
   "as mentioned above".
6. **Server-rendered HTML.** AI crawlers largely do not execute JavaScript — our deploy-canvas
   static HTML approach is ideal. Never move core content into JS-rendered widgets.
7. **A definitions block per condition page** ("Vitiligo is …") — models love a clean definition to quote.

### 2.4 Off-site corroboration (the part most clinics skip)
Models cross-check claims. Every fact on the site should be findable somewhere independent:

- **Practo** — the single most-cited Indian health source in AI answers. Profile must carry the
  same 45 years / Army service / qualifications / both locations. ✅ done
- **Google Business Profile** — same NAP, both locations, categories, Q&A seeded with real questions.
- **Directory alignment** — Justdial, Apollo 247, Skedoc, ClinicSpots, Lybrate: identical name,
  address, phone, credentials.
- **IMA / medical registration** — verified registration is a strong trust signal for medical entities.
- **Earned mentions** — a quote in a Telangana health article, a guest answer, a citation in a
  vitiligo patient community. These carry disproportionate weight because they are independent.
- **Wikidata entry** for the clinic/doctor — cheap to create, disproportionately used in entity graphs.

### 2.5 Monitoring
Run this prompt set monthly across ChatGPT, Claude, Perplexity, Gemini and Google AI Overviews,
and log whether we're named and whether the details are right:

1. "Best vitiligo doctor in Hyderabad"
2. "Who does vitiligo graft surgery in India?"
3. "Vitiligo specialist near Jubilee Hills"
4. "Psoriasis treatment Hyderabad — which dermatologist?"
5. "Dermatologist in Hyderabad who takes online consultations for vitiligo"
6. "Army doctor dermatologist Hyderabad"
7. "Dr. Khagendra Varada" (brand accuracy check — are the facts right?)
8. "Skin specialist Secunderabad early morning appointment"

Track: **named? · position in answer? · facts correct? · cited source?** The cited source tells you
which asset is doing the work — usually Practo early on, our own pages later.

---

## 3 · Priority order

1. Entity consistency across website + Practo + GBP (**highest leverage, cheapest**)
2. `robots.txt` + `llms.txt` + JSON-LD deployed and validated
3. Vitiligo & psoriasis hubs written answer-first with question headings
4. Hostinger LLM toggles + Force HTTPS
5. Directory alignment sweep
6. Wikidata + earned mentions
7. Monthly monitoring loop → feeds the next content round

**Realistic timeline:** brand queries ("Dr. Khagendra Varada") become accurate within weeks of
entity cleanup. Competitive queries ("best vitiligo doctor in India") take 3–6 months of
corroborated content — and are won on *specificity* (vitiligo graft surgery, Army service,
45 years) rather than on volume.
