"""report-html.py: mustaqil HTML, tillar, lenient kirishlar."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc

rh = importlib.import_module("report-html")
FX = Path(__file__).resolve().parent / "fixtures" / "report"


class ReportHtmlTests(unittest.TestCase):
    def _gen(self, lang: str, **extra):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        out, md = Path(td.name) / "r.html", Path(td.name) / "r.md"
        args = ["--state", str(FX / "state.json"), "--metrics", str(FX / "metrics.json"), "--ledger", str(FX / "ledger.jsonl"),
                "--pulse", str(FX / "pulse.json"), "--lang", lang, "--out", str(out), "--md", str(md)]
        proc = run_tool_inproc("report-html.py", *args)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return out.read_text(encoding="utf-8"), md.read_text(encoding="utf-8")

    def test_self_contained(self) -> None:
        h, _ = self._gen("uz")
        self.assertTrue(h.startswith("<!doctype html>"))
        for bad in ("http://", "https://", "<script", "<link", "@import"):
            self.assertNotIn(bad, h)
        self.assertIn("prefers-color-scheme:dark", h)
        self.assertIn("@media print", h)
        self.assertIn("<svg", h)
        self.assertIn("SINTETIK", h)

    def test_languages(self) -> None:
        self.assertIn("Natijalar hisoboti", self._gen("uz")[0])
        self.assertIn("Отчёт о результатах", self._gen("ru")[0])
        self.assertIn("Performance report", self._gen("en")[0])

    def test_sections_and_values(self) -> None:
        _, md = self._gen("en")
        for s in ("## Key metrics", "## By channel", "## Experiments", "## Creative ranking", "## Alerts", "## Next steps"):
            self.assertIn(s, md)
        self.assertIn("UGC vs Static", md)
        self.assertIn("frequency_fatigue", md)
        self.assertIn("media-buyer", md)
        self.assertIn("target: 8.00", md)

    def test_model_math(self) -> None:
        rows = [{"date": "2026-01-01", "platform": "meta", "level": "campaign", "spend": 100, "impressions": 10000, "clicks": 200,
                 "conversions": {"Lead": 10}, "conversion_value": 300}]
        m = rh.build_model({"goals": {"target_cpa": 12, "primary_event": "Lead"}}, rows, [], [], "en")
        self.assertAlmostEqual(m["total"]["cpa"], 10.0)
        self.assertAlmostEqual(m["total"]["roas"], 3.0)
        self.assertAlmostEqual(m["total"]["ctr"], 0.02)
        self.assertEqual(rh._tiles(m)[2]["s"], "good")

    def test_empty_and_lenient_inputs(self) -> None:
        m = rh.build_model({}, [], [{"weird": 1}], {"unknown": []}, "uz")
        h = rh.render_html(m)
        self.assertIn("<html", h)
        m2 = rh.build_model({}, [], [], [{"severity": "high", "title": "x", "extra": {"a": 1}}], "en")
        self.assertEqual(m2["alerts"][0]["title"], "x")

    def test_escaping(self) -> None:
        m = rh.build_model({"name": "<b>X</b>"}, [], [], [], "en")
        self.assertNotIn("<b>X</b>", rh.render_html(m))

    def test_no_input_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(run_tool_inproc("report-html.py", "--root", td, "--client", "ghost", "--out", str(Path(td) / "o.html")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
