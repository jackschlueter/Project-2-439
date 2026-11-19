import csv
import io
import unittest

from point_in_time import select_as_of


class PointInTimeTests(unittest.TestCase):
    def test_documented_alfred_known_answer(self):
        from pathlib import Path
        with Path(__file__).with_name("alfred_known_answer.csv").open(newline="") as file:
            actual = select_as_of(csv.DictReader(file), "2013-08-14")
        self.assertEqual([(r["date"], r["value"]) for r in actual],
                         [("1929-01-01", "1065.9"), ("1930-01-01", "975.5")])
        with Path(__file__).with_name("alfred_known_answer.csv").open(newline="") as file:
            self.assertEqual(select_as_of(csv.DictReader(file), "2013-08-13"), [])

    def test_revisions_and_future_period_do_not_leak(self):
        from pathlib import Path
        with Path(__file__).with_name("training_vintages.csv").open(newline="") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual([r["value"] for r in select_as_of(rows, "2020-03-01")],
                         ["10", "20"])
        self.assertEqual([r["value"] for r in select_as_of(rows, "2020-03-02")],
                         ["11", "20"])
        self.assertEqual([r["value"] for r in select_as_of(rows, "2020-05-01")],
                         ["11", "20", "40"])

    def test_overlapping_vintages_fail(self):
        data = """series_id,date,realtime_start,realtime_end,value
X,2020-01-01,2020-02-01,2020-03-02,10
X,2020-01-01,2020-03-01,9999-12-31,11
"""
        with self.assertRaisesRegex(ValueError, "overlapping vintages"):
            select_as_of(csv.DictReader(io.StringIO(data)), "2020-03-01")


if __name__ == "__main__":
    unittest.main()
