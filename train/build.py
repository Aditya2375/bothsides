"""Trim data/facts.json to what the page needs: last 6 fiscal years per company."""
import json
d = json.load(open("data/facts.json"))
out = {}
for t, r in d.items():
    ys = sorted(y for y, v in r["years"].items() if "revenue" in v and "net_income" in v)
    # one record per fiscal year end; skip stale duplicates
    ys = ys[-6:]
    if len(ys) < 4 or ys[-1] < "2025-06-01" or t in ("JPM", "BAC", "WFC"): continue
    rows = []
    for y in ys:
        v = r["years"][y]
        row = {"end": y, "acc": v["revenue"]["acc"], "filed": v["revenue"]["filed"]}
        for k, b in v.items(): row[k] = b["v"]
        rows.append(row)
    out[t] = {"name": r["name"].title(), "cik": r["cik"], "fy": rows}
json.dump(out, open("docs/facts.json", "w"), separators=(",", ":"))
print(len(out), "companies")
