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


class CalculatorTests(unittest.TestCase):
    """Calculator — Media matematikasi (Meta, Google, Telegram)."""

    def setUp(self) -> None:
        import calculator
        self.calc = calculator

    def test_breakeven_math(self) -> None:
        res = self.calc.calc_breakeven(price=100.0, cogs=40.0, shipping=10.0, processing_fee_pct=2.0)
        self.assertEqual(res["price"], 100.0)
        self.assertEqual(res["cogs"], 40.0)
        self.assertEqual(res["shipping"], 10.0)
        self.assertEqual(res["processing_fee"], 2.0)
        self.assertEqual(res["gross_profit_per_unit"], 48.0)
        self.assertEqual(res["breakeven_cpa"], 48.0)
        self.assertAlmostEqual(res["breakeven_roas"], 2.08, places=2)

    def test_meta_155_allocations(self) -> None:
        res = self.calc.calc_meta_155(daily_budget=200.0, target_cpa=20.0)
        alloc = res["allocations"]
        self.assertEqual(alloc["broad_prospecting_70pct"], 140.0)
        self.assertEqual(alloc["advantage_plus_25pct"], 50.0)
        self.assertEqual(alloc["reserve_5pct"], 10.0)

    def test_google_sculpt_channel_split(self) -> None:
        res = self.calc.calc_google_sculpt(monthly_budget=3000.0, target_cpa=25.0, avg_cpc=1.8, irrelevant_query_waste_pct=20.0)
        split = res["channel_split"]
        self.assertEqual(split["search_coliseum_60pct"], 1800.0)
        self.assertEqual(split["pmax_demandgen_40pct"], 1200.0)
        neg = res["negative_keyword_optimization"]
        self.assertEqual(neg["projected_monthly_waste_saved"], 360.0)

    def test_telegram_funnel_math(self) -> None:
        res = self.calc.calc_telegram_funnel(budget=600.0, cpm=3.0, ctr_pct=1.0, bot_start_pct=50.0, lead_activation_pct=20.0, order_conversion_pct=10.0, aov=50.0)
        self.assertEqual(res["impressions"], 200000)
        self.assertEqual(res["clicks"], 2000)
        self.assertEqual(res["bot_starts"], 1000)
        self.assertEqual(res["qualified_leads"], 200)
        self.assertEqual(res["orders_closed"], 20)
        self.assertEqual(res["projected_revenue"], 1000.0)

    def test_ladder_phase_split(self) -> None:
        res = self.calc.calc_testing_ladder(total_budget=1000.0, breakeven_cpa=15.0)
        phases = res["phases"]
        self.assertEqual(phases["phase_1_sandbox"]["allocated_budget"], 150.0)
        self.assertEqual(phases["phase_2_validation"]["allocated_budget"], 350.0)
        self.assertEqual(phases["phase_3_scale"]["allocated_budget"], 500.0)


if __name__ == "__main__":
    unittest.main()
