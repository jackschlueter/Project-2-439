# Portfolio lab preparation — October 20, 2026

## Mandate and fund universe

Today's portfolio is the Meridian Foundation Reserve, using the existing `Meridian_IPS_Explanation.md` and `Meridian_Foundation_Reserve_Mandate_Check.md` in `../../Recovered non-Costco files/`. The Thursday exercise switches to my own mandate.

**Lab 13 question:** “What does each simple portfolio earn and risk — and does any of them meet the Meridian mandate?” The answer below uses the course-authored training values supplied on October 20, 2026. These values are not market estimates and are separate from the ETF history in `prices.csv`.

**Numeric objective:** Seek a return of **CPI + 4.0 percentage points per year, net of costs, measured over rolling five-year periods**. This is a target, not a forecast or guarantee. The 60% global equity / 40% U.S. investment-grade bond mix is the comparison benchmark.

**One hard constraint to carry into the model:** At least **3% of total assets** ($3 million of the fictional $100 million reserve) must remain in cash or directly held eligible government securities to cover four $0.75 million quarterly payouts. This reserve is outside the three-fund price panel. SGOV is a short Treasury fund and a useful cash-like *candidate*, but the original mandate does not expressly count fund shares as eligible securities. Do not count SGOV toward the 3% floor without clarification.

| Ticker | Fund | Role in universe |
|---|---|---|
| SGOV | iShares 0–3 Month U.S. Treasury Bond ETF | Short Treasury / cash-like exposure |
| BND | Vanguard Total Bond Market ETF | Broad U.S. investment-grade bonds |
| VT | Vanguard Total World Stock ETF | Broad global equity |

These are research candidates, not recommended weights. Fund descriptions: [SGOV](https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf-sgov), [BND](https://advisors.vanguard.com/investments/products/bnd/vanguard-total-bond-market-etf), [VT](https://advisors.vanguard.com/investments/products/vt/vanguard-total-world-stock-etf).

## `prices.csv` provenance

Downloaded **October 20, 2026** from Yahoo Finance's chart endpoint. The `adjclose` field, rather than the unadjusted `close` field, was used for every ticker. The `Month` column labels a monthly bar; its price is that month's final adjusted close. Values are rounded to six decimal places. The panel has 61 complete months, **September 2021 through September 2026**, giving 60 monthly return intervals. October 2026 is omitted because it is incomplete. Yahoo may revise adjusted prices when corporate actions or distributions are processed; the raw responses are preserved in `source/`, and `build_prices.py` recreates the CSV from them.

| Ticker | Adjusted-close source | Local raw response |
|---|---|---|
| SGOV | [Yahoo Finance chart: SGOV](https://query2.finance.yahoo.com/v8/finance/chart/SGOV?period1=1630454400&period2=1790812800&interval=1mo&includeAdjustedClose=true) | `source/sgov_yahoo.json` |
| BND | [Yahoo Finance chart: BND](https://query2.finance.yahoo.com/v8/finance/chart/BND?period1=1630454400&period2=1790812800&interval=1mo&includeAdjustedClose=true) | `source/bnd_yahoo.json` |
| VT | [Yahoo Finance chart: VT](https://query2.finance.yahoo.com/v8/finance/chart/VT?period1=1630454400&period2=1790812800&interval=1mo&includeAdjustedClose=true) | `source/vt_yahoo.json` |

Monthly returns should be computed as `adjusted_close_this_month / adjusted_close_previous_month - 1`. A fixed 60/40 benchmark can then use `0.60 * VT_return + 0.40 * BND_return` each month; this assumes monthly rebalancing and is an analysis convention, not a claim about the handout's benchmark calculation.

## Lab 13 simple portfolios, using course training values

The inputs are: bills 3.5% expected return and 0.5% volatility; 10-year Treasury 4.3% and 7.0%; IG bonds 5.0% and 6.0%; global equity 8.0% and 16.0%. Correlations are bills/10-year 0.10, bills/IG 0.05, bills/equity 0.00, 10-year/IG 0.80, 10-year/equity −0.10, and IG/equity 0.25. All diagonal correlations are 1.00.

For each portfolio, expected return is `sum(weight × expected return)`. Variance is `sum over all i,j of weight_i × weight_j × volatility_i × volatility_j × correlation_ij`; volatility is its square root. The objective proxy is **6.5%** (= estimated CPI 2.5% + 4.0%). Reserve eligibility here includes bills and the 10-year note, as specified in the Lab 13 case. The required reserve is at least 3%.

| Portfolio | Weights (bills / 10-year / IG / equity) | Expected return | Volatility | Reserve eligible | 6.5% objective proxy? | 3% reserve floor? |
|---|---|---:|---:|---:|---|---|
| Benchmark | 0 / 0 / 40 / 60% | 6.80% | 10.46% | 0% | Above target by 0.30 pp before unspecified costs | Fail |
| Equal weight | 25 / 25 / 25 / 25% | 5.20% | 5.21% | 50% | Below target by 1.30 pp | Pass |
| Inverse volatility | 84.32 / 6.02 / 7.03 / 2.63% | 3.77% | 1.05% | 90.34% | Below target by 2.73 pp | Pass |

Inverse-volatility weights use `(1 / volatility_i) / sum(1 / volatility_j)`, so the 0.5%-volatility bill sleeve receives most of the allocation. More precise weights are 84.31618570%, 6.02258469%, 7.02634881%, and 2.63488080%.

**Benchmark volatility by hand:** `0.4² × 0.06² = 0.000576`; `0.6² × 0.16² = 0.009216`; covariance term `2 × 0.4 × 0.6 × 0.06 × 0.16 × 0.25 = 0.001152`. Sum `0.010944`; square root `0.1046135746 = 10.46%`. Expected return is `0.4 × 5.0% + 0.6 × 8.0% = 6.8%`.

**Mandate answer:** None can be identified as meeting both the 6.5% objective proxy and 3% reserve floor. The benchmark clears the expected-return proxy but has no eligible reserve. The other two pass the reserve floor but have expected returns below 6.5%. Expected returns are not guaranteed rolling five-year *net* returns; costs, the 90% five-day liquidity rule, turnover approval, and other mandate terms still need their own evidence. The 60/40 benchmark is a comparison, not a required allocation.

### Code validation, October 20, 2026

`portfolio.py` reproduced all three course answer rows to the displayed precision. Its volatility calculation includes every `i,j` correlation term, including the IG–equity covariance. Changing both IG–equity correlation cells from 0.25 to 0.50 raised the benchmark's volatility from **10.46% to 11.00%**, as expected; the original 0.25 values were restored. Changing both cells to 1.30 made the program stop with `ValueError: Correlations must be between -1 and 1`; the original values were restored and the baseline rerun. The partner-file swap remains to be done with the partner's actual `portfolio.py`.

The existing `../../Recovered non-Costco files/mandate.py` now includes candidate E, the benchmark at 40% IG bonds and 60% global equity. Its run reports **0.0% reserve-eligible** against a **3.0% minimum**, so E fails one checkable hard rule. The all-cash candidate D also passes the checkable hard rules, though its return objective is a separate issue.

## Partner explanation and reading

[OpenStax, *Principles of Finance*, §15.2, “Diversification” through “Portfolio Size and Risk”](https://openstax.org/books/principles-finance/pages/15-2-risk-and-return-to-multiple-assets): Two individually risky assets can form a less volatile portfolio when their returns do not move perfectly together. A bad period for one can be partly offset by a better period for the other. In variance terms, the covariance term falls as correlation falls. Equal weights in two assets that each have 10% volatility and zero correlation give `sqrt(0.5² × 10%² + 0.5² × 10%²) = 7.07%` volatility. Diversification reduces company-specific risk; it cannot remove economy-wide risk.

The benchmark's hand-calculated volatility is **10.46%**, reproduced above from the supplied course digits. For a two-asset benchmark, write its weights, volatilities, and correlation into this expression and calculate each term before taking the square root:

`benchmark volatility = sqrt((w₁σ₁)² + (w₂σ₂)² + 2w₁w₂σ₁σ₂ρ₁₂)`

Do not substitute the sample data in `prices.csv` for these course-authored training inputs.

**Five-minute, no-screen explanation:** Say that each asset has its own ups and downs, but portfolio risk also depends on whether those ups and downs happen together. If they do not, one can partly offset the other; the correlation/covariance term lowers the combined variance. For the 60/40 benchmark, multiplying the weights and volatilities gives standalone variance pieces 0.000576 and 0.009216; the correlation of 0.25 gives covariance piece 0.001152. Their sum is 0.010944, whose square root is 10.46%. This is below the weighted average of the separate volatilities (12.0%) and below equity's 16%, but **above** bonds' 6%. The example shows a diversification benefit; it does not show risk below *both* assets. That stronger outcome can happen with lower or negative correlation and suitable weights. Then ask your partner to repeat the arithmetic and swap roles.

[Streamlit's installation page](https://docs.streamlit.io/get-started/installation) uses `streamlit hello` for the demo. The demo started successfully and returned HTTP 200 at `http://127.0.0.1:8502` on October 20, 2026. [Basic concepts, through “Data flow”](https://docs.streamlit.io/get-started/fundamentals/main-concepts): By default, when someone changes a widget, Streamlit reruns the Python script from top to bottom, and the widget returns its current value on that run. A callback, if used, runs before the script rerun. Forms and fragments provide narrower update behavior when needed.
