from __future__ import annotations

import unittest

from backend.members.member1.calculate_combination import calculate_combination
from backend.members.member2.build_binomial_table import build_binomial_table
from backend.members.member5.validation import validate_team_inputs


class TeamProjectTests(unittest.TestCase):
    def test_calculate_combination_returns_expected_value(self) -> None:
        self.assertEqual(calculate_combination(10, 4), 210)
        self.assertEqual(calculate_combination(6, 2), 15)

    def test_build_binomial_table_contains_expected_answer(self) -> None:
        table = build_binomial_table(10)
        self.assertEqual(table[10][4], 210)
        self.assertEqual(table[6][2], 15)

    def test_validation_accepts_valid_values(self) -> None:
        self.assertEqual(validate_team_inputs("10", "4"), (10, 4))

    def test_validation_rejects_team_size_larger_than_total(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Developers per team cannot be larger than the total developers.",
        ):
            validate_team_inputs("4", "10")


if __name__ == "__main__":
    unittest.main()
