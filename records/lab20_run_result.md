# Lab 20 — Run Result: Equity Expected Return 8.00% → 7.25%

**Analyst:** Jack Schlueter  
**Run date:** November 22, 2026  
**Prediction:** [`lab20_pre_run_prediction.md`](lab20_pre_run_prediction.md), committed and pushed to GitHub in commit `723d43d` (2026-11-22 17:14:32 −0500) before this run  
**Baseline output:** [`lab20_baseline_output.txt`](lab20_baseline_output.txt), saved before the change  
**After output:** [`lab20_after_output.txt`](lab20_after_output.txt), saved after the change; every figure below comes from these two files  
**Run by:** Claude Code, at Jack's instruction, after the prediction was on GitHub (pushed through commit `afb99de`)

## What changed

Only global equity's expected annual return: **8.00% → 7.25%** (−0.75 percentage points). Held fixed: other sleeve returns (bills 3.50%, 10-year 4.30%, IG bonds 5.00%), all Lab 13 volatilities and correlations, 2.5% CPI, 4.0 pp spread, 0% costs, 6.5% return hurdle, 3% eligible reserve floor, long-only 5% grid, and the proposed 10% 95% one-year loss limit (on).

**Command:** `search(target=.065, reserve_floor=.03, equity_adjustment=-.0075, loss_limit=.10)` from `lab13_mandate.py`. In the app: sidebar equity slider at −0.75, loss limit checked.

## Before and after

| Case | Bills / 10-yr / IG / Equity | Return | Volatility | 95% loss | Verdict |
|---|---|---:|---:|---:|---|
| Baseline (equity 8.00%) | 0 / 20 / 25 / 55 | 6.51% | 9.44% | 9.02% | PASS |
| Old mix at equity 7.25% | 0 / 20 / 25 / 55 | 6.10% | 9.44% | 9.43% | FAIL: return 6.10% < 6.50% |
| **Re-optimized, loss limit on** | **No qualifying mix** | — | — | — | **FAIL → STOP** |
| Re-optimized, loss limit off (for comparison) | 0 / 10 / 20 / 70 | 6.50% | 11.57% | 12.53% | FAIL: loss 12.53% > 10% |

## Prediction vs. result

| Prediction | Result | Right? |
|---|---|---|
| Old mix return falls about 0.41 pp, to about 6.10%, below the hurdle | 6.51% → 6.10% (−0.41 pp); fails the 6.5% hurdle | Yes |
| Optimizer shifts toward equity, raising volatility and loss | Without the loss limit, equity rises 55% → 70%; volatility 9.44% → 11.57%; loss 9.02% → 12.53% | Yes |
| PASS → FAIL; no mix meets return, reserve, and loss rules together; STOP triggers | No qualifying mix with the loss limit on; STOP | Yes |
| Recommendation stays PILOT | PILOT (see below) | Yes |

**What the prediction left out:** it gave no number for the new volatility or loss. The comparison run shows the cheapest way back to the 6.5% hurdle needs 70% equity, with a 12.53% modeled loss. That is 2.5 points over the proposed limit, so the STOP is not a near miss.

## Effect on the decision

*Written by Jack Schlueter.*

My recommendation remains PILOT. Reducing the expected equity return from 8.00% to 7.25% caused the original portfolio's expected return to fall from 6.51% to 6.10%, below Meridian's 6.5% hurdle. When the optimizer attempted to find a new allocation, no portfolio could satisfy the return target, 3% reserve requirement, and proposed 10% loss limit simultaneously, triggering the STOP condition. Without the loss limit, the optimizer found a portfolio with 70% equities, but its estimated 12.53% one-year loss exceeded the proposed limit by 2.53 percentage points. These results reinforce my original concern that the process has very little room for error in its assumptions. However, I would not recommend rejecting the process because it worked as intended by identifying an infeasible situation rather than forcing an allocation. For the committee, this demonstrates that the process is useful for risk management but is not ready for full adoption. Before moving beyond the pilot stage, Meridian should validate its return estimates, formally approve the loss limit, and determine how to handle conflicts between its return objective and risk constraints. Until then, I would maintain the PILOT recommendation without authorizing a capital allocation.

*Education, not investment advice. Course-provided training assumptions; not a forecast.*
