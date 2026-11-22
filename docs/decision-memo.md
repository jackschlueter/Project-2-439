# Meridian Foundation Reserve — Investment Committee Decision Memo

**To:** Meridian Foundation Reserve Investment Committee  
**From:** Jack Schlueter, Portfolio Analyst  
**Date:** November 22, 2026  
**Subject:** Recommendation to Pilot Portfolio Selection Process  
**Decision:** PILOT

**AI Use Disclosure:** I used Claude Code, OpenAI Codex, and ChatGPT to assist with developing and refactoring the Meridian Portfolio Committee application, implementing portfolio optimization and risk calculations, defining the proposed 95% one-year loss measure, building sensitivity tests and historical-window and DGS10 signal analyses, writing tests and validation tools, and drafting project documentation, including the README, decision memo, cold-run instructions, and Edition A materials. AI contributed substantially to the coding and documentation process. I reviewed the outputs, evaluated the financial assumptions, interpreted the results, and take responsibility for the analysis and final investment committee recommendation. The detailed AI-use and validation record is documented in `docs/validation-and-ai-use.md`.

**Education, not investment advice.** This memo and its application are an academic project using course-provided assumptions and illustrative portfolio analysis. The results and recommendations are for educational purposes only and should not be relied upon for actual investment decisions.

## 1. Executive Recommendation

I recommend that the Meridian Investment Committee **PILOT** the proposed portfolio selection process rather than adopt it for immediate implementation.

The process identifies a portfolio that satisfies all currently tested constraints while meeting the foundation's illustrative 6.5% annual return hurdle. However, the recommended portfolio exceeds that hurdle by only 0.01 percentage points, making the result highly sensitive to changes in assumptions.

The process demonstrates potential value, but additional testing and validation are necessary before the committee can confidently rely on it to manage the foundation's $100 million reserve.

## 2. Client Objectives and Constraints

Meridian Foundation Reserve has a seven-year investment horizon and seeks CPI + 4% annually, net of costs, measured over rolling five-year periods. Assuming illustrative inflation of 2.5%, this translates to a 6.5% annual return target.

The foundation must maintain at least $3 million (3% of assets) in eligible reserves to fund four quarterly payouts of $750,000. Only cash, Treasury bills, and direct 10-year Treasuries qualify toward this requirement.

Additional constraints include:

- Long-only investments with no borrowing, short sales, or derivatives.
- Maximum 8% combined exposure (stock and bonds together) to any non-exempt issuer. Treasuries and diversified funds are exempt.
- Committee approval for annual turnover exceeding 25%.
- At least 90% of the portfolio redeemable within five business days.
- A 10% calendar-year loss limit that the policy does not yet define, with no stated breach response.

The 60% global equity / 40% investment-grade bond portfolio serves as a performance benchmark rather than a required allocation.

## 3. Process and Results

My proposed process evaluates portfolio allocations using expected returns, volatility, correlations, and the foundation's investment constraints. It searches long-only allocations in 5-percentage-point steps for the lowest-volatility portfolio that satisfies the return target, the eligible-reserve floor, and a proposed loss limit.

To make the 10% loss limit testable, I measure risk as the **95% one-year loss**: 1.645 × volatility − expected return. This is the loss the portfolio would exceed only about 5% of the time if returns were normally distributed. A portfolio passes if this figure is 10% or less.

The process identified the following allocation:

| Asset Class | Allocation |
|---|---:|
| Treasury Bills | 0% |
| 10-Year Treasuries | 20% |
| Investment-Grade Bonds | 25% |
| Global Equities | 55% |

This allocation produces an estimated return of 6.51%, exceeding the 6.5% hurdle by 0.01 percentage points, with 9.44% modeled volatility and a 9.02% 95% one-year loss, inside the proposed 10% limit. Its 20% allocation to direct 10-year Treasuries exceeds the 3% eligible-reserve requirement.

The process adds value by finding a feasible allocation when both comparison portfolios fail:

| Portfolio | Return | Volatility | 95% Loss | Eligible Reserve | Verdict |
|---|---:|---:|---:|---:|---|
| Equal weight (25% each) | 5.20% | 5.21% | 3.38% | 50% | FAIL — return below 6.5% |
| 60/40 benchmark | 6.80% | 10.46% | 10.41% | 0% | FAIL — reserve below 3%; loss above 10% |
| Proposed allocation | 6.51% | 9.44% | 9.02% | 20% | PASS |

Equal weight maintains reserves but misses the return target. The 60/40 benchmark meets the return target but holds no eligible reserves and exceeds the proposed loss limit.

However, this result demonstrates feasibility under the supplied assumptions, not evidence of reliable future performance. Issuer concentration and five-day liquidity requirements remain unverified.

## 4. Risks and Limitations

The most significant concern is the process's sensitivity to assumptions. I stress-tested it by changing one input at a time:

| Stress | Change | Result |
|---|---|---|
| Estimates | Equity expected return −1 point | **No qualifying allocation** under the loss limit |
| Estimates | Bond–equity correlation 0.25 → 0.50 | 0 / 40 / 0 / 60; still passes |
| Window | 60 vs. 36 months of ETF price history | Allocation moves 20 points |
| Costs | +0.50 point cost allowance | **No qualifying allocation** under the loss limit |
| Constraints | Raise the reserve floor in 5-point steps | First infeasible floor: 45% |
| Signal | 10-year Treasury return set to the 4.98% DGS10 yield | 5 / 40 / 0 / 55; 20 points shift into Treasuries |

Under the proposed 10% loss limit, a one-percentage-point cut in expected equity returns, or 0.50 points of added cost, leaves no allocation that passes. Without the loss limit, the equity cut still yields a portfolio (0/10/10/80), but its 95% one-year loss rises to 14.75%. The process has very little margin for error, and since expected returns are uncertain, the committee should not treat the 6.51% estimate as a dependable outcome.

**Window test.** Lab 13 provides no dated return history, so I used monthly adjusted prices for SGOV, BND, and VT (September 2021–September 2026) as stand-ins for bills, investment-grade bonds, and equities. Switching from 60 to 36 months of history moves the allocation from 65/0/35 to 85/0/15. There is no stand-in for the 10-year Treasury, and these ETFs are not Meridian's direct holdings.

**Point-in-time signal.** The 10-year Treasury training return is 4.30%. The 10-year Treasury yield (DGS10) knowable on October 31, 2026, from the archived ALFRED data was 4.98%. Using that yield as the 10-year estimate shifts 20 points into Treasuries. A yield approximates a note's return if held to maturity; it is not a one-year return forecast.

**Stop condition.** The process stops, and refers the decision to the committee, whenever no allocation meets the return, reserve, and loss rules. That condition already occurs under the equity and cost stresses.

Another limitation is that the return, volatility, and correlation assumptions are course training inputs rather than independently validated market estimates.

Additionally, I selected the 95% one-year loss measure to define the 10% loss limit and chose minimum volatility as the optimization objective. Both are analyst proposals that require committee or CIO approval before becoming formal investment policy. A normal-distribution loss measure also understates the risk of extreme losses.

Finally, a single-period analysis cannot establish whether the process will achieve CPI + 4% over rolling five-year periods.

## 5. Conditions for Adoption

Before recommending full adoption, I would require:

1. **Validated market inputs:** Replace training assumptions with defensible estimates and document their sources and dates.
2. **Robustness testing:** Demonstrate that the process still finds a compliant allocation under reasonable changes in expected returns, costs, and correlations.
3. **Complete compliance testing:** Verify issuer concentration, five-day liquidity, and turnover requirements.
4. **Formal risk policy:** Obtain committee approval for the 10% loss measure and define the response to a breach.
5. **CIO approval:** Confirm whether minimizing volatility is the appropriate optimization objective.
6. **Historical evaluation:** Obtain a dated return history for each sleeve, then run rolling five-year backtests comparing net performance with the CPI + 4% objective and the 60/40 benchmark. Lab 13 provides no dated history, so this cannot be done yet.

During the pilot, I would run simulated allocations through one annual rebalancing cycle without committing the foundation's capital. The pilot succeeds if the process produces a compliant allocation at each review under validated inputs. It fails if the stop condition triggers under realistic assumptions.

## 6. What Would Change My Recommendation?

I would upgrade my recommendation from **PILOT to ADOPT** if the process consistently identifies compliant portfolios using validated assumptions, remains feasible under the stress tests above, and passes the currently unverified investment constraints.

I would recommend **REJECT** if realistic market assumptions repeatedly trigger the stop condition, if the process cannot meet the foundation's liquidity requirements, or if the results remain excessively dependent on optimistic return estimates.

The most important factor is whether the process can produce reliable, compliant decisions across different market conditions rather than finding one allocation that barely passes under favorable assumptions.

## 7. Final Decision

**Recommendation: PILOT**

The proposed portfolio selection process is promising because it explicitly incorporates Meridian's return objective, eligible-reserve requirement, and a defined loss limit rather than relying on a standard allocation.

However, meeting the expected return hurdle by only 0.01 percentage points is not enough evidence to justify immediate adoption. The sensitivity tests, unverified constraints, and reliance on training assumptions create substantial uncertainty.

A controlled pilot would allow Meridian to evaluate the process's reliability, refine its risk controls, and determine whether it can support future investment decisions.

**The committee should approve further testing of the process, but not authorize a capital allocation based on the current results.**

---

*Figures reproduce with `python verify_project2.py` at default settings. See the README for setup.*
