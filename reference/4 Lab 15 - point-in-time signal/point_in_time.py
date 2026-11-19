"""Select the ALFRED observation version knowable on a decision date.

Input CSV columns: series_id,date,realtime_start,realtime_end,value.
ALFRED real-time intervals include both endpoints; 9999-12-31 is allowed.
"""

import argparse
import csv
from datetime import date
from math import isfinite
from pathlib import Path
import sys


FIELDS = ("series_id", "date", "realtime_start", "realtime_end", "value")


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid ISO date: {value!r}") from exc


def select_as_of(rows, decision_date):
    """Return one valid version per (series, observation date), sorted.

    An observation's period date is not its publication date. A version must
    cover the decision date in ALFRED's inclusive real-time interval.
    """
    cutoff = parse_date(decision_date)
    selected = {}
    for line, row in enumerate(rows, start=2):
        if not all(key in row for key in FIELDS):
            raise ValueError(f"Row {line}: expected columns {', '.join(FIELDS)}")
        series = row["series_id"].strip()
        if not series:
            raise ValueError(f"Row {line}: series_id is required")
        observed = parse_date(row["date"])
        start = parse_date(row["realtime_start"])
        end = parse_date(row["realtime_end"])
        if start > end:
            raise ValueError(f"Row {line}: real-time start exceeds end")
        if observed > cutoff or not start <= cutoff <= end:
            continue
        value = row["value"].strip()
        if value == ".":  # ALFRED's missing-value marker is not an observation.
            continue
        try:
            number = float(value)
        except ValueError as exc:
            raise ValueError(f"Row {line}: invalid value {value!r}") from exc
        if not isfinite(number):
            raise ValueError(f"Row {line}: value must be finite")
        key = (series, observed)
        if key in selected:
            raise ValueError(f"Row {line}: overlapping vintages for {series} {observed}")
        selected[key] = {
            "series_id": series,
            "date": observed.isoformat(),
            "value": value,
            "realtime_start": start.isoformat(),
            "realtime_end": end.isoformat(),
        }
    return [selected[key] for key in sorted(selected)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("decision_date", help="YYYY-MM-DD; date-level close of day")
    args = parser.parse_args()
    with args.csv_file.open(newline="", encoding="utf-8-sig") as source:
        rows = select_as_of(csv.DictReader(source), args.decision_date)
    writer = csv.DictWriter(sys.stdout,
                            fieldnames=("series_id", "date", "value", "realtime_start", "realtime_end"))
    writer.writeheader()
    writer.writerows(rows)


if __name__ == "__main__":
    main()
