"""Lab 13 course case checks for mandate and covariance math."""

import unittest

from lab13_mandate import (BENCHMARK, CORR, EQUAL_WEIGHT, loss95, mandate_verdict, proxy_window,
                           search, signal_yield, stats)


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

    def test_loss_limit_verdicts_and_stop(self):
        benchmark = stats(BENCHMARK)
        chosen = search(loss_limit=.10)
        self.assertEqual(chosen[0], (0, .20, .25, .55))
        self.assertAlmostEqual(loss95(chosen[1], chosen[2]), .0902, delta=.0001)
        self.assertEqual(mandate_verdict(chosen[0], chosen[1], chosen[3], .065, .03, chosen[2], .10)[0], "PASS")
        verdict, reasons = mandate_verdict(BENCHMARK, benchmark[0], benchmark[2], .065, .03, benchmark[1], .10)
        self.assertEqual(verdict, "FAIL")
        self.assertTrue(any("95% one-year loss" in reason for reason in reasons))
        self.assertIsNone(search(equity_adjustment=-.01, loss_limit=.10))
        self.assertIsNone(search(target=.07, loss_limit=.10))

    def test_signal_and_window_stresses(self):
        self.assertEqual(signal_yield()[1], 4.98)
        self.assertEqual(search(ten_year_return=.0498, loss_limit=.10)[0], (.05, .40, 0, .55))
        self.assertEqual(proxy_window()[0], (.65, 0, .35))
        self.assertEqual(proxy_window(36)[0], (.85, 0, .15))


if __name__ == "__main__":
    unittest.main()
