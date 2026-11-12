"""TyrionV5CalibratedAuditTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import unittest

from tests._helpers import TOOLS, VAULT

import catalog  # noqa: E402



class TyrionV5CalibratedAuditTests(unittest.TestCase):
    """Tyrion v5.0 — 8 ta texnik audit kamchiligini yopuvchi maxsus regressiya testlari."""

    def setUp(self) -> None:
        import importlib
        self.ma = importlib.import_module("meta-audience")
        self.cu = importlib.import_module("capi-utm-builder")
        self.mis = importlib.import_module("meta-insights-sync")
        self.shield = importlib.import_module("tyrion-shield")
        self.mcp = importlib.import_module("tyrion-mcp-server")

    def test_audit_1_saturation_confidence_intervals_and_model_disclosure(self) -> None:
        sat_heur = self.ma.calc_saturation(audience_size=200000, daily_budget=80.0, cpm=3.2, days=14, active_reach_ratio=0.55)
        self.assertEqual(sat_heur["active_reach_ratio"], 0.55)
        self.assertEqual(sat_heur["estimated_reachable_pool"], 110000)
        win = sat_heur["estimated_fatigue_window_days"]
        self.assertLess(win["conservative_early_fatigue_day"], win["baseline_fatigue_day"])
        self.assertGreater(win["optimistic_late_fatigue_day"], win["baseline_fatigue_day"])
        self.assertEqual(sat_heur["model_disclosure"]["data_source_type"], "HEURISTIC_PRIOR_MODEL")

        sat_meas = self.ma.calc_saturation(audience_size=200000, daily_budget=80.0, cpm=3.2, days=14, measured_freq_7d=1.75)
        self.assertEqual(sat_meas["model_disclosure"]["data_source_type"], "MEASURED_ACCOUNT_DATA")
        self.assertIn("MODERATE_CALIBRATED_LINEAR_PROJECTION", sat_meas["model_disclosure"]["confidence_level"])
        self.assertAlmostEqual(sat_meas["projected_frequency"], 3.5, places=2)

    def test_audit_2_overlap_unified_20pct_threshold_and_auction_disclaimer(self) -> None:
        healthy = self.ma.calc_overlap(size_a=100000, size_b=100000, shared=19000)
        self.assertEqual(healthy["status"], "HEALTHY_ISOLATION")
        self.assertEqual(healthy["threshold_policy_pct"], 20.0)
        self.assertEqual(healthy["metric_type"], "STATIC_AUDIENCE_POOL_INTERSECTION")
        self.assertIn("Static Pool Overlap", healthy["auction_competition_disclaimer"])

        moderate = self.ma.calc_overlap(size_a=100000, size_b=100000, shared=21000)
        self.assertEqual(moderate["status"], "MODERATE_OVERLAP")

        critical = self.ma.calc_overlap(size_a=100000, size_b=100000, shared=31000)
        self.assertEqual(critical["status"], "CRITICAL_COLLISION")

    def test_audit_3_live_meta_insights_sync_and_mcp_integration(self) -> None:
        raw_file = VAULT / "examples" / "demo-brand" / "assets" / "meta_graph_insights_raw.json"
        res = self.mis.sync_and_analyze(from_raw_json=raw_file, target_cpa=15.0, breakeven_roas=2.0)
        self.assertEqual(res["graph_api_version"], "v26.0")
        self.assertEqual(res["normalized_rows_count"], 3)
        self.assertEqual(res["audit_report"]["summary"]["total_conversions"], 33)
        verdicts = {d["name"]: d["verdict"] for d in res["audit_report"]["decisions"]}
        self.assertEqual(verdicts["L1_Broad_UZ_22_54"], "SCALE (+20% / 48h)")
        self.assertEqual(verdicts["L2_Narrow_Luxury_Stack"], "KILL_ZERO_CONV")

        mcp_resp = self.mcp.handle_request({
            "jsonrpc": "2.0",
            "id": 501,
            "method": "tools/call",
            "params": {
                "name": "tyrion_meta_live_insights",
                "arguments": {"from_raw_json": "examples/demo-brand/assets/meta_graph_insights_raw.json", "target_cpa": 15.0},
            },
        })
        payload = json.loads(mcp_resp["result"]["content"][0]["text"])
        self.assertEqual(payload["normalized_rows_count"], 3)

    def test_audit_4_unit_economics_cpa_and_lookalike_readiness_disclosure(self) -> None:
        econ_arch = self.ma.build_architecture(niche="ecom", daily_budget=150.0, aov=80.0, margin_pct=35.0)
        self.assertEqual(econ_arch["evidence_and_assumptions"]["cpa_source"], "UNIT_ECONOMICS_DERIVED")
        self.assertEqual(econ_arch["estimated_target_cpa_usd"], 18.2)

        fallback_arch = self.ma.build_architecture(niche="ecom", daily_budget=150.0)
        self.assertEqual(fallback_arch["evidence_and_assumptions"]["cpa_source"], "PROVISIONAL_HEURISTIC_FALLBACK")

        lal = self.ma.calc_lookalike(seed_size=500, seed_type="qualified_leads", country="UZ")
        self.assertIn("heuristic_seed_readiness_score_100", lal)
        self.assertFalse(lal["model_disclosure"]["is_meta_internal_score"])

    def test_audit_5_retargeting_no_telegram_bot_flag_and_zero_pool_honesty(self) -> None:
        proc = subprocess.run(
            [
                sys.executable, str(TOOLS / "meta-audience.py"),
                "retargeting", "--aov", "100", "--daily-visitors", "0",
                "--ig-engagers", "0", "--video-viewers", "0", "--no-telegram-bot", "--json",
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertFalse(data["has_telegram_bot"])
        self.assertEqual(data["total_retargetable_pool"], 0)
        self.assertEqual(data["recommended_retargeting_daily_budget_usd"], 0.0)
        self.assertEqual(data["retargeting_readiness"], "INSUFFICIENT_RETARGETING_POOL")
        for w in data["retargeting_windows"]:
            self.assertEqual(w["estimated_pool"], 0)
            self.assertFalse(w["window_viable"])
            self.assertNotIn("Telegram_Bot_Started_No_Contact_7d", w["sources"])

    def test_audit_5c_no_unreachable_dead_code_in_any_tool(self) -> None:
        status, detail, items = self.shield.scan_python_ast()
        self.assertEqual(status, "ok", f"Dead code or AST error found: {items}")
        self.assertEqual(items, [])

    def test_audit_6_tyrion_shield_scans_tests_and_discloses_scope(self) -> None:
        self.assertNotIn("tests", self.shield.SKIP_DIRS)
        res = self.shield.run_all()
        self.assertEqual(res["summary"]["errors"], 0)
        self.assertTrue(res["scope_and_limitations"]["tests_directory_scanned"])
        self.assertGreaterEqual(len(res["scope_and_limitations"]["non_covered_risks"]), 2)

    def test_audit_7_version_and_inventory_parity_across_all_manifests_and_docs(self) -> None:
        counts = catalog.scan()["counts"]
        self.assertEqual(counts["agents"], 31)
        self.assertEqual(counts["skills"], 65)
        self.assertEqual(counts["commands"], 27)
        self.assertEqual(counts["wiki"], 100)

        for jpath in ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json", "package.json"):
            jdata = json.loads((VAULT / jpath).read_text(encoding="utf-8"))
            self.assertEqual(jdata["version"], catalog.read_version(), f"Version drift in {jpath}")

        mp = json.loads((VAULT / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(mp["metadata"]["version"], catalog.read_version())
        self.assertEqual(mp["plugins"][0]["version"], catalog.read_version())
        self.assertIn("31 specialist agents", mp["metadata"]["description"])

        sec_txt = (VAULT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("31 agents", sec_txt)
        self.assertIn("65 skills", sec_txt)

    def test_audit_8_graph_api_defaults_to_v26_and_interpolates_dynamically(self) -> None:
        info_default = self.ma.get_interests("ecom")
        self.assertEqual(info_default["graph_api_version"], "v26.0")
        self.assertIn("/v26.0/search", info_default["graph_api_readonly_endpoint"])

        old_env = os.environ.get("META_GRAPH_API_VERSION")
        try:
            os.environ["META_GRAPH_API_VERSION"] = "v27.0"
            info_custom = self.ma.get_interests("ecom")
            self.assertEqual(info_custom["graph_api_version"], "v27.0")
            self.assertIn("/v27.0/search", info_custom["graph_api_readonly_endpoint"])
            self.assertNotIn("v22.0", info_custom["graph_api_readonly_endpoint"])

            capi_custom = self.cu.build_capi_payload("Lead", phone="+998901234567")
            self.assertEqual(capi_custom["graph_api_version"], "v27.0")
            self.assertIn("/v27.0/", capi_custom["capi_endpoint_template"])
        finally:
            if old_env is None:
                os.environ.pop("META_GRAPH_API_VERSION", None)
            else:
                os.environ["META_GRAPH_API_VERSION"] = old_env

    def test_audit_9_retargeting_has_telegram_bot_false_string_arg(self) -> None:
        proc = subprocess.run(
            [
                sys.executable, str(TOOLS / "meta-audience.py"),
                "retargeting", "--has-telegram-bot=false", "--daily-visitors", "500", "--json",
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertFalse(data["has_telegram_bot"])
        self.assertEqual(data["retargeting_readiness"], "READY_FOR_RETARGETING")

    def test_audit_10_live_insights_rejects_invalid_account_id(self) -> None:
        with self.assertRaises(ValueError):
            self.mis.normalize_account_id("invalid_acct_abc")
        self.assertEqual(self.mis.normalize_account_id("123456789"), "act_123456789")


if __name__ == "__main__":
    unittest.main()
