# In-class portfolio labs

Start with [Lab 13 - Meridian Portfolios.md](Lab%2013%20-%20Meridian%20Portfolios.md) for the course-input calculations, mandate check, validation, and discussion answers.

[Lab 14 - Preparation and Data.md](Lab%2014%20-%20Preparation%20and%20Data.md) records the reading, Streamlit check, fund universe, and monthly adjusted-price sources.

Runnable files:

- `portfolio.py` — preserves the Meridian baseline printout, estimates inputs from monthly prices, and searches long-only mixes in 5-point steps.
- `app.py` — edits expected returns and reserve eligibility, compares the current grid answer with the loaded-input answer, and accepts a monthly-price upload.
- `Project 2 mandate.md` — draft fictional scholarship-client mandate with objective, hard constraints, and one client question.
- `mandate.py` — checks Meridian candidates A–E, including the client's benchmark as E.
- `prices.csv` — September 2021–September 2026 monthly adjusted closes for SGOV, BND, and VT.
- `build_prices.py` and `source/` — reproduce `prices.csv` from the saved download responses.

Run `python3 portfolio.py`, `python3 mandate.py`, and `python3 build_prices.py` from this folder. Submit only the files your instructor requests.

Start the app with `streamlit run app.py --browser.gatherUsageStats false` from this folder. If your shell cannot find Streamlit, use `/Users/jakes/.local/bin/streamlit run app.py --browser.gatherUsageStats false`. It opens on Meridian; upload `prices.csv` to use the three-fund universe. The last-36 switch changes the estimates, while the right-hand comparison stays on all months under the same objective and reserve rule. Edit any return box or reserve tick box to see the grid answer change.

With the course inputs, Meridian's 6.5% target and 3% reserve floor yield a **5-point grid answer** of **0% bills / 20% 10-year / 25% IG / 55% equity**, with **6.51% expected return** and **9.44% modeled volatility**. The reserve share is 20%. An unrestricted continuous solution can differ; the app reports the required 5-point search result. If no grid mix qualifies, it displays “no mix meets the objective.”

The Project 2 draft uses **three funds: SGOV, BND, and VT**. Its 5.5% net target plus a 0.20% illustrative cost allowance means entering **5.7% gross** in the app; its draft reserve rule requires **4% in SGOV**. Five years of adjusted prices yield a grid answer of **75% SGOV / 0% BND / 25% VT**, with **3.82% modeled volatility**. Lowering VT's historical return estimate by one percentage point shifts the answer to **70% / 0% / 30%** and **4.55% volatility**. The original mix then earns **5.31% net**, below the unchanged target.

Meridian uses course training assumptions. Project 2 uses annualized historical estimates from 60 monthly returns, not forecasts. Expected returns are one-period proxies for rolling five-year objectives. This app models the reserve rule but does not certify the mandates' remaining rules. The Project 2 client and policy are proposed, not supplied client facts.
