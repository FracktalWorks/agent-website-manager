# -*- coding: utf-8 -*-
"""Shared WordPress REST client for the website_analysis skill.

Loads credentials from the repo-root .env (WORDPRESS_SITE_URL / _USERNAME /
_APP_PASSWORD), exposes a thin req() helper, and resolves the outputs dir.
Other scripts in this skill do `import wp_client as wp`.
"""
import os, json, base64, urllib.request, urllib.error
from pathlib import Path
from urllib.parse import urlparse


def _find_repo_root():
    """Nearest ancestor (of cwd, then of this file) that contains a .env."""
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for p in (start, *start.parents):
            if (p / ".env").exists():
                return p
    return Path.cwd()


REPO_ROOT = _find_repo_root()


def load_env():
    env = {}
    envfile = REPO_ROOT / ".env"
    if envfile.exists():
        for line in envfile.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    # real environment variables win over .env
    for k in ("WORDPRESS_SITE_URL", "WORDPRESS_USERNAME",
              "WORDPRESS_APP_PASSWORD", "HOSTINGER_API_TOKEN"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


ENV = load_env()
SITE = (ENV.get("WORDPRESS_SITE_URL") or "").rstrip("/")
_USER = ENV.get("WORDPRESS_USERNAME") or ""
_PW = ENV.get("WORDPRESS_APP_PASSWORD") or ""
AUTH = base64.b64encode(f"{_USER}:{_PW}".encode()).decode() if _USER and _PW else ""
UA = {"User-Agent": "Mozilla/5.0 (website-analysis)"}


def site_slug():
    host = (urlparse(SITE).netloc or SITE).replace("www.", "")
    return host.split(".")[0] or "site"


def req(path, method="GET", body=None, auth=True, timeout=60):
    """Call the WP REST API. `path` is relative to /wp-json/wp/v2/ unless it's a
    full URL. Returns parsed JSON."""
    url = path if path.startswith("http") else f"{SITE}/wp-json/wp/v2/{path.lstrip('/')}"
    data = json.dumps(body).encode() if body is not None else None
    headers = dict(UA); headers["Content-Type"] = "application/json"
    if auth and AUTH:
        headers["Authorization"] = f"Basic {AUTH}"
    r = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return json.load(resp)


def req_with_headers(path, timeout=60, auth=True):
    """Like req() but returns (json, response_headers) — used for X-WP-Total counts."""
    url = path if path.startswith("http") else f"{SITE}/wp-json/wp/v2/{path.lstrip('/')}"
    headers = dict(UA)
    if auth and AUTH:
        headers["Authorization"] = f"Basic {AUTH}"
    r = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return json.load(resp), dict(resp.headers)


def fetch(url, timeout=30):
    """GET raw text; returns '' on error (never raises)."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return ""


def status_of(url, timeout=20):
    """Return HTTP status code for a URL (follows redirects reports final)."""
    try:
        req_ = urllib.request.Request(url, headers=UA, method="GET")
        with urllib.request.urlopen(req_, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def out_dir(slug=None):
    slug = slug or site_slug()
    d = REPO_ROOT / "outputs" / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def save(name, data, slug=None):
    """Write a JSON report to outputs/<slug>/<name> and return the path."""
    path = out_dir(slug) / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
