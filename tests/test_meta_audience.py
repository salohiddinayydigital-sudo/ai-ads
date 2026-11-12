"""MetaAudienceTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import unittest



class MetaAudienceTests(unittest.TestCase):
    """meta-audience — Meta Ads Andromeda 2 auditoriya arxitekturasi, overlap va saturation."""

    def setUp(self) -> None:
        import importlib
        self.ma = importlib.import_module("meta-audience")

    def test_architect_builds_4_layers_and_exclusions(self) -> None:
        res = self.ma.build_architecture(
            niche="ecom", daily_budget=150.0, geo="tashkent", has_pixel=True, has_crm=True
        )
        self.assertEqual(len(res["audience_layers"]), 4)
        self.assertEqual(len(res["exclusion_matrix"]), 4)
        self.assertIn("Purchase_180d", res["audience_layers"][0]["exclusions"])

    def test_overlap_detects_collision_and_healthy_isolation(self) -> None:
        high = self.ma.calc_overlap(size_a=180000, size_b=120000, shared=45000)
        self.assertEqual(high["status"], "CRITICAL_COLLISION")
        self.assertAlmostEqual(high["overlap_of_smaller_pct"], 37.5, places=1)

        low = self.ma.calc_overlap(size_a=200000, size_b=150000, shared=15000)
        self.assertEqual(low["status"], "HEALTHY_ISOLATION")
        self.assertEqual(low["overlap_of_smaller_pct"], 10.0)

    def test_saturation_calculates_fatigue_day(self) -> None:
        sat = self.ma.calc_saturation(audience_size=250000, daily_budget=80.0, cpm=3.2, days=14)
        self.assertEqual(sat["status"], "HEALTHY_CAPACITY")
        self.assertGreater(sat["estimated_fatigue_day"], 14.0)

        oversat = self.ma.calc_saturation(audience_size=30000, daily_budget=150.0, cpm=4.0, days=14)
        self.assertEqual(oversat["status"], "OVERSATURATED_HIGH_RISK")

    def test_interests_returns_curated_taxonomy(self) -> None:
        info = self.ma.get_interests(niche="real-estate")
        self.assertIn("Real estate", info["core_interest_clusters"])
        self.assertTrue(info["uzbekistan_solventnost_filters"])

    def test_retargeting_builds_4_windows(self) -> None:
        res = self.ma.calc_retargeting(aov=250.0, daily_visitors=400, ig_engagers_30d=12000, video_viewers_14d=18000)
        self.assertEqual(len(res["retargeting_windows"]), 4)
        self.assertGreater(res["recommended_retargeting_daily_budget_usd"], 0)

    def test_lookalike_scores_seed_quality(self) -> None:
        strong = self.ma.calc_lookalike(seed_size=1200, seed_type="purchase_ltv", country="UZ")
        self.assertEqual(strong["seed_quality_score_100"], 100)
        self.assertEqual(len(strong["lal_tiers"]), 4)

        weak = self.ma.calc_lookalike(seed_size=80, seed_type="ig_engagers", country="UZ")
        self.assertLess(weak["seed_quality_score_100"], 40)

    def test_diagnose_identifies_hook_and_lp_bottlenecks(self) -> None:
        diag = self.ma.diagnose_metrics(cpm=3.5, ctr=0.6, cpc=0.58, lp_cvr=12.0, lead_to_sale=10.0)
        self.assertEqual(diag["overall_health"], "CRITICAL_BOTTLENECK_FOUND")
        self.assertTrue(any(b["stage"] == "HOOK_AND_CREATIVE_STOP_RATE" for b in diag["bottlenecks"]))


if __name__ == "__main__":
    unittest.main()
