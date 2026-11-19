"""Meridian Lab 13 mandate, course inputs, and Streamlit decision view."""

from itertools import product
from math import ceil, sqrt

import numpy as np
import pandas as pd
import streamlit as st

from pathlib import Path

from portfolio_engine import read_prices, rebalance
from pit_signal import VINTAGES, read_vintage, render_signal

ROOT = Path(__file__).resolve().parent
Z95 = 1.645  # one-sided 95% normal quantile
LOSS_LIMIT = .10  # analyst proposal for IPS S9; needs committee approval
NAMES = ("Treasury bills", "Treasury 10-year", "IG bonds", "Global equity")
MEANS = np.array((.035, .043, .050, .080))
VOL = np.array((.005, .070, .060, .160))
CORR = np.array(((1, .10, .05, 0), (.10, 1, .80, -.10),
                 (.05, .80, 1, .25), (0, -.10, .25, 1)))
ELIGIBLE = np.array((1, 1, 0, 0))
BENCHMARK = (0, 0, .40, .60)
EQUAL_WEIGHT = (.25, .25, .25, .25)


def covariance(correlation=CORR):
    return np.outer(VOL, VOL) * correlation


def stats(weights, means=MEANS, correlation=CORR):
    weights = np.asarray(weights, dtype=float)
    return (float(weights @ means), sqrt(float(weights @ covariance(correlation) @ weights)),
            float(weights @ ELIGIBLE))


def loss95(gross_return, volatility):
    """One-year loss exceeded about 5% of the time, assuming normal returns."""
    return Z95 * volatility - gross_return


def search(target=.065, reserve_floor=.03, equity_adjustment=0., correlation=CORR,
           loss_limit=None, ten_year_return=None):
    """Lowest-volatility qualifying long-only 5% mix; returns weights and stats."""
    means = MEANS.copy()
    means[3] += equity_adjustment
    if ten_year_return is not None:
        means[1] = ten_year_return
    best = None
    for a, b, c in product(range(21), repeat=3):
        d = 20 - a - b - c
        if d < 0:
            continue
        weights = (a / 20, b / 20, c / 20, d / 20)
        ret, vol, reserve = stats(weights, means, correlation)
        if ret + 1e-12 < target or reserve + 1e-12 < reserve_floor:
            continue
        if loss_limit is not None and loss95(ret, vol) > loss_limit + 1e-12:
            continue
        if best is None or vol < best[2]:
            best = (weights, ret, vol, reserve)
    return best


def signal_yield(vintage="2026-10-31"):
    """Latest DGS10 observation knowable in the saved ALFRED vintage: (date, percent)."""
    return read_vintage(VINTAGES[vintage].read_text(encoding="utf-8-sig"), vintage)[-1]


def proxy_window(months=None, target=.065, reserve_floor=.03, loss_limit=None):
    """Window stress on ETF stand-ins: SGOV for bills, BND for IG bonds, VT for equity.

    Returns (bills, IG, equity) weights, gross return, volatility; no 10-year proxy exists.
    """
    _, prices = read_prices(ROOT / "prices.csv")
    monthly = (prices[1:] / prices[:-1] - 1)[:, :3]
    if months:
        monthly = monthly[-months:]
    mean = monthly.mean(axis=0) * 12
    cov = np.cov(monthly, rowvar=False) * 12
    best = None
    for a in range(21):
        for b in range(21 - a):
            weights = np.array((a, b, 20 - a - b)) / 20
            ret, vol = float(weights @ mean), sqrt(float(weights @ cov @ weights))
            if ret + 1e-12 < target or weights[0] + 1e-12 < reserve_floor:
                continue
            if loss_limit is not None and loss95(ret, vol) > loss_limit + 1e-12:
                continue
            if best is None or vol < best[2]:
                best = (tuple(float(w) for w in weights), ret, vol)
    return best


def weight_text(weights):
    return " / ".join(f"{name} {weight:.0%}" for name, weight in zip(NAMES, weights))


def mandate_verdict(weights, gross_return, reserve, gross_hurdle, reserve_floor,
                    volatility=None, loss_limit=None):
    """Screen the return proxy, reserve, weight rules, and optional loss limit."""
    if weights is None:
        return "FAIL", ("No qualifying 5% grid mix",)
    failures = []
    if any(weight < 0 for weight in weights) or abs(sum(weights) - 1) > 1e-9:
        failures.append("Long-only weights must total 100%")
    if gross_return + 1e-12 < gross_hurdle:
        failures.append(f"Return proxy {gross_return:.2%} below {gross_hurdle:.2%} gross hurdle")
    if reserve + 1e-12 < reserve_floor:
        failures.append(f"Eligible reserve {reserve:.0%} below {reserve_floor:.0%} floor")
    checked = "return, reserve, and weight rules"
    if volatility is not None and loss_limit is not None:
        checked = "return, reserve, weight, and 95% loss rules"
        loss = loss95(gross_return, volatility)
        if loss > loss_limit + 1e-12:
            failures.append(f"95% one-year loss {loss:.2%} above {loss_limit:.0%} limit")
    return ("FAIL", tuple(failures)) if failures else ("PASS", (f"Checked {checked}",))


def render():
    with st.sidebar:
        st.header("Meridian · Lab 13")
        st.caption("Course-authored training estimates; not market data")
        cpi = st.number_input("Illustrative CPI assumption (%)", 0., 20., 2.5, .1, key="meridian_cpi")
        net_spread = st.number_input("Real return spread above CPI (pp)", 0., 20., 4.0, .1, key="meridian_spread")
        costs = st.number_input("Cost allowance (%)", 0., 5., 0.0, .05, key="meridian_costs",
                                help="Lab 13 supplies no cost estimate; zero reproduces its 6.5% proxy.")
        reserve_floor = st.number_input("Eligible reserve floor (%)", 0., 100., 3.0, .5, key="meridian_reserve")
        equity_edit = st.slider("Equity return estimate change (pp)", -5., 3., 0., .25,
                                key="meridian_equity_edit")
        st.divider()
        use_loss = st.checkbox("Enforce proposed 95% loss limit", value=True, key="meridian_use_loss",
                               help="Analyst proposal for IPS S9. Uncheck to see the screen without it.")
        loss_pct = st.number_input("Max one-year loss at 95% (%)", 1., 50., 100 * LOSS_LIMIT, .5,
                                   key="meridian_loss", disabled=not use_loss)
    hurdle = (cpi + net_spread + costs) / 100
    loss_limit = loss_pct / 100 if use_loss else None
    selected = search(hurdle, reserve_floor / 100, equity_edit / 100, loss_limit=loss_limit)
    edited_means = MEANS.copy()
    edited_means[3] += equity_edit / 100
    benchmark = stats(BENCHMARK, edited_means)
    equal_weight = stats(EQUAL_WEIGHT, edited_means)
    base = search()
    stress = search(equity_adjustment=-.01)
    raised_corr = CORR.copy()
    raised_corr[2, 3] = raised_corr[3, 2] = .50
    corr_case = search(correlation=raised_corr)

    st.caption("LAB 13 MANDATE  /  MERIDIAN FOUNDATION RESERVE  /  COURSE CASE")
    st.title("Meridian Portfolio Committee")
    st.write("The mandate seeks **CPI + 4 percentage points annually, net of costs, over rolling five-year periods**. The course's 2.5% CPI assumption produces a **6.5% net objective proxy**. This screen uses the Lab 13 training values; it cannot verify a future rolling return.")
    st.markdown('<div class="callout"><strong>Recommendation: PILOT the process.</strong> The constrained portfolio passes every checked rule, but only by 0.01 points of return, and a one-point equity cut or 0.50 points of extra cost leaves no mix that meets the proposed loss limit. The loss limit is not yet approved and liquidity is unverified. Do not allocate from this model alone.</div>', unsafe_allow_html=True)

    mandate, decision, scenarios, signal, trades, method = st.tabs(("Mandate register", "Decision", "Challenge", "Point-in-time signal", "Rebalance", "Method & evidence"))
    with mandate:
        st.subheader("The five mandate elements")
        register = pd.DataFrame([
            ("Objective", "CPI + 4 pp net per year, rolling five years; 6.5% proxy with 2.5% CPI", "Target; not a forecast"),
            ("Universe", "Direct Treasury bills, direct 10-year Treasury notes, IG bond fund, global equity index fund", "Four course sleeves"),
            ("Benchmark", "60% global equity / 40% IG bonds", "Comparison only; fails 3% reserve floor"),
            ("Risk measure", "Annualized volatility from the full covariance matrix, turned into a 95% one-year loss: 1.645 × volatility − expected return", "Proposed limit: loss ≤ 10% (S9); needs committee approval"),
            ("Limits", "≥3% eligible direct government reserve; long-only; 8% non-exempt issuer cap; >25% annual turnover requires approval; ≥90% liquid within five business days", "Only weights and reserve are checked here"),
        ], columns=("Element", "Policy / measure", "Status"))
        st.dataframe(register, hide_index=True, width="stretch")
        st.markdown("**Proposed loss rule:** the IPS mentions a 10% calendar-year loss limit but does not define the measure or breach response (S9). This app proposes a measure: the one-year loss exceeded only 5% of the time if returns are normal, **1.645 × volatility − expected return ≤ 10%**. Proposed breach response: if a target mix breaches it, the optimizer rejects that mix; if no mix passes, stop and refer to the committee. Normal returns understate fat-tail losses, so this is a modeled screen, not a guarantee. It stays a proposal until the committee approves it. Annual rebalancing and a seven-year planning horizon are additional policy terms.")
        st.caption("Treasury bills and direct 10-year notes count toward the 3% reserve in this course case. SGOV fund shares do not automatically satisfy Meridian's direct-security rule.")
        st.subheader("Benchmark check")
        a, b, c, d = st.columns(4)
        a.metric("Expected gross return", f"{benchmark[0]:.2%}")
        b.metric("Modeled volatility", f"{benchmark[1]:.2%}")
        c.metric("Eligible reserve", f"{benchmark[2]:.0%}", help="Benchmark holds no direct bills or 10-year notes")
        d.metric("95% one-year loss", f"{loss95(benchmark[0], benchmark[1]):.2%}")
        st.warning("Benchmark: FAIL on the 3% reserve floor, and above the proposed 10% loss limit. The 60/40 benchmark is a performance comparison, not a required allocation.")
    with decision:
        st.subheader("Two baselines beside the constrained portfolio")
        comparisons = (("Equal weight", EQUAL_WEIGHT, equal_weight),
                       ("60/40 benchmark", BENCHMARK, benchmark),
                       ("Constrained portfolio", selected[0] if selected else None,
                        selected[1:] if selected else None))
        for column, (name, weights, figures) in zip(st.columns(3), comparisons):
            with column.container(border=True):
                st.markdown(f"**{name}**")
                if figures is None:
                    verdict, reasons = mandate_verdict(None, 0, 0, hurdle, reserve_floor / 100)
                    st.write("No qualifying allocation")
                    st.error(f"{verdict} · {reasons[0]}")
                else:
                    gross, vol, reserve = figures
                    verdict, reasons = mandate_verdict(weights, gross, reserve, hurdle,
                                                        reserve_floor / 100, vol, loss_limit)
                    st.write(weight_text(weights))
                    st.write(f"Net return proxy **{gross - costs / 100:.2%}** · volatility **{vol:.2%}** · 95% loss **{loss95(gross, vol):.2%}** · eligible reserve **{reserve:.0%}**")
                    if verdict == "PASS":
                        st.success("PASS · " + reasons[0].lower())
                    else:
                        st.error("FAIL · " + "; ".join(reasons))
        st.caption("Verdicts cover the modeled return proxy, eligible-reserve floor, long-only full investment, and (when enforced) the proposed 95% loss limit. Issuer concentration, five-day liquidity, and realized returns still need evidence.")
        st.warning("Process stop condition: do not allocate if no mix meets the return, reserve, and loss settings. Under the proposed loss limit, a one-point equity cut or 0.50 points of extra cost already triggers this stop (see Challenge).")
        st.subheader("Lowest-volatility qualifying 5% grid mix")
        if selected:
            weights, gross, vol, reserve = selected
            st.write(f"**{weight_text(weights)}**")
            a, b, c, d, e = st.columns(5)
            a.metric("Expected net proxy", f"{gross - costs/100:.2%}")
            b.metric("Modeled volatility", f"{vol:.2%}")
            c.metric("95% one-year loss", f"{loss95(gross, vol):.2%}")
            d.metric("Eligible reserve", f"{reserve:.0%}")
            e.metric("Gross hurdle margin", f"{100*(gross-hurdle):.2f} pp")
            st.bar_chart(pd.DataFrame({"Weight": weights}, index=NAMES), horizontal=True,
                         color="#315c76", height=220)
        else:
            st.warning("STOP · No 5% grid mix clears the return, reserve, and loss settings. Do not force an allocation; refer to the committee.")
        st.caption("The optimizer enforces long-only, full investment, the direct-government reserve, and (when enforced) the proposed loss limit. It does not prove the issuer, liquidity, or turnover rules.")
        st.markdown("### Decision gates")
        st.checkbox("Committee approves the proposed 95% loss measure, 10% limit, and breach response")
        st.checkbox("Operations verifies five-day liquidity and issuer exposure")
        st.checkbox("Committee reviews costs and forward return assumptions")
        st.checkbox("Client and committee authorize any actual allocation")
        st.caption("Checkmarks are session notes. They do not change the pilot call or authorize trading.")
    with scenarios:
        st.subheader("Known-answer comparisons")
        rows = []
        for label, mix in (("Base training case", base), ("Equity return −1 pp", stress),
                           ("IG–equity correlation 0.50", corr_case)):
            rows.append({"Case": label, "Weights": weight_text(mix[0]),
                         "Return": f"{mix[1]:.2%}", "Volatility": f"{mix[2]:.2%}",
                         "Eligible reserve": f"{mix[3]:.0%}"})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.write("The base search returns **0/20/25/55**, 6.51% expected return and 9.44% volatility. Reducing equity's return estimate one point moves the largest weight 25 points and raises modeled volatility to 12.94%. These are course inputs, not market forecasts.")
        st.subheader("Stress run · current sidebar settings")
        rf = reserve_floor / 100
        estimate_case = search(hurdle, rf, (equity_edit - 1) / 100, loss_limit=loss_limit)
        cost_case = search(hurdle + .005, rf, equity_edit / 100, loss_limit=loss_limit)
        signal_date, signal_pct = signal_yield()
        signal_case = search(hurdle, rf, equity_edit / 100, loss_limit=loss_limit,
                             ten_year_return=signal_pct / 100)
        first_break = next((floor_pct for floor_pct in range(max(5, ceil(reserve_floor / 5) * 5), 101, 5)
                            if floor_pct > reserve_floor and
                            search(hurdle, floor_pct / 100, equity_edit / 100, loss_limit=loss_limit) is None), None)
        window_all = proxy_window(None, hurdle, rf, loss_limit)
        window_36 = proxy_window(36, hurdle, rf, loss_limit)

        def stress_row(case, change, answer):
            return {"Case": case, "Change from current": change,
                    "Allocation": weight_text(answer[0]) if answer else "No qualifying mix",
                    "Gross return": f"{answer[1]:.2%}" if answer else "—",
                    "Volatility": f"{answer[2]:.2%}" if answer else "—",
                    "95% loss": f"{loss95(answer[1], answer[2]):.2%}" if answer else "—",
                    "Screen": "FEASIBLE" if answer else "STOP · no mix"}

        def proxy_row(change, answer):
            return {"Case": "Window (ETF stand-ins)", "Change from current": change,
                    "Allocation": (" / ".join(f"{n} {w:.0%}" for n, w in
                                   zip(("SGOV≈bills", "BND≈IG", "VT≈equity"), answer[0]))
                                   if answer else "No qualifying mix"),
                    "Gross return": f"{answer[1]:.2%}" if answer else "—",
                    "Volatility": f"{answer[2]:.2%}" if answer else "—",
                    "95% loss": f"{loss95(answer[1], answer[2]):.2%}" if answer else "—",
                    "Screen": "FEASIBLE" if answer else "STOP · no mix"}

        stress_rows = [stress_row("Base", "Current settings", selected),
                       stress_row("Estimate", "Equity mean −1 pp", estimate_case),
                       proxy_row("All 60 months, Oct 2021–Sep 2026", window_all),
                       proxy_row("Last 36 months, Oct 2023–Sep 2026", window_36),
                       stress_row("Costs", "Cost allowance +0.50 pp", cost_case),
                       stress_row("Constraint",
                                  f"First infeasible reserve floor: {first_break}%" if first_break
                                  else "No infeasible reserve floor found",
                                  None if first_break else selected),
                       stress_row("Signal", f"10-year estimate = DGS10 {signal_pct:.2f}% ({signal_date})",
                                  signal_case)]
        st.dataframe(pd.DataFrame(stress_rows), hide_index=True, width="stretch")
        if window_all and window_36:
            move = 100 * max(abs(a - b) for a, b in zip(window_all[0], window_36[0]))
            st.write(f"**Window:** switching the stand-in history from 60 to 36 months moves the largest weight **{move:.0f} points**. Lab 13 gives no dated sleeve returns, so this uses the bundled SGOV/BND/VT adjusted closes as stand-ins; the 10-year sleeve has no stand-in and is left out of this row.")
        st.write(f"**Signal:** the training 10-year return is 4.30%. The DGS10 yield knowable in the 2026-10-31 ALFRED vintage was **{signal_pct:.2f}%**. A yield is a rough guide to a 10-year note's return if held to maturity, not a forecast of its one-year return.")
        if estimate_case is None or cost_case is None or selected is None:
            st.error("STOP triggered: at least one modest stress leaves no mix that meets the return, reserve, and loss settings. Do not allocate; the process stays at pilot until the committee resets the target, the loss limit, or the estimates.")
        else:
            st.warning("No stress row stops the process at the current settings. Adoption still needs committee approval of the loss limit and verified liquidity.")
        st.caption("The constraint row identifies a 5% grid breakpoint, not a proposed change to the IPS. Each stress changes one input family at a time; other settings stay fixed. ETF stand-ins are not Meridian's direct holdings.")
    with signal:
        render_signal()
    with trades:
        st.subheader("Review turnover before an approved rebalance")
        value = st.number_input("Reserve value ($)", min_value=1., value=100000000., step=1000000., key="meridian_value")
        columns = st.columns(4)
        current = tuple(col.number_input(f"Current {name} (%)", min_value=0., max_value=100.,
            value=default, step=5., key=f"meridian_current_{i}") / 100
            for i, (col, name, default) in enumerate(zip(columns, NAMES, (0., 0., 40., 60.))))
        st.caption("Default current holdings are the 60/40 benchmark mix, as if the reserve were moving from its benchmark to the target.")
        if selected:
            try:
                changes, turnover = rebalance(current, selected[0], value)
            except ValueError as exc:
                st.error(str(exc))
            else:
                table = pd.DataFrame({"Sleeve": NAMES, "Current": [f"{x:.0%}" for x in current],
                    "Target": [f"{x:.0%}" for x in selected[0]],
                    "Estimated change ($)": [round(x, 2) for x in changes]})
                st.dataframe(table, hide_index=True, width="stretch")
                st.metric("One-way turnover", f"{turnover:.1%}")
                if turnover > .25:
                    st.warning("Annual turnover exceeds 25%; committee approval is required by the IPS.")
                st.download_button("Download rebalance CSV", table.to_csv(index=False).encode(),
                    file_name="meridian_rebalance.csv", mime="text/csv")
        else:
            st.info("A qualifying target is needed before calculating changes.")
    with method:
        st.subheader("What the model checks")
        st.write("Expected return is the weight-averaged course return. Variance includes every pairwise covariance term: $w^T\\Sigma w$. Volatility is its square root. The 95% one-year loss is $1.645\\sigma - \\mu$, assuming normal returns. The search tests long-only weights in 5 percentage point steps and keeps the lowest-volatility mix meeting the gross return proxy, the eligible-reserve floor, and (when enforced) the loss limit.")
        st.dataframe(pd.DataFrame({"Sleeve": NAMES, "Training return": [f"{x:.1%}" for x in MEANS],
            "Training volatility": [f"{x:.1%}" for x in VOL],
            "Reserve eligible": ["Yes" if x else "No" for x in ELIGIBLE]}),
            hide_index=True, width="stretch")
        st.caption("Source: local Lab 13 Meridian portfolio case and Meridian IPS. Values are course-authored training inputs, not observed prices or investable return forecasts.")

    def verdict_text(weights, figures):
        if weights is None or figures is None:
            return "FAIL (no qualifying mix)"
        gross, vol, reserve = figures
        verdict, reasons = mandate_verdict(weights, gross, reserve, hurdle, rf, vol, loss_limit)
        return f"{verdict} ({'; '.join(reasons)})"

    def mix_or_stop(answer):
        return weight_text(answer[0]) if answer else "STOP, no mix"

    loss_text = f"95% one-year loss <= {loss_limit:.0%} (analyst proposal)" if loss_limit else "not enforced"
    memo = f"""MERIDIAN FOUNDATION RESERVE — COMMITTEE MEMO
Recommendation: PILOT the process; no allocation authorization.
Objective: CPI + 4 pp annually net over rolling five years; current proxy {cpi+net_spread:.2f}% net.
Universe: direct bills, direct 10-year Treasuries, IG bond fund, global equity index fund.
Benchmark: 60% global equity / 40% IG bonds; return {benchmark[0]:.2%}, volatility {benchmark[1]:.2%}, 95% loss {loss95(*benchmark[:2]):.2%}, eligible reserve {benchmark[2]:.0%}.
Risk measure: modeled volatility, expressed as 95% one-year loss (1.645 x volatility - return). Limit: {loss_text}.
Limits: >=3% direct-government reserve, long-only, 8% non-exempt issuer cap, >25% turnover approval, >=90% liquid within five business days.
Equal weight: {verdict_text(EQUAL_WEIGHT, equal_weight)}.
60/40 benchmark: {verdict_text(BENCHMARK, benchmark)}.
Constrained portfolio: {mix_or_stop(selected)}; {verdict_text(selected[0] if selected else None, selected[1:] if selected else None)}.
Stress run: equity -1 pp -> {mix_or_stop(estimate_case)}; costs +0.50 pp -> {mix_or_stop(cost_case)}; first infeasible reserve floor -> {first_break if first_break else 'not found'}%; 10-year estimate at DGS10 {signal_pct:.2f}% -> {mix_or_stop(signal_case)}.
Window (SGOV/BND/VT stand-ins): 60 months -> {' / '.join(f'{w:.0%}' for w in window_all[0]) if window_all else 'no mix'}; 36 months -> {' / '.join(f'{w:.0%}' for w in window_36[0]) if window_36 else 'no mix'}.
Stop condition: no mix meets the return, reserve, and loss settings; do not allocate and refer to the committee.
Unverified gates: committee approval of the loss limit, issuer exposure, liquidity, forward estimates, costs and trading authorization.
"""
    st.download_button("Download Meridian committee memo", memo,
                       file_name="meridian_committee_memo.txt", mime="text/plain")
