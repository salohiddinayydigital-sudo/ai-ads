"""`tyrion.py demo` (/start demo): boshidan oxirigacha ishlaydi va mustaqil HTML hisobot chiqaradi."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._helpers import VAULT


class DemoFlowTests(unittest.TestCase):
    def test_demo_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = subprocess.run([sys.executable, str(VAULT / "tools" / "tyrion.py"), "demo", "--out", td], capture_output=True, text=True, timeout=120)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            html = (Path(td) / "demo-brand-report.html").read_text(encoding="utf-8")
            self.assertIn("<svg", html)
            self.assertNotRegex(html, r"https?://")           # CDN yo'q
            self.assertNotIn("<script src", html)
            self.assertIn("prefers-color-scheme", html)
            self.assertIn("@media print", html)
            self.assertIn("SINTETIK", html)
            pulse = json.loads(next((Path(td) / "clients" / "demo-brand" / "pulse").glob("*.json")).read_text(encoding="utf-8"))
            checks = {f["check"] for f in pulse["findings"]}
            self.assertTrue({"cpa_drift", "tracking_break", "fatigue"} <= checks, checks)
            state = json.loads((Path(td) / "clients" / "demo-brand" / "state.json").read_text(encoding="utf-8"))
            self.assertTrue(state.get("synthetic"))
            self.assertIn("baseline", state)

    def test_demo_metrics_are_synthetic_and_schema_valid(self) -> None:
        sys.path.insert(0, str(VAULT / "tools"))
        import normalize as nz
        sys.path.insert(0, str(VAULT / "examples" / "demo-brand"))
        import generate_demo_metrics as g
        doc = g.build()
        self.assertEqual(nz.validate_metrics(doc), [])
        self.assertTrue(all(r["synthetic"] for r in doc["rows"]))
        self.assertEqual(g.build(), doc)  # deterministik


if __name__ == "__main__":
    unittest.main()
