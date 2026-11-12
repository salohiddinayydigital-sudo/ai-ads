"""evals/quality/run.py: deterministik tekshiruv turlari va hakam birlashtirish."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("tyrion_quality_run", TOOLS / "evals" / "quality" / "run.py")
_qrun = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("tyrion_quality_run", _qrun)
_spec.loader.exec_module(_qrun)


class CheckOneTests(unittest.TestCase):
    def test_contains_any_passes_on_any_value(self) -> None:
        ok, _ = _qrun.check_one({"type": "contains_any", "values": ["event_id", "dedup"]}, "CAPI event_id yo'q")
        self.assertTrue(ok)

    def test_contains_any_case_insensitive(self) -> None:
        ok, _ = _qrun.check_one({"type": "contains_any", "values": ["SPEND-GUARD"]}, "Bu spend-guard talabi")
        self.assertTrue(ok)

    def test_contains_all_fails_on_missing(self) -> None:
        ok, detail = _qrun.check_one({"type": "contains_all", "values": ["a", "zzz"]}, "faqat a bor")
        self.assertFalse(ok)
        self.assertIn("zzz", detail)

    def test_forbidden_any_fails_when_found(self) -> None:
        ok, detail = _qrun.check_one({"type": "forbidden_any", "values": ["ruxsatsiz"]}, "ruxsatsiz o'zgartirish")
        self.assertFalse(ok)
        self.assertIn("ruxsatsiz", detail)

    def test_regex_any_matches_number(self) -> None:
        ok, _ = _qrun.check_one({"type": "regex_any", "values": ["198[ .,]?000"]}, "Break-even CPA: 198 000 UZS")
        self.assertTrue(ok)

    def test_no_cyrillic_detects_cyrillic_text(self) -> None:
        ok, detail = _qrun.check_one({"type": "no_cyrillic"}, "Bu cyrillic: privet — kirill harflari bilan: \u043f\u0440\u0438\u0432\u0435\u0442")
        self.assertFalse(ok)
        self.assertIn("cyrillic_chars=", detail)

    def test_no_cyrillic_passes_on_latin(self) -> None:
        ok, _ = _qrun.check_one({"type": "no_cyrillic"}, "O'zbek lotin: yangi mijoz o'quv markazi")
        self.assertTrue(ok)

    def test_line_limit_enforces_count_and_length(self) -> None:
        text = "HOOK1: " + "x" * 100 + "\nHOOK2: " + "y" * 100 + "\nHOOK3: " + "z" * 100
        ok, _ = _qrun.check_one({"type": "line_limit", "prefix": "HOOK", "min_count": 3, "max_chars": 135}, text)
        self.assertTrue(ok)

    def test_line_limit_fails_when_over_length(self) -> None:
        text = "HOOK1: " + "x" * 140
        ok, detail = _qrun.check_one({"type": "line_limit", "prefix": "HOOK", "min_count": 1, "max_chars": 135}, text)
        self.assertFalse(ok)
        self.assertIn("over_limit=1", detail)

    def test_unknown_check_type_fails_closed(self) -> None:
        ok, detail = _qrun.check_one({"type": "mystery_check"}, "matn")
        self.assertFalse(ok)
        self.assertIn("unknown_check_type", detail)


class EvaluateRunsTests(unittest.TestCase):
    def test_missing_artifact_fails_all_checks(self) -> None:
        scenarios = [{"id": "QX", "job": "audit", "checks": [{"id": "c1", "type": "contains_any", "values": ["x"]}]}]
        with tempfile.TemporaryDirectory() as tmp:
            results = _qrun.evaluate_runs(Path(tmp), scenarios)
        self.assertEqual(results[0]["deterministic"]["passed"], 0)
        self.assertEqual(results[0]["deterministic"]["checks"][0]["detail"], "artifact_missing")

    def test_evaluate_reads_artifact_and_scores(self) -> None:
        scenarios = [{"id": "QY", "job": "budget", "checks": [{"id": "c1", "type": "contains_any", "values": ["spend-guard"]}]}]
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "QY").mkdir()
            (Path(tmp) / "QY" / "artifact.md").write_text("Bu rejada Spend-Guard talabi bor.\n", encoding="utf-8")
            results = _qrun.evaluate_runs(Path(tmp), scenarios)
        self.assertEqual(results[0]["deterministic"]["passed"], 1)
        self.assertEqual(results[0]["deterministic"]["total"], 1)


class MergeJudgeTests(unittest.TestCase):
    def test_merge_clamps_and_sums(self) -> None:
        results = [{"id": "QZ", "deterministic": {}}]
        judge = {"scenarios": [{"id": "QZ", "scores": {"evidence": 2, "accuracy": 5, "actionability": 0, "language_clarity": -1}, "notes": "n"}]}
        rubric = {"criteria": {"evidence": {}, "accuracy": {}, "actionability": {}, "language_clarity": {}}}
        _qrun.merge_judge(results, judge, rubric)
        scores = results[0]["judge"]["scores"]
        self.assertEqual(scores["accuracy"], 2)
        self.assertEqual(scores["language_clarity"], 0)
        self.assertEqual(results[0]["judge"]["score"], 4)

    def test_missing_judge_scenario_leaves_none(self) -> None:
        results = [{"id": "QW", "deterministic": {}}]
        judge = {"scenarios": []}
        rubric = {"criteria": {"evidence": {}}}
        _qrun.merge_judge(results, judge, rubric)
        self.assertIsNone(results[0]["judge"]["score"])


class ScenariosFileSanityTests(unittest.TestCase):
    def test_scenarios_cover_five_jobs_and_unique_ids(self) -> None:
        doc = json.loads((TOOLS / "evals" / "quality" / "scenarios.json").read_text(encoding="utf-8"))
        scenarios = doc["scenarios"]
        self.assertEqual(len(scenarios), 12)
        jobs = {s["job"] for s in scenarios}
        self.assertEqual(jobs, {"audit", "budget", "kreativ", "hisobot", "tracking"})
        ids = [s["id"] for s in scenarios]
        self.assertEqual(len(ids), len(set(ids)))
        for sc in scenarios:
            self.assertTrue(sc["checks"], f"{sc['id']} tekshiruvsiz")
            for ch in sc["checks"]:
                self.assertIn(ch["type"], _qrun.KNOWN_CHECK_TYPES)


if __name__ == "__main__":
    unittest.main()
