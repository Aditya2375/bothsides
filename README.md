# Both Sides

Pick a US company and see the bull case and the bear case, built by 16 fixed rules from its SEC 10-K numbers. Every point shows its figures and links to the filing. No language model writes any text.

Live: https://aditya2375.github.io/bothsides/

## How it works

1. `train/fetch.py` pulls annual XBRL facts (SEC EDGAR companyfacts) for 42 large US companies.
2. `train/build.py` keeps the last six fiscal years for 37 of them (banks are dropped because the rules do not fit them).
3. `docs/js/rules.js` holds the 16 rules and their thresholds. The page runs them in the browser. A rule stays silent when its inputs are missing from the filing.

## Does it work? No.

`train/signals.js` applies the same rules to every historical 10-K, and `train/backtest.py` compares the score with the next 12 months of return against SPY from two days after filing. Result: the strongest third did 4.6 points a year worse than the weakest third (95% bootstrap interval -14.6 to +4.7, correlation -0.10, 349 filings). That is not distinguishable from zero, and it is the number the page shows. The sample is the same big survivors throughout and observations overlap, so even this is optimistic. The thresholds were set before any returns were looked at and were not tuned afterwards.

## Limits

Not advice. 37 companies, 10-K only, no valuation, no guidance, some tags missing.

## Run it

```
python train/fetch.py && python train/build.py
node train/signals.js > data/signals.json && python train/backtest.py
cd docs && python -m http.server
```

MIT licence. Fonts: Playfair Display and IBM Plex Mono, SIL OFL (in `docs/fonts`). Data: SEC EDGAR.
