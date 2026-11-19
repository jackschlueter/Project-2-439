"""Apply the four Lab 15 provenance rules to the numbered training table."""

import csv
from datetime import date
from pathlib import Path


DECISION_DATE = date(2026, 3, 31)
TABLE = Path(__file__).with_name("training_table.csv")


def gate(rows, decision_date=DECISION_DATE):
    """Return row decisions and surviving rows; preserve original row numbers."""
    records = list(rows)
    decisions = {}
    seen = {}
    eligible = []

    for record in records:
        number = int(record["row"])
        if number in decisions:
            raise ValueError(f"Duplicate row number {number}")
        ticker = record["ticker"].strip()
        if not ticker:
            decisions[number] = "quarantined: missing ticker"
            continue
        signature = (ticker, record["month"], record["published_on"], record["price"])
        if signature in seen:
            decisions[number] = f"removed: exact duplicate of row {seen[signature]}"
            continue
        seen[signature] = number
        if date.fromisoformat(record["published_on"]) > decision_date:
            decisions[number] = "removed: published after decision date"
            continue
        eligible.append(record)

    latest = {}
    for record in eligible:
        key = (record["ticker"], record["month"])
        published = date.fromisoformat(record["published_on"])
        if key in latest and published == date.fromisoformat(latest[key]["published_on"]):
            raise ValueError(f"Conflicting same-day publications for {key}")
        if key not in latest or published > date.fromisoformat(latest[key]["published_on"]):
            latest[key] = record
    for record in eligible:
        number = int(record["row"])
        selected = latest[(record["ticker"], record["month"])]
        if record is selected:
            decisions[number] = "admitted"
        else:
            decisions[number] = f"removed: superseded by row {selected['row']}"
    return decisions, sorted(latest.values(), key=lambda r: int(r["row"]))


def signals(admitted):
    """Latest month's price return and zero-coupon yield for each rating."""
    by_ticker = {}
    for record in admitted:
        by_ticker.setdefault(record["ticker"], []).append(record)
    result = {}
    for ticker, records in by_ticker.items():
        records.sort(key=lambda r: r["month"])
        if len(records) < 2:
            continue
        previous, latest = records[-2:]
        old, new = float(previous["price"]), float(latest["price"])
        if old <= 0 or new <= 0:
            raise ValueError("Prices must be positive")
        result[ticker] = {
            "rows": (int(previous["row"]), int(latest["row"])),
            "months": (previous["month"], latest["month"]),
            "prices": (old, new),
            "return": new / old - 1,
            "latest_zero_yield": 100 / new - 1,
        }
    return result


def economic_flags(admitted):
    """Flag the separate bond-pricing checks; do not change gate decisions."""
    flags = []
    by_month = {}
    for record in admitted:
        price = float(record["price"])
        if price > 100:
            flags.append(f"row {record['row']}: {record['ticker']} price {price:.1f} "
                         f"exceeds 100; zero yield {100 / price - 1:+.2%}")
        by_month.setdefault(record["month"], {})[record["ticker"]] = record
    for month, ratings in sorted(by_month.items()):
        if all(ticker in ratings for ticker in ("AAA", "BBB", "CCC")):
            aaa, bbb, ccc = (float(ratings[ticker]["price"])
                             for ticker in ("AAA", "BBB", "CCC"))
            if not aaa > bbb > ccc:
                flags.append(f"{month}: credit-price order fails: "
                             f"AAA {aaa:.1f}, BBB {bbb:.1f}, CCC {ccc:.1f}")
    return flags


def main():
    with TABLE.open(newline="") as source:
        decisions, admitted = gate(csv.DictReader(source))
    for number, decision in sorted(decisions.items()):
        print(f"Row {number:2}: {decision}")
    print("\nLatest knowable month-over-month price returns:")
    for ticker, result in sorted(signals(admitted).items()):
        old, new = result["prices"]
        print(f"{ticker}: rows {result['rows'][0]}->{result['rows'][1]}, "
              f"{old:.1f}->{new:.1f}, return {result['return']:+.2%}, "
              f"latest zero yield {result['latest_zero_yield']:+.2%}")
    print("\nSeparate economic validation flags:")
    for flag in economic_flags(admitted):
        print(flag)


if __name__ == "__main__":
    main()
