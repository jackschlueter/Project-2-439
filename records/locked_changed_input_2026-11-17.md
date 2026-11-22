# Locked Changed-Input Record — Meridian equity return estimate

> **SUPERSEDED (2026-11-22).** This test was replaced by Jack's own AI-off prediction, `lab20_pre_run_prediction.md` (commit `723d43d`), and run in `lab20_run_result.md`. The Lab 20 run held the proposed 10% loss limit on, which this 2026-11-17 record predates. The case this record specifies (equity 7.25%, no loss limit) appears in `lab20_run_result.md` as the "loss limit off" comparison row: 0 / 10 / 20 / 70, 6.50% return, 11.57% volatility. The prediction below was not run on its own.

**Locked at:** 2026-11-17 21:41:55 UTC  
**Status:** Input and expectation recorded before the changed-input run. Do not execute the 7.25% case until this file is committed to GitHub and the remote commit is verified.  
**Purpose:** Test whether a modest equity-return estimate cut changes the lowest-volatility qualifying mix under the Lab 13 Meridian mandate.

## Frozen baseline and one changed input

The prior Lab 13 baseline uses expected returns of **3.50% Treasury bills / 4.30% 10-year Treasury / 5.00% IG bonds / 8.00% global equity**. Its 5% grid result is **0 / 20 / 25 / 55**, **6.51% expected gross return**, **9.44% modeled annual volatility**, and **20% eligible reserve**. These baseline figures are already known; this record does not represent a new run.

**Only change:** global equity's annual expected return estimate **8.00% → 7.25%** (−0.75 percentage points).

**Hold fixed:** bill, 10-year, and IG expected returns; all four volatilities (**0.50%, 7.00%, 6.00%, 16.00%**); all Lab 13 correlations; CPI proxy **2.50%**; required real spread **4.00 percentage points**; cost allowance **0.00%**; gross return hurdle **6.50%**; eligible direct-government reserve floor **3.00%**; long-only weights summing to 100%; and the **5 percentage point grid**. Treasury bills and direct 10-year notes remain reserve-eligible. The benchmark stays 60% global equity / 40% IG bonds.

## Prediction before execution

At the old 0/20/25/55 weights, the 0.75-point equity haircut reduces expected return by **0.55 × 0.75 = 0.4125 percentage points**, from 6.51% to about **6.10%**. The old mix should fail the unchanged 6.50% return proxy. I expect the qualifying search, if feasible, to move more weight into global equity and raise modeled volatility. I make **no prediction of the exact new weights or volatility**.

## Run and decision rule

After confirming the GitHub commit, run `search(target=.065, reserve_floor=.03, equity_adjustment=-.0075)` from `lab13_mandate.py` once and record its weights, expected gross return, modeled volatility, eligible reserve, mandate-screen verdict, and the remote commit evidence in a separate result file. If no mix qualifies, stop the allocation process. A passing modeled screen still does not resolve issuer concentration, five-day liquidity, the calendar-year loss rule, or trade authorization.

**Source records:** `lab13-source.md` and `meridian-ips-source.md` in this project.
