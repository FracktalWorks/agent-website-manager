#!/usr/bin/env python3
"""Quick GA4 page report for fracktal.in"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.tmp', 'scripts'))
from fetch_analytics import run_report

# Page-level report
data = run_report(
    "326785752",
    "2026-05-31",
    "2026-06-30",
    ["screenPageViews", "activeUsers", "averageSessionDuration"],
    ["pagePath"]
)

if not data:
    print("No data")
    sys.exit(1)

rows = sorted(data.get("rows", []), key=lambda r: int(r["metricValues"][0]["value"]), reverse=True)

print(f"{'Page':55s} | {'Views':>6s} | {'Users':>6s} | {'AvgTime':>8s}")
print("-" * 85)
for r in rows[:25]:
    path = r["dimensionValues"][0]["value"]
    views = r["metricValues"][0]["value"]
    users = r["metricValues"][1]["value"]
    atime = float(r["metricValues"][2]["value"])
    print(f"{path[:55]:55s} | {views:>6s} | {users:>6s} | {atime:>7.0f}s")
