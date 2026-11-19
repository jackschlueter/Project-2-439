# DGS10 point-in-time signal — data card

**Decision use:** Admit DGS10 only as dated interest-rate context to challenge a Treasury or bond-return assumption. Its only model use is one labeled stress case: the Challenge tab sets the Meridian 10-year sleeve's return estimate to the 2026-10-31 vintage yield (4.98%) to test the 4.30% training assumption. It never replaces an asset's base-case total return. Quarantine any intraday trading use until release-time evidence is documented.

| Field | Record |
|---|---|
| Series | DGS10, 10-year constant-maturity U.S. Treasury market yield, quoted on an investment basis. |
| Primary source | Federal Reserve Board H.15 Selected Interest Rates, distributed through [FRED DGS10](https://fred.stlouisfed.org/series/DGS10) and [ALFRED](https://fred.stlouisfed.org/docs/api/fred/alfred.html). |
| Units and frequency | Percent per annum, daily, not seasonally adjusted. It is a yield level, not a bond or ETF return. |
| Release timing | [H.15](https://www.federalreserve.gov/releases/h15/) normally posts Monday–Friday at 4:15 p.m., excluding holidays and closures. An ALFRED date-level vintage does not prove access before a particular intraday trade. |
| Historical snapshot | [2026-10-31 ALFRED CSV](https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=DGS10&vintage_date=2026-10-31&cosd=2026-10-01&coed=2026-11-03), saved locally as `dgs10_2026-10-31.csv`. Its latest observation is **2026-10-29, 4.98%**. |
| Later comparison | [2026-11-03 ALFRED CSV](https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=DGS10&vintage_date=2026-11-03&cosd=2026-10-01&coed=2026-11-03), saved locally as `dgs10_2026-11-03.csv`. It adds **2026-10-30, 4.94%**, and **2026-11-02, 4.91%**. |
| Download and scope | Both exact vintage CSVs were downloaded **2026-11-17** with observations limited to 2026-10-01 through 2026-11-03. The app accepts only the exact vintage column and excludes observations after the selected decision date. |
| Revisions / missing | Across common measured dates in these saved panels, **zero values differ**. ALFRED may revise data later; this is a two-vintage observation, not a permanent claim. Blank and `.` missing values are skipped. |
| Reproduction | The app reads the bundled CSV for the selected vintage. For an as-of signal it takes the latest nonmissing observation within that vintage, not the latest value in today's FRED chart. |
| File fingerprints | 2026-10-31 SHA-256 `eed9d9104b3233c27518214c714bb37f8601c49b3e53d30ba87c617f5733325f`; 2026-11-03 SHA-256 `c0d6dbc144980afc7b3eb25c9a583e9f2201688dd01aa184ed784dbbaea4c5a6`. |

The earlier local `DGS10_data_card.md` said a November 3 view ended on October 30. The November 3 *end-of-day* vintage downloaded November 17 includes November 2. The records establish different views; they do not establish the reason for that difference or prove a specific intraday publication time.
