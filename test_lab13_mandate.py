"""Lab 13 course case checks for mandate and covariance math."""

import unittest

from lab13_mandate import BENCHMARK, CORR, EQUAL_WEIGHT, mandate_verdict, search, stats


class MeridianKnownAnswers(unittest.TestCase):
    def test_benchmark_has_covariance_and_fails_reserve(self):
        expected_return, volatility, reserve = stats(BENCHMARK)
        self.assertAlmostEqual(expected_return, .068)
        self.assertAlmostEqual(volatility, .1046135746, places=8)
        self.assertEqual(reserve, 0)

    def test_base_and_challenges(self):
        base = search()
        self.assertEqual(base[0], (0, .20, .25, .55))
        self.assertAlmostEqual(base[2], .0944, delta=.0001)
        stressed = search(equity_adjustment=-.01)
        self.assertEqual(stressed[0], (0, .10, .10, .80))
        corr = CORR.copy()
        corr[2, 3] = corr[3, 2] = .50
        changed = search(correlation=corr)
        self.assertEqual(changed[0], (0, .40, 0, .60))

    def test_three_mandate_screen_verdicts(self):
        equal = stats(EQUAL_WEIGHT)
        benchmark = stats(BENCHMARK)
        chosen = search()
        self.assertEqual(mandate_verdict(EQUAL_WEIGHT, equal[0], equal[2], .065, .03)[0], "FAIL")
        self.assertIn("Return proxy", mandate_verdict(EQUAL_WEIGHT, equal[0], equal[2], .065, .03)[1][0])
        self.assertEqual(mandate_verdict(BENCHMARK, benchmark[0], benchmark[2], .065, .03)[0], "FAIL")
        self.assertIn("Eligible reserve", mandate_verdict(BENCHMARK, benchmark[0], benchmark[2], .065, .03)[1][0])
        self.assertEqual(mandate_verdict(chosen[0], chosen[1], chosen[3], .065, .03)[0], "PASS")


if __name__ == "__main__":
    unittest.main()
