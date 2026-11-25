// Apply the exact page rules to every historical fiscal year. Usage: node train/signals.js > data/signals.json
const { RULES } = require("../docs/js/rules.js");
const d = require("../data/facts.json");
const out = [];
for (const [t, c] of Object.entries(d)) {
  if (["JPM", "BAC", "WFC"].includes(t)) continue;
  const ys = Object.keys(c.years).sort().filter((y) => c.years[y].revenue && c.years[y].net_income);
  const rows = ys.map((y) => { const r = { end: y, filed: c.years[y].revenue.filed }; for (const [k, b] of Object.entries(c.years[y])) r[k] = b.v; return r; });
  for (let i = 5; i < rows.length; i++) {
    const w = rows.slice(i - 5, i + 1); let bull = 0, bear = 0;
    for (const r of RULES) { let o = null; try { o = r.f(w); } catch (e) {} if (o) { if (o.side === "bull") bull++; else bear++; } }
    out.push({ t, end: rows[i].end, filed: rows[i].filed, bull, bear });
  }
}
console.log(JSON.stringify(out));
