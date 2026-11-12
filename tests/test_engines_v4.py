"""TyrionV4EnginesTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import TOOLS, VAULT, run_tool_inproc as _run_tool_inproc



class TyrionV4EnginesTests(unittest.TestCase):
    """Tyrion v4.0 — Ad Export & Breakdown Effect, CAPI v22 & UTM, MCP Server, Multi-Harness Exporter va Eval Suite testlari."""

    def test_breakdown_effect_detects_marginal_cpa_trap(self) -> None:
        import importlib
        ae = importlib.import_module("ad-export-analyzer")
        trap = ae.analyze_breakdown_effect("IG Reels", 750.0, 50, "FB Feed", 150.0, 12)
        self.assertTrue(trap["breakdown_effect_trap_detected"])
        self.assertGreater(trap["projected_cpa_if_dominant_paused_usd"], trap["blended_cpa_usd"])

        balanced = ae.analyze_breakdown_effect("IG Reels", 400.0, 25, "FB Feed", 380.0, 24)
        self.assertFalse(balanced["breakdown_effect_trap_detected"])

    def test_ad_export_analyzer_parses_demo_json(self) -> None:
        import importlib
        ae = importlib.import_module("ad-export-analyzer")
        demo_file = VAULT / "examples" / "demo-brand" / "assets" / "meta_performance.json"
        res = ae.analyze_export(demo_file, target_cpa=15.0, breakeven_roas=2.0)
        self.assertGreater(res["total_items"], 0)
        self.assertIn("blended_cpa_usd", res["summary"])
        self.assertTrue(all("verdict" in d for d in res["decisions"]))

    def test_capi_v22_payload_hashes_pii_and_scores_emq(self) -> None:
        import importlib
        cu = importlib.import_module("capi-utm-builder")
        res = cu.build_capi_payload("Lead", phone="+998 (90) 123-45-67", email="Test@Brand.uz", city="Tashkent", value=200.0, order_id="ORD_55")
        self.assertGreaterEqual(res["estimated_emq_score_10"], 8.0)
        ud = res["capi_v22_payload"]["data"][0]["user_data"]
        # SHA-256 hex digest is 64 chars, never plaintext phone/email
        self.assertEqual(len(ud["ph"][0]), 64)
        self.assertEqual(len(ud["em"][0]), 64)
        self.assertNotIn("1234567", ud["ph"][0])

    def test_telegram_bot_utm_enforces_64_char_limit(self) -> None:
        import importlib
        cu = importlib.import_module("capi-utm-builder")
        res = cu.build_utm_links("https://brand.uz/offer", "meta", "very_long_campaign_name_exceeding_normal_limits_2026_test", "my_brand_bot")
        tg = res["telegram_bot_tracking"]
        self.assertTrue(tg["within_64_char_limit"])
        self.assertLessEqual(tg["payload_length"], 64)
        self.assertIn("{{campaign.name}}", res["full_tracked_url"])

    def test_mcp_server_jsonrpc_initialize_and_tool_call(self) -> None:
        import importlib
        mcp = importlib.import_module("tyrion-mcp-server")
        init_resp = mcp.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(init_resp["result"]["serverInfo"]["name"], "tyrion-mcp-server")

        list_resp = mcp.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertGreaterEqual(len(list_resp["result"]["tools"]), 7)

        call_resp = mcp.handle_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "tyrion_media_calculator", "arguments": {"price": 120, "cogs": 50, "shipping": 10}},
        })
        payload = json.loads(call_resp["result"]["content"][0]["text"])
        self.assertAlmostEqual(payload["breakeven_roas"], 2.08, places=2)

    def test_harness_exporter_dry_run_and_cursor_mdc(self) -> None:
        import importlib
        he = importlib.import_module("harness-export")
        with tempfile.TemporaryDirectory() as tmp:
            files = he.export_cursor(Path(tmp), dry_run=False)
            self.assertEqual(len(files), 8)
            sample = (Path(tmp) / files[0]).read_text(encoding="utf-8")
            self.assertIn("alwaysApply: true", sample)

    def test_skill_eval_suite_passes_100_pct(self) -> None:
        import importlib
        se = importlib.import_module("skill-eval")
        summary = se.run_evals()
        self.assertEqual(summary["failed"], 0, summary)
        self.assertEqual(summary["pass_rate_pct"], 100.0)

    def test_visual_studio_html_exists_and_has_5_tabs(self) -> None:
        studio = TOOLS / "tyrion-studio.html"
        self.assertTrue(studio.is_file())
        html = studio.read_text(encoding="utf-8")
        for tab_id in ("aud", "bd", "econ", "creo", "utm"):
            self.assertIn(f'id="{tab_id}"', html)

    def test_mcp_json_has_tyrion_core_server(self) -> None:
        mcp_cfg = json.loads((VAULT / ".mcp.json").read_text(encoding="utf-8"))
        servers = mcp_cfg.get("mcpServers", {})
        self.assertIn("tyrion-core", servers)
        self.assertNotIn("meta-ads", servers, "optional meta-ads server must not be in default .mcp.json")
        self.assertNotIn("google-ads", servers, "optional google-ads server must not be in default .mcp.json")
        integ = (VAULT / "docs" / "integrations.md").read_text(encoding="utf-8")
        self.assertIn("meta-ads-mcp", integ)
        self.assertIn("google-ads-mcp", integ)

    def test_windsurf_export_creates_windsurfrules(self) -> None:
        import importlib
        he = importlib.import_module("harness-export")
        with tempfile.TemporaryDirectory() as tmp:
            files = he.export_windsurf(Path(tmp), dry_run=False)
            self.assertEqual(files, [".windsurfrules"])
            self.assertTrue((Path(tmp) / ".windsurfrules").is_file())

    def test_capi_phone_normalization_uzbekistan(self) -> None:
        import importlib
        cu = importlib.import_module("capi-utm-builder")
        self.assertEqual(cu.normalize_phone("90 123-45-67"), "998901234567")
        self.assertEqual(cu.normalize_phone("+998 (97) 700-11-22"), "998977001122")

    def test_google_utm_uses_value_track_macros(self) -> None:
        import importlib
        cu = importlib.import_module("capi-utm-builder")
        res = cu.build_utm_links("https://brand.uz", "google", "search_coliseum")
        self.assertIn("{campaignid}", res["full_tracked_url"])
        self.assertIn("{keyword}", res["full_tracked_url"])

    def test_ad_export_wasted_spend_detection(self) -> None:
        import importlib
        ae = importlib.import_module("ad-export-analyzer")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "export.json"
            p.write_text(json.dumps([
                {"name": "Bleeder_Set", "spend": 60.0, "conversions": 0, "revenue": 0},
                {"name": "Winner_Set", "spend": 100.0, "conversions": 20, "revenue": 500.0},
            ]), encoding="utf-8")
            res = ae.analyze_export(p, target_cpa=15.0, breakeven_roas=2.0)
            self.assertEqual(res["summary"]["estimated_wasted_spend_usd"], 60.0)
            self.assertEqual(res["decisions"][0]["verdict"], "KILL_ZERO_CONV")

    def test_all_100_wiki_notes_have_zero_orphans(self) -> None:
        proc = _run_tool_inproc("vault-audit.py", str(VAULT))
        self.assertIn("[ORPHAN QAYD] 0", proc.stdout)
        self.assertIn("JAMI MUAMMO (bilim qatlami): 0", proc.stdout)

    def test_no_hardcoded_windows_drive_paths_in_skills_or_commands(self) -> None:
        for folder in ("skills", "commands", "rules", "contexts", "playbooks"):
            for md in (VAULT / folder).rglob("*.md"):
                txt = md.read_text(encoding="utf-8")
                self.assertNotIn("D:\tyrion", txt, f"Hardcoded D:\tyrion in {md}")
                self.assertNotIn(r"D:\projects", txt, f"Hardcoded D:\\projects in {md}")


if __name__ == "__main__":
    unittest.main()
