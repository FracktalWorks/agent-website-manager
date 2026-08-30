#!/usr/bin/env python
"""Baseline a site's link-authority PRESENTATION: what a would-be linker, a
news surface and an answer engine find when they arrive.

    python authority_audit.py https://example.com
    python authority_audit.py https://example.com --posts 8 --legacy old-urls.txt --json out.json

The deterministic half of the link_authority skill. It answers "is this site
in a state where earned links and citations can land and count". It cannot
see the account-side half -- Search Console's Links report, Bing Webmaster
Tools, an Ahrefs/Semrush backlink export -- the skill carries that as a
checklist for a human.

WHY EACH CHECK EXISTS. Every one has been a real silent failure:

  AI crawlers    robots.txt said `User-agent: GPTBot / Allow: /` while the
                 server answered GPTBot 429 for weeks. Crawlers obey the
                 server, not the file. The only way to see it is to fetch AS
                 the crawler, which is what this does for each one.
  sameAs         An Organization with no sameAs is a name an answer engine
                 cannot tie to the LinkedIn page, GitHub org, YouTube channel
                 or Wikidata item that vouch for it. Entity first, links after.
  feed           Discover's Follow feature, Bing, syndication and every reader
                 start from the feed. A feed that 404s, or whose newest item
                 is a year old, says "dormant" to all of them.
  legacy URLs    Links already earned point at OLD URLs. A product database
                 still listed four retired models of one brand; after a
                 rebuild every one of those links landed on a 404. Redirects
                 preserve authority the site already has, which is cheaper
                 than any new link. Pass the old URLs with --legacy.
  llms.txt       The one file a language model fetches on purpose.
  posts          The first N feed items are run through post_gate.py, so one
                 command says whether the newsroom is Discover-eligible.

Output is a report, not a gate: exit 1 if anything FAILs, 0 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import post_gate as pg  # noqa: E402

UA = ("Mozilla/5.0 (compatible; authority-audit/1.0; "
      "+https://github.com/agent-website-manager)")
TIMEOUT = 25
OK, WARN, FAIL, INFO = "OK", "WARN", "FAIL", "--"
ROWS: list[tuple[str, str, str]] = []

# (token in robots.txt, why it matters, the User-Agent to fetch with or None
#  when the token is robots-only and never crawls under its own name;
#  spoofable = the site may verify the bot by IP, so a refusal is not proof)
AI_AGENTS = [
    ("OAI-SearchBot", "ChatGPT search citations",
     "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; "
     "OAI-SearchBot/1.0; +https://openai.com/searchbot", False),
    ("GPTBot", "OpenAI training + browsing",
     "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
     "GPTBot/1.2; +https://openai.com/gptbot)", False),
    ("ClaudeBot", "Anthropic",
     "Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)", False),
    ("PerplexityBot", "Perplexity",
     "Mozilla/5.0 (compatible; PerplexityBot/1.0; "
     "+https://perplexity.ai/perplexitybot)", False),
    ("CCBot", "Common Crawl (feeds many models)",
     "CCBot/2.0 (https://commoncrawl.org/faq/)", False),
    ("Bingbot", "Bing: the index behind ChatGPT search",
     "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
     "bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/116.0.1938.76 "
     "Safari/537.36", True),
    ("Googlebot", "Google",
     "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
     "Googlebot/2.1; +http://www.google.com/bot.html) Chrome/120.0.0.0 "
     "Safari/537.36", True),
    ("Google-Extended", "Gemini training (robots-only token)", None, False),
]

PLATFORMS = {
    "linkedin.com": "linkedin", "youtube.com": "youtube", "github.com": "github",
    "wikidata.org": "wikidata", "wikipedia.org": "wikipedia",
    "crunchbase.com": "crunchbase", "x.com": "x", "twitter.com": "x",
    "instagram.com": "instagram", "facebook.com": "facebook",
    "g.page": "google-business", "maps.google.com": "google-business",
    "google.com": "google-business", "tracxn.com": "tracxn",
    "glassdoor.com": "glassdoor", "threads.net": "threads",
    "pinterest.com": "pinterest", "tiktok.com": "tiktok",
    "scholar.google.com": "scholar", "orcid.org": "orcid",
    "researchgate.net": "researchgate", "practo.com": "practo",
    "justdial.com": "justdial", "tripadvisor.com": "tripadvisor",
    "indiamart.com": "indiamart", "amazon.in": "amazon", "amazon.com": "amazon",
}
ORG_TYPES = {"Organization", "Corporation", "LocalBusiness", "Store",
             "MedicalBusiness", "MedicalClinic", "Physician", "Dentist",
             "TravelAgency", "TouristInformationCenter", "EducationalOrganization",
             "ProfessionalService", "OnlineStore", "NewsMediaOrganization"}


def row(status: str, label: str, detail: str = "") -> None:
    ROWS.append((status, label, detail))


def get(url: str, ua: str = UA, **kw):
    try:
        return requests.get(url, headers={"User-Agent": ua}, timeout=TIMEOUT, **kw)
    except requests.RequestException as e:
        return e


# ------------------------------------------------------------ pure helpers

def parse_robots(text: str) -> dict[str, list[tuple[str, str]]]:
    """agent (lower) -> [(directive, path)], groups sharing rules expanded;
    '__sitemaps__' -> [('sitemap', url)]."""
    groups: dict[str, list[tuple[str, str]]] = {}
    agents: list[str] = []
    rules: list[tuple[str, str]] = []

    def flush():
        for a in agents:
            groups.setdefault(a, []).extend(rules)

    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = (s.strip() for s in line.split(":", 1))
        k = k.lower()
        if k == "user-agent":
            if rules:
                flush()
                agents, rules = [], []
            agents.append(v.lower())
        elif k in ("allow", "disallow"):
            rules.append((k, v))
        elif k == "sitemap":
            groups.setdefault("__sitemaps__", []).append(("sitemap", v))
    if agents:
        flush()
    return groups


def robots_verdict(groups: dict, agent: str, path: str = "/") -> tuple[str, str]:
    """('allow'|'disallow', 'GPTBot'|'*'|'none'): longest matching rule wins,
    an Allow beats a Disallow of equal length, no group at all means allowed."""
    a = agent.lower()
    if a in groups:
        rules, src = groups[a], agent
    elif "*" in groups:
        rules, src = groups["*"], "*"
    else:
        return "allow", "none"
    best, verdict = -1, "allow"
    for d, p in rules:
        if not p:            # `Disallow:` with nothing = allow everything
            continue
        if rule_matches(p, path):
            n = len(p)
            if n > best or (n == best and d == "allow"):
                best, verdict = n, d
    return verdict, src


def rule_matches(pattern: str, path: str) -> bool:
    """robots.txt pattern semantics: anchored at the start, `*` is any run,
    a trailing `$` anchors the end. `/*?add-to-cart=` must NOT match `/`."""
    anchored = pattern.endswith("$")
    pat = pattern[:-1] if anchored else pattern
    rx = "^" + ".*".join(re.escape(part) for part in pat.split("*"))
    rx += "$" if anchored else ""
    return re.match(rx, path) is not None


def sameas_platforms(urls: list[str]) -> set[str]:
    out = set()
    for u in urls:
        host = urlparse(u).netloc.lower().removeprefix("www.")
        for dom, name in PLATFORMS.items():
            if host == dom or host.endswith("." + dom):
                out.add(name)
                break
    return out


def org_node(nodes: list[dict]) -> dict | None:
    for n in nodes:
        if types_of(n) & ORG_TYPES or "sameAs" in n:
            return n
    return None


def types_of(node: dict) -> set[str]:
    return pg.types_of(node)


def parse_date(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return parsedate_to_datetime(s)
    except (TypeError, ValueError):
        pass
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def cadence_days(dates: list[datetime]) -> float | None:
    ds = sorted((d for d in dates if d), reverse=True)[:6]
    if len(ds) < 3:
        return None
    gaps = [(ds[i] - ds[i + 1]).days for i in range(len(ds) - 1)]
    return statistics.median(gaps)


def feed_url_from_html(html: str, base: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("link", rel=lambda v: v and "alternate" in v):
        t = (link.get("type") or "").lower()
        if "rss" in t or "atom" in t:
            return urljoin(base, link.get("href", ""))
    return None


def blog_url_from_html(html: str, base: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    pat = re.compile(r"^/(blog|news|newsroom|insights|journal|articles|updates|press)/?$", re.I)
    for a in soup.find_all("a", href=True):
        u = urljoin(base, a["href"])
        if urlparse(u).netloc == urlparse(base).netloc and pat.match(urlparse(u).path or ""):
            return u
    return None


# ---------------------------------------------------------------- checks

def check_entity(html: str) -> None:
    nodes = pg.jsonld_nodes(html)
    org = org_node(nodes)
    if not org:
        row(FAIL, "entity", "no Organization/LocalBusiness JSON-LD on the home page")
        return
    same = org.get("sameAs") or []
    same = [same] if isinstance(same, str) else list(same)
    plats = sameas_platforms(same)
    label = f"{'/'.join(sorted(types_of(org)))} sameAs x{len(same)}"
    if not same:
        row(FAIL, "entity", label + ": nothing ties the name to any profile")
    elif len(plats) < 3:
        row(WARN, "entity", label + f" ({', '.join(sorted(plats)) or 'unrecognised'}): "
            "add the profiles that vouch for you (LinkedIn, YouTube, GitHub, Wikidata...)")
    else:
        row(OK, "entity", label + ": " + ", ".join(sorted(plats)))
    for want in ("linkedin", "wikidata"):
        if want not in plats:
            row(INFO, f"entity {want}", "not in sameAs")


def check_feed(base: str, html: str) -> list[dict]:
    cand = [feed_url_from_html(html, base)] if feed_url_from_html(html, base) else []
    cand += [urljoin(base, p) for p in ("/feed/", "/rss.xml", "/feed.xml",
                                        "/atom.xml", "/index.xml")]
    for u in cand:
        r = get(u)
        if isinstance(r, Exception) or r.status_code != 200:
            continue
        items = pg.feed_items(r.content)
        if not items:
            continue
        dates = [parse_date(i["date"]) for i in items]
        newest = max((d for d in dates if d), default=None)
        age = (datetime.now(timezone.utc) - newest).days if newest else None
        cad = cadence_days(dates)
        detail = f"{u}: {len(items)} items"
        if age is not None:
            detail += f", newest {age}d ago"
        if cad is not None:
            detail += f", one every ~{cad:.0f}d"
        if age is None:
            row(WARN, "feed", detail + ", undated items")
        elif age > 90:
            row(WARN, "feed", detail + ": reads as dormant (>90d)")
        else:
            row(OK, "feed", detail)
        authors = {i["author"] for i in items if i["author"]}
        if authors and all(a.lower() in pg.PLACEHOLDER_AUTHORS for a in authors):
            row(WARN, "feed authors", f"{', '.join(authors)}: roles, not people")
        elif authors:
            row(INFO, "feed authors", ", ".join(sorted(authors))[:90])
        return items
    row(FAIL, "feed", "no RSS/Atom feed found (tried the <link rel=alternate> and 5 usual paths)")
    return []


def check_blog(base: str, html: str) -> None:
    u = blog_url_from_html(html, base)
    if not u:
        row(WARN, "blog index", "no /blog, /news, /insights... link on the home page")
        return
    r = get(u)
    code = r.status_code if not isinstance(r, Exception) else "error"
    row(OK if code == 200 else FAIL, "blog index", f"{u} -> {code}")


def check_root_files(base: str) -> None:
    r = get(urljoin(base, "/llms.txt"))
    if isinstance(r, Exception) or r.status_code != 200:
        row(WARN, "llms.txt", "missing: the one file a model fetches on purpose")
    else:
        ct = r.headers.get("content-type", "")
        row(OK if "text/plain" in ct else WARN, "llms.txt",
            f"{len(r.text)} chars, {ct.split(';')[0] or 'no content-type'}")
    r = get(urljoin(base, "/BingSiteAuth.xml"))
    row(INFO, "BingSiteAuth.xml",
        "present" if not isinstance(r, Exception) and r.status_code == 200
        else "absent (fine if Bing was verified via GSC import or DNS)")


def check_robots_and_crawlers(base: str) -> None:
    r = get(urljoin(base, "/robots.txt"))
    if isinstance(r, Exception) or r.status_code != 200:
        row(WARN, "robots.txt", "not fetchable; every crawler assumes allow")
        groups = {}
    else:
        groups = parse_robots(r.text)
    # news sitemap
    smaps = [u for _, u in groups.get("__sitemaps__", [])] or [
        urljoin(base, "/sitemap_index.xml"), urljoin(base, "/sitemap.xml")]
    news = False
    for s in smaps[:3]:
        rs = get(s + ("&" if "?" in s else "?") + "x=audit")
        if isinstance(rs, Exception) or rs.status_code != 200:
            continue
        body = rs.text
        if "news" in s.lower() or "sitemap-news" in body or "xmlns:news" in body:
            news = True
            break
        for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)[:60]:
            if "news" in loc.lower():
                news = True
                break
        if news:
            break
    row(INFO, "news sitemap", "found" if news else
        "none (only needed once the newsroom publishes dated stories; then it is required)")
    # crawlers: what the file says vs what the server does
    stamp = int(time.time())
    for token, why, ua, spoofable in AI_AGENTS:
        verdict, src = robots_verdict(groups, token, "/")
        if ua is None:
            row(INFO, f"crawler {token}", f"robots {verdict} (via {src}); {why}")
            continue
        rr = get(base.rstrip("/") + f"/?audit={stamp}", ua=ua)
        code = rr.status_code if not isinstance(rr, Exception) else "error"
        if verdict == "disallow":
            row(INFO, f"crawler {token}", f"robots disallow (via {src}), server {code}; {why}")
        elif code == 200:
            row(OK, f"crawler {token}", f"robots allow, server 200; {why}")
        elif spoofable:
            row(INFO, f"crawler {token}",
                f"robots allow, server {code}: may be a verified-bot check rejecting a "
                f"spoofed UA; confirm in Bing/Google Webmaster crawl stats; {why}")
        else:
            row(FAIL, f"crawler {token}",
                f"robots allow (via {src}) but server answers {code}: invited by the file, "
                f"refused at the door (WAF / rate-limit rule); {why}")


def check_legacy(path: str, delay: float = 0.0) -> None:
    """Every old URL must 301 to a live page or still be live. `delay`
    spaces the requests: a burst of a few hundred got the probing IP
    throttled by the host (HTTPS and SSH both), which reads as FAILs."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    urls = [ln.strip() for ln in lines
            if ln.strip() and not ln.startswith("#")]
    for u in urls:
        if delay:
            time.sleep(delay)
        r = get(u, allow_redirects=True)
        if isinstance(r, Exception):
            row(FAIL, "legacy", f"{u}: {str(r)[:60]}")
            continue
        chain = [h.status_code for h in r.history]
        if r.status_code == 200 and not chain:
            row(OK, "legacy", f"{u}: still live")
        elif r.status_code == 200 and chain[0] in (301, 308):
            row(OK, "legacy", f"{u}: {chain[0]} -> {r.url}")
        elif r.status_code == 200:
            row(WARN, "legacy", f"{u}: {chain} (temporary redirect; make it 301)")
        else:
            row(FAIL, "legacy", f"{u}: ends {r.status_code}; earned links land on nothing")


def check_posts(items: list[dict], n: int) -> dict:
    report = {}
    for it in items[:n]:
        u = it["link"]
        if not u:
            continue
        rows = pg.gate(u)
        report[u] = rows
        fails = [lab for s, lab, _ in rows if s == FAIL]
        ready = any(lab == "Discover-ready" and s == OK for s, lab, _ in rows)
        status = FAIL if fails else (OK if ready else WARN)
        if ready:
            detail = "Discover-ready"
        elif fails:
            detail = "FAIL " + ", ".join(fails)
        else:
            warns = [f"{lab}: {d}" for s, lab, d in rows
                     if s == WARN and lab != "Discover-ready"]
            detail = "; ".join(warns)[:160]
        row(status, "post", f"{u}\n{'':30}{detail}")
    if report:
        ready = sum(1 for r in report.values()
                    if any(lab == "Discover-ready" and s == OK
                           for s, lab, _ in r))
        row(OK if ready == len(report) else WARN, "newsroom",
            f"{ready}/{len(report)} sampled posts Discover-ready")
    return report


# ------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url")
    ap.add_argument("--posts", type=int, default=5,
                    help="feed items to run through post_gate (0 to skip)")
    ap.add_argument("--legacy", help="file of old URLs that must 301 to live pages")
    ap.add_argument("--delay", type=float, default=0.5,
                    help="seconds between legacy-URL requests (host throttles bursts)")
    ap.add_argument("--json", help="write the report here")
    a = ap.parse_args()

    base = a.url if a.url.endswith("/") else a.url + "/"
    r = get(base)
    if isinstance(r, Exception) or r.status_code != 200:
        print(f"{base}: {r if isinstance(r, Exception) else r.status_code}")
        return 2
    base, html = r.url, r.text
    print(f"authority audit  {base}  {datetime.now(timezone.utc):%Y-%m-%d %H:%M}Z")

    check_entity(html)
    check_blog(base, html)
    items = check_feed(base, html)
    check_root_files(base)
    check_robots_and_crawlers(base)
    if a.legacy:
        check_legacy(a.legacy, a.delay)
    posts = check_posts(items, a.posts) if a.posts else {}

    width = max(len(lab) for _, lab, _ in ROWS)
    for s, label, detail in ROWS:
        print(f"  {s:4} {label:{width}}  {detail}")
    fails = sum(1 for s, _, _ in ROWS if s == FAIL)
    warns = sum(1 for s, _, _ in ROWS if s == WARN)
    print(f"\n{fails} FAIL, {warns} WARN")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"site": base, "rows": ROWS, "posts": posts}, f, indent=2)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
