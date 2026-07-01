---
name: woocommerce_management
description: >
  Manage WooCommerce store — products, orders, customers, coupons, reports,
  settings, shipping, taxes, and webhooks via the WooCommerce REST API (v3).
when_to_use: "User asks to manage WooCommerce store, products, orders, customers, coupons, reports, or settings"
authority: write
cost_tier: 2
version: 0.1.0
---

# WooCommerce Management Skill

Complete WooCommerce store management via the REST API (v3, integrated into
WordPress REST API). Control products, orders, customers, coupons, reports,
settings, shipping zones, payment gateways, and webhooks.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wc_rest_api.py` | WooCommerce REST API client — products, orders, customers, coupons |
| `scripts/wc_reports.py` | Sales reports, product reports, analytics |
| `scripts/wc_settings.py` | Store settings, tax, shipping, payments, emails, accounts |

## Usage

```bash
# Products
python .github/skills/woocommerce_management/scripts/wc_rest_api.py --action list-products
python .github/skills/woocommerce_management/scripts/wc_rest_api.py --action create-product \
  --name "T-Shirt" --type simple --price 29.99 --description "Cotton tee"
python .github/skills/woocommerce_management/scripts/wc_rest_api.py --action update-product \
  --id 123 --price 24.99 --stock 50

# Orders
python .github/skills/woocommerce_management/scripts/wc_rest_api.py --action list-orders --status processing
python .github/skills/woocommerce_management/scripts/wc_rest_api.py --action get-order --id 456
python .github/skills/woocommerce_management/scripts/wc_rest_api.py --action update-order \
  --id 456 --status completed

# Customers
python .github/skills/woocommerce_management/scripts/wc_rest_api.py --action list-customers
python .github/skills/woocommerce_management/scripts/wc_rest_api.py --action get-customer --id 78

# Coupons
python .github/skills/woocommerce_management/scripts/wc_rest_api.py --action list-coupons
python .github/skills/woocommerce_management/scripts/wc_rest_api.py --action create-coupon \
  --code "SUMMER25" --type percent --amount 25

# Reports
python .github/skills/woocommerce_management/scripts/wc_reports.py --action sales --period month
python .github/skills/woocommerce_management/scripts/wc_reports.py --action top-products --limit 10

# Settings
python .github/skills/woocommerce_management/scripts/wc_settings.py --action get --group general
python .github/skills/woocommerce_management/scripts/wc_settings.py --action update \
  --group products --option weight_unit --value kg
```

## Required Environment Variables

- `WORDPRESS_SITE_URL` — Your WordPress site URL
- `WOOCOMMERCE_CONSUMER_KEY` — WooCommerce REST API Consumer Key
- `WOOCOMMERCE_CONSUMER_SECRET` — WooCommerce REST API Consumer Secret

## Outputs

Writes results to `outputs/<project-slug>/wc_*.json`.
