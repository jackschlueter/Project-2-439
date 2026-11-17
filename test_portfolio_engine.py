"""Check the published mandate's known-answer scenarios and input gate."""

import unittest
from pathlib import Path

from portfolio_engine import estimate, optimize, read_prices, rebalance


ROOT = Path(__file__).resolve().parent


class PortfolioKnownAnswers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dates, prices = read_prices(ROOT / "prices.csv")
        cls.all_months = estimate(dates, prices)
        cls.last_36 = estimate(dates, prices, 36)

    def test_mandate_scenarios(self):
        cases = ((self.all_months, 0, (.45, 0, .55, 0)),
                 (self.all_months, -.01, (.35, 0, .65, 0)),
                 (self.last_36, 0, (.75, 0, .25, 0)))
        for estimates, vt_edit, expected in cases:
            with self.subTest(months=estimates.months, vt_edit=vt_edit):
                mix = optimize(estimates, .082, .10, vt_edit)
                self.assertEqual(mix.weights, expected)
                self.assertGreaterEqual(mix.gross_return, .082 - 1e-12)

    def test_rebalance_requires_full_weight(self):
        with self.assertRaisesRegex(ValueError, "total 100%"):
            rebalance((.5, 0, .4, 0), (.45, 0, .55, 0), 100000)


if __name__ == "__main__":
    unittest.main()
