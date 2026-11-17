"""Committee portfolio workbench. Start with: streamlit run app.py"""

from pathlib import Path
from math import ceil

import pandas as pd
import streamlit as st

from portfolio_engine import FUNDS, estimate, optimize, read_prices, rebalance, score
from lab13_mandate import mandate_verdict, render as render_lab13
from pit_signal import render_signal


st.set_page_config(page_title="Family Portfolio Committee", page_icon="◈", layout="wide")
st.markdown("""<style>
  .block-container{max-width:1180px;padding-top:2rem}
  h1,h2,h3{color:#19324a}
  [data-testid="stMetricValue"]{color:#19324a}
  .callout{padding:1rem 1.2rem;background:#eaf2ef;border-left:4px solid #568d78;margin:.8rem 0 1.5rem}
  .warningbox{padding:1rem 1.2rem;background:#f8f0e2;border-left:4px solid #c7a35f;margin:.8rem 0 1.5rem}
  .small{font-size:.85rem;color:#64748b}
</style>""", unsafe_allow_html=True)

ROOT = Path(__file__).resolve().parent

mode = st.sidebar.selectbox("Mandate", ("Meridian Foundation Reserve · Lab 13",
                                      "Young family · Project 2"))
if mode.startswith("Meridian"):
    render_lab13()
    st.stop()

with st.sidebar:
    st.header("Mandate controls")
    st.caption("Draft young-family policy · four ETF pilot universe")
    window_choice = st.selectbox("Estimation window", ("All available months", "Last 36 months"))
    net_goal = st.number_input("Net return objective (%)", 0.0, 30.0, 8.0, 0.1)
    costs = st.number_input("Annual cost allowance (%)", 0.0, 5.0, 0.20, 0.05)
    reserve_floor = st.number_input("Minimum SGOV weight (%)", 0.0, 100.0, 10.0, 5.0)
    vt_adjustment = st.slider("VT return estimate change (percentage points)", -5.0, 3.0, 0.0, 0.25)
    st.divider()
    uploaded = st.file_uploader("Optional replacement price panel", type="csv",
        help="Month,SGOV,BND,VT,TIP; consecutive monthly adjusted closes, oldest first.")
    st.caption("The bundled file loads automatically. Uploads are used only in this session.")

try:
    source = uploaded.getvalue() if uploaded else ROOT / "prices.csv"
    dates, prices = read_prices(source)
    all_estimates = estimate(dates, prices)
    selected = estimate(dates, prices, 36 if window_choice == "Last 36 months" else None)
    floor = (net_goal + costs) / 100
    result = optimize(selected, floor, reserve_floor / 100, vt_adjustment / 100)
    base = optimize(all_estimates, 0.082, 0.10)
    stress = optimize(all_estimates, 0.082, 0.10, -0.01)
    short = optimize(estimate(dates, prices, 36), 0.082, 0.10)
except (ValueError, UnicodeError, OSError) as exc:
    st.error(f"The price panel or model settings could not be used: {exc}")
    st.stop()


def mix_text(mix):
    return " / ".join(f"{w:.0%} {name}" for name, w in zip(FUNDS, mix.weights) if w > 0)


def record(mix):
    return {
        "Allocation": mix_text(mix) if mix else "None qualifies",
        "Gross return": f"{mix.gross_return:.2%}" if mix else "—",
        "Net after 0.20%": f"{mix.gross_return - .002:.2%}" if mix else "—",
        "Volatility": f"{mix.volatility:.2%}" if mix else "—",
    }


st.caption("INVESTMENT PROCESS  /  EDITION A  /  RESEARCH SNAPSHOT")
st.title("Family Portfolio Committee")
st.write("An operational workbench for a fictional young family saving for education in roughly 14–16 years. The proposed objective is **8.0% nominal annual return net of costs over rolling ten-year periods**, with at least **10% in SGOV**. The policy is a draft.")

if uploaded:
    st.info(f"Using uploaded data: {uploaded.name}. Review its source and availability date before any decision.")
else:
    st.caption("Using bundled monthly adjusted closes for SGOV, BND, VT, and TIP, September 2021–September 2026. Saved source downloads: 20 and 22 October 2026.")

decision, scenarios, signal, trades, method = st.tabs(("Committee decision", "Scenario challenge", "Point-in-time signal", "Rebalance worksheet", "Data & method"))

with decision:
    st.markdown('<div class="callout"><strong>Recommendation: PILOT.</strong> Use the full-sample allocation as a research starting point. Do not allocate client funds or adopt the optimizer as policy yet.</div>', unsafe_allow_html=True)
    adjusted_mean = selected.mean.copy()
    adjusted_mean[2] += vt_adjustment / 100
    equal_mix = score((.25, .25, .25, .25), adjusted_mean, selected.covariance)
    reference_mix = score((0, .40, .60, 0), adjusted_mean, selected.covariance)
    st.subheader("Two baselines beside the constrained portfolio")
    comparisons = (("Equal weight", equal_mix), ("60/40 VT/BND reference", reference_mix),
                   ("Constrained portfolio", result))
    for column, (name, mix) in zip(st.columns(3), comparisons):
        with column.container(border=True):
            st.markdown(f"**{name}**")
            if mix is None:
                st.write("No qualifying allocation")
                st.error("FAIL · No qualifying 5% grid mix")
            else:
                verdict, reasons = mandate_verdict(mix.weights, mix.gross_return,
                    mix.reserve, floor, reserve_floor / 100)
                st.write(mix_text(mix))
                st.write(f"Net return proxy **{mix.gross_return - costs / 100:.2%}** · volatility **{mix.volatility:.2%}** · SGOV reserve **{mix.reserve:.0%}**")
                if verdict == "PASS":
                    st.success("PASS · checked return, reserve, and weight rules")
                else:
                    st.error("FAIL · " + "; ".join(reasons))
    st.caption("The 60/40 reference is a transparent comparison, not a family-approved benchmark. Verdicts cover the modeled return proxy, SGOV floor, and weight rules; taxes, realized returns, and the missing loss limit remain unresolved.")
    st.warning("Process stop condition: do not allocate if approved return and SGOV rules have no qualifying mix, or a required window comparison lacks valid data. The draft loss limit and reserve definition also block adoption.")
    if result:
        st.subheader("Selected qualifying mix")
        st.write(f"**{mix_text(result)}**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Expected net return", f"{result.gross_return - costs / 100:.2%}", help="Historical arithmetic estimate less the entered cost allowance")
        c2.metric("Modeled volatility", f"{result.volatility:.2%}")
        c3.metric("SGOV reserve", f"{result.reserve:.0%}")
        c4.metric("Gross hurdle margin", f"{(result.gross_return - floor) * 100:.2f} pp")
        st.bar_chart(pd.DataFrame({"Weight": result.weights}, index=FUNDS), horizontal=True,
                     color="#315c76", height=220)
    else:
        st.warning("No long-only 5% grid allocation meets both the return hurdle and SGOV floor. Review the assumptions or mandate before proceeding.")
    st.caption(f"Current estimate window: {selected.start} to {selected.end}, {selected.months} monthly returns. Gross hurdle: {net_goal + costs:.2f}%.")
    st.markdown("### Why the call is pilot")
    st.write("The family has not stated an acceptable loss limit. The sample-based choice also moves materially when the history changes or VT's return estimate is reduced. The optimizer selects the least volatile qualifying *grid* mix; it cannot establish that future returns will meet a ten-year objective.")
    st.markdown("### Adoption gates")
    gate1 = st.checkbox("Client approves the SGOV reserve definition and withdrawal plan")
    gate2 = st.checkbox("Client states an acceptable loss measure and limit")
    gate3 = st.checkbox("Committee reviews forward return assumptions, costs, and taxes")
    gate4 = st.checkbox("Operations confirms liquidity and rebalance rules")
    st.caption(f"Readiness checklist: {sum((gate1, gate2, gate3, gate4))}/4 recorded in this session. Checking a box documents review; it does not authorize a trade.")

with scenarios:
    st.subheader("Challenge the binding estimate")
    if not all((base, stress, short)):
        st.warning("A required reference scenario has no qualifying mix for this data panel.")
    else:
        cases = pd.DataFrame([
            {"Case": "Full sample · default mandate", **record(base)},
            {"Case": "Full sample · VT return −1 pp", **record(stress)},
            {"Case": "Last 36 months · default mandate", **record(short)},
        ])
        st.dataframe(cases, hide_index=True, width="stretch")
        st.write(f"A one point cut to VT's estimated return moves the full-sample mix by **{max(abs(a-b) for a,b in zip(base.weights,stress.weights))*100:.0f} percentage points** in its largest weight. Switching to 36 months moves the largest weight by **{max(abs(a-b) for a,b in zip(base.weights,short.weights))*100:.0f} points**. The window comparison also changes covariance, so its entire shift cannot be assigned to the VT mean alone.")
    st.markdown("#### Current fund estimates")
    estimate_table = pd.DataFrame({
        "Fund": FUNDS,
        "Historical annual mean": [f"{100*x:.2f}%" for x in selected.mean],
        "Model return after VT edit": [f"{100*x + (vt_adjustment if f == 'VT' else 0):.2f}%" for f,x in zip(FUNDS, selected.mean)],
        "Annual volatility": [f"{100*x:.2f}%" for x in selected.covariance.diagonal() ** .5],
    })
    st.dataframe(estimate_table, hide_index=True, width="stretch")
    st.caption("These are sample statistics, not forecasts. The edited VT return changes the mean only; covariance is held fixed.")
    st.subheader("Four-way stress run · current sidebar settings")
    estimate_case = optimize(selected, floor, reserve_floor / 100, (vt_adjustment - 1) / 100)
    other_window = estimate(dates, prices, None if selected.months == 36 else 36)
    window_case = (optimize(other_window, floor, reserve_floor / 100, vt_adjustment / 100)
                   if other_window.months != selected.months else None)
    cost_case = optimize(selected, floor + .005, reserve_floor / 100, vt_adjustment / 100)
    first_break = next((floor_pct for floor_pct in range(max(5, ceil(reserve_floor / 5) * 5), 101, 5)
                        if floor_pct > reserve_floor and
                        optimize(selected, floor, floor_pct / 100, vt_adjustment / 100) is None), None)

    def stress_row(case, change, mix):
        return {"Case": case, "Change from current": change,
                "Allocation": mix_text(mix) if mix else "No qualifying mix",
                "Gross return": f"{mix.gross_return:.2%}" if mix else "—",
                "Volatility": f"{mix.volatility:.2%}" if mix else "—",
                "Screen": "FEASIBLE" if mix else "STOP · no mix"}

    stress_rows = [stress_row("Base", f"{selected.months} monthly returns", result),
                   stress_row("Estimate", "VT mean −1 pp", estimate_case)]
    if other_window.months != selected.months:
        stress_rows.append(stress_row("Window", f"Switch to {other_window.months} monthly returns", window_case))
    else:
        stress_rows.append({"Case": "Window", "Change from current": "No distinct second window",
            "Allocation": "Not available", "Gross return": "—", "Volatility": "—",
            "Screen": "STOP · evidence gap"})
    stress_rows.append(stress_row("Costs", "Cost allowance +0.50 pp", cost_case))
    stress_rows.append(stress_row("Constraint",
        f"First infeasible SGOV floor: {first_break}%" if first_break is not None else "No infeasible floor found",
        None if first_break is not None else result))
    st.dataframe(pd.DataFrame(stress_rows), hide_index=True, width="stretch")
    st.error("STOP allocation when the current approved return and SGOV rules have no qualifying mix, or a required window comparison lacks valid data. The family loss limit and reserve definition remain unapproved, so this process stays at pilot even when a model mix is feasible.")
    st.caption("The constraint row finds a 5% grid breakpoint, not a proposed policy change. Each stress changes only the named input family; the other current settings stay fixed.")

with signal:
    render_signal()

with trades:
    st.subheader("Translate an approved target into dollar changes")
    st.write("Enter the actual portfolio value and current weights. This worksheet estimates changes; it does not execute orders.")
    value = st.number_input("Portfolio value ($)", min_value=1.0, value=100000.0, step=1000.0)
    defaults = (45.0, 0.0, 55.0, 0.0)
    cols = st.columns(4)
    current = tuple(col.number_input(f"Current {fund} (%)", min_value=0.0, max_value=100.0,
        value=default, step=1.0) / 100 for col, fund, default in zip(cols, FUNDS, defaults))
    if not result:
        st.warning("No qualifying target is available for these settings.")
    else:
        try:
            changes, turnover = rebalance(current, result.weights, value)
        except ValueError as exc:
            st.error(str(exc))
        else:
            plan = pd.DataFrame({
                "Fund": FUNDS,
                "Current weight": [f"{x:.1%}" for x in current],
                "Target weight": [f"{x:.1%}" for x in result.weights],
                "Estimated change ($)": [round(x, 2) for x in changes],
                "Action": ["Buy" if x > .01 else "Sell" if x < -.01 else "Hold" for x in changes],
            })
            st.dataframe(plan, hide_index=True, width="stretch")
            st.metric("One-way turnover", f"{turnover:.1%}", help="Half the sum of absolute weight changes")
            st.caption("Exclude taxes, lots, spreads, fees, settlement, and any cash flows. Confirm the execution policy before trading.")
            st.download_button("Download rebalance CSV", plan.to_csv(index=False).encode(),
                               file_name="rebalance_plan.csv", mime="text/csv")

with method:
    st.subheader("Inputs and provenance")
    st.write(f"**Panel:** {dates[0]} to {dates[-1]} · {len(dates)} monthly prices · {len(dates)-1} return intervals. Source: {'session upload' if uploaded else 'bundled course panel'}.")
    st.write("Monthly simple return = adjusted close this month / previous month − 1. Annual mean = 12 × monthly arithmetic mean. Annual sample covariance = 12 × monthly sample covariance. Portfolio volatility is the square root of weighted annual covariance.")
    st.write("The search tries all long-only weights in 5 percentage point steps that total 100%. It requires expected **gross** return at least net objective plus cost allowance and SGOV weight at least the reserve floor, then selects the lowest modeled volatility. No borrowing, shorting, or derivatives are modeled.")
    st.markdown('<div class="warningbox">Saved adjusted closes can be revised after distributions and corporate actions. The data were downloaded after the final sample month, so this app does not claim a point-in-time backtest. ETF shares can fluctuate and are not bank cash.</div>', unsafe_allow_html=True)
    st.markdown("**Fund and risk references:** [SGOV issuer](https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf-sgov) · [BND issuer](https://advisors.vanguard.com/investments/products/bnd/vanguard-total-bond-market-etf) · [VT issuer](https://advisors.vanguard.com/investments/products/vt/vanguard-total-world-stock-etf) · [TIP issuer](https://www.ishares.com/us/products/239467/ishares-tips-bond-etf) · [SEC allocation guide](https://www.investor.gov/introduction-investing/getting-started/asset-allocation)")
    if not uploaded:
        st.download_button("Download bundled price CSV", (ROOT / "prices.csv").read_bytes(),
            file_name="prices.csv", mime="text/csv")

memo = f"""FAMILY PORTFOLIO COMMITTEE — RESEARCH MEMO
Recommendation: PILOT; no allocation or trade authorization.
Mandate: 8.0% net annual objective over rolling ten years; 10% minimum SGOV reserve (draft).
Current model: {mix_text(result) if result else 'no qualifying mix'}.
Price panel: {selected.start} to {selected.end}; {selected.months} monthly returns.
Gross hurdle: {net_goal + costs:.2f}%; VT estimate adjustment: {vt_adjustment:+.2f} pp.
Reason: loss tolerance and reserve rule need client approval; sample-window and return-estimate sensitivity require forward assumption review.
Stress run: VT mean -1 pp -> {mix_text(estimate_case) if estimate_case else 'no mix'}; alternate window -> {mix_text(window_case) if window_case else 'unavailable or no mix'}; costs +0.50 pp -> {mix_text(cost_case) if cost_case else 'no mix'}; first infeasible SGOV floor -> {first_break if first_break is not None else 'not found'}%.
Stop condition: no qualifying mix under approved settings or no valid required window comparison; do not allocate until the loss limit and reserve definition are approved.
Next gate: client risk interview, forward estimates, costs/taxes, liquidity and rebalance rules.
"""
st.download_button("Download committee memo", memo, file_name="committee_memo.txt", mime="text/plain")
st.caption("Research demonstration for a fictional client. No orders are connected to this app.")
