# Project 2 — Edition A (2026-11-19)

*Drafted with AI from the repository evidence on this date. Kept for comparison with a later Edition B; not submitted.*

## Decision and its user

Decision: whether the Meridian Foundation Reserve investment committee should **adopt, allocate to, rebalance, pilot, or reject** this portfolio-construction process under the Lab 13 mandate.

User: the Meridian investment committee. This is a process recommendation, not a trade instruction.

## Mandate (Lab 13)

- **Objective:** CPI + 4 pp annually net of costs over rolling five years; 6.5% proxy at 2.5% CPI.
- **Universe:** direct Treasury bills, direct 10-year Treasury notes, an IG bond fund, a global equity index fund.
- **Benchmark:** 60% global equity / 40% IG bonds.
- **Risk measure:** modeled volatility, expressed as 95% one-year loss = 1.645σ − μ.
- **Limits:** ≥3% eligible direct-government reserve; long-only; 8% issuer cap; >25% turnover needs approval; ≥90% liquid in five days. **Proposed:** 95% loss ≤ 10% (defines IPS S9; needs committee approval).

## Call: PILOT

Use 0 / 20 / 25 / 55 (bills / 10-year / IG / equity) as a research starting mix. No allocation authorization.

| Portfolio | Return | Volatility | 95% loss | Reserve | Verdict |
|---|---:|---:|---:|---:|---|
| Equal weight | 5.20% | 5.21% | 3.38% | 50% | FAIL — return |
| 60/40 benchmark | 6.80% | 10.46% | 10.41% | 0% | FAIL — reserve, loss |
| Constrained | 6.51% | 9.44% | 9.02% | 20% | PASS |

## Why not adopt

1. The constrained mix clears the hurdle by 0.01 pp.
2. Under the proposed loss limit, equity −1 pp **or** costs +0.50 pp leaves no qualifying mix: the stop condition fires.
3. Window stand-ins (SGOV/BND/VT) move 20 points between 60 and 36 months.
4. Setting the 10-year estimate to the decision-date DGS10 yield (4.98%) moves 20 points into the 10-year sleeve.
5. Liquidity, issuer exposure, and the loss limit itself are unapproved or unverified.

## What would change the call

Committee approval of a loss measure and limit (or a lower return target), verified liquidity and issuer exposure, and dated forward-looking estimates in place of training values.

## Open evidence gaps

- Partner cold run from a GitHub clone not yet done.
- Locked 7.25% equity changed-input test (`records/locked_changed_input_2026-11-17.md`) not yet run; its protocol requires a verified GitHub commit first.
