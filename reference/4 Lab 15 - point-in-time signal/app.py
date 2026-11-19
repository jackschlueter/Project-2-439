"""Lab 14 portfolio app. Run: streamlit run app.py"""

import hashlib

import streamlit as st

from portfolio import (
    CORRELATIONS, RESERVE_ELIGIBLE, RESERVE_MINIMUM, RETURNS, RETURN_TARGET,
    SLEEVES, VOLATILITIES, estimate_from_csv, search_five_point_mix,
)


st.set_page_config(page_title="Portfolio mandate lab", page_icon="📊")
st.title("Lowest-risk mix meeting the mandate")
st.caption("Built with AI help, a learning demonstration, not investment advice.")

with st.sidebar:
    st.header("Mandate and data")
    objective_pct = st.number_input(
        "Expected return objective (%)", value=100 * RETURN_TARGET, step=0.1
    )
    reserve_pct = st.number_input(
        "Reserve-eligible minimum (%)", min_value=0.0, max_value=100.0,
        value=100 * RESERVE_MINIMUM, step=0.5,
    )
    uploaded = st.file_uploader("Upload monthly adjusted prices (.csv)", type="csv")
    last_36 = st.toggle("Use only the last 36 monthly returns", value=False)

if uploaded is None:
    names, returns, volatilities, correlations = (
        SLEEVES, RETURNS, VOLATILITIES, CORRELATIONS
    )
    loaded_returns = RETURNS
    loaded_flags = RESERVE_ELIGIBLE
    source_key = "meridian"
    st.write("**Data:** Meridian's Lab 14 training estimates.")
else:
    try:
        names, returns, volatilities, correlations, window = estimate_from_csv(
            uploaded, last_36=last_36
        )
        _, loaded_returns, loaded_volatilities, loaded_correlations, full_window = (
            estimate_from_csv(uploaded)
        )
    except (ValueError, UnicodeError) as error:
        st.error(str(error))
        st.stop()
    loaded_flags = tuple(1.0 if name.upper() == "SGOV" else 0.0 for name in names)
    source_key = hashlib.sha1(uploaded.getvalue()).hexdigest()[:10]
    st.write(
        f"**Data:** {uploaded.name}; {window[2]} monthly return intervals, "
        f"{window[0]}–{window[1]}. Annualized historical estimates, not forecasts."
    )
    st.caption(
        f"Loaded comparison uses all {full_window[2]} monthly returns. "
        "SGOV is initially marked reserve-eligible under the proposed Project 2 policy."
    )
    if names == ("SGOV", "BND", "VT", "TIP"):
        st.info(
            "Proposed young-family mandate: set the objective to 8.2% gross "
            "(8.0% net plus a 0.2% illustrative cost allowance), set the "
            "reserve minimum to 10%, and count SGOV as eligible."
        )

st.subheader("Estimates and reserve eligibility")
edited_returns = []
edited_flags = []
for name, estimate, eligible in zip(names, returns, loaded_flags):
    left, right = st.columns([2, 1])
    edited_pct = left.number_input(
        f"{name} expected return estimate (%)", value=float(100 * estimate),
        step=0.1, format="%.2f",
        key=f"return_{source_key}_{'36' if last_36 else 'all'}_{name}",
    )
    checked = right.checkbox(
        f"{name} reserve-eligible", value=bool(eligible),
        key=f"reserve_{source_key}_{name}",
    )
    edited_returns.append(edited_pct / 100)
    edited_flags.append(float(checked))


def show_answer(result, asset_names):
    if result is None:
        st.warning("no mix meets the objective")
        return
    weights, expected_return, volatility, reserve_share = result
    st.dataframe(
        {"Asset": asset_names,
         "Weight (%)": [round(100 * weight, 2) for weight in weights]},
        hide_index=True, width="stretch",
    )
    st.write(
        f"Return **{expected_return:.2%}** · Volatility **{volatility:.2%}** · "
        f"Reserve-eligible **{reserve_share:.2%}**"
    )


try:
    current = search_five_point_mix(
        edited_returns, volatilities, correlations, objective_pct / 100,
        reserve_pct / 100, edited_flags,
    )
    if uploaded is None:
        baseline = search_five_point_mix(
            RETURNS, VOLATILITIES, CORRELATIONS, RETURN_TARGET,
            RESERVE_MINIMUM, RESERVE_ELIGIBLE,
        )
    else:
        baseline = search_five_point_mix(
            loaded_returns, loaded_volatilities, loaded_correlations,
            objective_pct / 100, reserve_pct / 100, edited_flags,
        )
except ValueError as error:
    st.error(str(error))
    st.stop()

left, right = st.columns(2)
with left:
    st.subheader("Current controls")
    show_answer(current, names)
with right:
    st.subheader("All months as loaded" if uploaded else "Meridian as loaded")
    st.caption(
        "CSV all-month estimates with the same objective and reserve rule."
        if uploaded else "Meridian defaults; 6.5% objective, 3% reserve floor."
    )
    show_answer(baseline, names)

if current is not None and baseline is not None:
    largest_change = max(
        abs(a - b) * 100 for a, b in zip(current[0], baseline[0])
    )
    st.metric("Largest weight change", f"{largest_change:.2f} percentage points")
else:
    st.write("Largest weight change: unavailable because one case has no qualifying mix.")

st.caption(
    "Search tests weights in 5-percentage-point steps. A lower-risk mix may lie "
    "between grid points. Historical CSV averages are estimates, not forecasts."
)
