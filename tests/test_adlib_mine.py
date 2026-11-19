"""adlib-mine: faollik kunlari, klasterlar, offer naqshlari, PROXY yorlig'i."""

from __future__ import annotations

import importlib
import json
import unittest
from datetime import date
from pathlib import Path

from tests._helpers import run_tool_inproc

am = importlib.import_module("adlib-mine")
FX = Path(__file__).parent / "fixtures" / "adlib"
TODAY = date(2026, 11, 19)


class AdlibMineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.res = am.mine(am.load(FX / "ads.json"), TODAY)

    def test_proxy_label(self) -> None:
        self.assertIn("PROXY", self.res["label"])
        self.assertEqual(self.res["advertisers"]["Brand X"]["activity_days"]["label"], "PROXY")

    def test_activity_days(self) -> None:
        x = self.res["advertisers"]["Brand X"]
        self.assertEqual(x["ads"], 3)
        self.assertEqual(x["active_now"], 2)
        self.assertEqual(x["activity_days"]["max"], (TODAY - date(2026, 9, 1)).days)

    def test_clusters_and_offers(self) -> None:
        x = self.res["advertisers"]["Brand X"]
        self.assertEqual(max(x["angle_clusters"], key=x["angle_clusters"].get), "narx")
        self.assertIn("foizli chegirma", x["offer_patterns"])
        self.assertIn("bepul konsultatsiya/sinov", x["offer_patterns"])
        self.assertEqual(x["variants_per_creative_group"]["g1"], 2)

    def test_counter_briefs(self) -> None:
        b = {c["vs"]: c for c in self.res["counter_briefs"]}
        self.assertEqual(b["Brand X"]["their_dominant_angle"], "narx")
        self.assertEqual(b["Brand Y"]["their_dominant_angle"], "ishonch")
        self.assertIn("gipoteza", b["Brand X"]["status"])

    def test_csv_ru(self) -> None:
        r = am.mine(am.load(FX / "ads.csv"), TODAY)
        z = r["advertisers"]["Brand Z"]
        self.assertEqual(z["angle_clusters"], {"narx": 2})
        self.assertEqual(z["active_now"], 1)

    def test_cli_and_errors(self) -> None:
        p = run_tool_inproc("adlib-mine.py", "mine", "--input", str(FX / "ads.json"), "--today", "2026-11-19")
        self.assertEqual(p.returncode, 0)
        self.assertIn("advertisers", json.loads(p.stdout))
        self.assertEqual(run_tool_inproc("adlib-mine.py", "mine", "--input", "/nope.json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
