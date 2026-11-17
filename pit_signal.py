"""One reproducible ALFRED vintage signal: DGS10 rate context."""

import csv
from datetime import date
from io import StringIO
from math import isfinite
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
VINTAGES = {
    "2026-10-31": ROOT / "dgs10_2026-10-31.csv",
    "2026-11-03": ROOT / "dgs10_2026-11-03.csv",
}


def read_vintage(raw: str, vintage_date: str):
    """Accept only the requested DGS10 vintage and observations by its date."""
    cutoff = date.fromisoformat(vintage_date)
    reader = csv.DictReader(StringIO(raw))
    expected = ["observation_date", f"DGS10_{cutoff:%Y%m%d}"]
    if reader.fieldnames != expected:
        raise ValueError(f"Expected the exact ALFRED columns: {', '.join(expected)}")
    rows = []
    seen = set()
    for row in reader:
        observed = date.fromisoformat(row["observation_date"])
        if observed > cutoff:
            raise ValueError("A future observation appears in the selected vintage.")
        if observed in seen:
            raise ValueError("Duplicate observation date in the vintage.")
        seen.add(observed)
        value = row[expected[1]].strip()
        if value in ("", "."):
            continue
        number = float(value)
        if not isfinite(number):
            raise ValueError("DGS10 values must be finite.")
        rows.append((observed, number))
    if len(rows) < 2 or rows != sorted(rows):
        raise ValueError("Vintage needs two or more ordered observations.")
    return rows


def render_signal():
    st.subheader("DGS10 · 10-year Treasury yield")
    st.write("A dated **rate-context signal** for challenging the Treasury or bond assumption. It is a yield level in percent per year, **not** a bond or ETF total return, and it never enters the optimizer.")
    selected = st.selectbox("Decision-date ALFRED vintage", tuple(VINTAGES), key="dgs10_vintage",
        help="Only two source snapshots are bundled. Each is selected by its exact ALFRED vintage date.")
    raw = VINTAGES[selected].read_text(encoding="utf-8-sig")
    rows = read_vintage(raw, selected)
    previous, latest = rows[-2:]
    a, b, c = st.columns(3)
    a.metric("Latest knowable observation", f"{latest[1]:.2f}%", help=f"Measured {latest[0]}")
    b.metric("Observation date", latest[0].isoformat())
    c.metric("Change from prior observation", f"{(latest[1]-previous[1])*100:+.0f} bp")
    st.caption(f"Selected vintage: {selected}. Prior observation: {previous[0]} at {previous[1]:.2f}%. The measured date is not the publication date.")
    st.line_chart(pd.DataFrame({"DGS10 yield (%)": [value for _, value in rows]},
                               index=[day for day, _ in rows]), height=210)
    if selected == "2026-10-31":
        st.info("The later 2026-11-03 vintage adds October 30 (4.94%) and November 2 (4.91%). Neither value is admitted into the October 31 signal.")
    st.markdown("**Use decision:** ADMIT for dated rate context only. QUARANTINE as an intraday trading signal without release-time evidence. REJECT as an asset-return input.")
    st.download_button("Download selected vintage CSV", raw.encode(),
                       file_name=VINTAGES[selected].name, mime="text/csv", key="dgs10_download")
    st.markdown("### Data card")
    card = pd.DataFrame([
        ("Series / source", "DGS10; Federal Reserve Board H.15 via FRED/ALFRED"),
        ("Measure", "10-year constant-maturity U.S. Treasury market yield, investment basis"),
        ("Units / frequency", "Percent per annum; daily; not seasonally adjusted"),
        ("Observation vs availability", "Latest measured date can precede vintage date; ALFRED vintage gates the known information set"),
        ("Release timing", "H.15 normally posts at 4:15 p.m. on business days; date-level CSV does not prove intraday access"),
        ("Missing / revisions", "Blank and dot cells skipped; exact vintage column checked; no common-date revisions in these two saved October panels"),
        ("Use / exclusion", "Rate context and bond-assumption challenge only; never substitute for asset total returns"),
        ("Snapshot record", "Both CSVs downloaded 2026-11-17; 2026-10-31 and 2026-11-03 ALFRED vintage dates"),
    ], columns=("Field", "Value"))
    st.dataframe(card, hide_index=True, width="stretch")
    st.markdown("[DGS10 definition](https://fred.stlouisfed.org/series/DGS10) · [H.15 release timing](https://www.federalreserve.gov/releases/h15/) · [ALFRED real-time periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html)")
    st.download_button("Download full data card", (ROOT / "dgs10-data-card.md").read_bytes(),
                       file_name="dgs10-data-card.md", mime="text/markdown", key="dgs10_card")
    st.caption("The earlier Lab 16 card described a November 3 intraday view ending October 30. The November 3 end-of-day vintage downloaded November 17 also contains November 2. This app uses the preserved CSVs and does not infer why the two views differ.")
