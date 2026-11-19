"""client-workspace.py v2: state, baseline, decisions."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc

cw = importlib.import_module("client-workspace")
FX = Path(__file__).resolve().parent / "fixtures" / "report" / "metrics.json"


def row(date, spend, imp, clk, lead, freq=1.0, level="campaign"):
    return {"date": date, "platform": "meta", "account_id": "a", "level": level, "entity_id": "c1", "spend": spend,
            "impressions": imp, "clicks": clk, "frequency": freq, "conversions": {"Lead": lead}}


class StateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = self.td.name

    def run_cw(self, *a):
        return run_tool_inproc("client-workspace.py", *a, "--root", self.root)

    def test_init_get_set_validate(self) -> None:
        p = self.run_cw("init", "--client", "Nur Residence", "--target-cpa", "8", "--margin-pct", "25", "--aov", "100", "--synthetic")
        self.assertEqual(p.returncode, 0, p.stderr)
        st = cw.load_state("nur-residence", Path(self.root))
        self.assertEqual(st["goals"]["target_cpa"], 8.0)
        self.assertEqual(st["economics"]["breakeven_roas"], 4.0)
        self.assertEqual(cw.validate_state(st), [])
        self.assertTrue((Path(self.root) / "nur-residence" / "data" / "raw").is_dir())
        g = self.run_cw("state", "get", "goals.target_cpa", "--client", "nur-residence")
        self.assertEqual(json.loads(g.stdout), 8.0)
        self.assertEqual(self.run_cw("state", "set", "goals.target_cpa", "9.5", "--client", "nur-residence").returncode, 0)
        self.assertEqual(cw.load_state("nur-residence", Path(self.root))["goals"]["target_cpa"], 9.5)
        self.assertEqual(self.run_cw("state", "set", "goals.target_cpa", "-3", "--client", "nur-residence").returncode, 2)
        self.assertEqual(cw.load_state("nur-residence", Path(self.root))["goals"]["target_cpa"], 9.5)
        self.assertEqual(self.run_cw("state", "validate", "--client", "nur-residence").returncode, 0)
        self.assertEqual(self.run_cw("state", "get", "no.such", "--client", "nur-residence").returncode, 2)

    def test_init_idempotent_and_missing(self) -> None:
        self.run_cw("init", "--client", "a")
        self.run_cw("state", "set", "name", '"Changed"', "--client", "a")
        self.run_cw("init", "--client", "a")
        self.assertEqual(cw.load_state("a", Path(self.root))["name"], "Changed")
        self.assertEqual(self.run_cw("state", "validate", "--client", "ghost").returncode, 2)

    def test_validate_detects_errors(self) -> None:
        errs = cw.validate_state({"schema": "x", "slug": "Bad Slug", "language": "de"})
        self.assertGreaterEqual(len(errs), 4)
        bad = {"schema": "client-state.v1", "slug": "a", "name": "A", "language": "uz", "market": "uz", "goals": {}, "updated": "x",
               "next_steps": [{"action": "do"}]}
        self.assertTrue(any("next_steps" in e for e in cw.validate_state(bad)))

    def test_scaffold_still_works(self) -> None:
        p = self.run_cw("new", "--client", "Old Style", "--niche", "ecom", "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue((Path(self.root) / "old-style" / "BRIEF.md").is_file())

    def test_decisions(self) -> None:
        self.run_cw("init", "--client", "d")
        self.run_cw("decision", "add", "Byudjet +15%", "--why", "CPA<target", "--owner", "mb", "--metric", "CPA", "--client", "d")
        out = json.loads(self.run_cw("decision", "list", "--client", "d").stdout)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["owner"], "mb")


class BaselineTests(unittest.TestCase):
    def test_median_known_values(self) -> None:
        rows = [row("2026-10-01", 10, 1000, 20, 2), row("2026-10-02", 20, 1000, 20, 2), row("2026-10-03", 90, 1000, 20, 3, freq=3.0)]
        b = cw.compute_baseline(rows, event="Lead")
        self.assertEqual(b["cpa"], 10.0)            # kunlik CPA: 5, 10, 30 -> median 10
        self.assertEqual(b["cpm"], 20.0)            # 10, 20, 90 -> 20
        self.assertAlmostEqual(b["ctr"], 0.02)
        self.assertAlmostEqual(b["cvr"], 0.1)       # 0.1, 0.1, 0.15 -> 0.1
        self.assertEqual(b["frequency"], 1.0)
        self.assertEqual(b["days_used"], 3)
        self.assertEqual(b["evidence_label"], "MEASURED_ACCOUNT_DATA")

    def test_window_excludes_old_days(self) -> None:
        rows = [row("2026-08-01", 1000, 1000, 10, 1), row("2026-10-30", 10, 1000, 10, 5)]
        b = cw.compute_baseline(rows, event="Lead")
        self.assertEqual(b["days_used"], 1)
        self.assertEqual(b["cpa"], 2.0)

    def test_level_pick_avoids_double_count(self) -> None:
        rows = [row("2026-10-01", 10, 1000, 10, 2), row("2026-10-01", 10, 1000, 10, 2, level="ad")]
        self.assertEqual(cw.compute_baseline(rows, event="Lead")["cpa"], 5.0)

    def test_empty_and_zero_conversions(self) -> None:
        self.assertIn("error", cw.compute_baseline([]))
        self.assertIsNone(cw.compute_baseline([row("2026-10-01", 10, 1000, 10, 0)], event="Lead")["cpa"])

    def test_cli_writes_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_tool_inproc("client-workspace.py", "init", "--client", "b", "--root", td)
            p = run_tool_inproc("client-workspace.py", "baseline", "--client", "b", "--metrics", str(FX), "--root", td, "--level", "ad")
            self.assertEqual(p.returncode, 0, p.stderr)
            st = cw.load_state("b", Path(td))
            self.assertEqual(st["baseline"]["window_days"], 28)
            self.assertEqual(st["baseline"]["days_used"], 28)
            self.assertEqual(run_tool_inproc("client-workspace.py", "baseline", "--client", "b", "--metrics", "/nope.json", "--root", td).returncode, 2)


if __name__ == "__main__":
    unittest.main()
