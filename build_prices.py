"""Build a 61-month adjusted-close panel from saved Yahoo Finance responses."""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).parent
TICKERS = ("SGOV", "BND", "VT", "TIP")
rows_by_ticker = {}

for ticker in TICKERS:
    source = HERE / "source" / f"{ticker.lower()}_yahoo.json"
    chart = json.loads(source.read_text())["chart"]["result"][0]
    dates = chart["timestamp"]
    prices = chart["indicators"]["adjclose"][0]["adjclose"]
    monthly = {}
    for timestamp, price in zip(dates, prices, strict=True):
        month = datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m")
        if price is None or price <= 0 or month in monthly:
            raise ValueError(f"Invalid or duplicate price for {ticker} in {month}")
        monthly[month] = price
    rows_by_ticker[ticker] = monthly

months = sorted(set.intersection(*(set(rows) for rows in rows_by_ticker.values())))
expected = [f"{year}-{month:02d}" for year in range(2021, 2027) for month in range(1, 13)]
expected = expected[expected.index("2021-09") : expected.index("2026-09") + 1]
if months != expected or any(len(rows) != len(expected) for rows in rows_by_ticker.values()):
    raise ValueError("Expected 61 aligned months, September 2021 through September 2026")

with (HERE / "prices.csv").open("w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(("Month", *TICKERS))
    for month in months:
        writer.writerow((month, *(f"{rows_by_ticker[ticker][month]:.6f}" for ticker in TICKERS)))

print(f"Wrote {len(months)} months and {len(months) - 1} return intervals")
