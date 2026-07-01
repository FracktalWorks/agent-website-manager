#!/usr/bin/env python3
"""
WooCommerce REST API Client (v3)

Full CRUD operations for WooCommerce store management.
Products, orders, customers, coupons, categories, tags, attributes.

Usage:
    python wc_rest_api.py --action list-products
    python wc_rest_api.py --action create-product --name "T-Shirt" --price 29.99
    python wc_rest_api.py --action list-orders --status processing
"""

import os, sys, json, argparse, base64
from pathlib import Path
from urllib.parse import urljoin
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
WC_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "")
WC_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET", "")

API_BASE = f"{WP_URL}/wp-json/wc/v3"
AUTH_STR = base64.b64encode(f"{WC_KEY}:{WC_SECRET}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {AUTH_STR}",
    "Content-Type": "application/json",
    "User-Agent": "Agent-Website-Manager/1.0",
}


def _check():
    missing = []
    if not WP_URL:
        missing.append("WORDPRESS_SITE_URL")
    if not WC_KEY:
        missing.append("WOOCOMMERCE_CONSUMER_KEY")
    if not WC_SECRET:
        missing.append("WOOCOMMERCE_CONSUMER_SECRET")
    if missing:
        print(json.dumps({"error": True, "message": f"Missing: {', '.join(missing)}"}))
        sys.exit(1)


def _get(ep, params=None):
    url = urljoin(API_BASE + "/", ep.lstrip("/"))
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json(), dict(r.headers)


def _post(ep, data):
    url = urljoin(API_BASE + "/", ep.lstrip("/"))
    r = requests.post(url, headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def _put(ep, data):
    url = urljoin(API_BASE + "/", ep.lstrip("/"))
    r = requests.put(url, headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def _delete(ep, params=None):
    url = urljoin(API_BASE + "/", ep.lstrip("/"))
    r = requests.delete(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


# ── Products ────────────────────────────────────────────────────────────

def action_list_products(args):
    params = {"per_page": args.per_page or 20, "page": args.page or 1}
    if args.status:
        params["status"] = args.status
    if args.search:
        params["search"] = args.search
    if args.category:
        params["category"] = args.category
    data, headers = _get("products", params)
    items = [{"id": p["id"], "name": p["name"], "price": p["price"],
              "stock": p.get("stock_quantity", "N/A"), "status": p["status"]}
             for p in data]
    return {"products": items, "total": headers.get("X-WP-Total", len(items))}


def action_get_product(args):
    p = _get(f"products/{args.id}")[0]
    return {"id": p["id"], "name": p["name"], "slug": p["slug"],
            "price": p["price"], "regular_price": p["regular_price"],
            "sale_price": p["sale_price"], "stock": p.get("stock_quantity"),
            "status": p["status"], "categories": p.get("categories", []),
            "images": [{"id": i["id"], "src": i["src"]} for i in p.get("images", [])],
            "description": p.get("description", "")[:300],
            "short_description": p.get("short_description", "")[:200]}


def action_create_product(args):
    data = {"name": args.name, "type": args.type or "simple"}
    if args.price:
        data["regular_price"] = str(args.price)
    if args.description:
        data["description"] = args.description
    if args.short_description:
        data["short_description"] = args.short_description
    if args.sku:
        data["sku"] = args.sku
    if args.stock is not None:
        data["stock_quantity"] = int(args.stock)
        data["manage_stock"] = True
    if args.status:
        data["status"] = args.status
    if args.categories:
        data["categories"] = [{"id": int(c)} for c in args.categories.split(",")]
    result = _post("products", data)
    return {"created": True, "product": {"id": result["id"], "name": result["name"],
            "price": result.get("price", ""), "link": result.get("permalink", "")}}


def action_update_product(args):
    data = {}
    if args.name:
        data["name"] = args.name
    if args.price is not None:
        data["regular_price"] = str(args.price)
    if args.sale_price is not None:
        data["sale_price"] = str(args.sale_price)
    if args.stock is not None:
        data["stock_quantity"] = int(args.stock)
        data["manage_stock"] = True
    if args.status:
        data["status"] = args.status
    result = _put(f"products/{args.id}", data)
    return {"updated": True, "product": {"id": result["id"], "name": result["name"],
            "price": result.get("price", ""), "stock": result.get("stock_quantity")}}


def action_delete_product(args):
    _delete(f"products/{args.id}", {"force": args.force})
    return {"deleted": True, "id": args.id}


def action_list_categories(args):
    params = {"per_page": args.per_page or 50, "page": args.page or 1}
    data, headers = _get("products/categories", params)
    cats = [{"id": c["id"], "name": c["name"], "slug": c["slug"],
             "count": c["count"]} for c in data]
    return {"categories": cats, "total": headers.get("X-WP-Total", len(cats))}


# ── Orders ──────────────────────────────────────────────────────────────

def action_list_orders(args):
    params = {"per_page": args.per_page or 20, "page": args.page or 1}
    if args.status:
        params["status"] = args.status
    if args.search:
        params["search"] = args.search
    if args.after:
        params["after"] = args.after
    if args.before:
        params["before"] = args.before
    data, headers = _get("orders", params)
    items = [{"id": o["id"], "number": o.get("number", ""),
              "status": o["status"], "total": o["total"],
              "currency": o["currency"],
              "customer": o.get("billing", {}).get("first_name", "") + " " +
                          o.get("billing", {}).get("last_name", ""),
              "date": o.get("date_created", "")}
             for o in data]
    return {"orders": items, "total": headers.get("X-WP-Total", len(items))}


def action_get_order(args):
    o = _get(f"orders/{args.id}")[0]
    return {"id": o["id"], "number": o.get("number", ""), "status": o["status"],
            "total": o["total"], "currency": o["currency"],
            "billing": o.get("billing", {}), "shipping": o.get("shipping", {}),
            "items": [{"name": i["name"], "qty": i["quantity"],
                       "total": i["total"]} for i in o.get("line_items", [])],
            "date": o.get("date_created", ""),
            "payment_method": o.get("payment_method_title", "")}


def action_update_order(args):
    data = {}
    if args.status:
        data["status"] = args.status
    result = _put(f"orders/{args.id}", data)
    return {"updated": True, "order": {"id": result["id"], "number": result.get("number", ""),
            "status": result["status"]}}


# ── Customers ───────────────────────────────────────────────────────────

def action_list_customers(args):
    params = {"per_page": args.per_page or 20, "page": args.page or 1}
    if args.search:
        params["search"] = args.search
    data, headers = _get("customers", params)
    items = [{"id": c["id"], "name": c.get("first_name", "") + " " + c.get("last_name", ""),
              "email": c["email"], "orders": c.get("orders_count", 0),
              "total_spent": c.get("total_spent", "0")}
             for c in data]
    return {"customers": items, "total": headers.get("X-WP-Total", len(items))}


# ── Coupons ─────────────────────────────────────────────────────────────

def action_list_coupons(args):
    params = {"per_page": args.per_page or 20, "page": args.page or 1}
    data, headers = _get("coupons", params)
    items = [{"id": c["id"], "code": c["code"], "type": c.get("discount_type", ""),
              "amount": c["amount"], "usage": c.get("usage_count", 0),
              "expires": c.get("date_expires", "Never")}
             for c in data]
    return {"coupons": items, "total": headers.get("X-WP-Total", len(items))}


def action_create_coupon(args):
    data = {"code": args.code, "discount_type": args.type or "percent",
            "amount": str(args.amount)}
    if args.min_amount:
        data["minimum_amount"] = str(args.min_amount)
    if args.max_amount:
        data["maximum_amount"] = str(args.max_amount)
    if args.usage_limit:
        data["usage_limit"] = int(args.usage_limit)
    if args.expires:
        data["date_expires"] = args.expires
    result = _post("coupons", data)
    return {"created": True, "coupon": {"id": result["id"], "code": result["code"],
            "type": result.get("discount_type", ""), "amount": result["amount"]}}


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="WooCommerce REST API Client")
    parser.add_argument("--action", required=True, choices=[
        "list-products", "get-product", "create-product", "update-product", "delete-product",
        "list-categories",
        "list-orders", "get-order", "update-order",
        "list-customers",
        "list-coupons", "create-coupon",
    ])
    parser.add_argument("--id", type=int)
    parser.add_argument("--name")
    parser.add_argument("--type")
    parser.add_argument("--price", type=float)
    parser.add_argument("--sale-price", dest="sale_price", type=float)
    parser.add_argument("--description")
    parser.add_argument("--short-description", dest="short_description")
    parser.add_argument("--sku")
    parser.add_argument("--stock", type=int)
    parser.add_argument("--status")
    parser.add_argument("--categories")
    parser.add_argument("--category")
    parser.add_argument("--search")
    parser.add_argument("--after")
    parser.add_argument("--before")
    parser.add_argument("--code")
    parser.add_argument("--amount", type=float)
    parser.add_argument("--min-amount", dest="min_amount", type=float)
    parser.add_argument("--max-amount", dest="max_amount", type=float)
    parser.add_argument("--usage-limit", dest="usage_limit", type=int)
    parser.add_argument("--expires")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--per-page", dest="per_page", type=int)
    parser.add_argument("--page", type=int)

    args = parser.parse_args()
    _check()

    action_map = {
        "list-products": lambda: action_list_products(args),
        "get-product": lambda: action_get_product(args),
        "create-product": lambda: action_create_product(args),
        "update-product": lambda: action_update_product(args),
        "delete-product": lambda: action_delete_product(args),
        "list-categories": lambda: action_list_categories(args),
        "list-orders": lambda: action_list_orders(args),
        "get-order": lambda: action_get_order(args),
        "update-order": lambda: action_update_order(args),
        "list-customers": lambda: action_list_customers(args),
        "list-coupons": lambda: action_list_coupons(args),
        "create-coupon": lambda: action_create_coupon(args),
    }

    try:
        result = action_map[args.action]()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except requests.HTTPError as e:
        detail = ""
        try:
            detail = e.response.json()
        except Exception:
            detail = e.response.text
        print(json.dumps({"error": True, "status": e.response.status_code,
                          "message": str(e), "detail": detail}, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
