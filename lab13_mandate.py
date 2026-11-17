"""Meridian Lab 13 mandate, course inputs, and Streamlit decision view."""

from itertools import product
from math import ceil, sqrt

import numpy as np
import pandas as pd
import streamlit as st

from portfolio_engine import rebalance
from pit_signal import render_signal

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


def search(target=.065, reserve_floor=.03, equity_adjustment=0., correlation=CORR):
    """Lowest-volatility qualifying long-only 5% mix; returns weights and stats."""
    means = MEANS.copy()
    means[3] += equity_adjustment
    best = None
    for a, b, c in product(range(21), repeat=3):
        d = 20 - a - b - c
        if d < 0:
            continue
        weights = (a / 20, b / 20, c / 20, d / 20)
        ret, vol, reserve = stats(weights, means, correlation)
        if ret + 1e-12 < target or reserve + 1e-12 < reserve_floor:
            continue
        if best is None or vol < best[2]:
            best = (weights, ret, vol, reserve)
    return best


def weight_text(weights):
    return " / ".join(f"{name} {weight:.0%}" for name, weight in zip(NAMES, weights))


def mandate_verdict(weights, gross_return, reserve, gross_hurdle, reserve_floor):
    """Screen only the return proxy, reserve, and portfolio weight rules."""
    if weights is None:
        return "FAIL", ("No qualifying 5% grid mix",)
    failures = []
    if any(weight < 0 for weight in weights) or abs(sum(weights) - 1) > 1e-9:
        failures.append("Long-only weights must total 100%")
    if gross_return + 1e-12 < gross_hurdle:
        failures.append(f"Return proxy {gross_return:.2%} below {gross_hurdle:.2%} gross hurdle")
    if reserve + 1e-12 < reserve_floor:
        failures.append(f"Eligible reserve {reserve:.0%} below {reserve_floor:.0%} floor")
    return ("FAIL", tuple(failures)) if failures else ("PASS", ("Checked return, reserve, and weight rules",))


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
    hurdle = (cpi + net_spread + costs) / 100
    selected = search(hurdle, reserve_floor / 100, equity_edit / 100)
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
    st.markdown('<div class="callout"><strong>Recommendation: PILOT the process.</strong> The benchmark fails the eligible-reserve floor, and key liquidity and loss-limit evidence is unresolved. Do not allocate from this model alone.</div>', unsafe_allow_html=True)

    mandate, decision, scenarios, signal, trades, method = st.tabs(("Mandate register", "Decision", "Challenge", "Point-in-time signal", "Rebalance", "Method & evidence"))
    with mandate:
        st.subheader("The five mandate elements")
        register = pd.DataFrame([
            ("Objective", "CPI + 4 pp net per year, rolling five years; 6.5% proxy with 2.5% CPI", "Target; not a forecast"),
            ("Universe", "Direct Treasury bills, direct 10-year Treasury notes, IG bond fund, global equity index fund", "Four course sleeves"),
            ("Benchmark", "60% global equity / 40% IG bonds", "Comparison only; fails 3% reserve floor"),
            ("Risk measure", "Annualized portfolio volatility from full covariance matrix", "Modeled; no approved volatility cap"),
            ("Limits", "≥3% eligible direct government reserve; long-only; 8% non-exempt issuer cap; >25% annual turnover requires approval; ≥90% liquid within five business days", "Only weights and reserve are checked here"),
        ], columns=("Element", "Policy / measure", "Status"))
        st.dataframe(register, hide_index=True, width="stretch")
        st.markdown("**Unresolved loss rule:** the IPS mentions a 10% calendar-year limit but does not define the loss measure or breach response. It is **not** an enforceable model cap. Annual rebalancing and a seven-year planning horizon are additional policy terms.")
        st.caption("Treasury bills and direct 10-year notes count toward the 3% reserve in this course case. SGOV fund shares do not automatically satisfy Meridian's direct-security rule.")
        st.subheader("Benchmark check")
        a, b, c = st.columns(3)
        a.metric("Expected gross return", f"{benchmark[0]:.2%}")
        b.metric("Modeled volatility", f"{benchmark[1]:.2%}")
        c.metric("Eligible reserve", f"{benchmark[2]:.0%}", help="Benchmark holds no direct bills or 10-year notes")
        st.warning("Benchmark reserve: FAIL. The 60/40 benchmark is a performance comparison, not a required allocation.")
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
                                                        reserve_floor / 100)
                    st.write(weight_text(weights))
                    st.write(f"Net return proxy **{gross - costs / 100:.2%}** · volatility **{vol:.2%}** · eligible reserve **{reserve:.0%}**")
                    if verdict == "PASS":
                        st.success("PASS · checked return, reserve, and weight rules")
                    else:
                        st.error("FAIL · " + "; ".join(reasons))
        st.caption("Verdicts cover the modeled return proxy, eligible-reserve floor, and long-only full investment. Issuer concentration, five-day liquidity, realized returns, and the unresolved loss rule still need evidence.")
        st.warning("Process stop condition: do not allocate if the approved return and reserve settings have no qualifying mix. Adoption is also stopped until a valid window stress and an enforceable loss rule exist.")
        st.subheader("Lowest-volatility qualifying 5% grid mix")
        if selected:
            weights, gross, vol, reserve = selected
            st.write(f"**{weight_text(weights)}**")
            a, b, c, d = st.columns(4)
            a.metric("Expected net proxy", f"{gross - costs/100:.2%}")
            b.metric("Modeled volatility", f"{vol:.2%}")
            c.metric("Eligible reserve", f"{reserve:.0%}")
            d.metric("Gross hurdle margin", f"{100*(gross-hurdle):.2f} pp")
            st.bar_chart(pd.DataFrame({"Weight": weights}, index=NAMES), horizontal=True,
                         color="#315c76", height=220)
        else:
            st.warning("No 5% grid mix clears the return and reserve floors. Do not force an allocation.")
        st.caption("The optimizer enforces long-only, full investment, and the direct-government reserve. It does not prove the issuer, liquidity, turnover, or annual-loss rules.")
        st.markdown("### Decision gates")
        st.checkbox("Committee defines the calendar-year loss measure and breach response")
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
        st.subheader("Four-way stress run · current sidebar settings")
        estimate_case = search(hurdle, reserve_floor / 100, (equity_edit - 1) / 100)
        cost_case = search(hurdle + .005, reserve_floor / 100, equity_edit / 100)
        first_break = next((floor_pct for floor_pct in range(max(5, ceil(reserve_floor / 5) * 5), 101, 5)
                            if floor_pct > reserve_floor and
                            search(hurdle, floor_pct / 100, equity_edit / 100) is None), None)

        def stress_row(case, change, answer):
            return {"Case": case, "Change from current": change,
                    "Allocation": weight_text(answer[0]) if answer else "No qualifying mix",
                    "Gross return": f"{answer[1]:.2%}" if answer else "—",
                    "Volatility": f"{answer[2]:.2%}" if answer else "—",
                    "Screen": "FEASIBLE" if answer else "STOP · no mix"}

        stress_rows = [stress_row("Base", "Current settings", selected),
                       stress_row("Estimate", "Equity mean −1 pp", estimate_case),
                       {"Case": "Window", "Change from current": "Shorter historical window",
                        "Allocation": "Not available: Lab 13 gives no dated returns",
                        "Gross return": "—", "Volatility": "—", "Screen": "STOP · evidence gap"},
                       stress_row("Costs", "Cost allowance +0.50 pp", cost_case)]
        if first_break is not None:
            stress_rows.append(stress_row("Constraint", f"First infeasible reserve floor: {first_break}%",
                                          None))
        else:
            stress_rows.append(stress_row("Constraint", "No infeasible reserve floor found", selected))
        st.dataframe(pd.DataFrame(stress_rows), hide_index=True, width="stretch")
        st.error("STOP for adoption: the Lab 13 inputs cannot support a window stress, and the calendar-year loss rule is undefined. A live allocation also stops whenever the currently approved return and reserve settings have no qualifying mix.")
        st.caption("The constraint row identifies a 5% grid breakpoint, not a proposed change to the IPS. The four stresses change one input family at a time; the return target and other settings stay fixed.")
    with signal:
        render_signal()
    with trades:
        st.subheader("Review turnover before an approved rebalance")
        value = st.number_input("Reserve value ($)", min_value=1., value=100000000., step=1000000., key="meridian_value")
        columns = st.columns(4)
        current = tuple(col.number_input(f"Current {name} (%)", min_value=0., max_value=100.,
            value=default, step=5., key=f"meridian_current_{i}") / 100
            for i, (col, name, default) in enumerate(zip(columns, NAMES, (0., 20., 25., 55.))))
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
        st.write("Expected return is the weight-averaged course return. Variance includes every pairwise covariance term: $w^T\\Sigma w$. Volatility is its square root. The search tests long-only weights in 5 percentage point steps and keeps those meeting the gross return proxy and eligible-reserve floor.")
        st.dataframe(pd.DataFrame({"Sleeve": NAMES, "Training return": [f"{x:.1%}" for x in MEANS],
            "Training volatility": [f"{x:.1%}" for x in VOL],
            "Reserve eligible": ["Yes" if x else "No" for x in ELIGIBLE]}),
            hide_index=True, width="stretch")
        st.caption("Source: local Lab 13 Meridian portfolio case and Meridian IPS. Values are course-authored training inputs, not observed prices or investable return forecasts.")

    memo = f"""MERIDIAN FOUNDATION RESERVE — COMMITTEE MEMO
Recommendation: PILOT the process; no allocation authorization.
Objective: CPI + 4 pp annually net over rolling five years; current proxy {cpi+net_spread:.2f}% net.
Universe: direct bills, direct 10-year Treasuries, IG bond fund, global equity index fund.
Benchmark: 60% global equity / 40% IG bonds; modeled return {benchmark[0]:.2%}, volatility {benchmark[1]:.2%}, eligible reserve 0% (fails).
Equal-weight baseline: 25% each; modeled gross return {equal_weight[0]:.2%}, volatility {equal_weight[1]:.2%}, eligible reserve {equal_weight[2]:.0%}; {mandate_verdict(EQUAL_WEIGHT, equal_weight[0], equal_weight[2], hurdle, reserve_floor/100)[0]} checked rules.
60/40 benchmark verdict: {mandate_verdict(BENCHMARK, benchmark[0], benchmark[2], hurdle, reserve_floor/100)[0]} checked rules; {', '.join(mandate_verdict(BENCHMARK, benchmark[0], benchmark[2], hurdle, reserve_floor/100)[1])}.
Risk measure: modeled annual volatility; no approved volatility cap. Calendar-year 10% loss rule lacks definition and breach response.
Limits: >=3% direct-government reserve, long-only, 8% non-exempt issuer cap, >25% turnover approval, >=90% liquid within five business days.
Current grid result: {weight_text(selected[0]) if selected else 'none qualifies'}; {mandate_verdict(selected[0] if selected else None, selected[1] if selected else 0, selected[3] if selected else 0, hurdle, reserve_floor/100)[0]} checked rules.
Stress run: equity mean -1 pp -> {weight_text(estimate_case[0]) if estimate_case else 'no mix'}; window -> unavailable (no dated Lab 13 returns); costs +0.50 pp -> {weight_text(cost_case[0]) if cost_case else 'no mix'}; first infeasible reserve floor -> {first_break if first_break is not None else 'not found'}%.
Stop condition: no qualifying mix under approved settings, missing valid window evidence, or undefined loss rule; do not allocate.
Unverified gates: issuer exposure, liquidity, loss rule, forward estimates, costs and trading authorization.
"""
    st.download_button("Download Meridian committee memo", memo,
                       file_name="meridian_committee_memo.txt", mime="text/plain")
