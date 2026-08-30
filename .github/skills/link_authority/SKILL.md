---
name: link_authority
description: >
  Earn the links, mentions and citations that move a site's authority:
  baseline audit, preserve-and-claim inventory, linkable assets, a
  Discover-eligible newsroom, expertise channels (journalist requests,
  academic, open-source, events), LinkedIn and community done canonical-first,
  and the AI-citation track. Includes a site audit and a per-article gate.
when_to_use: >
  The user asks how to rank higher, get backlinks, "get into Google News",
  start a blog or newsroom, use LinkedIn for SEO, be cited by ChatGPT /
  Perplexity / AI Overviews, or asks whether some link scheme they were told
  about is worth doing. Step 11 of the brand launch runbook.
authority: write
cost_tier: 2
version: 1.0.0
---

# Link authority: links, newsroom, LinkedIn, citations

A site ranks on what other sites say about it. This skill is how the agent
earns that — for any brand, in any vertical — without buying anything, and
how it proves the site is in a state where what it earns can land.

## What counts (the value ladder)

| Signal | Moves Google ranking? | Moves AI citations? | Where it comes from |
|---|---|---|---|
| **Followed editorial link** from a relevant page | Yes, the most | Yes | press, academic pages, partner pages, resource lists, open-source repos |
| **Followed profile/directory link** | Some | Yes (entity) | investor & incubator portfolios, product databases, registries, event exhibitor lists |
| **Nofollow link** on a high-visibility page | A hint, not equity | Yes | LinkedIn, Reddit, YouTube, press-release wires, marketplaces |
| **Unlinked brand mention** | Barely | **Yes — 3× the correlation of links** | any of the above, podcasts, forums, papers |

Two consequences shape everything below. First, the same act — a real
article in a real outlet — earns all four at once, so **do things that earn
the top row and the rest follows**. Second, AI answer engines weigh mentions
and entity consistency more than PageRank, so the cheap bottom rows are not
wasted; they are the AI-citation track.

## What is dead — answer these in one line

People arrive with schemes. Each of these is over, with a date:

| Scheme | Status |
|---|---|
| "Set up a Google Publisher / Google News account for a backlink" | Publisher Center stopped taking publications **April 2024**; fully automatic pages since **March 2025**. Inclusion never passed link authority; it is a distribution surface, and promotional content is excluded by policy. |
| "Submit to Bing News PubHub" | **Retired early 2025.** MSN Partner Hub is invite/apply for real publishers. |
| "Answer HARO queries" | HARO/Connectively shut **9 Dec 2024**. Living replacements: **Qwoted**, **Source of Sources** (Shankman, free), **Featured** (owns the HARO name since Apr 2025), **Help a B2B Writer**. Overlap between platforms is ~17%, so watch more than one. |
| "Guest posts on Google-News-approved sites" | This is **site reputation abuse** — algorithmic since the **Aug 2025** spam update; **Oct 2025** targeted AI guest-post farms specifically. Worthless at best, penalised at worst. |
| "Post on Blogger / Google Sites for a Google-domain link" | Subdomains carry their own authority; a link from blogspot is a link from a user-generated page. |
| "Press-release wire for links" | Wire links are nofollow. Wires are for reach and mentions, not equity. |
| "Buy a link package / PBN / reciprocal ring" | Link spam policy, enforced. Never. |

## Run the baseline first

```bash
python .github/skills/link_authority/scripts/authority_audit.py https://example.com \
       --posts 8 --legacy outputs/<site>/legacy-urls.txt --json outputs/<site>/authority-audit.json
python .github/skills/link_authority/scripts/post_gate.py --feed https://example.com/feed/ --n 8
python .github/skills/link_authority/scripts/post_gate.py --html dist/blog/x.html --url https://example.com/blog/x/
```

`authority_audit.py` is the on-domain half: entity (`sameAs`), feed
liveness and cadence, blog index, `llms.txt`, news sitemap, **every AI
crawler fetched under its own User-Agent and compared with what robots.txt
promised**, legacy-URL redirects, and the first N posts through the article
gate. Exit 1 on any FAIL. `post_gate.py` is the per-article gate: article
schema (and *where* it sits), machine-readable date, linked named byline,
og:image ≥ 1200 px, `max-image-preview:large`, canonical, length,
answer-first lead, internal links, outbound citations, a Discover-ready
verdict, and on-page SEO rows (added 2026-08-30): title 40–60 chars, meta
description 70–165, exactly one `h1`, an `h2` outline with no heading
jumps, and **every in-article image HEAD-checked** (lazy-load `data-src`
followed; `alt=""` counts as decorative, only a missing alt attribute is
flagged) — broken images are a FAIL.

The **account-side half** is a human checklist, recorded in memory:

1. **Search Console → Links report**: top linked pages, top linking sites,
   anchor text. Export it; it is the only free, first-party backlink list.
2. **Bing Webmaster Tools** verified (import from GSC) — Bing's index is what
   ChatGPT search cites from (≈87 % overlap).
3. **Ahrefs Webmaster Tools** (free for verified sites) or Semrush for
   referring domains, lost links and the spam-link picture.
4. **Google Alerts** + **Talkwalker Alerts** for the brand name, founders,
   product names — this is the unlinked-mention feed.
5. If the site was ever hacked: check the Links report for spam URLs being
   linked (the injected pages attract spam links). **410** those URLs; do
   **not** disavow unless there is a manual action.

## The method — seven moves, in order

Order matters because each move makes the next one cheaper. Do not start
with outreach; start with what already exists.

### 1. Preserve what is already earned

Every link the site already has points at a URL that may no longer exist.
List every URL that ever carried a link or a listing (old product pages,
old blog slugs, the pre-rebuild sitemap, whatever a product database or
directory still lists) in `outputs/<site>/legacy-urls.txt` and make the
audit prove each one 301s to a live page. This is the highest-ROI hour in
the whole skill: **a redirect recovers a link that already exists**.

Then reclaim unlinked mentions: search the brand name, founders and
products; every article, database entry or profile that names the brand
without linking gets one polite request with the exact URL.

### 2. Claim what is already ours

Make the **relationship inventory** before any prospecting. For every
entity below, the ask is "please list us with a link"; the reason to say
yes already exists:

- **Money and mentorship**: investors' portfolio pages, incubators and
  accelerators (alumni pages), grant bodies.
- **Institutions that recognise the brand**: ministries, missions,
  associations, awards — every logo on the site's "recognised by" band is a
  page that can link back.
- **Customers, partners, suppliers, integrators, resellers** — "our
  partners" pages, case studies co-published on *their* site.
- **Registries**: Startup India / DPIIT, GeM, state startup cells, industry
  bodies, professional councils (medical, tourism, engineering).
- **Product databases and directories for the vertical** (see the prospect
  libraries) — including updating stale listings that name retired products.
- **Entity anchors**: Wikidata item, Crunchbase, Tracxn, GitHub org,
  Google Business Profile — every one goes into the Organization `sameAs`.
- **Events**: every exhibitor/speaker listing is a followed link on a
  relevant domain.
- **Founders' own footprints**: alma mater alumni features, conference bios,
  podcast guest pages.

Log each in the tracker (see *Plan and measure*). Expect 15–40 links from
this move alone on an established brand, at near-zero cost.

### 3. Build 2–3 linkable assets

Links need something to point at that is more useful than a product page.
Pick from the types that reliably get cited, and pick the two or three the
brand can make **from data it already has**:

| Asset type | What it is | Why people link |
|---|---|---|
| **Original data** | an index, a benchmark, a survey, a price tracker from the brand's own operations | journalists and bloggers cite numbers |
| **Reference database** | a materials table, a species list, a procedure list with measured facts | the page other pages send readers to |
| **Free tool / calculator** | cost estimator, checker, converter | tools get bookmarked and listed |
| **Regulatory / procedural guide** | tariff codes, licensing steps, seasonal rules, insurance codes | accountants, agents, forums link to the thing that answers the question |
| **Research roundup** | "studies that used our equipment / our site / our data" with citations | reciprocity: cite researchers, they cite you |
| **Original test or teardown** | a comparison the brand ran and photographed | forums and reviews cite the evidence |

Rules: real numbers, a method section, a date, a named author, an
embeddable chart/table, a "cite this" line, and updates on a schedule
(the update is a new news hook each time).

### 4. The newsroom

One blog, two tracks, one gate:

- **Newsroom track** — dated, bylined, short (400–800 words), a news hook
  (launch, customer win, recognition, data release, policy comment, event).
  Schema `NewsArticle`. This is what Discover, Top Stories and journalists
  pick up.
- **Field-notes track** — evergreen guides and explainers, `BlogPosting`,
  first-hand experience in the byline's voice, updated on a schedule.

Requirements that make a post eligible (all measured by `post_gate.py`):

1. `NewsArticle`/`BlogPosting` JSON-LD with `headline`, `datePublished`,
   `dateModified`, `author` as a `Person` **with a URL**, `image`,
   `publisher`. On deploy paths that keep only `<body>`, put the JSON-LD
   in the body.
2. A visible date and a **linked byline** to an author page carrying
   credentials, photo, role, and the author's `sameAs` (LinkedIn, Scholar,
   ORCID, GitHub). No "admin".
3. `og:image` **≥ 1200 px wide**, and `<meta name="robots"
   content="max-image-preview:large">`.
4. Answer-first lead: the first paragraph states the fact the headline
   promised. Engines quote it; readers stay.
5. At least two internal links and at least one outbound citation.
6. RSS/Atom feed valid and live; `<link rel="alternate" type="application/rss+xml">`
   in the head (Discover's Follow feature reads it).
7. A **news sitemap** once dated stories exist (Google News / Top Stories
   read it; 48-hour window, ≤ 1,000 URLs).
8. IndexNow ping on publish (Bing → ChatGPT), Search Console URL inspection
   for the first pieces.
9. Every piece through the prose gate if the site has one (`slop.py` on the
   in-repo engine) — cadence of AI copy is the tell, not vocabulary.

There is **no application** for Google News, Discover or Top Stories:
eligibility is technical + editorial, judged per topic. Google's **June 2026
Discover update** weighted first-hand experience and named author
credentials above everything else — the founder's byline on a story
about something the founder actually did is the strongest single input.

Cadence that a small team sustains: **2 field-notes a month + news as it
happens (never less than one a month) + one data asset a quarter**. The
agent drafts and structures; the human adds the first-hand paragraph and
signs the byline. Nothing publishes without a named human's sign-off.

### 5. Earn with expertise

- **Journalist request platforms** — Qwoted, Source of Sources, Featured,
  Help a B2B Writer. One expert profile per founder, credentials that are
  verifiable, reply within the hour, answer the question asked with a
  number and a first-hand detail, never pitch. Expect 1 in 8 to land; each
  is a followed editorial link on a news domain.
- **Academic reciprocity** — find papers, theses and lab pages that used
  the brand's product/place/service (Google Scholar alert, ResearchGate);
  publish the research roundup (move 3); email the lab with the roundup URL
  and ask for an equipment/partners mention.
- **Open-source** — if the brand ships software, profiles, models or data,
  upstream them: printer profiles into slicer repos, plugins into plugin
  registries, datasets to the repositories the field uses. A README link
  from a major repo is a followed link on a very high-authority domain and
  a listing in the software itself.
- **Industry press** — pitch the trade titles for the vertical with the
  news track pieces, one at a time, exclusive first. Most trade sites run
  vendor news for free if it is actual news with a picture.
- **Speaking, judging, awards, standards committees** — every one is a
  bio page with a link.

### 6. Compound: LinkedIn, community, video

**LinkedIn is not a link source; it is a demand and relationship engine.**
All LinkedIn links are nofollow. Its value: articles and newsletters are
indexed by Google and cited by AI engines (LinkedIn rose faster than any
other source in AI citations into 2026); brand-name search volume rises;
and the journalists, professors and procurement people who will later link
are *on* it.

The playbook, **canonical-first**:

1. Publish on the site. Wait until Google has indexed it (URL inspection).
2. Then post on LinkedIn a **rewritten** version — the first third redone,
   a different headline, the data table as an image — ending with "full
   method and data at ‹site URL›". Never paste the full article the same
   day; LinkedIn will outrank the original.
3. Founder **newsletter** (fortnightly; set the SEO title/description
   LinkedIn offers) + company page (3 posts/week: one data point, one
   story, one document/carousel) + **comments** on the posts of the people
   you want links from — that is where the relationship starts.
4. Employees share with their own words, not the company copy.

**Community**: Reddit is the most-cited domain across AI engines. Rules —
a real person's account with affiliation disclosed; answer with data, never
a pitch; link only when the link *is* the answer, never in your first ten
comments in a subreddit; follow subreddit rules on vendors. Same for Quora,
Stack Exchange, vertical forums, Discord/WhatsApp groups where relevant.

**YouTube**: the channel link is nofollow, but videos rank in Google, get
embedded (embeds carry the channel/site link), and are cited by AI. One
video per data asset and per news story is enough.

### 7. The AI-citation track

What gets a brand named in ChatGPT, Perplexity, Gemini and AI Overviews:

1. **Be in Bing's index** (ChatGPT search) — Bing Webmaster Tools + IndexNow.
2. **Crawlers can actually fetch** — the audit fetches as OAI-SearchBot,
   GPTBot, ClaudeBot, PerplexityBot, CCBot and compares with robots.txt.
   "Allow in robots, 429 at the server" is the trap.
3. `llms.txt` at the root: what the site is, in plain text, with the key
   URLs.
4. **Answer-first pages**: each key page states its fact in the first
   paragraph; FAQ/Product/Service schema is the machine copy.
5. **Entity consistency**: one name, one address, one description
   everywhere; Organization `sameAs` to every profile; Wikidata item.
6. **Mentions on the platforms engines read**: review platforms and
   directories for the vertical, Reddit, LinkedIn, local and trade press.
7. **Measure**: pick 10 target prompts, run them monthly across ChatGPT,
   Perplexity, Gemini, AI Overviews, record whether and how the brand is
   named. That number is the KPI for this track.

## Plan and measure

Outputs this skill produces, per site:

| File | What |
|---|---|
| `outputs/<site>/authority-plan.md` | the plan, from `templates/strategy.md` — situation, assets, channel tiers, newsroom spec, LinkedIn, 90-day plan, metrics |
| `outputs/<site>/link-prospects.csv` | the tracker: `target, kind, url, contact, ask, status (found/asked/live/declined), link_url, date` |
| `outputs/<site>/legacy-urls.txt` | every URL that ever earned a link, for the audit's redirect check |
| `outputs/<site>/authority-audit.json` | the baseline, re-run monthly |

Monthly metrics: referring domains (Ahrefs/GSC), links live from the
tracker, non-branded clicks (GSC), Discover impressions (GSC → Discover
report), AI-citation share on the 10 prompts, feed cadence. Targets in the
plan are per site; a realistic first 90 days on an established brand is
**+25–40 referring domains**, most from moves 1–2.

## Outreach rules

One email, to a named person, one specific ask, the exact URL, and why
*their* reader benefits. Subject line is the fact, not "collaboration".
Follow up once after a week, never twice. Anchor text is the brand or the
natural phrase — never the money keyword. Sponsored is disclosed and
`rel="sponsored"`. Nothing is paid for a link. Nothing is exchanged for a
link. If an outlet asks for money, it is an ad; decide as an ad.

## Traps that cost real time

- **Invited by robots.txt, refused by the server.** A WAF or rate-limit rule
  returned 429 to GPTBot for weeks while robots.txt said Allow. Only a
  fetch *as the crawler* shows it. Fix the rule, then re-run the audit.
  Before blaming a plugin, fetch a **static file and a 404 path** as the
  crawler: if those are refused too, PHP never ran and the rule is at the
  web server or the host's edge. On Hostinger shared hosting that rule is
  the host's own ("server-level rate limits for automated traffic",
  documented as not disableable per site); the only customer lever is
  CDN → AI Audit, else a support ticket. Also check *which* crawler is
  refused: if OAI-SearchBot and ChatGPT-User get 200, ChatGPT search still
  cites the site and the loss is training inclusion only.
- **Probing gets the prober throttled.** A burst of ~80 bot-UA requests
  (plus repeated SSH logins) made Hostinger time out every request from
  the probing IP — HTTPS *and* SSH — for a while. Run the audit once, not
  in loops; space matrix tests out; never test from the deploy machine
  right before a deploy.
- **Schema in the head that never shipped.** A deploy path that keeps only
  `<body>` dropped every JSON-LD in `<head>` — Product on 20 pages, FAQ on
  37. The gate reports where the schema sits; on such paths put it in the
  body.
- **Stale listings point at dead URLs.** A product database listed four
  retired models; after a rebuild all four links landed on 404. Build the
  legacy list *before* the rebuild, from the old sitemap and the
  directories.
- **Spam links after a hack.** Injected spam URLs attract spam links; the
  Links report fills with them. 410 the URLs; do not disavow without a
  manual action; do not panic-remove real links.
- **LinkedIn outranking the site.** Full text posted to LinkedIn before the
  original was indexed. Canonical-first, rewritten, later.
- **Placeholder authors.** Posts by "admin" carry no E-E-A-T and fail the
  Discover byline weighting. Real people, real pages, real credentials.
- **Discover images.** Everything else right, hero image 1024 px wide: no
  card. ≥ 1200 px plus the preview meta.
- **"We were featured" without a link.** A mention is not a link until it
  is; ask, with the URL, every time.

## Prospect libraries

`prospects/universal.md` applies to every brand; the vertical files add the
directories, databases, press and communities of a field. Read the
universal file and the matching vertical file when building the tracker;
when a new vertical arrives, write its file from the same headings so the
next site starts warm.

| File | For |
|---|---|
| `prospects/universal.md` | investors, incubators, registries, entity anchors, journalist platforms, events, alumni |
| `prospects/manufacturing-hardware.md` | machines, materials, industrial products; 3D printing specifically |
| `prospects/healthcare-clinic.md` | doctors, clinics, medical practices |
| `prospects/travel-experiences.md` | tours, safaris, stays, destination brands |

## Where this fits

After `search_presence` (the site must be indexable and registered before
links can count) and after the site's own gates (`verify.py`, `seo.py`,
`slop.py`). In the brand launch runbook it is **step 11**. On the in-repo
site engine the publish sequence for an article is: `post_gate.py --html`
→ deploy → `post_gate.py <live URL>` → IndexNow → tracker updated.
