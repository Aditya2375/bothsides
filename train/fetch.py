"""Pull annual XBRL facts from SEC EDGAR for a fixed list of large US companies."""
import json, time, urllib.request
UA = {"User-Agent": "Aditya Kulkarni aditya.sidekick@gmail.com"}
TICKERS = "AAPL MSFT GOOGL AMZN META NVDA TSLA JPM XOM JNJ WMT PG KO PEP COST HD DIS NFLX INTC AMD CSCO ORCL ADBE CRM NKE MCD BA CAT GE F GM T VZ PFE MRK ABBV UNH CVX BAC WFC IBM TXN QCOM".split()
TAGS = {
 "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
 "gross_profit": ["GrossProfit"],
 "op_income": ["OperatingIncomeLoss"],
 "net_income": ["NetIncomeLoss"],
 "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
 "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
 "assets": ["Assets"],
 "liabilities": ["Liabilities"],
 "equity": ["StockholdersEquity"],
 "cur_assets": ["AssetsCurrent"],
 "cur_liab": ["LiabilitiesCurrent"],
 "cash": ["CashAndCashEquivalentsAtCarryingValue"],
 "debt": ["LongTermDebt", "LongTermDebtNoncurrent"],
 "shares": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
}
def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
tk = {v["ticker"]: v for v in get("https://www.sec.gov/files/company_tickers.json").values()}
out = {}
for t in TICKERS:
    if t not in tk: continue
    cik = str(tk[t]["cik_str"]).zfill(10)
    try: f = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
    except Exception as e: print("skip", t, e); continue
    g = f["facts"].get("us-gaap", {})
    rec = {"name": tk[t]["title"], "cik": cik, "years": {}}
    for key, tags in TAGS.items():
        best = {}
        for tag in tags:
            for u in ("USD", "shares"):
                for r in g.get(tag, {}).get("units", {}).get(u, []):
                    if r.get("form") != "10-K" or r.get("fp") != "FY" or "start" not in r: continue
                    days = (time.mktime(time.strptime(r["end"], "%Y-%m-%d")) - time.mktime(time.strptime(r["start"], "%Y-%m-%d"))) / 86400
                    if not 340 <= days <= 380: continue
                    y = r["end"]
                    if y not in best or r["filed"] > best[y]["filed"]: best[y] = {"v": r["val"], "acc": r["accn"], "filed": r["filed"], "tag": tag}
        if key in ("assets", "liabilities", "equity", "cur_assets", "cur_liab", "cash", "debt"):
            best = {}
            for tag in tags:
                for r in g.get(tag, {}).get("units", {}).get("USD", []):
                    if r.get("form") != "10-K" or r.get("fp") != "FY": continue
                    y = r["end"]
                    if y not in best or r["filed"] > best[y]["filed"]: best[y] = {"v": r["val"], "acc": r["accn"], "filed": r["filed"], "tag": tag}
        for y, b in best.items():
            rec["years"].setdefault(y, {})[key] = b
    out[t] = rec
    print(t, len(rec["years"]), flush=True)
    time.sleep(0.25)
json.dump(out, open("data/facts.json", "w"), separators=(",", ":"))
