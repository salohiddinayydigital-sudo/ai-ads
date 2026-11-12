"""TyrionV7CreativeAndMetaStackTests, CreativeMatrixAndWorkspaceTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._helpers import TOOLS, VAULT



class TyrionV7CreativeAndMetaStackTests(unittest.TestCase):
    """Tyrion v7.0.0 — /ad-creative Skill, 9:16 Video Ad Scripting, Andromeda Entity-ID/PDA Engine, AI-Tell Linter & Meta 2026 5-System Stack Tests."""

    def setUp(self) -> None:
        self.cm = importlib.import_module("creative-matrix")
        self.ss = importlib.import_module("skill-search")
        self.mte = importlib.import_module("meta-targeting-engine")
        self.ma = importlib.import_module("meta-audience")
        self.mcp = importlib.import_module("tyrion-mcp-server")

    def test_v7_01_ad_creative_skill_and_command_registered_and_routed(self) -> None:
        self.assertTrue((VAULT / "skills" / "ad-creative" / "SKILL.md").is_file())
        self.assertTrue((VAULT / "commands" / "ad-creative.md").is_file())
        self.assertTrue((VAULT / ".claude" / "commands" / "ad-creative.md").is_file())

        for q in (
            "Video reklama va reels skript yozib ber (/ad-creative)",
            "Generate an iMessage reveal video ad and Meta ad copy variations",
            "Сценарий видео рекламы и UGC креатив для стоматологии",
        ):
            plan = self.ss.route_task(q, load=True)
            all_skills = plan["required_skills"] + plan["supporting_skills"]
            self.assertTrue({"ad-creative", "reels-scripting"} & set(all_skills), f"Expected ad-creative or reels-scripting in {all_skills}")
            self.assertIn("tools/creative-matrix.py", plan["tools_to_use"])

    def test_v7_02_video_script_generator_supports_all_7_formats_and_safe_zone_specs(self) -> None:
        for fmt in (
            "ugc_reaction_demo", "founder_authority", "no_yapping_split_screen",
            "imessage_reveal", "chatgpt_reveal", "greenscreen_proof", "faceless_motion_explainer"
        ):
            script = self.cm.generate_video_script(
                niche="medical",
                product="Tish implantatsiyasi",
                problem="Tish yo'qotilishi",
                format_name=fmt,
                language="uz_latin",
                market="uz",
            )
            self.assertEqual(script["schema"], "tyrion.video_ad_script/v7")
            self.assertEqual(script["format"], fmt)
            self.assertEqual(len(script["hook_variations_0_3s"]), 3)
            self.assertEqual(len(script["storyboard_scenes"]), 5)
            self.assertIn("720x1200", script["production_specs"]["text_safe_zone"])
            self.assertFalse(script["ai_tells_check"]["has_ai_tells"])

    def test_v7_03_pda_diversity_plan_prevents_andromeda_entity_id_collapse(self) -> None:
        pda = self.cm.build_pda_diversity_plan(niche="ecom", product="Espresso Machine", price=300.0, market="eu", currency="EUR")
        self.assertEqual(pda["schema"], "tyrion.pda_creative_diversity/v7")
        self.assertEqual(len(pda["pda_concepts"]), 6)
        formats_used = {c["assigned_format"] for c in pda["pda_concepts"]}
        self.assertGreaterEqual(len(formats_used), 5, "PDA concepts must use distinct visual formats for unique Andromeda Entity IDs")
        for c in pda["pda_concepts"]:
            self.assertIn("falsifiable_hypothesis", c)
            self.assertIn("visual_signature_for_unique_entity_id", c)

    def test_v7_04_ad_copy_generator_and_no_ai_tells_linter(self) -> None:
        # Test AI-tell detector catches contrast reveals, hook slop, stock clichés, and em-dashes
        dirty = "Stop scrolling! It's not just a CRM, it's a growth engine — unlock the power of automation."
        lint_res = self.cm.lint_ai_tells(dirty)
        self.assertTrue(lint_res["has_ai_tells"])
        self.assertGreaterEqual(lint_res["issues_count"], 3)
        self.assertNotIn("—", lint_res["cleaned_text"])
        self.assertNotIn("Stop scrolling", lint_res["cleaned_text"])

        # Test platform-validated ad copy pack
        for plat in ("meta", "google_rsa", "tiktok", "linkedin", "telegram"):
            pack = self.cm.generate_ad_copy_pack(
                platform=plat,
                product="AI CRM",
                problem="Lost sales leads",
                proof="500+ B2B teams",
                language="en",
            )
            self.assertEqual(pack["platform"], plat)
            self.assertEqual(len(pack["variations"]), 3)
            for v in pack["variations"]:
                self.assertTrue(v["within_platform_limits"], f"Exceeded limits on {plat}: {v}")
                self.assertEqual(v["ai_tells_detected"], 0)

    def test_v7_05_meta_2026_five_system_stack_and_practitioner_playbook_present(self) -> None:
        arch = self.ma.build_architecture(niche="ecom", daily_budget=150.0, geo="US", currency="USD")
        stack_info = arch["meta_2026_ai_stack_and_value_rules"]
        self.assertEqual(len(stack_info["five_system_hierarchy"]), 5)
        self.assertIn("GUIDED_CREATION", stack_info["asc_api_mode"])
        self.assertIn("Value Rules", stack_info["value_rules_guidance"])

        old_tok = os.environ.pop("META_ACCESS_TOKEN", None)
        try:
            rep = self.mte.search_and_validate_targeting(product="Stomatologiya", niche="medical", country="UZ")
            pb = rep["targetologist_report"]["9_practitioner_ads_manager_playbook"]
            self.assertEqual(pb["mode"], "PRACTITIONER_ZERO_CODING_ADS_MANAGER_SETUP")
            self.assertIn("GEM", pb["meta_2026_5_system_stack"])
            self.assertIn("UTIS", pb["meta_2026_5_system_stack"])
            self.assertGreaterEqual(len(pb["step_by_step_ads_manager_setup"]), 6)
        finally:
            if old_tok is not None:
                os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_v7_06_launch_blueprint_and_token_efficiency_profiler(self) -> None:
        bp = self.ma.build_launch_blueprint(
            product="Toshkent Implant Stomatologiya",
            niche="medical",
            daily_budget=50.0,
            aov=300.0,
            margin_pct=50.0,
            lead_to_sale_cvr=15.0,
            country="UZ",
            language="uz_latin",
            currency="USD",
        )
        self.assertEqual(bp["schema"], "tyrion.launch_blueprint/v7.1")
        self.assertTrue(bp["zero_llm_tokens_execution"])
        self.assertIn("1_unit_economics_and_guardrails", bp)
        self.assertIn("2_audience_architecture_and_meta_2026_stack", bp)
        self.assertIn("3_detailed_targeting_and_ads_manager_setup", bp)
        self.assertIn("4_andromeda_pda_creative_diversity", bp)
        self.assertIn("5_ready_to_shoot_video_script_9x16", bp)
        self.assertIn("6_platform_native_ad_copy", bp)
        self.assertIn("7_lead_quality_and_sales_conversion_gate", bp)
        self.assertIn("8_seven_day_kill_scale_protocol", bp)
        self.assertFalse(bp["5_ready_to_shoot_video_script_9x16"]["ai_tells_check"]["has_ai_tells"])
        self.assertEqual(bp["6_platform_native_ad_copy"]["variations"][0]["ai_tells_detected"], 0)

        prof = self.ss.compute_token_profile("Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top")
        self.assertEqual(prof["schema"], "tyrion.token_profile/v7.1")
        self.assertEqual(prof["zero_token_python_engines"]["llm_token_cost"], 0)
        compact_info = prof["router_modes_comparison"]["compact"]
        prog_info = prof["router_modes_comparison"]["progressive"]
        self.assertLessEqual(compact_info["loaded_bytes"], 4500)
        self.assertLess(compact_info["loaded_bytes"], prog_info["loaded_bytes"])
        self.assertGreaterEqual(compact_info["savings_pct"], 99.0)

        intel = self.ma.analyze_audience_competitors_and_offers(
            product="Ingliz tili IELTS Akademiyasi",
            niche="edu",
            competitors=["Cambridge", "Thompson"],
            price=120.0,
            country="UZ",
        )
        self.assertEqual(intel["schema"], "tyrion.market_intel_and_offers/v7.2")
        self.assertEqual(len(intel["1_audience_jtbd_and_4_segments"]), 4)
        self.assertIn("meta_ad_library_url", intel["2_competitor_teardown_and_gaps"]["official_ad_spy_links"])
        self.assertIn("5_bonus_stack", intel["3_master_grand_slam_offer"])

        r_typo = self.ss.route_task("Audioturiya va rabotchilar Analiz qilish.audioturiyaga turi taklif berishchi?")
        self.assertEqual(r_typo["intent_analysis"]["detected_language"], "uz_latin")
        self.assertEqual(r_typo["primary_agent"], "positioning-strategist")
        self.assertIn("ads-competitor", r_typo["required_skills"] + r_typo["supporting_skills"])
        self.assertIn("offers", r_typo["required_skills"] + r_typo["supporting_skills"])

        mcp = importlib.import_module("tyrion-mcp-server")
        mcp_intel = mcp.call_tool("tyrion_meta_audience", {"mode": "market-intel", "product": "IELTS Kurs", "niche": "edu", "daily_budget": 50.0})
        self.assertEqual(mcp_intel["schema"], "tyrion.market_intel_and_offers/v7.2")
        mcp_bp = mcp.call_tool("tyrion_meta_audience", {"mode": "launch-blueprint", "product": "IELTS Kurs", "niche": "edu", "daily_budget": 50.0})
        self.assertEqual(mcp_bp["schema"], "tyrion.launch_blueprint/v7.1")


class CreativeMatrixAndWorkspaceTests(unittest.TestCase):
    """Tyrion v3.0 — creative-matrix.py, client-workspace.py va tyrion.py master CLI testlari."""

    def test_creative_matrix_builds_9_cells(self) -> None:
        import importlib
        cm = importlib.import_module("creative-matrix")
        res = cm.build_matrix(niche="ecom", product="Kostyum", price=150.0)
        self.assertEqual(len(res["matrix_3x3"]), 9)

    def test_creative_hooks_generates_3_languages(self) -> None:
        import importlib
        cm = importlib.import_module("creative-matrix")
        res = cm.generate_hooks(niche="edtech", offer="IELTS 7.0 3 oyda")
        for lang in ("uz_latin", "uz_cyrillic", "ru"):
            self.assertIn(lang, res["hooks_by_language"])
            self.assertGreaterEqual(len(res["hooks_by_language"][lang]), 3)

    def test_creative_fatigue_detects_weak_hook(self) -> None:
        import importlib
        cm = importlib.import_module("creative-matrix")
        res = cm.analyze_fatigue(hook_rate=18.0, hold_rate=15.0, ctr_drop_pct=10.0, frequency=1.5, ftir=70.0)
        self.assertEqual(res["status"], "WEAK_3S_HOOK")

    def test_client_workspace_scaffolds_5_files(self) -> None:
        import importlib
        cw = importlib.import_module("client-workspace")
        with tempfile.TemporaryDirectory() as tmp:
            res = cw.scaffold_client(
                client="Test Brand", niche="real-estate", monthly_budget=3000.0,
                aov=45000.0, margin_pct=25.0, geo="tashkent", root=Path(tmp), dry_run=False
            )
            cdir = Path(res["workspace_dir"])
            for fname in ("BRIEF.md", "AUDIENCE-MAP.md", "CREATIVE-MATRIX.md", "TRACKING-CHECKLIST.md", "journal.md"):
                self.assertTrue((cdir / fname).is_file(), f"Yaratilmadi: {fname}")

    def test_tyrion_master_cli_status(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "tyrion.py"), "status"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("TYRION v7.0.0", proc.stdout)
        self.assertIn("Single-Root ECC v7.0.0", proc.stdout)


if __name__ == "__main__":
    unittest.main()
