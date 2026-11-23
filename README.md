# Meridian Portfolio Committee — Python web app

**AI Use Disclosure:** I used Claude Code, OpenAI Codex, and ChatGPT to assist with developing and refactoring the Meridian Portfolio Committee application, implementing portfolio optimization and risk calculations, defining the proposed 95% one-year loss measure, building sensitivity tests and historical-window and DGS10 signal analyses, writing tests and validation tools, and drafting project documentation, including the README, decision memo, and cold-run instructions. AI contributed substantially to the coding and documentation process. I reviewed the outputs, evaluated the financial assumptions, interpreted the results, and take responsibility for the analysis and final investment committee recommendation. The detailed AI-use and validation record is documented in `docs/validation-and-ai-use.md`.

**Education, not investment advice.** This application is an academic project using course-provided assumptions and illustrative portfolio analysis. Its results and recommendations are for educational purposes only and should not be relied upon for actual investment decisions.

A Streamlit investment management app for the **Meridian Foundation Reserve mandate from Lab 13**. It shows the mandate, compares two transparent baselines with a constrained portfolio, checks each against the mandate, stress-tests the result, uses a point-in-time rate signal, and turns a target into a rebalance worksheet. The committee recommendation is **PILOT**. The app does not place trades.

## The recommendation: PILOT

Choices were adopt, allocate to, rebalance, pilot, or reject. The call is **pilot the process**: use **0% bills / 20% 10-year Treasury / 25% IG bonds / 55% global equity** as a research starting mix, with **no allocation or trade authorization**.

- **Why not reject:** the constrained portfolio passes every checked rule: 6.51% return proxy, 20% eligible reserve, 9.02% modeled 95% one-year loss. Both baselines fail at least one rule. The process does what the mandate asks.
- **Why not adopt or allocate:** the mix clears the 6.5% hurdle by only 0.01 points. Under the proposed 10% loss limit, a one-point cut in the equity estimate **or** 0.50 points of extra cost leaves **no mix that passes**, so the stop condition fires under modest stress. The loss limit is the analyst's proposal, not yet committee policy. Issuer concentration and five-day liquidity are not verified. All return inputs are course training values.
- **What would change the call to adopt:** the committee approves a loss measure and limit (or a lower return target), operations verifies liquidity and issuer exposure, and dated forward-looking estimates replace the training values.

## Videos

| Video | Length | Link |
|---|---|---|
| Video 1 | 2:30 | https://youtu.be/70vq2xUNwTE |
| Video 2 | — | Not yet recorded |
| Video 3 | — | Not yet recorded |

The videos are unlisted and play without signing in. The full submission manifest is in [docs/submission-manifest.md](docs/submission-manifest.md).

## Reach the decision from this folder

Use Python 3.12 or later. Get the code and move into its folder:

```bash
git clone https://github.com/jackschlueter/Project-2-439.git
cd Project-2-439
```

(Without git: on the GitHub page click **Code → Download ZIP**, unzip it, and open a terminal in the unzipped folder.) Then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python verify_project2.py
python -m unittest -v test_portfolio_engine.py test_lab13_mandate.py test_pit_signal.py
```

The verifier prints both baselines and the constrained portfolio with their PASS/FAIL verdicts, every stress result, and the decision. It stops with an error if any saved number fails to reproduce. On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Start the app

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

The first time Streamlit runs, it may ask for an email address in the terminal. It is optional: press **Enter** to skip. Then open the **Local URL** Streamlit prints, usually `http://localhost:8501`. Stop the server with Ctrl+C. No API key, account, or network access is needed after installation.

## Operate it

1. **Mandate register** — objective, universe, benchmark, risk measure, and limits, plus the proposed loss rule.
2. **Decision** — equal weight, the 60/40 benchmark, and the constrained portfolio side by side, each with PASS or FAIL and the rule it failed. The sidebar changes the CPI assumption, cost allowance, reserve floor, equity return estimate, and loss limit (or turns the loss limit off); verdicts update.
3. **Challenge** — one stress table covering estimates, window, costs, constraints, and the signal, and whether the stop condition fires.
4. **Point-in-time signal** — the saved DGS10 ALFRED vintage and its data card.
5. **Rebalance** — dollar changes from current holdings (default: the 60/40 benchmark) and the 25% annual turnover approval trigger.
6. **Method & evidence** — the math and input values. Download the committee memo for a text record of the current settings and call.

## Lab 13 mandate register

| Element | Meridian policy |
|---|---|
| Objective | CPI + 4 percentage points annually **net of costs**, measured over rolling five years. At illustrative CPI 2.5%, the net proxy is 6.5%. |
| Universe | Direct Treasury bills, direct 10-year Treasury notes, an investment-grade bond fund, and a global equity index fund. |
| Benchmark | 60% global equity / 40% U.S. investment-grade bonds. It is a comparison, not a required weight. |
| Risk measure | Modeled annualized volatility from the full covariance matrix, expressed as a **95% one-year loss = 1.645 × volatility − expected return** (normal returns assumed). |
| Limits | At least 3% in eligible direct government holdings; long-only; 8% combined non-exempt issuer cap; committee approval above 25% annual turnover; at least 90% redeemable within five business days. **Proposed:** 95% one-year loss ≤ 10%. Annual rebalancing and a seven-year horizon also apply. |

**The loss limit is an analyst proposal.** IPS statement S9 mentions a 10% calendar-year loss limit but defines neither the measure nor the breach response. This app proposes the measure above. Proposed breach response: the optimizer rejects any mix above the limit; if no mix passes, stop and refer to the committee. Normal returns understate fat-tail losses, so this is a screen, not a guarantee. The sidebar can turn it off.

The optimizer checks long-only weights, full investment, the return proxy, the reserve floor, and the loss limit. The app calculates turnover when current holdings are entered. It **does not certify** issuer concentration, five-day liquidity, or realized rolling returns. Return, volatility, and correlation values are **course-authored training inputs**, not market data.

## Baselines and verdicts (default settings)

| Portfolio | Bills / 10-yr / IG / Equity | Return | Volatility | 95% loss | Reserve | Verdict |
|---|---|---:|---:|---:|---:|---|
| Equal weight | 25 / 25 / 25 / 25 | 5.20% | 5.21% | 3.38% | 50% | **FAIL** — return below 6.5% |
| 60/40 benchmark | 0 / 0 / 40 / 60 | 6.80% | 10.46% | 10.41% | 0% | **FAIL** — reserve below 3%; loss above 10% |
| Constrained portfolio | 0 / 20 / 25 / 55 | 6.51% | 9.44% | 9.02% | 20% | **PASS** — all checked rules |

A PASS is a model-screen result, not full IPS or trade approval.

## Stress run and stop condition

All rows enforce the proposed 10% loss limit and change one thing at a time.

| Stress | Change | Result |
|---|---|---|
| Estimates | Equity mean −1 pp | **STOP — no mix passes.** Without the loss limit: 0 / 10 / 10 / 80, 95% loss 14.75% |
| Estimates | IG–equity correlation 0.25 → 0.50 | 0 / 40 / 0 / 60; volatility 9.73% |
| Window | 60 vs 36 months of SGOV/BND/VT prices as stand-ins for bills/IG/equity | 65/0/35 → 85/0/15: **20-point move** |
| Costs | +0.50 pp cost allowance | **STOP — no mix passes** |
| Constraints | Raise reserve floor in 5% steps | First infeasible floor: **45%** (a breakpoint, not a proposed policy) |
| Signal | 10-year estimate = DGS10 4.98% instead of 4.30% | 5 / 40 / 0 / 55; volatility 8.96%: **20 points** shift into the 10-year sleeve |

**Window stand-ins:** Lab 13 gives no dated returns, so the window row uses the bundled ETF adjusted closes (Sep 2021–Sep 2026; see `mandate-source.md` for sources and download dates). There is no 10-year stand-in, so that row covers three sleeves. ETFs are not Meridian's direct holdings.

**Stop condition:** do not allocate when no mix meets the return, reserve, and loss settings; refer to the committee. It fires today under the equity and cost stresses, so the process stops at **pilot**.

## Point-in-time DGS10 signal

The bundled signal uses the exact **2026-10-31 ALFRED vintage**. Its latest nonmissing observation is **2026-10-29, 4.98%**; the later **2026-11-03 vintage** adds October 30 and November 2 observations. The app checks the vintage-specific CSV column and rejects any observation dated after the selected vintage. It works without live data access. The [data card](dgs10-data-card.md) records source, definition, units, release timing, revisions, fingerprints, and permitted use.

**How it is used:** only as the Signal stress row. It replaces the 10-year sleeve's 4.30% training return with the yield knowable on the decision date. A yield approximates a note's return if held to maturity; it is not a one-year return forecast and never replaces an asset's base-case return. Date-level vintages do not establish intraday availability.

## Files

- `app.py` — Streamlit entry point.
- `lab13_mandate.py` — Meridian mandate register, training values, baselines, verdicts, loss limit, stress run, rebalance, and memo.
- `verify_project2.py` — one-command reproduction of the decision evidence.
- `pit_signal.py`, `dgs10_2026-10-31.csv`, `dgs10_2026-11-03.csv`, `dgs10-data-card.md` — point-in-time rate signal and its source record.
- `portfolio_engine.py` — price reader and rebalance math.
- `prices.csv`, `build_prices.py`, `source/` — ETF adjusted closes used for the window stress, the builder, and the saved raw Yahoo responses.
- `lab13-source.md`, `meridian-ips-source.md` — Lab 13 case and IPS source records.
- `mandate-source.md` — **old young-family draft, not this project's mandate**; kept only for the ETF price sources and download dates.
- `docs/decision-memo.md` — committee decision memo.
- `single_file/` — `app.py` is the whole app in one file, with the data built in. Runs alone: `pip install numpy pandas streamlit`, then `python -m streamlit run app.py`. Regenerate after code changes with `python single_file/build.py`.
- `docs/validation-and-ai-use.md` — validation checks and AI-use log.
- `docs/submission-manifest.md` — Brightspace submission manifest: GitHub links for every location and YouTube links for the videos.
- `records/` — partner cold-run record; Lab 20 pre-run prediction, baseline and after outputs, and run result; the superseded 2026-11-17 locked changed-input record; Edition A draft.
- `reference/` — copies of the earlier Lab 13–15 work this app was built from. Not used by the app.
- `requirements.txt` — Python dependencies.
