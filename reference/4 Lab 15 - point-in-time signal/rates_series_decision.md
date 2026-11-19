# Thursday rates checkout and Project 2 call

## Known answer and code explanation

### Live Lab 16 check, run 2026-11-03

With `asof_app.py` set to **2026-10-05**, the four ALFRED snapshots matched the stated known answer: BAA **2026-09-01, 6.47**; FEDFUNDS **2026-09-01, 3.75**; DGS10 **2026-10-02, 5.28**; MORTGAGE30US **2026-10-01, 7.28**. The live app returned four charts and no errors.

For **PAYEMS** at **2025-01-15**, the last known observation was **2024-12-01, 159,536** (thousands). The current FRED CSV shows **158,316** for that same December observation, **1,220 lower**. With the app's default 2020-01-01 start date, **59** common-date values were revised and **21** newer observations appeared. The revision count is therefore nonzero, confirming that the comparison did not read today's data twice. Values and counts can change if the current FRED series is revised again after this check.

The documented ALFRED sample gives `GNPCA` 1929 = **1065.9** and 1930 = **975.5** on **2013-08-14**; the sample has no version valid on 2013-08-13. The separate synthetic example changes January 2020 from **10** (known March 1) to **11** (known March 2) and adds April **40** only by May 1. Run `python3 -m unittest -v test_point_in_time.py` to repeat the checks.

`rates_app.py` gets rows from public FRED/ALFRED graph CSV downloads, an uploaded CSV, or the classroom examples. The live ALFRED URL requests `vintage_date=trade date` and `coed=trade date`; the returned column names the requested vintage. For uploads and examples, `point_in_time.select_as_of` keeps a row only when its observation date is no later than the decision date and its inclusive real-time interval contains that date. It rejects overlapping versions. The chart, table, comparison, and download use the selected rows. The public graph download needs no API key or account.

## Common question and partner exchange

**D — the question:** Was each number in your series knowable on the day you would have traded on it — and may Project 2 use it?

**Five-minute, no-screen explanation:** Name one rate you think moves your universe and why; have your partner write the reason down, then swap. For the proposed SGOV/BND/VT/TIP universe, DGS10 is a plausible rate to discuss because changing Treasury yields can change bond prices, especially for BND and TIP. This is a hypothesis for partner review, not a recorded partner response.

| Series | FRED page | Frequency |
|---|---|---|
| BAA | https://fred.stlouisfed.org/series/BAA | Monthly |
| FEDFUNDS | https://fred.stlouisfed.org/series/FEDFUNDS | Monthly |
| DGS10 | https://fred.stlouisfed.org/series/DGS10 | Daily |
| MORTGAGE30US | https://fred.stlouisfed.org/series/MORTGAGE30US | Weekly |

**Real rate timing check:** In the public BAA ALFRED CSV, the **2026-03-31** vintage ends with February 2026 = **5.81**; the **2026-04-30** vintage adds March 2026 = **6.04**. A March 31 trade could not use that March observation from this source. The exact source CSV links are generated in the app.

## Series and Project 2 decision

**The prework series ID was not found in the available course files.** The app starts with `DGS10` as an example. FRED identifies DGS10 as the daily, percent-quoted 10-year Treasury constant-maturity yield from the Federal Reserve Board's H.15 release. Its level is a yield, not the realized total return of SGOV, BND, VT, or TIP.

**Call for DGS10: admit for dated rate context only.** It may help explain the interest-rate setting or challenge a bond-return assumption once a decision-date ALFRED vintage is saved and cited. It may **not** replace any ETF adjusted-close return, enter the four-fund optimizer as an asset return, or be described as a forecast. This is a call on the example DGS10 only, pending confirmation that DGS10 was the chosen prework series. The student's actual prework series has no admission call yet if it differs from DGS10.

**Partner attack to invite:** Ask whether the selected observation was published by the trade time, whether a later revision appears in a current FRED chart, and whether the series' units match the intended model input. Record the partner's response before changing the call; no partner response is documented here.

**Checkout:** Show the dated chart and as-of CSV, the known-answer values, one changed vintage, the filter line that blocks future knowledge, and the series admission call above. Then record one thing learned and one remaining question after the partner review.

Sources: [FRED observations API](https://fred.stlouisfed.org/docs/api/fred/series_observations.html), [real-time period rules](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html), [DGS10 series definition](https://fred.stlouisfed.org/series/DGS10).
