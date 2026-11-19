# Lab 13 — Meridian portfolio risk and mandate check

**Question:** What does each simple portfolio earn and risk, and does any of them meet the Meridian mandate? All returns, volatilities, and correlations below are **course-authored training values, not market estimates**.

## Inputs and method

| Sleeve | Expected return | Volatility |
|---|---:|---:|
| Treasury bills | 3.5% | 0.5% |
| Treasury 10-year note | 4.3% | 7.0% |
| Investment-grade bond fund | 5.0% | 6.0% |
| Global equity index fund | 8.0% | 16.0% |

| Correlation | Bills | 10-year | IG bonds | Equity |
|---|---:|---:|---:|---:|
| Bills | 1.00 | 0.10 | 0.05 | 0.00 |
| 10-year | 0.10 | 1.00 | 0.80 | −0.10 |
| IG bonds | 0.05 | 0.80 | 1.00 | 0.25 |
| Equity | 0.00 | −0.10 | 0.25 | 1.00 |

Expected portfolio return is `sum(weight × sleeve return)`. Portfolio volatility is the square root of `sum over all i,j (weight_i × weight_j × volatility_i × volatility_j × correlation_ij)`. The correlation terms matter: leaving them out gives the wrong benchmark answer.

The objective proxy is **6.5%**: estimated CPI 2.5% plus 4.0 percentage points. The tested reserve floor is **3%**, with Treasury bills and the 10-year note reserve-eligible. The actual mandate seeks CPI + 4% **net of costs over rolling five-year periods**; the one-period expected-return comparison cannot establish that future result.

## Known-answer check

| Portfolio | Weights: bills / 10-year / IG / equity | Expected return | Volatility | Reserve-eligible | Meets 6.5% proxy? | Passes 3% reserve? |
|---|---|---:|---:|---:|---|---|
| Benchmark | 0.0 / 0.0 / 40.0 / 60.0 | 6.80% | 10.46% | 0.0% | Yes | **No** |
| Equal weight | 25.0 / 25.0 / 25.0 / 25.0 | 5.20% | 5.21% | 50.0% | No | Yes |
| Inverse volatility | 84.3 / 6.0 / 7.0 / 2.6 | 3.77% | 1.05% | 90.3% | No | Yes |

Inverse-volatility weights are proportional to `1 / sleeve volatility`, then normalized to sum to 100%. The 0.5%-volatility bill sleeve receives **84.3%**; this lowers modeled volatility but also pulls expected return toward the bills' 3.5%.

### Benchmark by hand

Return: `0.40 × 5.0% + 0.60 × 8.0% = 6.80%`.

Variance:

```text
(0.40 × 0.06)²                         = 0.000576
(0.60 × 0.16)²                         = 0.009216
2 × 0.40 × 0.60 × 0.06 × 0.16 × 0.25 = 0.001152
Total variance                         = 0.010944
Volatility = sqrt(0.010944)            = 0.1046136 = 10.46%
```

Without the covariance term, the result would be about **9.90%**, which is incorrect for the supplied correlation.

## Meridian decision

No baseline both reaches the 6.5% expected-return proxy and satisfies the 3% reserve floor. The benchmark clears the return proxy but holds **0%** in eligible reserves. Equal weight and inverse volatility pass the reserve floor but fall short of the return proxy. The 60/40 benchmark is a performance comparison, not a required allocation. Other mandate checks, costs, turnover, and realized five-year returns need separate evidence.

I would show the CIO the **benchmark first** because it is the client's own comparison portfolio and fails the client's reserve rule. That makes the tradeoff between the return objective and hard liquidity need immediately visible.

## Prove the engines

`portfolio.py` reproduces every known-answer row above. Changing **both** IG–equity correlation cells from 0.25 to 0.50 raises benchmark volatility to **11.00%**. Restoring 0.25 returns it to **10.46%**. Changing both cells to **1.30** makes the program stop with `ValueError: Correlations must be between -1 and 1`; 0.25 was restored afterward. Run `python3 portfolio.py` to see the final baseline.

`mandate.py` includes candidate **E** at 40% IG bonds and 60% global equity. Running it reports **0.0% reserve-eligible** against a **3.0% minimum**, so E fails the reserve rule. The existing all-cash candidate D passes the checkable hard rules, though an all-cash allocation does not solve the return objective. Run `python3 mandate.py` to inspect all A–E checks.

The partner-file swap and spoken, no-AI code explanation require the partner's file and participation; they have not been recorded as completed here.

## Explain diversification aloud

Two risky assets can be less risky together when their returns do not move perfectly together: one can partly offset the other's swings. Correlation below +1 lowers the portfolio's volatility relative to perfectly synchronized returns at the same weights. In this example, +1 correlation would give **12.0%** benchmark volatility, versus **10.46%** with 0.25 correlation. The 10.46% result is below equity's 16% but above IG bonds' 6%; this example shows a diversification benefit, not risk below *both* assets. [OpenStax §15.2](https://openstax.org/books/principles-finance/pages/15-2-risk-and-return-to-multiple-assets) provides the reading.
