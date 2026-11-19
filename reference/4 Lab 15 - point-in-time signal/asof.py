"""Lab 15: four-rule point-in-time gate and naive comparison.

Edit TABLE and DECISION_DATE below, then run: python asof.py
"""

from datetime import date
from decimal import Decimal
from io import StringIO
import csv


# Editable inputs
DECISION_DATE = "2026-03-31"
TABLE = """row,ticker,month,published_on,price
1,AAA,2026-01,2026-02-10,101.0
2,AAA,2026-02,2026-03-10,104.0
3,AAA,2026-03,2026-04-10,109.0
4,AAA,2026-02,2026-03-25,103.0
5,BBB,2026-01,2026-02-10,98.0
6,BBB,2026-02,2026-03-10,97.0
7,BBB,2026-02,2026-03-10,97.0
8,BBB,2026-03,2026-04-10,92.0
9,CCC,2026-01,2026-02-10,110.0
10,CCC,2026-02,2026-04-05,112.0
11,,2026-02,2026-03-10,99.0
12,CCC,2026-02,2026-03-10,111.0
"""


def read_rows(table):
    rows = []
    for item in csv.DictReader(StringIO(table.strip())):
        rows.append({
            "row": int(item["row"]),
            "ticker": item["ticker"].strip(),
            "month": item["month"],
            "published_on": date.fromisoformat(item["published_on"]),
            "price": Decimal(item["price"]),
        })
    if len({item["row"] for item in rows}) != len(rows):
        raise ValueError("Row numbers must be unique")
    if any(item["price"] <= 0 for item in rows):
        raise ValueError("Prices must be positive")
    return rows


def latest_publications(rows):
    """Keep the latest publication for each ticker and measured month."""
    latest = {}
    for item in rows:
        key = (item["ticker"], item["month"])
        if key not in latest or item["published_on"] > latest[key]["published_on"]:
            latest[key] = item
        elif (item["published_on"] == latest[key]["published_on"]
              and item["price"] != latest[key]["price"]):
            raise ValueError(f"Conflicting publications for {key} on one date")
    return sorted(latest.values(), key=lambda item: (item["ticker"], item["month"]))


def gate(rows, decision_date):
    # Rule 1: quarantine missing tickers.
    quarantined = [item["row"] for item in rows if not item["ticker"]]
    working = [item for item in rows if item["ticker"]]

    # Rule 2: remove exact duplicates, preserving the first row number.
    seen = set()
    duplicates = []
    unique = []
    for item in working:
        identity = (item["ticker"], item["month"],
                    item["published_on"], item["price"])
        if identity in seen:
            duplicates.append(item["row"])
        else:
            seen.add(identity)
            unique.append(item)

    # Rule 3: remove publications after the decision date.
    future = [item["row"] for item in unique
              if item["published_on"] > decision_date]
    knowable = [item for item in unique
                if item["published_on"] <= decision_date]

    # Rule 4: keep the latest knowable publication per ticker and month.
    panel = latest_publications(knowable)
    kept = {item["row"] for item in panel}
    superseded = [item["row"] for item in knowable if item["row"] not in kept]
    return panel, quarantined, duplicates, future, superseded


def signals(panel):
    by_ticker = {}
    for item in panel:
        by_ticker.setdefault(item["ticker"], []).append(item)
    result = {}
    for ticker, items in sorted(by_ticker.items()):
        items.sort(key=lambda item: item["month"])
        if len(items) < 2:
            result[ticker] = None
            continue
        previous, latest = items[-2:]
        change = (latest["price"] / previous["price"] - 1) * 100
        result[ticker] = (previous["month"], latest["month"], change,
                          previous["row"], latest["row"])
    return result


def print_signals(title, panel):
    print(title)
    for ticker, result in signals(panel).items():
        if result is None:
            print(f"  {ticker}: insufficient months")
        else:
            previous_month, latest_month, change, old_row, new_row = result
            print(f"  {ticker}: {latest_month} vs {previous_month}: "
                  f"{change:+.2f}% (rows {old_row} -> {new_row})")


def main():
    cutoff = date.fromisoformat(DECISION_DATE)
    rows = read_rows(TABLE)
    panel, quarantined, duplicates, future, superseded = gate(rows, cutoff)
    print(f"Decision date: {cutoff}; input rows: {len(rows)}")
    print("Row funnel (rules applied in order):")
    print(f"  1. Missing ticker: 0 removed; {len(quarantined)} quarantined {quarantined}")
    print(f"  2. Exact duplicate: {len(duplicates)} removed {duplicates}")
    print(f"  3. Published later: {len(future)} removed {future}")
    print(f"  4. Earlier revision: {len(superseded)} removed {superseded}")
    print(f"  Remaining: {len(panel)} admitted rows")
    print("As-of panel (row, ticker, month, published on, price):")
    for item in panel:
        print(f"  {item['row']:>2}  {item['ticker']}  {item['month']}  "
              f"{item['published_on']}  {item['price']:.1f}")
    print_signals("As-of signals:", panel)
    naive = latest_publications([item for item in rows if item["ticker"]])
    print_signals("Naive signals (ignore publication date):", naive)


if __name__ == "__main__":
    main()
