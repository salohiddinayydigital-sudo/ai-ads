"""audit_scoring.py: health + evidence coverage."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc

import audit_scoring as a  # noqa: E402


def chk(i, status, sev="medium", ev="MEASURED_ACCOUNT_DATA"):
    return {"id": i, "status": status, "severity": sev, "evidence_label": ev}


class AuditScoringTests(unittest.TestCase):
    def test_known_values(self) -> None:
        r = a.score([chk("a", "pass", "critical"), chk("b", "fail", "high"), chk("c", "warn", "low"), chk("d", "unknown"), chk("e", "n_a")])
        # (5*1 + 3*0 + 1*0.5) / 9 = 61.1
        self.assertEqual(r["health"], 61.1)
        self.assertEqual(r["evidence_coverage_pct"], 75.0)  # 3 baholangan / 4 qo'llanadigan
        self.assertEqual(r["unknown_ids"], ["d"])
        self.assertEqual(r["critical_failures"], [])

    def test_unknown_not_counted_in_health(self) -> None:
        self.assertEqual(a.score([chk("a", "pass"), chk("b", "unknown", "critical")])["health"], 100.0)

    def test_nothing_scored(self) -> None:
        r = a.score([chk("a", "unknown"), chk("b", "n_a")])
        self.assertIsNone(r["health"])
        self.assertEqual(r["evidence_coverage_pct"], 0.0)
        self.assertIsNone(a.score([chk("b", "n_a")])["evidence_coverage_pct"])

    def test_critical_failure_listed(self) -> None:
        self.assertEqual(a.score([chk("x", "fail", "critical")])["critical_failures"], ["x"])

    def test_validation_errors(self) -> None:
        self.assertIn("error", a.score([{"id": "a", "status": "ok", "severity": "high", "evidence_label": "MEASURED_ACCOUNT_DATA"}]))
        self.assertIn("error", a.score([chk("a", "pass"), chk("a", "fail")]))
        self.assertIn("error", a.score([chk("a", "pass", ev="UNVERIFIED")]))
        self.assertTrue(a.validate_checks("x"))

    def test_cli(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "c.json"
            p.write_text(json.dumps({"checks": [chk("a", "pass")]}))
            proc = run_tool_inproc("audit_scoring.py", "score", "--checks", str(p), "--json")
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(json.loads(proc.stdout)["health"], 100.0)
            p.write_text(json.dumps([chk("a", "bad")]))
            self.assertEqual(run_tool_inproc("audit_scoring.py", "score", "--checks", str(p)).returncode, 2)
            self.assertEqual(run_tool_inproc("audit_scoring.py", "score", "--checks", str(Path(td) / "nope")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
