"""call-insights: consent, PII redaksiya, e'tiroz aniqlash, kichik namuna himoyasi (sintetik fixture)."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc

ci = importlib.import_module("call-insights")
FX = Path(__file__).parent / "fixtures" / "calls" / "calls.json"


class CallInsightsTests(unittest.TestCase):
    def test_consent_drop(self) -> None:
        calls, dropped = ci.load_calls(FX)
        self.assertEqual((len(calls), dropped), (4, 1))

    def test_redact(self) -> None:
        out = ci.redact("Raqamim +998 90 123 45 67, ali@example.test")
        self.assertNotIn("998", out)
        self.assertNotIn("@", out)

    def test_detect(self) -> None:
        found, buy = ci.detect("Bu juda qimmat, boshqa joyda arzonroq")
        self.assertEqual(found, {"narx", "raqobatchi"})
        self.assertFalse(buy)
        found, buy = ci.detect("Qachon kelay?")
        self.assertTrue(buy)
        found, _ = ci.detect("Я не оставлял заявку. В рекламе была другая цена.")
        self.assertTrue({"sorov_yoq", "vada_mos_emas", "narx"} <= found)

    def test_analyze_by_ad(self) -> None:
        calls, _ = ci.load_calls(FX)
        s = ci.analyze(calls, "ad")
        self.assertEqual(s["A1"]["calls"], 2)
        self.assertEqual(s["A1"]["good_rate"], 0.5)
        self.assertEqual(s["A2"]["no_answer_rate"], 0.5)

    def test_cli_small_sample_warning(self) -> None:
        r = run_tool_inproc("call-insights.py", "report", "--input", str(FX))
        self.assertEqual(r.returncode, 0)
        self.assertIn("KICHIK NAMUNA", r.stdout)
        self.assertNotIn("+998", r.stdout)

    def test_brief_respects_min_calls(self) -> None:
        r = run_tool_inproc("call-insights.py", "brief", "--input", str(FX), "--min-calls", "2")
        self.assertIn("A1 | narx", r.stdout)

    def test_missing_file(self) -> None:
        r = run_tool_inproc("call-insights.py", "report", "--input", "/nonexistent")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
