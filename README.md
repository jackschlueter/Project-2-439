# Family Portfolio Committee — Python web app

A Streamlit investment management workbench. It opens on the **Meridian Foundation Reserve mandate from Lab 13** and offers the later young-family Project 2 draft as a separate mode. Each mode calculates a qualifying allocation, challenges the estimates, and turns a target into a rebalance worksheet. The committee recommendation is **pilot**. The app does not place trades.

## Project 2: reach the decision from this repository

For the four-fund young-family case, the committee call is **PILOT**: use **45% SGOV / 0% BND / 55% VT / 0% TIP** as a research starting mix, with **no trade authorization**. The mandate is fictional and still needs client approval. The full 60-return sample clears the draft 8.0% net goal by only about 0.01 percentage points; a 36-return window moves 30 points from VT to SGOV, and a one-point cut in VT's historical mean moves 10 points from SGOV to VT. The couple has no approved loss limit. These are the reasons to stop at pilot.

From a fresh clone, use Python 3.12 and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python verify_project2.py
python -m unittest -v test_portfolio_engine.py test_lab13_mandate.py test_pit_signal.py
```

The verifier prints the full-sample allocation, the one-point VT challenge, the last-36-month allocation, and the decision. On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`. Read [the mandate and source record](mandate-source.md) for the draft objective, partner challenge, price URLs and download dates, and the client question. The bundled [prices](prices.csv) can be rebuilt from [saved raw Yahoo chart responses](source/) with `python build_prices.py`; the builder uses adjusted closes and requires 61 aligned months. The [cold-run audit](records/project2_cold_run_2026-11-17.md) records what a repository-only reader could verify and what remains unresolved.

## Start the app

Use Python 3.12 (the version used to verify this app). From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the **Local URL** printed by Streamlit, usually `http://localhost:8501`. On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead of `source .venv/bin/activate`. Stop the server with Ctrl+C. No API key, account, or network data fetch is needed after installation.

## Operate it

1. Keep the sidebar's default **Meridian Foundation Reserve · Lab 13** mode. Open **Mandate register** to see the objective, universe, benchmark, risk measure, and limits. The 60/40 benchmark fails the 3% direct-government reserve floor.
2. Open **Decision** to see equal weight, the 60/40 benchmark, and the constrained portfolio side by side. Each shows a PASS or FAIL for the checked mandate rules and names any failed rule. Change the CPI proxy, cost allowance, reserve floor, or equity return estimate in the sidebar to see the verdicts update.
3. Open **Challenge** for one stress table that changes estimates, window, costs, and the reserve constraint one at a time. Meridian has no dated return series, so its window row is an evidence gap and stops adoption. The constraint row finds the first infeasible reserve floor on the 5% grid; it is a breakpoint, not a proposed policy. Open **Point-in-time signal** for the saved DGS10 ALFRED vintage and data card. Open **Rebalance** for dollar changes and the 25% annual turnover approval trigger.
4. Use the sidebar's **Young family · Project 2** mode for the separate four ETF pilot. Its bundled `prices.csv` loads automatically. It also shows equal weight, a clearly labeled 60/40 VT/BND reference, and the constrained mix side by side with modeled PASS/FAIL reasons. Default settings are an 8.0% net objective, 0.20% illustrative annual costs, and a 10% SGOV floor. Upload a replacement panel only if you have one with documented provenance.
5. In either mode, read the method tab and download the committee memo for a text record of the current settings and call.

The Meridian mode uses fixed **course-authored training inputs**; it does not use ETF prices. In the young-family mode, a replacement panel must have `Month,SGOV,BND,VT,TIP` columns, monthly `YYYY-MM` dates in consecutive oldest-first order, and positive adjusted closes. The upload stays in the browser session. Its default panel has 61 monthly prices from September 2021 through September 2026, giving 60 return intervals.

## Point-in-time DGS10 signal

The bundled signal uses the exact **2026-10-31 ALFRED vintage**. Its latest nonmissing observation is **2026-10-29, 4.98%**; the later **2026-11-03 vintage** adds October 30 and November 2 observations. Select either saved vintage in the app. The app checks the vintage-specific CSV column and rejects any observation dated after the selected vintage. It works without live data access. The [data card](dgs10-data-card.md) records source, definition, units, release timing, revisions, fingerprints, and permitted use. Date-level vintages do not establish intraday availability. DGS10 is a yield level, not an asset total return.

## Lab 13 mandate register

| Element | Meridian policy |
|---|---|
| Objective | CPI + 4 percentage points annually **net of costs**, measured over rolling five years. At illustrative CPI 2.5%, the net proxy is 6.5%. |
| Universe | Direct Treasury bills, direct 10-year Treasury notes, an investment-grade bond fund, and a global equity index fund. |
| Benchmark | 60% global equity / 40% U.S. investment-grade bonds. It is a comparison, not a required weight; it fails the 3% reserve floor. |
| Risk measure | Modeled annualized portfolio volatility from the full covariance matrix. No approved volatility cap. The 10% calendar-year loss statement lacks a defined measure and breach response. |
| Limits | At least 3% in eligible direct government holdings; long-only; 8% combined non-exempt issuer cap; committee approval above 25% annual turnover; at least 90% redeemable within five business days. Annual rebalancing and seven-year planning horizon also apply. |

The optimizer directly checks long-only weights, full investment, the expected-return proxy, and the reserve floor. The app calculates turnover when current holdings are entered. It **does not certify** issuer concentration, five-day liquidity, realized rolling returns, or the unresolved loss rule. SGOV fund shares in the Project 2 mode do not automatically count as Meridian's eligible direct holdings. The Meridian default reproduces **0/20/25/55**, 6.51% return and 9.44% volatility from the course case.

Default modeled mandate screen: **equal weight FAILS** the 6.5% return proxy (5.20%); the **60/40 benchmark FAILS** the 3% eligible-reserve floor (0%); the **constrained portfolio PASSES** the checked return, reserve, and weight rules (6.51% return, 20% eligible reserve). A PASS is a model-screen result, not full IPS or trade approval.

**Stop condition:** do not allocate when no mix meets the currently approved return and reserve settings or when a required window comparison lacks valid dated data. Meridian has no such time series in Lab 13, and its 10% calendar-year loss rule is undefined, so the process stops at **pilot**. In the family mode, an unapproved loss limit and SGOV reserve definition likewise prevent adoption. Hypothetical breakpoint stresses show when a tighter reserve floor would make the model infeasible; they do not change the current policy.

## Decision and limitations

In the **young-family mode**, the default full-sample result is **45% SGOV / 0% BND / 55% VT / 0% TIP**. Cutting VT's annual mean by one point changes it to **35/0/65/0**; using the last 36 months changes it to **75/0/25/0**. These are least-volatility answers on a 5% long-only grid that clear an 8.2% gross hurdle. Historical means and covariance are estimates, not forward forecasts. The family has not approved a loss limit or the SGOV reserve definition. Before adoption, the client and committee must review those terms, forward returns, costs, taxes, liquidity, and rebalancing.

The saved adjusted closes were downloaded from Yahoo Finance chart `adjclose` responses on October 20 and 22, 2026. The preserved source record is `mandate-source.md` and the original raw responses are in the course lab folder. The app does not use a live feed or claim a point-in-time backtest.

## Files

- `app.py` — Streamlit interface and memo export.
- `lab13_mandate.py` — Meridian mandate register, training values, benchmark, limits, and decision view.
- `pit_signal.py`, `dgs10_2026-10-31.csv`, `dgs10_2026-11-03.csv`, and `dgs10-data-card.md` — point-in-time rate signal and its source record.
- `portfolio_engine.py` — data validation, annualized estimates, 5% grid search, and rebalance math.
- `prices.csv` — bundled monthly adjusted-close panel.
- `requirements.txt` — Python dependencies.
- `lab13-source.md` and `meridian-ips-source.md` — Lab 13 case and IPS source records.
- `mandate-source.md` — later young-family course mandate.

## Verify the known answers

```bash
python -m unittest -v test_portfolio_engine.py test_lab13_mandate.py test_pit_signal.py
```
