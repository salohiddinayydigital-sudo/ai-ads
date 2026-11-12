"""calculator.py: son validatsiyasi va chiqish kodlari."""

from __future__ import annotations

import unittest

from tests._helpers import run_tool_inproc

import calculator  # noqa: E402


class CalculatorValidationTests(unittest.TestCase):
    def _run(self, *args: str):
        return run_tool_inproc("calculator.py", *args)

    def test_breakeven_nan_price_fails(self) -> None:
        proc = self._run("breakeven", "--price", "nan", "--cogs", "10")
        self.assertEqual(proc.returncode, 2)

    def test_breakeven_inf_and_negative(self) -> None:
        self.assertEqual(self._run("breakeven", "--price", "inf", "--cogs", "10").returncode, 2)
        self.assertEqual(self._run("breakeven", "--price", "100", "--cogs", "-1").returncode, 2)
        self.assertEqual(self._run("breakeven", "--price", "100", "--cogs", "nan").returncode, 2)
        self.assertEqual(self._run("breakeven", "--price", "100", "--cogs", "40", "--shipping", "inf").returncode, 2)

    def test_function_level_rejects_nan(self) -> None:
        for fn, kwargs in (
            (calculator.calc_breakeven, dict(price=float("nan"), cogs=10.0)),
            (calculator.calc_meta_155, dict(daily_budget=float("nan"), target_cpa=10.0)),
            (calculator.calc_meta_155, dict(daily_budget=10.0, target_cpa=float("inf"))),
            (calculator.calc_google_sculpt, dict(monthly_budget=100.0, target_cpa=float("nan"), avg_cpc=1.0)),
            (calculator.calc_telegram_funnel, dict(budget=float("nan"))),
            (calculator.calc_telegram_funnel, dict(budget=100.0, cpm=float("inf"))),
            (calculator.calc_testing_ladder, dict(total_budget=100.0, breakeven_cpa=float("nan"))),
            (calculator.calc_testing_ladder, dict(total_budget=100.0, breakeven_cpa=-3.0)),
        ):
            with self.assertRaises(ValueError, msg=f"{fn.__name__} {kwargs}"):
                fn(**kwargs)

    def test_unprofitable_result_error_is_nonzero_exit(self) -> None:
        proc = self._run("breakeven", "--price", "50", "--cogs", "60")
        self.assertNotEqual(proc.returncode, 0)

    def test_valid_runs_exit_zero(self) -> None:
        self.assertEqual(self._run("breakeven", "--price", "100", "--cogs", "40", "--json").returncode, 0)
        self.assertEqual(self._run("ladder", "--total-budget", "1000", "--breakeven-cpa", "15").returncode, 0)
        self.assertEqual(self._run("meta-155", "--daily-budget", "150", "--target-cpa", "15").returncode, 0)

    def test_nan_in_other_subcommands(self) -> None:
        self.assertEqual(self._run("meta-155", "--daily-budget", "nan", "--target-cpa", "15").returncode, 2)
        self.assertEqual(self._run("telegram-funnel", "--budget", "100", "--ctr", "nan").returncode, 2)
        self.assertEqual(self._run("google-sculpt", "--monthly-budget", "1000", "--target-cpa", "20", "--avg-cpc", "inf").returncode, 2)


if __name__ == "__main__":
    unittest.main()
