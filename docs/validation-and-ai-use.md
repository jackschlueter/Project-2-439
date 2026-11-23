# Validation and AI-use record

## Sources and as-of boundary

| Input | Source | As-of / download date |
|---|---|---|
| Sleeve returns, volatilities, correlations, Meridian mandate | Course-authored Lab 13 training values ([`lab13-source.md`](../lab13-source.md)) and Meridian IPS S1–S10 ([`meridian-ips-source.md`](../meridian-ips-source.md)) | Course material; training values, not market estimates |
| DGS10 10-year Treasury yield (signal stress only) | Federal Reserve H.15 via ALFRED vintages, saved as `dgs10_2026-10-31.csv` and `dgs10_2026-11-03.csv` ([data card](../dgs10-data-card.md)) | Decision vintage 2026-10-31 (latest observation 2026-10-29, 4.98%); downloaded 2026-11-17 |
| SGOV / BND / VT / TIP adjusted closes (window stress only) | Yahoo Finance chart responses in `source/`, built into `prices.csv` by `build_prices.py` ([price-source table](../mandate-source.md)) | Monthly, September 2021–September 2026; downloaded 2026-10-20 (TIP 2026-10-22); incomplete October 2026 excluded |

**Boundary:** the decision uses nothing dated after the 2026-10-31 DGS10 vintage and the September 2026 month-end prices. The app excludes DGS10 observations after the selected vintage date.

## Validation

Run from the app folder after `pip install -r requirements.txt`:

- `python verify_project2.py` reproduces every figure behind the decision (baselines, verdicts, each stress, the signal case) and stops with an error if any saved number changes.
- `python -m unittest -v test_portfolio_engine.py test_lab13_mandate.py test_pit_signal.py` runs 9 known-answer tests, including the Lab 13 Meridian answer (0/20/25/55, 6.51%, 9.44%), the loss-limit verdicts, and the DGS10 vintage gate.
- `records/project2_cold_run_2026-11-17.md` records clean-folder runs and the partner cold run from a fresh GitHub clone (2026-11-22, partner: OpenAI Codex, not a classmate). Run 1 reached PILOT with all 9 tests passing and the app running; it found one README gap (no `cd` step, and no mention of Streamlit's optional email prompt), fixed in commit `7cf29ec`. The rerun after the fix had no project-command failures.
- `single_file/app.py` was rendered alone, with no other project files beside it, and matched the main app's figures.
- The changed-input test is in the Locked Changed-Input Record below.
- **Saved executed output (2026-11-23):** [`records/verify_output.txt`](../records/verify_output.txt) (verifier: baselines, stresses, signal case, PILOT decision) and [`records/unittest_output.txt`](../records/unittest_output.txt) (9 tests, all OK).

## Limitations

- Sleeve returns, volatilities, and correlations are course training values, not validated market estimates.
- The 95% one-year loss measure assumes normally distributed returns, so it understates extreme-loss risk.
- The 10% loss limit and the minimum-volatility objective are analyst proposals, not approved policy.
- The result is single-period; it cannot show whether the process meets CPI + 4% over rolling five-year periods.
- Issuer concentration, five-day liquidity, and turnover rules are not fully tested.
- The window stress uses SGOV/BND/VT as stand-ins for bills/IG/equity; there is no 10-year Treasury sleeve history.
- The DGS10 signal is a yield level used for one labeled stress, not a return forecast; its intraday release timing is unverified.
- The partner cold run was done by OpenAI Codex, not a classmate, and it confirmed server startup, not a rendered page.

## Locked Changed-Input Record

**Locked:** Jack's AI-off prediction, [`records/lab20_pre_run_prediction.md`](../records/lab20_pre_run_prediction.md), was committed and pushed to GitHub in commit `723d43d` (2026-11-22 17:14:32 −0500) before the run. Jack wrote it without AI; Claude Code only saved it verbatim and pushed it.

**One changed input:** global equity's expected annual return, 8.00% → 7.25% (−0.75 pp). Everything else held fixed: other sleeve returns, all volatilities and correlations, 2.5% CPI, 4.0 pp spread, 0% costs, 6.5% return hurdle, 3% eligible reserve floor, long-only 5% grid, and the proposed 10% one-year loss limit (on).

**Run:** after the prediction was on GitHub, Claude Code ran `search(target=.065, reserve_floor=.03, equity_adjustment=-.0075, loss_limit=.10)` from `lab13_mandate.py` and saved [`records/lab20_baseline_output.txt`](../records/lab20_baseline_output.txt) (before) and [`records/lab20_after_output.txt`](../records/lab20_after_output.txt) (after).

| Case | Bills / 10-yr / IG / Equity | Return | Volatility | 95% loss | Verdict |
|---|---|---:|---:|---:|---|
| Baseline (equity 8.00%) | 0 / 20 / 25 / 55 | 6.51% | 9.44% | 9.02% | PASS |
| Old mix at equity 7.25% | 0 / 20 / 25 / 55 | 6.10% | 9.44% | 9.43% | FAIL: return below 6.50% |
| Re-optimized, loss limit on | No qualifying mix | — | — | — | FAIL → STOP |
| Re-optimized, loss limit off (comparison) | 0 / 10 / 20 / 70 | 6.50% | 11.57% | 12.53% | FAIL: loss above 10% |

**Prediction vs. result:** all four predictions held. The old mix fell about 0.41 pp to 6.10%; the optimizer needed more equity (70% without the loss limit); no mix met return, reserve, and loss rules together, so STOP triggered; the recommendation stayed PILOT. The prediction gave no number for the new volatility or loss.

**Effect on the decision (Jack):** PILOT stands. The STOP shows the process catches an infeasible case instead of forcing an allocation, but it has little room for error in its return assumptions. Full write-up: [`records/lab20_run_result.md`](../records/lab20_run_result.md), assembled by Claude Code from the saved outputs except the "Effect on the decision" paragraph, which Jack wrote.

**Earlier draft:** [`records/locked_changed_input_2026-11-17.md`](../records/locked_changed_input_2026-11-17.md) locked the same equity change on 2026-11-17 but predates the loss limit and was never run on its own. It is superseded by the record above.

## AI-use log

Entries before 2026-11-19 (the 2026-11-16/17 app build, cold-run audit, and locked changed-input record) are in this repository's git history and `records/`; add reviews for them if your course requires it.

2026-11-19 — Claude Code located the Project 2 files across the course folder and `~/portfolio-committee-app` and copied them into `AIFinance2026/Project 2/`.
**Review (Jack, 11/22):** Accepted.

2026-11-19 — Claude Code removed the young-family mode from `app.py` so the app runs only the Lab 13 Meridian mandate, and rewrote `README.md` and `verify_project2.py` around the Meridian decision. Earlier code remains in git history.
**Review (Jack, 11/22):** Accepted.

2026-11-19 — Claude Code proposed and implemented a 95% one-year loss measure (1.645 × volatility − expected return) with a 10% limit to define IPS S9, enforced it in the optimizer and the PASS/FAIL verdicts, and made it switchable in the sidebar. The limit is labeled an analyst proposal pending committee approval. Result: the constrained mix passes (9.02%); the benchmark fails (10.41%); equity −1 pp and costs +0.50 pp each leave no qualifying mix.
**Review (Jack, 11/22):** Accepted.

2026-11-19 — Claude Code replaced the window-stress "evidence gap" with a stand-in window stress using the bundled SGOV/BND/VT adjusted closes for bills/IG/equity (60 vs 36 months: 65/0/35 → 85/0/15).
**Review (Jack, 11/22):** Accepted.

2026-11-19 — Claude Code connected the DGS10 point-in-time signal to the stress run: the 10-year sleeve's return estimate is set to the 2026-10-31 vintage yield of 4.98% (result 5/40/0/55). Updated the signal tab and data card wording.
**Review (Jack, 11/22):** Accepted.

2026-11-19 — Claude Code changed the rebalance tab's default current holdings to the 60/40 benchmark, deleted the outdated young-family static site (`dist/`, `.openai/`), updated the cold-run record, drafted Project 2 Edition A, added tests (9 pass), and committed the changes locally.
**Review (Jack, 11/22):** Accepted.

2026-11-22 — Claude Code revised Jack's decision-memo draft (corrected the second baseline, the loss-limit framing of the stresses, payout timing and the issuer rule; added the window, signal, constraint and stop-condition results) and saved it as `docs/decision-memo.md`.
**Review (Jack, __/__):**

2026-11-22 — Claude Code built `single_file/app.py`, a self-contained version of the app generated by `single_file/build.py`, and checked it matched the main app.
**Review (Jack, __/__):**

2026-11-22 — Jack wrote the Lab 20 pre-run prediction without AI. He shared the finished text with Claude Code only so it could save it verbatim and push it; Claude Code gave no feedback on the expected outcome before the commit.

2026-11-22 — Claude Code saved the baseline output, ran the equity 7.25% case after the prediction was on GitHub, saved the after output, and assembled `records/lab20_run_result.md` (change, before/after table, prediction-vs-result table). Jack wrote the "Effect on the decision" paragraph himself.
**Review (Jack, __/__):**

2026-11-22 — Claude Code added Jack's AI-use disclosure and education statement (written by Jack) to the top of the README and decision memo, moved this log to `docs/validation-and-ai-use.md`, and added the validation section.
**Review (Jack, __/__):**

