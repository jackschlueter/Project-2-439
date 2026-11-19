"""FRED-style interest-rate page. Run: streamlit run asof_app.py"""

import csv
from datetime import date
from io import StringIO
from math import isfinite
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import streamlit as st


SERIES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year mortgage rate",
}
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv"
ALFRED_CSV = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"


def parse_csv(body, series_id, expected_column):
    reader = csv.DictReader(StringIO(body.decode("utf-8-sig")))
    if reader.fieldnames != ["observation_date", expected_column]:
        raise ValueError(f"Unexpected CSV columns for {series_id}: {reader.fieldnames}")
    values = {}
    for row in reader:
        raw = row[expected_column]
        if raw in ("", ".", None):
            continue
        measured = date.fromisoformat(row["observation_date"])
        if measured in values:
            raise ValueError(f"Duplicate observation date for {series_id}: {measured}")
        value = float(raw)
        if not isfinite(value):
            raise ValueError(f"Nonfinite value for {series_id} on {measured}")
        values[measured] = value
    return values


def download(url):
    try:
        with urlopen(url, timeout=25) as response:
            return response.read()
    except HTTPError as exc:
        raise ValueError(f"HTTP {exc.code}; check the series ID") from exc
    except (URLError, TimeoutError) as exc:
        raise ValueError(f"Download failed: {exc}") from exc


@st.cache_data(show_spinner=False, ttl=3600)
def today_values(series_id):
    """One public FRED CSV request for the current series."""
    url = FRED_CSV + "?" + urlencode({"id": series_id})
    return parse_csv(download(url), series_id, series_id)


@st.cache_data(show_spinner=False)
def asof_values(series_id, known_on):
    """One public ALFRED CSV request for this series and vintage date."""
    url = ALFRED_CSV + "?" + urlencode({"id": series_id, "vintage_date": known_on})
    column = f"{series_id}_{known_on.replace('-', '')}"
    return parse_csv(download(url), series_id, column)


st.set_page_config(page_title="Rates as known", page_icon="📈", layout="wide")
st.title("Rates as known on a date")
st.caption("Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded today; built with AI help, a learning demonstration, not investment advice.")

with st.sidebar:
    chosen = st.multiselect(
        "Rate series",
        options=list(SERIES),
        default=list(SERIES),
        format_func=lambda series_id: f"{series_id} — {SERIES[series_id]}",
    )
    other = st.text_input("Add another FRED series ID").strip().upper()
    start = st.date_input("Start date", value=date(2020, 1, 1))
    known_on = st.date_input("As known on", value=date.today())

if other:
    if not other.replace("_", "").isalnum():
        st.error(f"{other}: enter a valid FRED series ID")
    elif other not in chosen:
        chosen.append(other)

if not chosen:
    st.info("Choose at least one series.")
    st.stop()

summary = []
for series_id in chosen:
    st.subheader(f"{series_id} — {SERIES.get(series_id, 'FRED series')}")
    try:
        today = today_values(series_id)
        past = asof_values(series_id, known_on.isoformat())
        past = {day: value for day, value in past.items() if day <= known_on}
        if not today:
            raise ValueError("No current observations returned")
    except (ValueError, UnicodeError, csv.Error) as exc:
        st.error(f"{series_id}: {exc}")
        continue

    chart = [{"date": day, "value": value} for day, value in sorted(today.items()) if day >= start]
    if chart:
        st.line_chart(chart, x="date", y="value")
    else:
        st.info("No current observations in the selected chart window.")

    past_window = {day: value for day, value in past.items() if day >= start}
    today_window = {day: value for day, value in today.items() if day >= start}
    past_last = max(past_window) if past_window else None
    today_last = max(today_window) if today_window else None
    st.write(
        f"Last known on {known_on}: **{past_last.isoformat()} — {past_window[past_last]:g}**"
        if past_last else f"No observation known on {known_on} in the selected window."
    )
    if past_last and past_last in today:
        st.caption(f"Today's value for that same measured date: {today[past_last]:g}")
    new_count = sum(day > past_last for day in today_window) if past_last else len(today_window)
    revised_count = sum(today_window[day] != value for day, value in past_window.items() if day in today_window)
    summary.append({
        "Series": f"[{series_id}](https://fred.stlouisfed.org/series/{series_id})",
        "Last measured, as known then": past_last.isoformat() if past_last else "—",
        "Value, as known then": past_window[past_last] if past_last else None,
        "Last measured, today": today_last.isoformat() if today_last else "—",
        "Value, today": today_window[today_last] if today_last else None,
        "New values after then": new_count,
        "Revised values on same dates": revised_count,
    })

st.subheader("Series comparison")
st.caption(f"Counts and last observations use dates from {start.isoformat()} onward. A dot in the source data is missing and is excluded.")
if summary:
    st.markdown(
        "| Series | Last measured, as known then | Value, as known then | Last measured, today | Value, today | New values after then | Revised values on same dates |\n"
        "|---|---|---:|---|---:|---:|---:|\n" +
        "\n".join("| " + " | ".join(str(row[key]) if row[key] is not None else "—" for key in row) + " |" for row in summary)
    )
else:
    st.warning("No series could be loaded.")
