import csv
import unittest

from training_gate import TABLE, economic_flags, gate, signals


class TrainingGateTests(unittest.TestCase):
    def test_known_answer_and_signal(self):
        with TABLE.open(newline="") as source:
            decisions, admitted = gate(csv.DictReader(source))
        self.assertEqual([int(row["row"]) for row in admitted], [1, 4, 5, 6, 9, 12])
        self.assertEqual(decisions[7], "removed: exact duplicate of row 6")
        self.assertEqual(decisions[2], "removed: superseded by row 4")
        self.assertEqual(decisions[11], "quarantined: missing ticker")
        self.assertEqual([i for i, value in decisions.items() if "published after" in value],
                         [3, 8, 10])
        actual = signals(admitted)
        self.assertAlmostEqual(actual["AAA"]["return"], 103 / 101 - 1)
        self.assertAlmostEqual(actual["BBB"]["return"], 97 / 98 - 1)
        self.assertAlmostEqual(actual["CCC"]["return"], 111 / 110 - 1)
        flags = economic_flags(admitted)
        self.assertEqual(len(flags), 6)  # Four above-par rows; two months of bad ordering.
        self.assertTrue(any("2026-02: credit-price order fails" in flag for flag in flags))


if __name__ == "__main__":
    unittest.main()
