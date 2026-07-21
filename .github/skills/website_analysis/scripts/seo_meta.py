# -*- coding: utf-8 -*-
"""Read / update Yoast SEO meta (title, description, focus keyword) via REST.

Used to *execute* the fixes a report recommends. Yoast's title/metadesc meta are
REST-exposed on this install; a PUT updates them (and %%sep%% / %%sitename%%
template variables are allowed in the title).

Usage:
  python seo_meta.py read 31954 31832
  python seo_meta.py read --type post 5002
  python seo_meta.py set 31832 --title "3D Printer Manufacturer in India %%sep%% %%sitename%%" \
                               --desc "..." [--focus "..."]
"""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp_client as wp

KEYS = {"title": "_yoast_wpseo_title", "desc": "_yoast_wpseo_metadesc",
        "focus": "_yoast_wpseo_focuskw"}


def _base(post_type):
    return {"page": "pages", "post": "posts", "product": "product"}.get(post_type, post_type)


def read(pid, post_type="page"):
    d = wp.req(f"{_base(post_type)}/{pid}?context=edit")
    m = d.get("meta", {}) or {}
    print("=" * 55, pid, d.get("slug"))
    print("  template:", repr(d.get("template")))
    for label, key in KEYS.items():
        print(f"  {key} = {m.get(key)!r}")


def setmeta(pid, post_type, title, desc, focus):
    meta = {}
    if title is not None: meta[KEYS["title"]] = title
    if desc is not None:  meta[KEYS["desc"]] = desc
    if focus is not None: meta[KEYS["focus"]] = focus
    d = wp.req(f"{_base(post_type)}/{pid}", method="POST", body={"meta": meta})
    m = d.get("meta", {}) or {}
    print("UPDATED", pid)
    for key in KEYS.values():
        if key in meta:
            print(f"  {key} = {m.get(key)!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", default="page", help="page | post | product")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read"); r.add_argument("ids", nargs="+", type=int)
    s = sub.add_parser("set"); s.add_argument("id", type=int)
    s.add_argument("--title"); s.add_argument("--desc"); s.add_argument("--focus")
    a = ap.parse_args()
    if a.cmd == "read":
        for i in a.ids:
            read(i, a.type)
    elif a.cmd == "set":
        setmeta(a.id, a.type, a.title, a.desc, a.focus)


if __name__ == "__main__":
    main()
