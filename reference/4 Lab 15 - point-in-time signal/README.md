# Lab 15 portfolio app

## Thursday rates checkout

The requested four-series page is `asof_app.py`. Run `~/.local/bin/streamlit run asof_app.py --browser.gatherUsageStats false` from this folder. It starts with BAA, FEDFUNDS, DGS10, and MORTGAGE30US, downloads one FRED current CSV and one ALFRED vintage CSV per series, plots the current values, and compares the two date-level views in a linked table. An unknown extra ID produces a per-series error while the four selected charts continue to render. FRED's current download is cached for one hour; historical vintage downloads are cached by series and date.

Run `~/.local/bin/streamlit run rates_app.py --browser.gatherUsageStats false` from this folder. The new `rates_app.py` shows the observation values knowable at the **close of a selected date**. Its default live view downloads real ALFRED graph CSVs for BAA, FEDFUNDS, DGS10, MORTGAGE30US, or a chosen FRED ID; no key or account is needed. Select a second date or today's FRED view to see added and revised values. The sidebar links to the exact source CSVs. The public graph CSV supplies a requested vintage, rather than each observation's full real-time interval. The export labels its `as_of_date` accordingly.

Use **Classroom examples → Documented GNPCA known answer → 2013-08-14** to get 1929 = 1065.9 and 1930 = 975.5. The prior day returns no rows. Use **Synthetic revision exercise** with 2020-03-01 and 2020-05-01 to see a revised January value and an April observation appear only in the later view. You can also upload a five-column ALFRED CSV; its `realtime_start` and `realtime_end` fields are checked by `select_as_of`. Downloads include the chosen as-of date.

The intended prework series ID is not recorded in this folder. `DGS10` is the app's **example**, not a claim about the student's choice. See `rates_series_decision.md` for the provisional Project 2 call. An actual use decision needs the chosen ID, its units and source, a saved as-of export, and a stated portfolio role. The app supports date-level availability only; it cannot prove intraday access or turn a rate into an ETF total return.

This folder is a self-contained copy of today's work. The earlier `in class labs` files remain in place.

- `portfolio.py` — Tuesday's unchanged printed baselines, five-point portfolio search, and monthly-price estimator.
- `app.py` — Streamlit controls for Meridian and an uploaded four-fund price panel.
- `prices.csv` — 61 monthly adjusted closes, September 2021–September 2026, for SGOV, BND, VT, and TIP.
- `Project 2 mandate.md` — proposed young-family mandate, price sources and dates, app results, partner challenge, call, estimation risk, and Mermaid chart.
- `requirements.txt` — Python packages used by the app.
- `build_prices.py` and `source/` — rebuild the CSV from saved download responses.
- `point_in_time.py` — select only ALFRED observation versions valid on a decision date.
- `alfred_known_answer.csv` — two rows reproduced from the St. Louis Fed API documentation.
- `training_vintages.csv` — explicitly synthetic revisions for the trade-date comparison.
- `training_table.csv` and `training_gate.py` — the instructor's 12-row fictional bond table and four ordered provenance rules.
- `test_training_gate.py` — fixed-answer test for row dispositions, returns, and economic flags.
- `test_point_in_time.py` — known-answer, revision-leak, and overlap checks.

From this folder, run `python portfolio.py` to check Tuesday's printed values. Start the app with `streamlit run app.py --browser.gatherUsageStats false`. Upload this folder's `prices.csv`; for the proposed 30-year-old couple with young children, set the gross objective to **8.2%** (the 8.0% net goal plus an illustrative 0.2% cost allowance), set the reserve minimum to **10%**, and count **SGOV** as reserve-eligible. The app still opens with Meridian's 6.5% and 3% training defaults.

## Point-in-time checkout

Run `python3 point_in_time.py alfred_known_answer.csv 2013-08-14` and
`python3 -m unittest -v test_point_in_time.py`.

The [St. Louis Fed observation API example](https://fred.stlouisfed.org/docs/api/fred/series_observations.html) publishes GNPCA values **1065.9 for 1929** and **975.5 for 1930**, each with `realtime_start` and `realtime_end` of **2013-08-14**. The filter returns those two values on that date and no rows on **2013-08-13**. This is a documented, small known-answer check of date-level availability, not a claim about the first publication of those historic figures. A synthetic revision test proves that a later vintage and a future observation do not enter an earlier decision snapshot. An overlapping vintage is rejected because it would make the as-of answer ambiguous.

In `training_vintages.csv`, the **2020-03-01** decision snapshot is January **10** and February **20**. The **2020-05-01** snapshot is January **11**, February **20**, and April **40**. Thus January's displayed value rose **1 (10%)** after the decision; April is one wholly later observation. These numbers and dates are synthetic classroom data, not an ALFRED series.

### Instructor training table, decision date March 31, 2026

Run `python3 training_gate.py` and `python3 -m unittest -v test_training_gate.py`. The gate preserves row numbers and applies missing ticker, exact duplicate, future publication, and latest available revision in that order. Rows **1, 4, 5, 6, 9, 12** are admitted; **11** is quarantined; **2, 3, 7, 8, 10** are removed. Returns from January to the latest knowable February are AAA **+1.98%** (101 to 103), BBB **−1.02%** (98 to 97), and CCC **+0.91%** (110 to 111). After the trade date, AAA and BBB March prices arrived on April 10 (rows 3 and 8), and CCC February was revised from 111 to 112 on April 5 (row 10, +1 or +0.90%). They cannot enter the March 31 signal.

The separate economic validation reports four admitted prices above 100 (AAA January/February and CCC January/February), each implying a negative one-year zero-coupon yield. The required credit-price order AAA > BBB > CCC fails in both months; CCC is more expensive than AAA and BBB. Provenance admission does not certify economic sense.

Input CSV columns are `series_id,date,realtime_start,realtime_end,value`, matching the ALFRED API observation fields with `series_id` added for multi-series files. Each real-time interval is **inclusive at both ends**, as the [Fed's real-time-period documentation](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html) specifies. The date is treated as the close of day; the file has no release time, so it cannot establish availability earlier within that day. To audit another decision, export ALFRED observations including both real-time fields and record the source URL and export date with the file.

The Meridian **0/20/25/55, 6.51% return, 9.44% volatility** result remains the separate portfolio-engine known answer in `Project 2 mandate.md`. Those course estimates have no documented release dates, so they cannot serve as evidence of what was publicly knowable on a historical decision date. The Yahoo price panel likewise was downloaded after the October 16 Costco valuation date; its saved responses do not prove that the adjusted closes were then available in their present form.
