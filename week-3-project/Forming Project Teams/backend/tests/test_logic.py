from __future__ import annotations

import unittest

from backend.member.member1.calculate_combination import calculate_combination
from backend.member.member2.build_binomial_table import build_binomial_table
from backend.validation import validate_team_inputs


class TestCalculateCombination(unittest.TestCase):
    def test_returns_expected_value(self):
        self.assertEqual(calculate_combination(5, 2), 10)
        self.assertEqual(calculate_combination(10, 3), 120)
        self.assertEqual(calculate_combination(0, 0), 1)
        self.assertEqual(calculate_combination(5, 0), 1)
        self.assertEqual(calculate_combination(5, 5), 1)


class TestBuildBinomialTable(unittest.TestCase):
    def test_contains_expected_answer(self):
        table = build_binomial_table(10)
        self.assertEqual(table[10][4], 210)
        self.assertEqual(table[6][2], 15)


class TestValidation(unittest.TestCase):
    def test_accepts_valid_values(self) -> None:
        self.assertEqual(validate_team_inputs("10", "4"), (10, 4))

    def test_rejects_team_size_larger_than_total(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Developers per team cannot be larger than the total developers.",
        ):
            validate_team_inputs("4", "10")

    def test_validate_rejects_negative_numbers(self):
        with self.assertRaises(ValueError):
            validate_team_inputs("-1", "2")

    def test_validate_rejects_non_integer(self):
        with self.assertRaises(ValueError):
            validate_team_inputs("abc", "2")

    def test_validate_rejects_empty_input(self):
        with self.assertRaises(ValueError):
            validate_team_inputs("", "")


if __name__ == "__main__":
    unittest.main()
