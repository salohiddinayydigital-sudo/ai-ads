"""creative-analytics: Wilson, nomlash, minimal namuna, g'olib/o'chirish, xilma-xillik."""

from __future__ import annotations

import importlib
import json
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc

ca = importlib.import_module("creative-analytics")
FX = Path(__file__).parent / "fixtures" / "creative"


class CreativeAnalyticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.res = ca.analyze(ca.load_rows(str(FX / "metrics.json")),
                              json.loads((FX / "creatives.json").read_text())["creatives"], "Lead")

    def test_wilson_known_values(self) -> None:
        lo, hi = ca.wilson(50, 100)
        self.assertAlmostEqual(lo, 0.4038, places=3)
        self.assertAlmostEqual(hi, 0.5962, places=3)
        self.assertIsNone(ca.wilson(0, 0))
        self.assertEqual(ca.wilson(0, 10)[0], 0.0)

    def test_parse_name(self) -> None:
        self.assertEqual(ca.parse_name("PRICE_QUESTION_UGC_MOM_v2")["persona"], "mom")
        self.assertEqual(ca.parse_name("random name"), {})

    def test_metric_definitions(self) -> None:
        a1 = self.res["ads"]["a1"]
        self.assertEqual(a1["hook_rate"], 0.3)
        self.assertEqual(a1["hold_rate"], 0.4)
        self.assertEqual(a1["cpa"], 7.5)
        self.assertEqual(a1["roas"], round(40 * 20 / 300, 3))
        self.assertEqual(self.res["ads"]["a4"]["hook_rate"], None)

    def test_min_sample_rule(self) -> None:
        a6 = self.res["ads"]["a6"]
        self.assertFalse(a6["sufficient"])
        self.assertEqual(a6["verdict_note"], "ma'lumot yetarli emas")
        self.assertNotIn("a6", [k["ad_id"] for k in self.res["kill_list"]])

    def test_winner_dna_and_kill(self) -> None:
        self.assertEqual(self.res["winner_dna"]["angle"]["value"], "price")
        self.assertEqual(self.res["winner_dna"]["format"]["value"], "ugc")
        self.assertEqual([k["ad_id"] for k in self.res["kill_list"]], ["a5"])

    def test_briefs_untested_and_max3(self) -> None:
        b = self.res["next_briefs"]
        self.assertTrue(1 <= len(b) <= 3)
        tested = {(t["tags"].get("angle"), t["tags"].get("hook_type"), t["tags"].get("format")) for t in self.res["ads"].values()}
        for x in b:
            self.assertNotIn((x["angle"], x["hook_type"], x["format"]), tested)

    def test_diversity(self) -> None:
        mono = ca.diversity_score([{"angle": "a", "hook_type": "h", "format": "f", "persona": "p"}] * 4)
        self.assertEqual(mono["score"], 0.0)
        div = ca.diversity_score([{"angle": str(i), "hook_type": str(i), "format": str(i), "persona": str(i)} for i in range(4)])
        self.assertEqual(div["score"], 100.0)

    def test_cli(self) -> None:
        p = run_tool_inproc("creative-analytics.py", "analyze", "--metrics", str(FX / "metrics.json"), "--creatives", str(FX / "creatives.json"))
        self.assertEqual(p.returncode, 0)
        self.assertIn("definitions", json.loads(p.stdout))
        self.assertEqual(run_tool_inproc("creative-analytics.py", "suggest-tags", "--metrics", "/nope").returncode, 2)


if __name__ == "__main__":
    unittest.main()
