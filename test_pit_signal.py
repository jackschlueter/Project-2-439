"""DGS10 as-of snapshot and leakage gate checks."""

import unittest

from pit_signal import ROOT, read_vintage


class DGS10SnapshotTests(unittest.TestCase):
    def test_earlier_vintage_excludes_later_observations(self):
        early = read_vintage((ROOT / "dgs10_2026-10-31.csv").read_text(), "2026-10-31")
        later = read_vintage((ROOT / "dgs10_2026-11-03.csv").read_text(), "2026-11-03")
        self.assertEqual((early[-1][0].isoformat(), early[-1][1]), ("2026-10-29", 4.98))
        self.assertEqual((later[-1][0].isoformat(), later[-1][1]), ("2026-11-02", 4.91))
        self.assertNotIn("2026-10-30", [day.isoformat() for day, _ in early])

    def test_reject_wrong_vintage_or_future_observation(self):
        raw = "observation_date,DGS10_20261031\n2026-10-29,4.98\n2026-11-02,4.91\n"
        with self.assertRaisesRegex(ValueError, "future observation"):
            read_vintage(raw, "2026-10-31")
        with self.assertRaisesRegex(ValueError, "exact ALFRED columns"):
            read_vintage(raw, "2026-11-03")


if __name__ == "__main__":
    unittest.main()
