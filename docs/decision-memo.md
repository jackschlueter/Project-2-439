# Meridian Foundation Reserve — Investment Committee Decision Memo

**To:** Meridian Foundation Reserve Investment Committee  
**From:** Jack Schlueter, Portfolio Analyst  
**Date:** November 22, 2026  
**Subject:** Recommendation to Pilot Portfolio Selection Process  
**Decision:** PILOT

**AI Use Disclosure:** I used Claude Code, OpenAI Codex, and ChatGPT to assist with developing and refactoring the Meridian Portfolio Committee application, implementing portfolio optimization and risk calculations, defining the proposed 95% one-year loss measure, building sensitivity tests and historical-window and DGS10 signal analyses, writing tests and validation tools, and drafting project documentation, including the README, decision memo, and cold-run instructions. AI contributed substantially to the coding and documentation process. I reviewed the outputs, evaluated the financial assumptions, interpreted the results, and take responsibility for the analysis and final investment committee recommendation. The detailed AI-use and validation record is documented in `docs/validation-and-ai-use.md`.

**Education, not investment advice.** This memo and its application are an academic project using course-provided assumptions and illustrative portfolio analysis. The results and recommendations are for educational purposes only and should not be relied upon for actual investment decisions.

## 1. Recommendation

I recommend that the committee **PILOT** the proposed portfolio selection process, with **no capital allocation or trade authorization**. The process finds a portfolio that passes every tested rule, but it clears the 6.5% return hurdle by only 0.01 percentage points, and modest stresses leave no portfolio that passes. It is promising but not yet reliable enough to manage the foundation's $100 million reserve.

## 2. Objectives and Constraints

Meridian has a seven-year horizon and seeks CPI + 4% a year, net of costs, over rolling five-year periods; with illustrative 2.5% inflation, that is a 6.5% return target. It must hold at least 3% ($3 million) in eligible reserves for four quarterly payouts of $750,000; only cash, Treasury bills, and direct 10-year Treasuries count. Other rules: long-only with no borrowing, shorts, or derivatives; at most 8% in any non-exempt issuer; committee approval for turnover above 25%; at least 90% redeemable within five business days; and a 10% calendar-year loss limit that the policy does not define. The 60/40 global equity / investment-grade bond portfolio is a benchmark, not a required allocation.

## 3. Process and Results

The process searches long-only allocations in 5-point steps for the lowest-volatility portfolio that meets the return target, the reserve floor, and a loss limit. To make the 10% limit testable, I measure the **95% one-year loss** as 1.645 × volatility − expected return: the loss exceeded about 5% of the time if returns are normal. A portfolio passes if it is 10% or less.

| Portfolio | Bills / 10-yr / IG / Equity | Return | Volatility | 95% Loss | Reserve | Verdict |
|---|---|---:|---:|---:|---:|---|
| Equal weight | 25 / 25 / 25 / 25 | 5.20% | 5.21% | 3.38% | 50% | FAIL — return below 6.5% |
| 60/40 benchmark | 0 / 0 / 40 / 60 | 6.80% | 10.46% | 10.41% | 0% | FAIL — reserve below 3%; loss above 10% |
| **Proposed** | **0 / 20 / 25 / 55** | **6.51%** | **9.44%** | **9.02%** | **20%** | **PASS** |

The process adds value by finding a feasible portfolio when both comparisons fail. This shows feasibility under the supplied assumptions, not reliable future performance.

## 4. Risks and Limitations

I stress-tested the process one input at a time:

| Stress | Change | Result |
|---|---|---|
| Estimates | Equity expected return −1 point | **No qualifying allocation** under the loss limit |
| Estimates | Bond–equity correlation 0.25 → 0.50 | 0 / 40 / 0 / 60; still passes |
| Window | 60 vs. 36 months of ETF price history | 65/0/35 → 85/0/15 (bills/IG/equity): 20-point move |
| Costs | +0.50 point cost allowance | **No qualifying allocation** under the loss limit |
| Constraints | Raise the reserve floor in 5-point steps | First infeasible floor: 45% |
| Signal | 10-year return set to the 4.98% DGS10 yield | 5 / 40 / 0 / 55; 20 points shift into Treasuries |

- **Little margin for error.** A 1-point equity cut or 0.50 points of cost triggers the **stop condition**: no allocation passes, so the decision goes back to the committee. Without the loss limit, the equity cut still yields 0/10/10/80, but its 95% loss rises to 14.75%.
- **Window stand-ins.** Lab 13 has no dated history, so the window test uses SGOV, BND, and VT prices (September 2021–September 2026) for bills, IG bonds, and equity. There is no 10-year stand-in, and these ETFs are not Meridian's holdings.
- **Signal.** DGS10 knowable on October 31, 2026 (ALFRED) was 4.98% versus the 4.30% training return. A yield approximates a held-to-maturity return, not a one-year forecast.
- **Inputs and policy.** Returns, volatilities, and correlations are course training values, not validated estimates. The loss measure and the minimum-volatility objective are my proposals and need committee or CIO approval. A normal-distribution loss understates extreme losses.
- **Untested rules.** Issuer concentration, five-day liquidity, and turnover are unverified, and a single-period analysis cannot show CPI + 4% over rolling five-year periods.

## 5. Pilot, and What Would Change My Recommendation

During the pilot, I would run simulated allocations through one annual rebalancing cycle without committing capital. Before adoption I would require: dated, sourced market estimates in place of training values; a compliant allocation under reasonable changes in returns, costs, and correlations; verified issuer, liquidity, and turnover rules; committee approval of the loss measure and a breach response; CIO confirmation of the minimum-volatility objective; and rolling five-year backtests against CPI + 4% and the 60/40 benchmark once dated sleeve history exists.

- **ADOPT** if the process consistently finds compliant portfolios with validated inputs, stays feasible under the stresses above, and passes the unverified rules.
- **REJECT** if realistic assumptions repeatedly trigger the stop condition, the process cannot meet liquidity requirements, or results stay dependent on optimistic return estimates.

**The committee should approve further testing of the process, but not authorize a capital allocation based on the current results.**

---

*Figures reproduce with `python verify_project2.py` at default settings. See the README for setup.*
