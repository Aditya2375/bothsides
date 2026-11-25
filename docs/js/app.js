"use strict";
const $ = (id) => document.getElementById(id);
const el = (tag, cls, txt) => { const n = document.createElement(tag); if (cls) n.className = cls; if (txt !== undefined) n.textContent = txt; return n; };
let DATA = {};
function evaluate(co) {
  const y = co.fy, bull = [], bear = [], quiet = [];
  for (const r of RULES) { let o = null; try { o = r.f(y); } catch (e) { o = null; } if (!o) { quiet.push(r.name); continue; } const row = { text: o.text, nums: o.nums, rule: r.name }; (o.side === "bull" ? bull : bear).push(row); }
  return { bull, bear, quiet };
}
function edgar(co, fy) { return "https://www.sec.gov/Archives/edgar/data/" + parseInt(co.cik, 10) + "/" + fy.acc.replace(/-/g, "") + "/"; }
function render(t) {
  const co = DATA[t], last = co.fy[co.fy.length - 1], ev = evaluate(co);
  $("coName").textContent = co.name + " (" + t + ")";
  $("coMeta").textContent = "Latest 10-K: fiscal year ended " + last.end + ", filed " + last.filed;
  $("nBull").textContent = ev.bull.length; $("nBear").textContent = ev.bear.length;
  const sc = $("scale"); sc.textContent = "";
  const total = ev.bull.length + ev.bear.length || 1;
  const b1 = el("span", "sb"), b2 = el("span", "sr"); sc.append(b1, b2);
  b1.setAttribute("data-w", Math.round((ev.bull.length / total) * 100)); b2.setAttribute("data-w", Math.round((ev.bear.length / total) * 100));
  b1.className = "sb w" + Math.round((ev.bull.length / total) * 20) * 5; b2.className = "sr w" + Math.round((ev.bear.length / total) * 20) * 5;
  for (const [id, list] of [["bull", ev.bull], ["bear", ev.bear]]) {
    const ol = $(id); ol.textContent = "";
    if (!list.length) ol.append(el("li", "none", "Nothing in the filing triggers a rule on this side."));
    for (const p of list) { const li = el("li"); li.append(el("p", "pt", p.text)); if (p.nums) li.append(el("p", "nums", p.nums)); li.append(el("p", "src", p.rule + " · ")); const a = el("a", "", "10-K, FY " + last.end.slice(0, 4)); a.href = edgar(co, last); a.rel = "noopener noreferrer"; li.lastChild.append(a); ol.append(li); }
  }
  $("nc").textContent = ev.quiet.length ? "Rules with no result for this company (no trigger or missing data): " + ev.quiet.join(", ") + "." : "";
  const cols = [["revenue", "Revenue"], ["gross_profit", "Gross profit"], ["op_income", "Operating income"], ["net_income", "Net income"], ["cfo", "Operating cash flow"], ["capex", "Capex"], ["assets", "Assets"], ["liabilities", "Liabilities"], ["cash", "Cash"], ["debt", "Long-term debt"]];
  const tb = $("tbl"); tb.textContent = "";
  const hr = el("tr"); hr.append(el("th", "", "Fiscal year end")); for (const [, n] of cols) hr.append(el("th", "", n)); tb.append(el("thead")); tb.lastChild.append(hr);
  const body = el("tbody");
  for (const fy of co.fy.slice().reverse()) { const tr = el("tr"); const th = el("th", "", fy.end); tr.append(th); for (const [k] of cols) tr.append(el("td", "", typeof fy[k] === "number" ? usd(fy[k]) : "n/a")); body.append(tr); }
  tb.append(body);
}
function drawRules() { const ul = $("rulelist"); for (const r of RULES) { const li = el("li"); li.append(el("strong", "", r.name)); li.append(el("span", "", r.rule)); ul.append(li); } }
function drawBacktest(bt) {
  const box = $("bt"); box.textContent = "";
  if (!bt) { box.append(el("p", "fine", "Backtest file not loaded.")); return; }
  box.append(el("p", "lede2", bt.summary));
  const g = el("div", "bars");
  const max = Math.max(...bt.groups.map((x) => Math.abs(x.mean)), 1);
  for (const x of bt.groups) { const row = el("div", "brow"); row.append(el("span", "bl", x.label + " (n=" + x.n + ")")); const bar = el("span", "bar " + (x.mean >= 0 ? "pos" : "neg") + " w" + Math.min(100, Math.round((Math.abs(x.mean) / max) * 20) * 5)); row.append(bar); row.append(el("span", "bv", (x.mean >= 0 ? "+" : "") + x.mean.toFixed(1) + " pts vs S&P 500")); g.append(row); }
  box.append(g);
  for (const n of bt.notes) box.append(el("p", "fine", n));
}
fetch("facts.json").then((r) => r.json()).then((d) => { DATA = d; const sel = $("co"); for (const t of Object.keys(d).sort()) { const o = el("option", "", t + " · " + d[t].name); o.value = t; sel.append(o); } sel.addEventListener("change", () => render(sel.value)); sel.value = "AAPL" in d ? "AAPL" : Object.keys(d)[0]; render(sel.value); }).catch(() => { $("coName").textContent = "Could not load data."; });
drawRules();
fetch("backtest.json").then((r) => r.json()).then(drawBacktest).catch(() => drawBacktest(null));
