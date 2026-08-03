---
name: search_presence
description: >
  Make a site findable by search engines, answer engines and maps: root
  favicon, canonical host, sitemap + robots, Search Console, Bing (via GSC
  import), IndexNow, LocalBusiness schema with coordinates, Google Business
  Profile hygiene, and a keyless map embed. Includes a live checker.
when_to_use: >
  A site is about to launch or has just launched; the user asks why they do
  not appear in Google/Bing/ChatGPT, why the favicon is a grey globe, why the
  map pin is wrong, or asks to "do the SEO setup" for a brand.
authority: write
cost_tier: 1
version: 1.0.0
---

# Search & answer-engine presence

Presence splits in two, and the split is the whole point of this skill:

| Half | Lives in | Verified by |
|---|---|---|
| **Presentation** — files, tags, redirects | the domain | `scripts/presence_check.py` |
| **Registration** — properties, profiles, submissions | accounts | the checklist below, by a human |

A site can pass every technical audit and be invisible because nobody claimed
the Search Console property. It can be registered everywhere and still show a
grey globe because the icon is not at `/favicon.ico`. Do both halves.

## Run the checker first

```bash
python .github/skills/search_presence/scripts/presence_check.py \
       https://example.com --local --indexnow-key <key>
```

`--local` adds a LocalBusiness schema audit. Exit 1 means something FAILed.
Every check in it exists because that exact failure happened silently on a
real site — the script's docstring says which.

## Launch checklist (registration half)

Order matters: verification first, because everything else attaches to it.

1. **Search Console property.** Prefer a **Domain property** (`sc-domain:x`) —
   it covers every subdomain and both schemes at once. Verify by DNS TXT.
2. **Submit the sitemap** in that property. Publishing one is not submitting
   one.
3. **Bing Webmaster Tools — import from Search Console**, do not add the site
   manually. The import carries verification *and* the sitemap in one step.
   Bing matters far beyond its search share: **ChatGPT's web search runs on
   Bing's index**, so it is the most direct answer-engine lever available.
4. **IndexNow** — publish `/<key>.txt` containing exactly the key, then submit
   changed URLs on every deploy. The key is **not a secret**: publishing it is
   how ownership is proved, so it must stay stable once used.
5. **Analytics** wired and reporting (GA4 or equivalent).
6. **Google Business Profile**, if the business has a place people visit — see
   below.
7. **Record the account state** in memory (which login owns what, property
   type, IDs). The next session cannot see inside an account and will waste a
   turn guessing.

## Traps that cost real time

**The favicon is not the `<link rel=icon>`.** Google fetches `/favicon.ico`
from the site root as its fallback, and if the only declaration is an SVG it
uses nothing. The icon must also be **square with a side that is a multiple of
48**. And once fixed, the favicon index refreshes on **its own cadence**, days
to weeks behind the page index — so after a correct fix the right answer is
"it is fixed, now wait", not another change. Prove the fix with the checker,
not by staring at the SERP.

**Domain property vs URL-prefix property.** They are different properties with
different names. Tools that report a `propertyID` like `https://example.com/`
are not proof a URL-prefix property exists; asking the API which properties the
account owns is. Hardcoding the wrong form gives a 403 that reads as a
permissions problem and is really a naming one.

**OAuth consent screens in "Testing" expire refresh tokens after 7 days.**
`invalid_grant` means only that. Publish the consent screen to stop it.
Also: request only scopes the consent screen declares — an undeclared scope
fails the whole flow with a bare `access_denied`, indistinguishable from the
user pressing Cancel.

**Verification meta tags are often unnecessary.** If the property was verified
by DNS or carried in by a GSC import, adding a `google-site-verification` meta
is dead markup. Check what is already verified before plumbing anything.

**A second listing splits everything.** Duplicate or stale business listings
divide reviews, links and map signals. Find them and report them as duplicates.

## Local business: the map, the pin and the name

**Coordinates.** `geo` is the field most often missing, and without it the pin
is placed by string-matching the address. Get lat/long by right-clicking the
pin in Google Maps and put it in the LocalBusiness schema. Also emit `hasMap`
pointing at the listing.

**Embedding a map with no API key.** The official Embed API needs a billable
key, which then has to live in the repo. This works instead, free, keyless and
quota-free:

```
https://maps.google.com/maps?output=embed&z=16&q=<url-encoded business+area>
```

It only renders when framed — opened as a top-level document it refuses. Load
it `loading="lazy"` so it costs nothing until scrolled to; that is the JS-free
equivalent of a click-to-load facade.

**A map block is not a map.** Put the name, address, hours and phone next to
the frame as real text (`<address>`), not as a caption. The iframe is a picture
to a crawler; the text beside it is the NAP that has to match the profile
character for character.

**The directions link and the embed must point at the same place.** They are
two URLs in two formats and nothing connects them — a build-time invariant that
compares the query of each is the cheap fix. Diverging silently means the
button opens one clinic and the map shows another.

**Renaming a profile is a risk, not an edit.** A complete name replacement with
no shared words is the pattern Google's systems treat as listing hijacking, and
healthcare is its most policed vertical. Expect re-verification. Google judges
the name against the sign on the building, so **fabricate the signage first**,
photograph it, then submit once. Never a bridging name ("Old — New"); that is
keyword stuffing and risks a suspension that would cost the reviews. Keeping a
former name as the second half of the profile name is legitimate when the
business genuinely traded under it and it carries search demand.

## Answer engines

- **Bing first** (see above) — it is the index behind ChatGPT search.
- **`llms.txt`** at the root: a plain-text digest of what the site says, for
  models that fetch it. Ship it and name it in the sitemap generation step.
- **Schema is the machine copy.** FAQPage, Service, Physician/LocalBusiness
  and Organization give an engine facts it can quote without inferring them
  from prose.
- **Canonical, singular facts.** Answer engines quote whatever they find; two
  spellings of the address in two places produce two answers.

## Where this fits

Deploy pipelines should end with the ping, not start with it — publish, then
`indexnow`, then check. On the in-repo site engine
(`.github/skills/site_generator`) that is `deploy.py push → publish →
indexnow`, and `searchconsole.py` in the site directory reads coverage and
inspects individual URLs.
