# Lab 14 — Reading, fund universe, data, and Streamlit

**Timing:** The Lab 13 portfolio is Meridian's. The later assignment asks for the student's own mandate. The three-fund universe here was drafted from the Meridian case; replace it if the later assignment uses a different personal mandate.

## Reading questions

Read [OpenStax *Principles of Finance* §15.2](https://openstax.org/books/principles-finance/pages/15-2-risk-and-return-to-multiple-assets), from “Diversification” through “Portfolio Size and Risk.” Diversification spreads exposure across assets whose returns do not move exactly together. A correlation below +1 makes the portfolio less volatile than the same weighted assets moving perfectly together; it does not guarantee volatility below every component. The benchmark calculation and partner explanation are in [Lab 13 - Meridian Portfolios.md](Lab%2013%20-%20Meridian%20Portfolios.md).

Read [Streamlit's installation page](https://docs.streamlit.io/get-started/installation) and [Basic concepts through Data flow](https://docs.streamlit.io/get-started/fundamentals/main-concepts). Streamlit 1.66.0 is installed. The `streamlit hello` demo started and returned HTTP 200 on October 20, 2026 at `http://127.0.0.1:8502`. By default, changing a control makes Streamlit rerun the Python script from top to bottom with the control's current value.

## Fund universe and mandate reference

Meridian's return objective is **CPI + 4.0 percentage points annually, net of costs over rolling five-year periods**. Using the course's estimated CPI of 2.5% gives a **6.5% training target**. One hard constraint is **at least 3%** in cash or eligible directly held government securities for the four quarterly payouts. The 60% global equity / 40% U.S. IG bond allocation is a benchmark, not a required holding mix.

| Ticker | Fund | Universe role | Fund description |
|---|---|---|---|
| SGOV | iShares 0–3 Month U.S. Treasury Bond ETF | Cash-like / short Treasury fund | [iShares](https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf-sgov) |
| BND | Vanguard Total Bond Market ETF | U.S. investment-grade bonds | [Vanguard](https://advisors.vanguard.com/investments/products/bnd/vanguard-total-bond-market-etf) |
| VT | Vanguard Total World Stock ETF | Global equity | [Vanguard](https://advisors.vanguard.com/investments/products/vt/vanguard-total-world-stock-etf) |

**Reserve distinction:** SGOV is a fund holding short Treasuries. The Meridian case explicitly counts Treasury bills and the 10-year note, not SGOV fund shares, as reserve-eligible. Do not count SGOV toward the hard 3% reserve until that eligibility is clarified. The reserve can be modeled separately from the three-fund price panel.

## `prices.csv` sources and method

Downloaded **October 20, 2026** from the Yahoo Finance chart endpoint. Each ticker uses the response's `adjclose` field. `Month` is a monthly bar label and the value is that month's final adjusted close, rounded to six decimal places. The panel covers **September 2021–September 2026**, 61 complete months and 60 monthly return intervals. Incomplete October 2026 was omitted. Yahoo may revise adjusted prices after distributions or corporate actions; raw responses are saved in `source/`, and `build_prices.py` rebuilds the CSV.

| Ticker | Adjusted-close source | Saved response |
|---|---|---|
| SGOV | [Yahoo chart](https://query2.finance.yahoo.com/v8/finance/chart/SGOV?period1=1630454400&period2=1790812800&interval=1mo&includeAdjustedClose=true) | `source/sgov_yahoo.json` |
| BND | [Yahoo chart](https://query2.finance.yahoo.com/v8/finance/chart/BND?period1=1630454400&period2=1790812800&interval=1mo&includeAdjustedClose=true) | `source/bnd_yahoo.json` |
| VT | [Yahoo chart](https://query2.finance.yahoo.com/v8/finance/chart/VT?period1=1630454400&period2=1790812800&interval=1mo&includeAdjustedClose=true) | `source/vt_yahoo.json` |

For monthly simple returns, use `current adjusted close / previous adjusted close - 1`. These historical prices are distinct from the course-authored expected return, volatility, and correlation inputs used in Lab 13.
