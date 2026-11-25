"""Score vs the next 12 months of return relative to SPY, from the filing date. Prices: Yahoo adjusted close."""
import json, urllib.request, bisect, random, statistics, time, datetime as dt
S = json.load(open("data/signals.json"))
def px(t):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=15y&interval=1d&events=div,splits"
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["chart"]["result"][0]
    ts = d["timestamp"]; ad = d["indicators"]["adjclose"][0]["adjclose"]
    return [(dt.datetime.utcfromtimestamp(a).strftime("%Y-%m-%d"), b) for a, b in zip(ts, ad) if b]
P = {}
for t in sorted({s["t"] for s in S} | {"SPY"}):
    try: P[t] = px(t)
    except Exception as e: print("no prices", t, e)
    time.sleep(0.3)
def at(t, day):
    a = P[t]; i = bisect.bisect_left([x[0] for x in a], day)
    return a[i] if i < len(a) else None
rows = []
for s in S:
    if s["t"] not in P: continue
    start = (dt.date.fromisoformat(s["filed"]) + dt.timedelta(days=2)).isoformat()
    end = (dt.date.fromisoformat(start) + dt.timedelta(days=365)).isoformat()
    a, b, m0, m1 = at(s["t"], start), at(s["t"], end), at("SPY", start), at("SPY", end)
    if not (a and b and m0 and m1): continue
    if b[0] < end[:7] + "-01" or b[0] > (dt.date.fromisoformat(end) + dt.timedelta(days=7)).isoformat(): continue
    rows.append({"net": s["bull"] - s["bear"], "ex": ((b[1] / a[1]) - (m1[1] / m0[1])) * 100, "t": s["t"], "y": s["filed"][:4]})
print(len(rows), "observations")
nets = sorted(r["net"] for r in rows)
lo, hi = nets[len(nets) // 3], nets[2 * len(nets) // 3]
G = {"Weakest third": [r for r in rows if r["net"] <= lo], "Middle": [r for r in rows if lo < r["net"] < hi], "Strongest third": [r for r in rows if r["net"] >= hi]}
random.seed(7)
def boot(a, b, n=4000):
    ds = []
    for _ in range(n):
        ds.append(statistics.fmean(random.choices([x["ex"] for x in a], k=len(a))) - statistics.fmean(random.choices([x["ex"] for x in b], k=len(b))))
    ds.sort(); return ds[int(.025 * n)], ds[int(.975 * n)]
top, bot = G["Strongest third"], G["Weakest third"]
diff = statistics.fmean([x["ex"] for x in top]) - statistics.fmean([x["ex"] for x in bot])
ci = boot(top, bot)
def corr():
    x = [r["net"] for r in rows]; y = [r["ex"] for r in rows]; mx, my = statistics.fmean(x), statistics.fmean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (len(x) * statistics.pstdev(x) * statistics.pstdev(y))
c = corr()
out = {"groups": [{"label": k, "n": len(v), "mean": statistics.fmean([x["ex"] for x in v])} for k, v in G.items()],
 "summary": f"No, not in this sample. Using the same rules on every 10-K since about 2014, the strongest third by score returned {diff:+.1f} points a year versus the weakest third, relative to the S&P 500 (95% bootstrap interval {ci[0]:+.1f} to {ci[1]:+.1f}). Correlation of score with next-year excess return: {c:+.2f} over {len(rows)} filings.",
 "notes": ["Return is measured from two days after the 10-K filing date for 12 months, dividends included, against SPY.", "The same 37 companies are used throughout, and they are big survivors, so absolute returns are flattered. Observations overlap in time and move with the market, so the interval is optimistic.", "Treat this as a sanity check on the rules, not as evidence you could trade on."]}
json.dump(out, open("docs/backtest.json", "w"), indent=1)
print(json.dumps(out, indent=1))
