# Brand launch runbook — site, deploy, presence, profiles

The order in which a brand goes live, and which skill owns each step. Each
step names its gate: do not advance past a red gate, because every later step
multiplies the error across pages, assets and indexes.

Derived from taking drvarada.com from nothing to 61 live pages, a deployed
WordPress render target, search registration and a set of platform profiles.
The phases are the same for any brand; only the content changes.

---

## 0. Facts before pixels

Get these from the client and write them into `siteconf.py` / `chrome.py`
once, as the single source: legal and trading name, any **former name** and
whether it still carries search demand, one-line and paragraph descriptions,
address, coordinates, phone, the **single booking path**, hours, fees,
credentials, and the accounts that own the domain, the analytics and the
business profile.

A former name is usually an asset, not an embarrassment: it holds reviews,
links and the searches of everyone who knew the business before.

**Gate:** every fact appears exactly once in the source. Two copies of an
address is two answers to the same question, and one of them will go stale.

## 1. Scaffold

`python .github/skills/site_generator/scripts/new_site.py <name>` — copies the
engine verbatim. Site-specific values live only in `siteconf.py`.

Skill: [site_generator](../.github/skills/site_generator/SKILL.md)

## 2. Design system

Choose from the 152-package corpus before designing anything from scratch;
paste the `:root` token block whole rather than cherry-picking values.

Skill: [design_system_management](../.github/skills/design_system_management/SKILL.md)
· Corpus: [design-systems/INDEX.md](design-systems/INDEX.md)

**Gate:** contrast checked (AA) after any brand recolour — `brandkit.py`
does the derivation and the repair.

## 3. Content as data

Pages are data in `content/*.py`; markup lives only in `chrome.py`. Write the
copy against the facts from step 0, and let the build's banned-phrase,
negation and slop checks fail the marketing reflexes.

**Gate:** `python build.py` clean, including the consent gate on any
before/after or patient-result imagery.

## 4. Prove it renders

`python verify.py --all` — real Chrome, every page, five widths, horizontal
overflow and broken images. Static checks pass pages that render broken.

**Gate:** 100% clean. Not "clean except". If a sweep reports files missing,
suspect your own concurrent build before suspecting the pages.

## 5. Deploy

`deploy.py check → assets → push → publish → live`. **Assets before pages,
always** — a page that ships first renders against images that are not there
yet, and the cache remembers.

Skill: [html_deploy](../.github/skills/html_deploy/SKILL.md) ·
[deployment_manager](../.github/skills/deployment_manager/SKILL.md)

**Gate:** `deploy.py check` runs the build, the render sweep and the engine
tests itself. Then confirm the live URL, not the build output.

## 6. Search presence

Root `/favicon.ico`, canonical host, sitemap in robots, Search Console domain
property, sitemap submitted, **Bing imported from Search Console** (it is the
index behind ChatGPT search), IndexNow key published and pinged on deploy,
LocalBusiness schema with **coordinates**.

Skill: [search_presence](../.github/skills/search_presence/SKILL.md)

**Gate:**
`python .github/skills/search_presence/scripts/presence_check.py <url> --local`

## 7. Brand assets for the platforms

Favicon set, Business Profile logo (circle-safe) and 16:9 cover, WhatsApp
profile and catalogue tiles, social cards, signage. Rendered from the brand's
own SVG lockups by a script that can be re-run when the brand shifts.

Skill: [brand_assets](../.github/skills/brand_assets/SKILL.md)

**Gate:** `asset_check.py --sheet` and **look at the contact sheet** at the
size the platform draws it.

## 8. Profiles and the map

Business Profile filled out (categories, services, hours, photos, description
to the platform's own limit), duplicates reported, the map embedded on the
site with the NAP beside it as real text, and every profile's address
character-identical to the site's.

**Gate:** the directions link and the map embed resolve to the same place —
enforce it at import time, not by eye.

## 9. Record what is not in the repo

Write to memory what no file can show: which account owns which property, what
is pending on whose side, which decisions were made and why. The next session
starts blind to every account.

Skill: [memory_management](../.github/skills/memory_management/SKILL.md)

---

## Failure modes that repeat across brands

| Symptom | Cause | Where it is handled |
|---|---|---|
| Grey globe in search results | no `/favicon.ico` at the root; SVG-only declaration | step 6 |
| Right site, wrong pin | LocalBusiness has no `geo` | step 6 |
| Illegible tile in a catalogue or a grid | judged at upload size, not consumption size | step 7 |
| Artwork that quietly lies | a price or hours baked into the picture | step 7 |
| A field stops being editable in the live editor | an `EDITABLE_*` constant was made derived | site engine contract |
| Copy that is no longer true | it described external state that changed | step 0's single-source rule |
| Page renders against missing images | pages pushed before assets | step 5 |
| "It looks broken" after a correct fix | index caches refresh on their own cadence | step 6 |
