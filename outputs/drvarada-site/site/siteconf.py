"""What this particular site is made of.

WHY THIS EXISTS
  The same two lists — which content modules hold pages, and which chrome
  constants a person may edit — were written out separately in `build.py`,
  `linkscan.py` and `editor.py`. Adding a content module meant remembering all
  three, and forgetting `linkscan.py` produced the worst kind of wrong answer:
  "this link is used once" for a link used on twenty pages, from a control that
  offers to change every one of them.

  It is also the seam a new site is cut along. `new_site.py` writes a fresh copy
  of this file and leaves the engine untouched, so "start another site" is a
  content problem rather than a fork.

Everything here is site-specific. Nothing in the engine should grow a default
for it — a missing module should be a loud import error, not a silent gap.
"""

from __future__ import annotations

# Content modules holding a PAGES list, in the order pages should be built.
# Order matters only for the site manifest and the build log; slugs are unique.
MODULES = ("brand", "vitiligo", "psoriasis", "hyderabad_medical",
           "hyderabad_skin", "treatments", "secunderabad", "national", "languages")

# Chrome constants the live editor's site-details form may write.
#
# The URL-ish ones are validated against a scheme allow-list before they land
# inside an href on every page; the rest are free text. Keep the two groups in
# step with `EDITABLE_URLS` below.
EDITABLE_CONSTANTS = (
    "WHATSAPP", "PHONE", "PHONE_ALT", "PHONE_LANDLINE",
    "PHONE_SHOW", "PHONE_ALT_SHOW", "PHONE_LANDLINE_SHOW",
    "PRACTO_REVIEWS", "GOOGLE_REVIEWS", "MAPS", "ADDRESS", "HOURS",
    "PATIENTS", "REVIEWS", "RATING",
    "REVIEWER", "REVIEWED",
)

# The subset of the above that ends up in an href and must therefore be a URL,
# a tel: or a mailto: — never anything that could close the attribute.
EDITABLE_URLS = ("WHATSAPP", "PHONE", "PHONE_ALT", "PHONE_LANDLINE",
                 "PRACTO_REVIEWS", "MAPS")

# Constants that hold a link destination, for `linkscan.py`. A destination in a
# constant is already the "everywhere" case: one write covers every use.
LINK_CONSTANTS = ("WHATSAPP", "PHONE", "PHONE_ALT", "PHONE_LANDLINE",
                  "PRACTO_REVIEWS", "MAPS")

# IndexNow — push changed URLs to Bing instead of waiting to be crawled.
#
# Bing, Yandex, Seznam and Naver share one IndexNow endpoint: POST a list of
# URLs and they fetch them within minutes rather than whenever a crawler next
# happens by. Google does not participate, so this complements the sitemap
# rather than replacing it.
#
# It matters here beyond Bing's own search share: **ChatGPT's web search runs on
# Bing's index**, so how quickly Bing sees a page is how quickly an answer engine
# can cite it.
#
# The key is NOT a secret. The protocol works by having you publish it at
# `https://<host>/<key>.txt` — possession of that URL is the entire proof that
# you control the host, which is why it must stay stable once used. Rotating it
# silently breaks submissions until the new file is live.
INDEXNOW_KEY = "8f423cfc452b76f39c2b1b5c63cf4780"
