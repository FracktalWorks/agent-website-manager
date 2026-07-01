#!/usr/bin/env python3
"""
WooCommerce Reports & Analytics

Sales reports, product performance, category breakdown, coupon usage,
and customer analytics via WooCommerce REST API.

Usage:
    python wc_reports.py --action sales --period month
    python wc_reports.py --action top-products --limit 10
    python wc_reports.py --action overview
"""

import os, sys, json, argparse, base64
from pathlib import Path
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
WC_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "")
WC_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET", "")
AUTH = base64.b64encode(f"{WC_KEY}:{WC_SECRET}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
API = f"{WP_URL}/wp-json/wc/v3"


def _check():
    missing = [v for v, k in [("WP_URL", WP_URL), ("WC_KEY", WC_KEY),
                ("WC_SECRET", WC_SECRET)] if not k]
    if missing:
        print(json.dumps({"error": True, "message": f"Missing: {', '.join(missing)}"}))
        sys.exit(1)


def _get(ep, params=None):
    r = requests.get(f"{API}/{ep.lstrip('/')}", headers=HEADERS,
                     params=params, timeout=30)
    r.raise_for_status()
    return r.json(), dict(r.headers)


def _date_range(period):
    """Get date range for a given period string."""
    now = datetime.now()
    periods = {
        "today": (now.replace(hour=0, minute=0, second=0).isoformat(), now.isoformat()),
        "yesterday": ((now - timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat(),
                      (now - timedelta(days=1)).replace(hour=23, minute=59, second=59).isoformat()),
        "week": ((now - timedelta(days=7)).isoformat(), now.isoformat()),
        "month": ((now - timedelta(days=30)).isoformat(), now.isoformat()),
        "quarter": ((now - timedelta(days=90)).isoformat(), now.isoformat()),
        "year": ((now - timedelta(days=365)).isoformat(), now.isoformat()),
    }
    return periods.get(period, periods["month"])


def action_sales(args):
    """Sales overview for a period."""
    after, before = _date_range(args.period or "month")

    # Get all completed orders in the period
    orders_data, headers = _get("orders", {
        "status": "completed", "after": after, "before": before,
        "per_page": 100, "page": 1,
    })

    total_revenue = sum(float(o.get("total", 0)) for o in orders_data)
    order_count = len(orders_data)

    # Get total pages for accurate count
    total_pages = int(headers.get("X-WP-TotalPages", 1))
    total_orders = int(headers.get("X-WP-Total", order_count))

    # Average order value
    avg_order = round(total_revenue / order_count, 2) if order_count > 0 else 0

    return {
        "period": args.period or "month",
        "date_range": {"after": after, "before": before},
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "average_order_value": avg_order,
        "currency": orders_data[0].get("currency", "") if orders_data else "",
    }


def action_top_products(args):
    """Top selling products by order count."""
    after, before = _date_range(args.period or "month")
    limit = args.limit or 10

    # Fetch products
    products, _ = _get("products", {"per_page": limit, "orderby": "popularity",
                                     "order": "desc"})
    result = []
    for p in products:
        result.append({
            "id": p["id"], "name": p["name"], "price": p["price"],
            "stock": p.get("stock_quantity", 0),
            "status": p["status"], "total_sales": p.get("total_sales", 0),
        })
    return {"top_products": result, "period": args.period or "month", "limit": limit}


def action_coupon_usage(args):
    """Coupon usage report."""
    coupons, _ = _get("coupons", {"per_page": 50})
    used = [{"code": c["code"], "type": c.get("discount_type", ""),
             "amount": c["amount"], "used": c.get("usage_count", 0)}
            for c in coupons if c.get("usage_count", 0) > 0]
    used.sort(key=lambda x: x["used"], reverse=True)
    return {"coupons_used": used, "total_coupon_types": len(set(c["type"] for c in used))}


def action_overview(args):
    """Quick store overview — one command to see everything."""
    # Products count
    products, ph = _get("products", {"per_page": 1})
    total_products = int(ph.get("X-WP-Total", 0))

    # Orders today
    today = datetime.now().strftime("%Y-%m-%d")
    orders, oh = _get("orders", {"after": f"{today}T00:00:00", "per_page": 1})
    orders_today = int(oh.get("X-WP-Total", 0))

    # Customers
    customers, ch = _get("customers", {"per_page": 1})
    total_customers = int(ch.get("X-WP-Total", 0))

    # Coupons
    coupons, coh = _get("coupons", {"per_page": 1})
    total_coupons = int(coh.get("X-WP-Total", 0))

    # Orders in processing
    processing, _ = _get("orders", {"status": "processing", "per_page": 1})

    return {
        "store_url": WP_URL,
        "total_products": total_products,
        "total_customers": total_customers,
        "total_coupons": total_coupons,
        "orders_today": orders_today,
        "orders_processing": len(processing),
        "timestamp": datetime.now().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="WooCommerce Reports")
    parser.add_argument("--action", required=True, choices=[
        "sales", "top-products", "coupon-usage", "overview",
    ])
    parser.add_argument("--period", choices=["today", "yesterday", "week", "month", "quarter", "year"])
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    _check()

    actions = {
        "sales": lambda: action_sales(args),
        "top-products": lambda: action_top_products(args),
        "coupon-usage": lambda: action_coupon_usage(args),
        "overview": lambda: action_overview(args),
    }

    try:
        print(json.dumps(actions[args.action](), indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
