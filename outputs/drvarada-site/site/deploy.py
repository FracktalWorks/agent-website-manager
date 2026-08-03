"""Publish this site to WordPress — the repo stays the source of truth.

WHY THIS EXISTS RATHER THAN `open_design_bridge.py deploy-canvas`
  The bridge deploys ONE page to the site named by `WORDPRESS_SITE_URL`. Four
  things make it the wrong tool here, each of which silently produces a broken
  site rather than an error:

  1. `WORDPRESS_SITE_URL` is fracktal.in. Running the bridge here would publish
     61 pages onto a different client's site.
  2. It hoists inline `<style>` tags. Our production build links an external
     stylesheet, so it would hoist nothing and publish 61 unstyled pages.
  3. It discards `<head>`. Canonicals, hreflang for the Telugu and Hindi pages,
     robots and og: tags all live there; only JSON-LD survives. It writes the
     description to a Yoast field, and Yoast is not installed on drvarada.com.
  4. It keeps no slug -> page-ID ledger, so a second run creates 61 duplicates
     instead of updating.

THE MODEL
  WordPress is a render target, not a place anyone edits. Each page is a real
  `page` post with its own ID, slug, parent and permalink; its body is one
  Custom HTML block on Elementor's chrome-free `elementor_canvas` template, so
  it renders byte-identical to `dist-prod/`. Editing happens here, in Python,
  through `editor.py` — and `deploy.py` pushes the result to the same page IDs.

  `<head>` is carried across verbatim as post meta and re-printed by the
  must-use plugin in `wp/drvarada-site.php`. Verbatim matters: reimplementing
  the head in PHP means it drifts the first time build.py changes and nobody
  notices, because a missing canonical looks like nothing at all.

STATE
  `.deploy/state.json` maps slug -> {id, hash, url}. The hash is of the exact
  content posted, so `plan` can say "8 changed, 51 unchanged" and `push` can
  skip the 51. Delete the file and the next run re-adopts pages by slug rather
  than duplicating them.

USAGE
  python deploy.py check        # connectivity + gates, writes nothing
  python deploy.py plan         # diff against the live site, writes nothing
  python deploy.py assets       # FTPS/SFTP sync of dist-prod/assets + mu-plugin
  python deploy.py push         # create/update pages (draft by default)
  python deploy.py publish      # flip the pushed pages to published
  python deploy.py retire       # trash the Hostinger AI placeholder pages + 301
  python deploy.py live         # fetch every published URL and check it
  python deploy.py purge        # clear LiteSpeed
  python deploy.py all          # check -> assets -> push  (still draft)
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from ftplib import FTP_TLS
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
DIST = ROOT / "dist-prod"
STATE = ROOT / ".deploy" / "state.json"
MU_PLUGIN = ROOT / "wp" / "drvarada-site.php"

sys.path.insert(0, str(ROOT))
from content.urls import URLS  # noqa: E402
import siteconf  # noqa: E402

# Parent pages WordPress needs so a nested permalink resolves. `vitiligo` and
# `psoriasis` are real pages of ours; these four only exist to hold a URL
# segment, so they are published (a draft parent 404s its children), noindexed,
# and redirected by the mu-plugin.
STUB_PARENTS = {
    "about":     ("About", "about-dr-khagendra-varada"),
    "locations": ("Locations", "locations-secunderabad"),
    "te":        ("తెలుగు", "te-vitiligo"),
    "hi":        ("हिन्दी", "hi-vitiligo"),
}

# The Hostinger AI starter pages. Every one is placeholder carrying a Springfield,
# Massachusetts address and a (123) 123 123 phone number — a local-SEO liability
# to leave indexed once 61 real pages exist. `about` and `contact` are REUSED
# (our page takes that ID) so those URLs never break; the rest are trashed with
# a 301 to the nearest real page.
REUSE = {"about": "about-dr-khagendra-varada", "contact": "contact"}
RETIRE = {
    "home": "index", "home-2": "index", "home-v2": "index",
    "about-2": "about-dr-khagendra-varada",
    "services": "treatments", "services-2": "treatments",
    "contact-2": "contact",
}


# ── environment ──────────────────────────────────────────────────────────────

def env() -> dict[str, str]:
    """Read .env. Never printed, never logged — see `mask()` for display."""
    out = {}
    f = REPO / ".env"
    if not f.exists():
        die(f"no .env at {f}")
    for line in f.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def mask(value: str) -> str:
    return f"{value[:3]}…{value[-2:]}" if len(value) > 6 else "…"


def die(msg: str) -> None:
    print(f"  FAIL  {msg}")
    raise SystemExit(1)


# ── WordPress REST ───────────────────────────────────────────────────────────

class WP:
    def __init__(self, e: dict[str, str]):
        for k in ("DRVARADA_SITE_URL", "DRVARADA_USERNAME", "DRVARADA_APP_PASSWORD"):
            if not e.get(k):
                die(f"{k} missing from .env")
        self.site = e["DRVARADA_SITE_URL"].rstrip("/")
        tok = f'{e["DRVARADA_USERNAME"]}:{e["DRVARADA_APP_PASSWORD"]}'.encode()
        self.auth = base64.b64encode(tok).decode()

    def call(self, path: str, method: str = "GET", data: dict | None = None):
        body = json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(
            f"{self.site}/wp-json/{path}", data=body, method=method,
            headers={"Authorization": f"Basic {self.auth}",
                     "Content-Type": "application/json",
                     "User-Agent": "drvarada-deploy"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            raise RuntimeError(f"{method} {path} -> {exc.code}: {detail}") from None

    def pages(self) -> list[dict]:
        """Every page, both statuses. 100 is the REST maximum per request."""
        out, page = [], 1
        while True:
            batch = self.call(f"wp/v2/pages?per_page=100&page={page}"
                              "&status=publish,draft,pending,private"
                              "&_fields=id,slug,status,link,parent,title")
            out += batch
            if len(batch) < 100:
                return out
            page += 1


# ── the page a slug becomes ──────────────────────────────────────────────────

def head_and_body(html: str) -> tuple[str, str, str]:
    """Split a built page into the head we re-print and the body we post.

    charset, viewport and <title> are dropped, and the title is returned
    separately so the plugin can feed it to `pre_get_document_title`.

    Printing our own <title> did not work: the Hostinger theme's header.php
    emits one LITERALLY, before wp_head() is ever called, so no hook can stop it
    — the page ended up with three. Filtering the title WordPress builds is the
    only way to get exactly one, and to have it be the string build.py
    length-checked rather than a "Page Name - Site Name" reconstruction that
    disagrees with the canonical and og:title beside it.
    """
    head = html[html.find("<head>") + 6:html.find("</head>")]
    head = re.sub(r'<meta charset="[^"]*"\s*/?>', "", head)
    head = re.sub(r'<meta name="viewport"[^>]*>', "", head)
    title = re.search(r"<title>(.*?)</title>", head, re.S)
    head = re.sub(r"<title>.*?</title>", "", head, flags=re.S)
    body = html[html.find("<body>") + 6:html.rfind("</body>")]
    return head.strip(), body.strip(), (title.group(1).strip() if title else "")


def content_block(body: str) -> str:
    """The body as one Gutenberg Custom HTML block.

    The admin app-password carries `unfiltered_html`, so the markup is stored
    and served intact. No widget conversion means no per-post Elementor CSS,
    which in turn means the "CSS did not regenerate / stale render" class of
    failure cannot occur here at all.
    """
    return f"<!-- wp:html -->\n{body}\n<!-- /wp:html -->"


def page_payload(slug: str, html: str, parent_id: int, status: str) -> dict:
    head, body, doc_title = head_and_body(html)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    name = doc_title or (h1.group(1) if h1 else slug)
    # The admin list reads better without the brand suffix on all 61 rows; the
    # browser title keeps it, via _drv_title below.
    name = re.sub(r"\s*\|\s*Dr\. Varada.*$", "", name.strip())
    return {
        "title": re.sub(r"<[^>]+>", "", name),
        "slug": slug.rsplit("/", 1)[-1],
        "content": content_block(body),
        "status": status,
        "parent": parent_id,
        "template": "elementor_canvas",
        "meta": {
            "_drv_head": head,          # printed verbatim by the mu-plugin
            "_drv_title": doc_title,    # fed to pre_get_document_title
            "_drv_managed": "1",        # marks this page as repo-owned
            "_elementor_edit_mode": "", # stop Elementor claiming the render
        },
    }


def wp_slug(path: str) -> str:
    """`/vitiligo/types-and-stages/` -> `types-and-stages` (the leaf only)."""
    return path.strip("/").rsplit("/", 1)[-1] or "index"


def parent_path(path: str) -> str:
    seg = path.strip("/").rsplit("/", 1)
    return seg[0] if len(seg) > 1 else ""


def tree() -> list[tuple[str, str, str]]:
    """(slug, url path, parent path), parents before children."""
    rows = [(s, u, parent_path(u)) for s, u in URLS.items() if s != "index"]
    return sorted(rows, key=lambda r: (r[1].count("/"), r[0]))


# ── gates ────────────────────────────────────────────────────────────────────

def plain(text: str) -> str:
    """Strip anything the Windows console cannot encode.

    verify.py prints box-drawing and an en dash; piping that through a cp1252
    stdout raises UnicodeEncodeError and takes down the deploy on a *successful*
    gate, which is a maddening way to fail.
    """
    return text.encode("ascii", "replace").decode("ascii")


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout + p.stderr)


def gates() -> None:
    """Never deploy a build that has not passed the same checks as a commit."""
    print("\n  gates")
    code, out = run([sys.executable, "build.py", "--links=production"], ROOT)
    if code:
        print(plain(out[-2000:]))
        die("production build failed")
    built = re.search(r"built (\d+) pages", out)
    print(f"    build      ok   {built.group(1) if built else '?'} pages -> dist-prod/")

    code, out = run([sys.executable, "verify.py", "--all"], ROOT)
    if code or "all" not in out:
        print(plain(out[-2000:]))
        die("verify.py reported render defects")
    print(f"    verify     ok   {plain(out.strip().splitlines()[-1].strip())}")

    code, out = run([sys.executable, "-m", "pytest", "tests/test_site_engine.py", "-q"], REPO)
    if code:
        print(plain(out[-1500:]))
        die("engine tests failed")
    print(f"    tests      ok   {plain(out.strip().splitlines()[-1].strip())}")


# ── assets over FTPS (or SFTP when paramiko is present) ──────────────────────

def tls_context() -> ssl.SSLContext:
    """Full CA-chain validation, hostname match relaxed — and here is why.

    Hostinger's FTP certificate is a genuine Sectigo-issued `*.hstgr.io`, but
    hPanel hands you an IP address to connect to, and no Hostinger API exposes
    the server's hstgr.io name. Verifying the hostname against an IP therefore
    fails every time, and the tempting fix — plain FTP — sends the password in
    clear text on every deploy.

    So the chain is still verified against the system trust store (a self-signed
    or forged certificate is rejected), and `assert_hostinger` below additionally
    requires the certificate to be the *.hstgr.io one. What is given up is proof
    of *which* Hostinger host answered, on an IP that came from the control
    panel. That is a far smaller exposure than an unencrypted login.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False           # verify_mode stays CERT_REQUIRED
    return ctx


def assert_hostinger(ftp: FTP_TLS) -> None:
    cert = ftp.sock.getpeercert() or {}
    names = {v for k, v in cert.get("subjectAltName", ()) if k == "DNS"}
    if not any(n == "hstgr.io" or n.endswith(".hstgr.io") for n in names):
        die(f"FTPS certificate is not Hostinger's (SAN={sorted(names) or 'none'}) "
            "— refusing to send credentials")


def sync_assets(e: dict[str, str], dry: bool = False) -> None:
    host, user = e.get("DRVARADA_FTP_HOST"), e.get("DRVARADA_FTP_USER")
    pwd, root = e.get("DRVARADA_FTP_PASS"), e.get("DRVARADA_FTP_ROOT", "/public_html")
    if not (host and user and pwd):
        die("DRVARADA_FTP_HOST / _USER / _PASS missing from .env — see the deploy plan")

    # sitemap.xml and robots.txt sit at the build root, not under assets/. They
    # have to ship: the mu-plugin turns off wp-sitemap.xml (it would compete for
    # the same job carrying none of the hreflang alternates), so forgetting these
    # leaves the site with no sitemap at all — and the Telugu and Hindi pages
    # depend on the alternates in this one to be understood as translations.
    local = [p for p in (DIST / "assets").rglob("*") if p.is_file()]
    local += [DIST / n for n in ("sitemap.xml", "robots.txt", "llms.txt",
                                 "favicon.ico",
                                 f"{siteconf.INDEXNOW_KEY}.txt")
              if (DIST / n).exists()]
    extra = [MU_PLUGIN] if MU_PLUGIN.exists() else []
    total = sum(p.stat().st_size for p in local + extra)
    print(f"\n  assets   {len(local)} file(s) + {len(extra)} mu-plugin, "
          f"{total/1024:.0f} KB -> {host} as {mask(user)}")
    for p in local:
        print(f"    {p.relative_to(DIST).as_posix():<40} {p.stat().st_size/1024:>7.1f} KB")
    if dry:
        print("    (dry run — nothing sent)")
        return

    ftp = FTP_TLS(context=tls_context())
    ftp.encoding = "utf-8"               # listings carry non-ASCII names
    ftp.connect(host, int(e.get("DRVARADA_FTP_PORT", 21)), timeout=60)
    # `connect()` leaves a PLAIN socket — with explicit FTPS the handshake happens
    # inside `login()`, which would put the certificate check after the password
    # had already gone. `auth()` is that same handshake, called early so the
    # assertion below actually guards the credentials. `login()` then sees an
    # SSLSocket and skips re-authenticating.
    ftp.auth()
    assert_hostinger(ftp)
    ftp.login(user, pwd)
    ftp.prot_p()

    def ensure(path: str) -> None:
        cur = ""
        for part in path.strip("/").split("/"):
            cur += "/" + part
            try:
                ftp.mkd(cur)
            except Exception:
                pass                     # already there, which is the normal case

    for p in local:
        rel = p.relative_to(DIST).as_posix()
        dest = f"{root.rstrip('/')}/{rel}"
        ensure(dest.rsplit("/", 1)[0])
        with p.open("rb") as fh:
            ftp.storbinary(f"STOR {dest}", fh)
        print(f"    sent {rel}")
    ensure_charset(ftp, root, e)

    # The mu-plugin goes last, and with a net under it. A must-use plugin is
    # parsed on EVERY request including wp-admin, so a single syntax error takes
    # the whole site down with no way to switch it off from the dashboard. PHP is
    # not installed locally, so the syntax cannot be checked before upload —
    # instead the site is probed straight afterwards and the file removed again
    # if it stopped answering. Rolling back over FTP takes about a second; being
    # locked out of wp-admin does not.
    for p in extra:
        dest = f"{root.rstrip('/')}/wp-content/mu-plugins/{p.name}"
        ensure(dest.rsplit("/", 1)[0])
        with p.open("rb") as fh:
            ftp.storbinary(f"STOR {dest}", fh)
        print(f"    sent wp-content/mu-plugins/{p.name}")

        ok, detail = site_healthy(e)
        if ok:
            print(f"    health   site answering ({detail}) — mu-plugin live")
        else:
            ftp.delete(dest)
            back, d2 = site_healthy(e)
            print(f"    health   FAILED ({detail}) — mu-plugin REMOVED, "
                  f"site {'recovered' if back else 'STILL DOWN: ' + d2}")
            ftp.quit()
            die("mu-plugin broke the site and was rolled back; fix the PHP and retry")
    ftp.quit()


HTACCESS_MARK = "# BEGIN drvarada-charset"
HTACCESS_BLOCK = rf"""{HTACCESS_MARK}
# Declare UTF-8 for the flat files we publish.
#
# llms.txt lists the Telugu and Hindi pages with their own descriptions, and the
# server was sending `Content-Type: text/plain` with NO charset. Browsers then
# fall back to windows-1252 and every multi-byte character turns to mojibake —
# the file was correct on disk and unreadable in a browser. Naive fetchers that
# trust the header rather than sniffing get the same garbage, which for a file
# whose entire purpose is being read by machines is the whole ballgame.
#
# Outside the # BEGIN WordPress block on purpose: WordPress rewrites its own
# section whenever permalinks are saved and would discard anything inside it.
# Two earlier attempts are recorded here because the next person will try them
# in the same order. `AddCharset UTF-8 .txt` — ignored. `AddType "text/plain;
# charset=UTF-8" .txt` — also ignored; this stack does not apply mod_mime
# directives from .htaccess to static files. mod_headers does get applied, so
# the header is set outright rather than derived from the extension.
<IfModule mod_headers.c>
  <FilesMatch "\.(txt)$">
    Header set Content-Type "text/plain; charset=UTF-8"
  </FilesMatch>
  <FilesMatch "\.(xml)$">
    Header set Content-Type "application/xml; charset=UTF-8"
  </FilesMatch>
</IfModule>
# END drvarada-charset
"""


def ensure_charset(ftp: FTP_TLS, root: str, e: dict[str, str]) -> None:
    """Append the charset block to .htaccess, with a rollback if the site dies.

    A malformed directive here 500s every URL on the domain, so the previous
    contents are held in memory and restored the moment the health check fails.
    """
    import io
    path = f"{root.rstrip('/')}/.htaccess"
    buf = io.BytesIO()
    try:
        ftp.retrbinary(f"RETR {path}", buf.write)
        current = buf.getvalue().decode("utf-8", "replace")
    except Exception:
        current = ""                      # no .htaccess yet; ours becomes it
    # Replace our block rather than skipping when it is present. Skipping meant
    # the FIRST directive written could never be corrected — and the first one
    # (AddCharset) was the one LiteSpeed ignored.
    if HTACCESS_MARK in current:
        head, _, rest = current.partition(HTACCESS_MARK)
        _, _, tail = rest.partition("# END drvarada-charset")
        current = (head.rstrip("\n") + "\n" + tail.lstrip("\n")).strip("\n")
    updated = (HTACCESS_BLOCK + "\n" + current) if current else HTACCESS_BLOCK
    ftp.storbinary(f"STOR {path}", io.BytesIO(updated.encode("utf-8")))
    ok, detail = site_healthy(e)
    if ok:
        print(f"    charset   .htaccess updated, site answering ({detail})")
        return
    ftp.storbinary(f"STOR {path}", io.BytesIO(current.encode("utf-8")))
    back, d2 = site_healthy(e)
    print(f"    charset   FAILED ({detail}) — .htaccess RESTORED, "
          f"site {'recovered' if back else 'STILL DOWN: ' + d2}")
    die("the charset directive broke the site and was rolled back")


def site_healthy(e: dict[str, str]) -> tuple[bool, str]:
    """Front page and REST both answering. Anything 5xx means the plugin broke."""
    base = e["DRVARADA_SITE_URL"].rstrip("/")
    results = []
    for path in ("/", "/wp-json/"):
        try:
            req = urllib.request.Request(base + path,
                                         headers={"User-Agent": "drvarada-deploy"})
            with urllib.request.urlopen(req, timeout=30) as r:
                results.append(f"{path} {r.status}")
                if r.status >= 500:
                    return False, f"{path} {r.status}"
        except urllib.error.HTTPError as exc:
            results.append(f"{path} {exc.code}")
            if exc.code >= 500:
                return False, f"{path} {exc.code}"
        except Exception as exc:
            return False, f"{path} {type(exc).__name__}"
    return True, ", ".join(results)


# ── state ledger ─────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"pages": {}, "stubs": {}}


def save_state(s: dict) -> None:
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(s, indent=1, ensure_ascii=False), encoding="utf-8")


def digest(payload: dict) -> str:
    """Hash everything that is actually sent, meta included.

    This used to name the meta keys it cared about one by one, and adding a new
    one silently broke the ledger: fixing `_drv_stub_target` changed nothing the
    hash looked at, so `push` reported "unchanged 65" and skipped the very pages
    the fix was for. Hashing the whole payload means any change deploys.
    """
    keyed = {k: payload[k] for k in ("title", "content", "parent", "template")}
    keyed["meta"] = payload["meta"]
    return hashlib.sha256(
        json.dumps(keyed, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_check(e: dict) -> None:
    wp = WP(e)
    info = wp.call("")
    print(f"\n  wordpress  {wp.site}  ({info.get('name')})")
    live = wp.pages()
    print(f"    reachable, {len(live)} page(s) currently on the site")
    ftp_ready = all(e.get(k) for k in ("DRVARADA_FTP_HOST", "DRVARADA_FTP_USER",
                                       "DRVARADA_FTP_PASS"))
    print(f"    ftp creds  {'present' if ftp_ready else 'MISSING — assets cannot sync yet'}")
    print(f"    mu-plugin  {'present' if MU_PLUGIN.exists() else 'MISSING'}")
    gates()


def cmd_plan(e: dict, apply: bool = False, status: str = "draft") -> None:
    if not DIST.exists():
        die("no dist-prod/ — run `python deploy.py check` first")
    wp = WP(e)
    state = load_state()
    live = {p["slug"]: p for p in wp.pages()}
    ids: dict[str, int] = {}
    create, update, same = [], [], []

    def resolve(slug: str, payload: dict, key: str) -> None:
        known = state[key].get(slug, {})
        existing = live.get(payload["slug"])
        pid = known.get("id") or (existing["id"] if existing else None)
        h = digest(payload)
        if pid is None:
            create.append((slug, payload, h))
        elif known.get("hash") != h:
            update.append((slug, payload, h, pid))
        else:
            same.append(slug)
            ids[slug] = pid
        if pid:
            ids[slug] = pid

    # 1. stub parents first — a child cannot be created before its parent exists
    for seg, (title, target) in STUB_PARENTS.items():
        payload = {"title": title, "slug": seg, "content": "", "status": "publish",
                   "parent": 0, "template": "elementor_canvas",
                   "meta": {"_drv_head": "", "_drv_managed": "1",
                            # The URL PATH, not our internal slug. The plugin
                            # used get_page_by_path() on the slug and always got
                            # null: `about-dr-khagendra-varada` is our key, but
                            # in WordPress that page's path is
                            # `about/dr-khagendra-varada`. The stubs answered 200
                            # instead of redirecting.
                            "_drv_stub_target": URLS[target],
                            "_elementor_edit_mode": ""}}
        resolve(f"__stub__{seg}", payload, "stubs")

    # 2. index, then every page shallowest-first so parents resolve
    rows = [("index", "/", "")] + tree()
    for slug, path, parent in rows:
        f = DIST / ("index.html" if slug == "index" else f"{slug}.html")
        if not f.exists():
            die(f"{slug}: {f.name} missing from dist-prod/")
        pid_parent = 0
        if parent:
            owner = next((s for s, u in URLS.items() if u.strip("/") == parent), None)
            key = owner or f"__stub__{parent}"
            pid_parent = ids.get(key, 0)
            if not pid_parent and not apply:
                pid_parent = -1          # will exist by the time we write
        payload = page_payload(slug, f.read_text(encoding="utf-8"),
                               max(pid_parent, 0), status)
        payload["slug"] = wp_slug(path)
        resolve(slug, payload, "pages")

    print(f"\n  plan against {wp.site}")
    print(f"    create   {len(create):>3}")
    print(f"    update   {len(update):>3}")
    print(f"    unchanged{len(same):>3}")
    for slug, payload, _ in create[:60]:
        print(f"      + {slug:<38} -> {URLS.get(slug, '/'+payload['slug']+'/')}")
    for slug, _, _, pid in update[:60]:
        print(f"      ~ {slug:<38} (id {pid})")
    if not apply:
        print("\n    dry run — nothing written. `push` applies it.")
        return

    for slug, payload, h in create:
        if payload["parent"] == 0 and slug not in ("index", *[f"__stub__{s}" for s in STUB_PARENTS]):
            path = URLS.get(slug, "")
            if parent_path(path):
                owner = next((s for s, u in URLS.items()
                              if u.strip("/") == parent_path(path)), None)
                payload["parent"] = ids.get(owner or f"__stub__{parent_path(path)}", 0)
        res = wp.call("wp/v2/pages", "POST", payload)
        key = "stubs" if slug.startswith("__stub__") else "pages"
        state[key][slug] = {"id": res["id"], "hash": h, "url": res.get("link", "")}
        ids[slug] = res["id"]
        print(f"    created {slug:<38} id {res['id']}")
        save_state(state)
    for slug, payload, h, pid in update:
        # Never re-send `status` on an update. `push` defaults to draft so a
        # first deploy is not public — but sending that on an update would
        # unpublish a live page, and once the site is up an ordinary content
        # deploy would take all 61 pages offline at once. Status is owned by
        # `publish`/wp-admin; `push` owns content. (Found the hard way: the test
        # page went back to 404 on its second push.)
        payload = {k: v for k, v in payload.items() if k != "status"}
        res = wp.call(f"wp/v2/pages/{pid}", "POST", payload)
        key = "stubs" if slug.startswith("__stub__") else "pages"
        state[key][slug] = {"id": res["id"], "hash": h, "url": res.get("link", "")}
        print(f"    updated {slug:<38} id {res['id']}")
        save_state(state)
    # What this push actually touched, for `indexnow` to submit. Recorded here
    # rather than recomputed later because by the time anything else runs, the
    # hashes in `state` already match the build and the diff is gone.
    state["last_push"] = sorted(
        {s for s, *_ in create} | {s for s, *_ in update}
        - {s for s in state.get("stubs", {})})
    save_state(state)
    print(f"\n    state -> {STATE.relative_to(REPO)}")


def cmd_publish(e: dict) -> None:
    wp, state = WP(e), load_state()
    front = state["pages"].get("index", {}).get("id")
    n = 0
    for slug, rec in {**state["stubs"], **state["pages"]}.items():
        wp.call(f"wp/v2/pages/{rec['id']}", "POST", {"status": "publish"})
        n += 1
    print(f"  published {n} page(s)")
    if front:
        wp.call("wp/v2/settings", "POST", {"show_on_front": "page", "page_on_front": front})
        print(f"  front page set to id {front}")


def cmd_retire(e: dict) -> None:
    """Trash the placeholder pages, after redirect rules are in the mu-plugin."""
    wp, state = WP(e), load_state()
    live = {p["slug"]: p for p in wp.pages()}
    managed = {r["id"] for r in {**state["pages"], **state["stubs"]}.values()}
    for slug, target in RETIRE.items():
        p = live.get(slug)
        if not p or p["id"] in managed:
            print(f"    skip {slug} (absent, or now one of ours)")
            continue
        wp.call(f"wp/v2/pages/{p['id']}", "DELETE")     # to trash, recoverable
        print(f"    trashed {slug} (id {p['id']}) -> 301 to {URLS.get(target, '/')}")
    print("  redirects are served by the mu-plugin from the same table.")


def cmd_live(e: dict) -> None:
    """Fetch every published URL and prove it is really serving our page.

    Deliberately serial with a pause. Eight parallel requests made seventeen
    pages return 500 on this shared plan — a worker limit, not a fault in the
    pages (every one of them answered 200 when asked on its own). A concurrent
    checker here would report a broken site that is not broken, which is the
    worst kind of test.
    """
    base = e["DRVARADA_SITE_URL"].rstrip("/")
    bad, sizes = [], []
    for slug, path in URLS.items():
        try:
            req = urllib.request.Request(base + path, headers={"User-Agent": "drv-live"})
            with urllib.request.urlopen(req, timeout=45) as r:
                body = r.read().decode("utf-8", "replace")
            problems = [n for n, ok in (
                ("status", r.status == 200),
                ("stylesheet", "/assets/site.css" in body),
                ("canonical", f'rel="canonical" href="{base}{path}"' in body),
                ("theme-css-leak", "hostinger-ai-theme/assets/css" not in body),
            ) if not ok]
            sizes.append(len(body))
            if problems:
                bad.append((slug, path, ", ".join(problems)))
        except Exception as exc:
            bad.append((slug, path, f"{type(exc).__name__}"))
        time.sleep(0.4)
    print(f"\n  live check — {len(URLS)} URLs on {base}")
    print(f"    clean    {len(URLS) - len(bad)}")
    for slug, path, why in bad:
        print(f"    FAIL     {slug:<36} {path:<38} {why}")
    if sizes:
        sizes.sort()
        print(f"    page size  median {sizes[len(sizes)//2]/1024:.0f} KB, "
              f"max {sizes[-1]/1024:.0f} KB")


def cmd_purge(e: dict) -> None:
    """Purge via our own mu-plugin route — it is the one we know exists."""
    try:
        res = WP(e).call("drvarada/v1/purge", "POST", {})
        print(f"  litespeed purged (mu-plugin {res.get('plugin')})")
    except Exception as exc:
        print(f"  purge route unavailable ({str(exc)[:90]}); "
              "purge from wp-admin if pages look stale")


def cmd_indexnow(e: dict, changed_only: bool = True) -> None:
    """Tell Bing which URLs changed, instead of waiting to be crawled.

    Defaults to the pages this deploy actually touched, read from the same
    ledger `push` writes. Submitting all 61 every time is not an error, but it
    is noise, and IndexNow's stated abuse guard is exactly that: hosts that
    resubmit unchanged URLs get their submissions throttled. `--all` is there
    for a first run or after a rebuild, and says so.
    """
    key = siteconf.INDEXNOW_KEY
    base = e["DRVARADA_SITE_URL"].rstrip("/")
    host = base.split("://", 1)[1]
    key_url = f"{base}/{key}.txt"
    ua = {"User-Agent": "drvarada-deploy"}

    # The key file is the whole ownership proof. If it is not live, every
    # submission is rejected with 403 and the message is not obvious, so check
    # first and say plainly what is wrong.
    try:
        req = urllib.request.Request(key_url, headers=ua)
        with urllib.request.urlopen(req, timeout=30) as r:
            served = r.read().decode("utf-8", "replace").strip()
    except Exception as ex:
        print(f"\n  key file unreachable at {key_url} ({type(ex).__name__})")
        print("  run `python deploy.py assets` first — it ships the key file")
        return
    if served != key:
        print(f"\n  key file at {key_url} does not contain the key")
        print("  rebuild and re-run `assets`")
        return

    state = load_state()
    if changed_only:
        urls = [base + URLS[s] for s in state.get("last_push", []) if s in URLS]
        if not urls:
            print("\n  nothing changed in the last push — "
                  "use `indexnow --all` to resubmit everything")
            return
    else:
        urls = [base + p for p in URLS.values()]

    payload = json.dumps({"host": host, "key": key, "keyLocation": key_url,
                          "urlList": sorted(set(urls))}).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow", data=payload,
        headers={"Content-Type": "application/json; charset=utf-8", **ua})
    print(f"\n  indexnow  submitting {len(set(urls))} URL(s) for {host}")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            code = r.status
    except urllib.error.HTTPError as ex:
        code = ex.code
    # 200 accepted, 202 accepted but the key is still being validated.
    if code in (200, 202):
        print(f"    accepted ({code}) — Bing, Yandex, Seznam and Naver share "
              f"this endpoint; Google does not participate")
    elif code == 403:
        print(f"    rejected (403) — key file not valid for this host")
    elif code == 422:
        print(f"    rejected (422) — a URL did not belong to {host}")
    else:
        print(f"    unexpected response {code}")


def cmd_settings(e: dict, apply: bool = False) -> None:
    """Make WordPress's own options agree with the site's constants.

    The pages are ours, but the OPTIONS TABLE is not — it still holds whatever
    was typed into Settings → General when the install was made, and nothing in
    the build ever touches it. That is how `blogname` came to read "Dr Varada's
    Skin Center" while every page, the schema and the Google listing said
    "Dr. Varada's Skin & Hair Center": a third spelling of the brand, injected
    by WordPress into feed titles, the RSS `<title>`, and anywhere a plugin asks
    for the site name. Answer engines quote whatever they find, and a business
    with three names is three businesses to a machine trying to reconcile them.

    Ping and comment defaults are here for a different reason. Every existing
    page already has both closed, so this is not a live problem — it is a
    LATENT one: the defaults apply to whatever is created next, and a medical
    site that grows a comment form grows comment spam, which is a ranking
    liability rather than a cosmetic one.

    Read-only by default. `--apply` writes.
    """
    import html as _html

    import chrome as C
    wp = WP(e)

    def same(stored, wanted: str) -> bool:
        """Compare a stored option against what we asked for.

        WordPress core's `sanitize_option()` runs `wp_kses_post()` and then
        `esc_html()` over `blogname` and `blogdescription` before saving, so a
        brand containing `&` or an apostrophe comes back as
        `Dr. Varada&#039;s Skin &amp; Hair Center`. It renders correctly — WP
        decodes on output — but a naive `stored == wanted` reports the write as
        having failed, every time, forever. That is a false alarm that would
        send the next reader hunting for a plugin that does not exist.
        """
        return _html.unescape(str(stored)) == wanted
    want = {
        "title": C.BRAND_PLAIN,
        # The tagline is empty on this install. WordPress's own default is
        # "Just another WordPress site"; empty is better than that and worse
        # than the truth, and it surfaces in feeds and search snippets.
        "description": f"Dermatologist in {C.LOCALITY}, {C.CITY} — "
                       f"vitiligo, psoriasis, skin and hair",
        "default_comment_status": "closed",
        "default_ping_status": "closed",
    }
    have = wp.call("wp/v2/settings")
    drift = {k: v for k, v in want.items() if not same(have.get(k), v)}
    print(f"\n  settings on {wp.site}")
    for k, v in want.items():
        cur = have.get(k)
        ok = same(cur, v)
        print(f"    {'ok ' if ok else '->'} {k:24} {cur!r}")
        if not ok:
            print(f"       {'':24} {v!r}")
    if not drift:
        print("\n    nothing to change.")
        return
    if not apply:
        print(f"\n    {len(drift)} to change — dry run. "
              "`settings --apply` writes.")
        return
    wp.call("wp/v2/settings", method="POST", data=drift)
    after = wp.call("wp/v2/settings")
    bad = [k for k, v in want.items() if not same(after.get(k), v)]
    # Read back rather than trusting the write. Some options are filtered by a
    # plugin or a mu-plugin on save, so a 200 does not prove the value stuck.
    if bad:
        die("applied, but these did not stick (a plugin may be filtering "
            f"them): {', '.join(bad)}")
    print(f"\n    applied {len(drift)}, verified by read-back.")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    e = env()
    if cmd == "check":
        cmd_check(e)
    elif cmd == "plan":
        cmd_plan(e, apply=False)
    elif cmd == "assets":
        sync_assets(e, dry="--dry-run" in sys.argv)
    elif cmd == "push":
        cmd_plan(e, apply=True, status="draft")
    elif cmd == "publish":
        cmd_publish(e); cmd_purge(e)
    elif cmd == "live":
        cmd_live(e)
    elif cmd == "purge":
        cmd_purge(e)
    elif cmd == "indexnow":
        cmd_indexnow(e, changed_only="--all" not in sys.argv)
    elif cmd == "settings":
        cmd_settings(e, apply="--apply" in sys.argv)
    elif cmd == "retire":
        cmd_retire(e); cmd_purge(e)
    elif cmd == "all":
        cmd_check(e); sync_assets(e); cmd_plan(e, apply=True, status="draft")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
