"""--metrics / --from-metrics: ad-export-analyzer, creative-matrix (fatigue/iterate), calculator (metrics.v1)."""

from __future__ import annotations

import json
import unittest

from tests._helpers import VAULT, run_tool_inproc

FIX = str(VAULT / "tests" / "fixtures" / "metrics" / "legacy_creative.json")
BAD = str(VAULT / "tests" / "fixtures" / "metrics" / "does_not_exist.json")


def _json(proc):
    return json.loads(proc.stdout)


class AnalyzerMetricsTests(unittest.TestCase):
    def test_analyze_from_metrics_matches_totals(self) -> None:
        p = run_tool_inproc("ad-export-analyzer.py", "analyze", "--metrics", FIX, "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        res = _json(p)
        self.assertAlmostEqual(res["summary"]["total_spend"] if "summary" in res else res["total_spend"], 8 * 70.0, places=1)

    def test_requires_file_or_metrics(self) -> None:
        self.assertEqual(run_tool_inproc("ad-export-analyzer.py", "analyze", "--json").returncode, 2)

    def test_bad_metrics_file_exit_2(self) -> None:
        self.assertEqual(run_tool_inproc("ad-export-analyzer.py", "analyze", "--metrics", BAD, "--json").returncode, 2)


class CreativeMetricsTests(unittest.TestCase):
    def test_fatigue_from_metrics_detects_ctr_drop_and_frequency(self) -> None:
        p = run_tool_inproc("creative-matrix.py", "fatigue", "--metrics", FIX, "--entity-id", "ad_a", "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        src = _json(p)["metrics_source"]
        self.assertEqual(src["hook_rate"], 20.0)
        self.assertEqual(src["hold_rate"], 15.0)
        self.assertGreater(src["ctr_drop_pct"], 20.0)
        self.assertGreater(src["frequency"], 2.0)
        self.assertEqual(src["evidence_label"], "MEASURED_ACCOUNT_DATA")

    def test_fatigue_manual_arg_overrides_metrics(self) -> None:
        p = run_tool_inproc("creative-matrix.py", "fatigue", "--metrics", FIX, "--entity-id", "ad_a", "--hook-rate", "40", "--json")
        self.assertEqual(p.returncode, 0)
        self.assertIn("40.0", json.dumps(_json(p)))

    def test_fatigue_without_video_data_is_error(self) -> None:
        p = run_tool_inproc("creative-matrix.py", "fatigue", "--metrics", FIX, "--entity-id", "ad_b", "--json")
        self.assertEqual(p.returncode, 2)

    def test_fatigue_unknown_entity_error(self) -> None:
        self.assertEqual(run_tool_inproc("creative-matrix.py", "fatigue", "--metrics", FIX, "--entity-id", "nope", "--json").returncode, 2)

    def test_iterate_from_metrics(self) -> None:
        p = run_tool_inproc("creative-matrix.py", "iterate", "--metrics", FIX, "--entity-id", "ad_a", "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        res = _json(p)
        self.assertEqual(res["metrics_source"]["hook_rate"], 20.0)


class CalculatorMetricsTests(unittest.TestCase):
    def test_breakeven_price_from_median_aov(self) -> None:
        p = run_tool_inproc("calculator.py", "breakeven", "--from-metrics", FIX, "--cogs", "10", "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        res = _json(p)
        self.assertEqual(res["from_metrics"]["median_aov"], 50.0)

    def test_manual_price_wins(self) -> None:
        a = _json(run_tool_inproc("calculator.py", "breakeven", "--from-metrics", FIX, "--price", "100", "--cogs", "10", "--json"))
        b = _json(run_tool_inproc("calculator.py", "breakeven", "--price", "100", "--cogs", "10", "--json"))
        for k, v in b.items():
            self.assertEqual(a[k], v, k)

    def test_ladder_cpa_suggestion(self) -> None:
        p = run_tool_inproc("calculator.py", "ladder", "--total-budget", "1000", "--from-metrics", FIX, "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIsNotNone(_json(p)["from_metrics"]["median_cpa"])

    def test_missing_price_without_metrics_fails(self) -> None:
        self.assertEqual(run_tool_inproc("calculator.py", "breakeven", "--cogs", "10", "--json").returncode, 2)

    def test_bad_metrics_file(self) -> None:
        self.assertEqual(run_tool_inproc("calculator.py", "breakeven", "--from-metrics", BAD, "--cogs", "1", "--json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
