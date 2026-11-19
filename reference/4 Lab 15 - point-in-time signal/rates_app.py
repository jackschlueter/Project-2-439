"""FRED-style point-in-time rates explorer. Run: streamlit run rates_app.py"""

import csv
from datetime import date
from io import StringIO
from math import isfinite
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import streamlit as st

from point_in_time import select_as_of


HERE = Path(__file__).parent
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv"
ALFRED_CSV = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"
RATE_IDS = ("BAA", "FEDFUNDS", "DGS10", "MORTGAGE30US", "Yours")
FIELDS = ("series_id", "date", "value", "as_of_date", "realtime_start", "realtime_end")


def read_example(filename):
    with (HERE / filename).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def fetch_graph_csv(series_id, cutoff, observation_start, current=False):
    """Read the public graph CSV for a specified ALFRED vintage or today's FRED view."""
    params = {"id": series_id, "cosd": observation_start, "coed": cutoff}
    if not current:
        params["vintage_date"] = cutoff
    url = (FRED_CSV if current else ALFRED_CSV) + "?" + urlencode(params)
    try:
        with urlopen(url, timeout=20) as response:
            body = response.read().decode("utf-8-sig")
    except HTTPError as exc:
        raise ValueError(f"St. Louis Fed CSV returned HTTP {exc.code}; check the series ID") from exc
    except (URLError, TimeoutError, UnicodeError) as exc:
        raise ValueError(f"St. Louis Fed CSV request failed: {exc}") from exc
    reader = csv.DictReader(StringIO(body))
    if not reader.fieldnames or reader.fieldnames[0] != "observation_date" or len(reader.fieldnames) != 2:
        raise ValueError("Unexpected St. Louis Fed CSV format")
    value_column = reader.fieldnames[1]
    expected_column = series_id if current else f"{series_id}_{cutoff.replace('-', '')}"
    if value_column != expected_column:
        raise ValueError(f"Unexpected source column {value_column!r}; expected {expected_column!r}")
    result = []
    seen = set()
    for item in reader:
        if item[value_column] in ("", ".", None):
            continue
        observed = date.fromisoformat(item["observation_date"])
        if observed > date.fromisoformat(cutoff):
            raise ValueError("Source returned a future observation")
        if observed in seen:
            raise ValueError(f"Source returned duplicate observation date {observed}")
        seen.add(observed)
        try:
            number = float(item[value_column])
        except ValueError as exc:
            raise ValueError(f"Source returned invalid value for {observed}") from exc
        if not isfinite(number):
            raise ValueError(f"Source returned nonfinite value for {observed}")
        result.append({"series_id": series_id, "date": observed.isoformat(),
                       "value": item[value_column], "as_of_date": "current" if current else cutoff,
                       "realtime_start": "", "realtime_end": ""})
    return result, url


def snapshot(rows, cutoff, series_id):
    matching = [row for row in rows if row.get("series_id", "").strip() == series_id]
    return [{**row, "as_of_date": cutoff} for row in select_as_of(matching, cutoff)]


def csv_bytes(rows):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows({key: row.get(key, "") for key in FIELDS} for row in rows)
    return output.getvalue().encode("utf-8")


st.set_page_config(page_title="Rates | As known", page_icon="📈", layout="wide")
st.title("Rates, as known on a date")
st.caption("FRED-style series view with ALFRED real-time vintages. Dates are interpreted at the close of day.")

with st.sidebar:
    st.header("Data and decision date")
    source = st.radio("Source", ("Live FRED / ALFRED", "Upload ALFRED CSV", "Classroom examples"))
    uploaded = None
    if source == "Upload ALFRED CSV":
        uploaded = st.file_uploader("ALFRED observations CSV", type="csv")
        st.caption("Required columns: series_id, date, realtime_start, realtime_end, value")
    elif source == "Live FRED / ALFRED":
        choice = st.selectbox("Rate series", RATE_IDS, index=2)
        series_id = st.text_input("Your FRED series ID").strip().upper() if choice == "Yours" else choice
        observation_start = st.date_input("Chart starts", value=date(2025, 1, 1))
        st.caption("Public FRED and ALFRED graph downloads; no key or account.")
    else:
        example = st.selectbox("Example", ("Documented GNPCA known answer", "Synthetic revision exercise"))
    cutoff = st.date_input("Trade date / known by", value=date(2013, 8, 14) if source == "Classroom examples" else date(2026, 3, 31))
    compare = st.checkbox("Compare with a second date", value=False)
    second_date = st.date_input("Second date", value=date(2026, 4, 30)) if compare else None
    show_current = st.checkbox("Compare with FRED as read today", value=False) if source == "Live FRED / ALFRED" else False
    load = st.button("Load real data", type="primary") if source == "Live FRED / ALFRED" else True

if source == "Upload ALFRED CSV":
    if uploaded is None:
        st.info("Upload an ALFRED observation file to explore its vintages, or choose a classroom example.")
        st.stop()
    try:
        rows = list(csv.DictReader(StringIO(uploaded.getvalue().decode("utf-8-sig"))))
    except UnicodeError as exc:
        st.error(f"Could not read CSV: {exc}")
        st.stop()
    missing = set(("series_id", "date", "realtime_start", "realtime_end", "value")) - set(rows[0] if rows else ())
    if missing:
        st.error("Missing CSV columns: " + ", ".join(sorted(missing)))
        st.stop()
    series_ids = sorted({row["series_id"].strip() for row in rows if row["series_id"].strip()})
    if not series_ids:
        st.error("No series IDs found in the CSV")
        st.stop()
    series_id = st.selectbox("Series", series_ids)
    source_note = f"Uploaded {uploaded.name}; capture its source URL and export date for an audit."
elif source == "Classroom examples":
    filename = "alfred_known_answer.csv" if example.startswith("Documented") else "training_vintages.csv"
    rows = read_example(filename)
    series_id = rows[0]["series_id"]
    source_note = ("St. Louis Fed API documentation example, GNPCA, 2013-08-14."
                   if filename == "alfred_known_answer.csv" else
                   "Synthetic classroom data; not an actual FRED series.")
else:
    if not load:
        st.info("Choose a series and trade date, then press Load real data.")
        st.stop()
    if not series_id or not series_id.replace("_", "").isalnum():
        st.error("Enter a valid FRED series ID")
        st.stop()
    if observation_start > cutoff or (second_date is not None and observation_start > second_date):
        st.error("Chart start must be no later than each selected trade date")
        st.stop()
    try:
        current, first_url = fetch_graph_csv(series_id, cutoff.isoformat(), observation_start.isoformat())
        later, second_url = (fetch_graph_csv(series_id, second_date.isoformat(), observation_start.isoformat())
                             if second_date is not None else ([], ""))
        today_rows, today_url = (fetch_graph_csv(series_id, date.today().isoformat(), observation_start.isoformat(), current=True)
                                 if show_current else ([], ""))
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    source_note = "Public St. Louis Fed graph CSV; each ALFRED file is a requested historical vintage."

if source != "Live FRED / ALFRED":
    try:
        current = snapshot(rows, cutoff.isoformat(), series_id)
        later = snapshot(rows, second_date.isoformat(), series_id) if second_date is not None else []
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

st.subheader(series_id)
st.caption(source_note)
if source == "Live FRED / ALFRED":
    st.link_button("Series page on FRED", f"https://fred.stlouisfed.org/series/{series_id}")
    st.markdown(f"[ALFRED vintage CSV]({first_url})" +
                (f" · [second vintage CSV]({second_url})" if second_url else "") +
                (f" · [current FRED CSV]({today_url})" if today_url else ""))
st.metric("Observations known by " + cutoff.isoformat(), len(current))

if not current:
    st.warning("No observations were knowable on this date in the selected data. An upload may contain only a limited set of vintages.")
else:
    st.line_chart({"date": [row["date"] for row in current], "value": [float(row["value"]) for row in current]}, x="date", y="value")
    st.dataframe(current, hide_index=True, width="stretch")
    st.download_button("Download as-of CSV", csv_bytes(current), file_name=f"{series_id}_{cutoff}_asof.csv", mime="text/csv")

if second_date is not None:
    first_values = {row["date"]: float(row["value"]) for row in current}
    second_values = {row["date"]: float(row["value"]) for row in later}
    changed = [{"observation_date": day, "first": first_values.get(day), "second": second_values.get(day)}
               for day in sorted(first_values.keys() | second_values.keys())
               if first_values.get(day) != second_values.get(day)]
    st.subheader("What changed by " + second_date.isoformat())
    st.write(f"{len(changed)} observations added, removed, or revised between the two views.")
    st.dataframe(changed, hide_index=True, width="stretch")

if show_current:
    asof_values = {row["date"]: float(row["value"]) for row in current}
    current_values = {row["date"]: float(row["value"]) for row in today_rows}
    revised = [{"observation_date": day, "as_of": asof_values.get(day), "today": current_values.get(day)}
               for day in sorted(asof_values.keys() | current_values.keys())
               if asof_values.get(day) != current_values.get(day)]
    st.subheader("ALFRED then vs FRED today")
    st.write(f"{len(revised)} observations differ across the requested chart window.")
    st.dataframe(revised, hide_index=True, width="stretch")

st.caption("Observation date is the period measured, not the release date. ALFRED vintage dates are date-level and cannot establish intraday availability. Real-time intervals in uploaded files include both endpoints. Missing values (.) are omitted. A rate level is not an ETF total return or a forecast.")
