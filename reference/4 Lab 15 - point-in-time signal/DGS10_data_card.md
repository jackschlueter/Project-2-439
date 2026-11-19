# DGS10 data card — working series for Lab 16

**Series ID:** DGS10. The prework series ID was not recorded in the available course files; DGS10 is the working choice for this checkout, pending confirmation.

**Source and link:** [Board of Governors of the Federal Reserve System, H.15 Selected Interest Rates](https://www.federalreserve.gov/releases/h15/), distributed through the [FRED DGS10 page](https://fred.stlouisfed.org/series/DGS10). The historical snapshot is from [ALFRED's 2026-10-31 CSV](https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=DGS10&vintage_date=2026-10-31); the comparison is the [current FRED CSV](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10).

**What it measures:** The daily market yield on U.S. Treasury securities at a 10-year constant maturity, quoted on an investment basis. The Treasury interpolates the constant-maturity yield from its daily nominal yield curve. This is a yield level, not the return from buying a particular Treasury bond or ETF.

**Units and frequency:** Percent per annum, daily, not seasonally adjusted.

**Publication lag:** The H.15 release is posted Monday through Friday at **4:15 p.m.**, except holidays or closures. In this check, the 2026-10-31 ALFRED vintage ended at **2026-10-29, 4.98%**. Today's view includes **2026-10-30, 4.94%**, so the October 30 value was not in the October 31 download. That is roughly one business day of observed lag here. Date-level ALFRED data cannot establish access before a specific intraday trade time.

**Revisions:** With the app's 2020-01-01 start date, **zero** values on common measured dates changed between the 2026-10-31 vintage and today's download. This daily market rate showed almost no lag and no revisions in this comparison. It is an observed result, not a guarantee that DGS10 never changes. The FRED page says data are subject to revision.

**Today check:** Setting “As known on” to **2026-11-03** gave the same latest measured date and value as current FRED: **2026-10-30, 4.94%**, with **zero** newer values and **zero** revisions.

**Three values read against the FRED page:**

| Measured date | FRED page | Current CSV | Match |
|---|---:|---:|---|
| 2026-10-28 | 5.05% | 5.05% | Yes |
| 2026-10-29 | 4.98% | 4.98% | Yes |
| 2026-10-30 | 4.94% | 4.94% | Yes |

**Download date:** 2026-11-03. These current values and revision counts can change after a new release.

**Partner attack status:** No partner's chosen field or question has been provided yet. The two sentences below are a prepared answer to a challenge about **publication timing** and should be replaced or confirmed after the exchange.

**Prepared two-sentence answer:** The 2026-10-31 ALFRED view ends on October 29, while today's FRED view adds October 30, so an October 31 trade could not use the October 30 value from this source. The [H.15 release page](https://www.federalreserve.gov/releases/h15/) says it posts on business days at 4:15 p.m., and the app's date-level snapshot cannot prove what was available before a particular intraday trade.

**Project 2 call — admit for dated rate context:** Use the last value in an ALFRED vintage available by each trade date to describe the rate setting or challenge a bond assumption; DGS10 is not an ETF total return and cannot replace SGOV, BND, or TIP returns in the optimizer. Change this call to **quarantine** for any numeric trading signal if its trade time is before the release or the vintage cannot be documented; **reject** it as a direct asset-return input.

## Explain the code to a partner

Open [`asof_values` in `asof_app.py`](asof_app.py):

1. `@st.cache_data(show_spinner=False)` caches the result for each `(series_id, known_on)` pair, so rerunning the page does not download that same vintage again.
2. `def asof_values(series_id, known_on):` takes the FRED ID and the decision date as text; the date is part of the query and cache key.
3. The docstring says this function makes one public ALFRED CSV request for that series and date.
4. `url = ... urlencode(...)` builds an ALFRED graph URL with `id` and `vintage_date`. The **vintage_date** field asks for what the source showed on that date, preventing today's later values from entering the historical view.
5. `column = ...` builds the expected CSV heading, such as `DGS10_20261031`; this check catches a response for the wrong vintage or series.
6. `return parse_csv(download(url), series_id, column)` downloads once, then parses the exact expected column. `parse_csv` drops `.` missing values and rejects duplicate dates or nonfinite numbers.
7. In the page loop, `past = {day: value ... if day <= known_on}` rejects an observation whose measured date is later than the decision date. The `start` control later limits the chart and counts; it is **not** the publication gate.

**Question to answer from the code:** “Does caching today's FRED CSV turn it into an historical vintage?” No: `today_values` has a separate URL and cache, while `asof_values` sends `vintage_date=known_on` to ALFRED and checks its vintage-specific column.

**Next AI question if needed:** Can ALFRED's date-level graph CSV prove availability before an intraday trade? No; a timestamped release record and trade time would be needed for that stricter test.

## Learn and reflect

1. **What is it?** DGS10 is a 10-year constant-maturity Treasury yield in percent per annum, not a price or realized return.
2. **How does it work?** The ALFRED `vintage_date`, the expected vintage column, and the `day <= known_on` filter control the historical information set. The current FRED chart is a separate comparison.
3. **Why is “cleaned the data” insufficient?** Cleaning can remove missing or malformed entries, but a data card also records the source, units, measured period, release timing, vintage, revisions, download date, and permitted use. A perfectly clean current CSV can still leak future information into a backtest.

The observed lag is about one business day in this check: October 30 was absent on October 31 and present today. A backtest using today's DGS10 values at an October 31 decision would overstate what was then knowable by including that extra observation; it could overstate strategy performance, but this checkout does not calculate the size or direction of any performance effect.
