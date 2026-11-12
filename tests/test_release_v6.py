"""TyrionV6GlobalReleaseTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers import VAULT

import catalog  # noqa: E402



class TyrionV6GlobalReleaseTests(unittest.TestCase):
    """Tyrion v6.0.0 Global Release — Cross-Platform Hooks/MCP, Markets, Locales, Currencies, Consent Gate & Progressive Budget Tests."""

    def setUp(self) -> None:
        self.ss = importlib.import_module("skill-search")
        self.mloc = importlib.import_module("market_locale")
        self.cu = importlib.import_module("capi-utm-builder")
        self.cm = importlib.import_module("creative-matrix")
        self.calc = importlib.import_module("calculator")
        self.ma = importlib.import_module("meta-audience")
        self.ae = importlib.import_module("ad-export-analyzer")

    def test_v6_01_hooks_json_has_no_placeholders_py3_or_relative_paths(self) -> None:
        hooks_path = VAULT / "hooks" / "hooks.json"
        self.assertTrue(hooks_path.is_file())
        self.assertFalse((VAULT / "hooks.json").exists(), "Duplicate root hooks.json must be removed")
        self.assertFalse((VAULT / ".claude" / "settings.json").exists(), "Duplicate .claude/settings.json must be removed")

        raw = hooks_path.read_text(encoding="utf-8")
        self.assertNotIn("{{", raw, "Unexpanded {{VAULT}} placeholder in hooks/hooks.json")
        self.assertNotIn("py -3", raw, "Windows-only py -3 in hooks/hooks.json")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", raw)

        cfg = json.loads(raw)
        for event_name, groups in cfg["hooks"].items():
            for grp in groups:
                for hk in grp["hooks"]:
                    cmd = hk["command"]
                    self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cjs", cmd)
                    if event_name == "Stop":
                        self.assertLessEqual(hk.get("timeout", 999), 5, "Stop hook timeout must be <= 5s")

    def test_v6_02_hooks_and_mcp_work_from_external_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as ext_dir:
            env = dict(**os.environ, CLAUDE_PLUGIN_ROOT=str(VAULT))
            env.pop("TYRION_DEV", None)

            # 1. SessionStart brief from external cwd
            p_brief = subprocess.run(
                ["node", str(VAULT / "hooks" / "run-hook.cjs"), "brief"],
                cwd=ext_dir, env=env, capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(p_brief.returncode, 0, p_brief.stderr)
            self.assertIn("Tyrion:", p_brief.stdout)

            # 2. PreToolUse guard on an external file Write via stdin must never block
            stdin_payload = json.dumps({
                "tool_name": "Write",
                "tool_input": {"file_path": str(Path(ext_dir) / "src" / "index.ts")},
            })
            p_guard = subprocess.run(
                ["node", str(VAULT / "hooks" / "run-hook.cjs"), "guard", "--warn-only", "--quiet"],
                input=stdin_payload, cwd=ext_dir, env=env, capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(p_guard.returncode, 0, p_guard.stderr)

            # 3. PostToolUse ingest and Stop dod in external cwd exit 0 immediately (maintainer-only)
            for mode in ("ingest", "dod"):
                p_m = subprocess.run(
                    ["node", str(VAULT / "hooks" / "run-hook.cjs"), mode, "--warn-only"],
                    cwd=ext_dir, env=env, capture_output=True, text=True, timeout=5,
                )
                self.assertEqual(p_m.returncode, 0, f"{mode} failed in external cwd: {p_m.stderr}")

            # 4. MCP STDIO server via run-hook.cjs --mcp from external cwd
            mcp_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n"
            p_mcp = subprocess.run(
                ["node", str(VAULT / "hooks" / "run-hook.cjs"), "--mcp"],
                input=mcp_req, cwd=ext_dir, env=env, capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(p_mcp.returncode, 0, p_mcp.stderr)
            resp = json.loads(p_mcp.stdout.strip().splitlines()[0])
            self.assertEqual(resp["result"]["serverInfo"]["version"], catalog.read_version())

    def test_v6_03_hook_fail_open_when_script_missing_unless_strict(self) -> None:
        with tempfile.TemporaryDirectory() as fake_root:
            env_std = dict(**os.environ, CLAUDE_PLUGIN_ROOT=fake_root, TYRION_HOOK_PROFILE="standard")
            p_std = subprocess.run(
                ["node", str(VAULT / "hooks" / "run-hook.cjs"), "guard", "--warn-only"],
                cwd=fake_root, env=env_std, capture_output=True, text=True, timeout=5,
            )
            self.assertEqual(p_std.returncode, 0, "Standard profile must fail open (exit 0) when hook script is missing")
            self.assertIn("non-blocking", p_std.stderr)

            env_strict = dict(**os.environ, CLAUDE_PLUGIN_ROOT=fake_root, TYRION_HOOK_PROFILE="strict")
            p_strict = subprocess.run(
                ["node", str(VAULT / "hooks" / "run-hook.cjs"), "guard", "--warn-only"],
                cwd=fake_root, env=env_strict, capture_output=True, text=True, timeout=5,
            )
            self.assertEqual(p_strict.returncode, 2, "Strict profile must exit 2 when hook script is missing")

    def test_v6_04_router_germany_shopify_query_loads_eu_eur_and_no_uzbek_rule(self) -> None:
        plan = self.ss.route_task("My Shopify store in Germany has low ROAS on Meta", load=True)
        ia = plan["intent_analysis"]
        self.assertEqual(ia["detected_market"], "eu")
        self.assertEqual(ia["detected_currency"], "EUR")
        self.assertEqual(ia["detected_language"], "en")
        self.assertNotIn("rules/30-ozbekiston-konteksti.md", plan["rules_to_load"])
        self.assertNotIn("uzbekistan-market-intel", plan["required_skills"] + plan["supporting_skills"])
        self.assertIn("markets/eu/README.md", plan["rules_to_load"])
        self.assertIn("markets/eu/benchmarks.md", plan["rules_to_load"])
        regs = " ".join(plan["market_context"]["regulations"]["frameworks"])
        self.assertIn("GDPR", regs)
        self.assertIn("Consent Mode v2", regs)

    def test_v6_05_router_tashkent_real_estate_query_loads_uz_market_and_uzbek_rule(self) -> None:
        plan = self.ss.route_task("Toshkentda ko'chmas mulk uchun Meta reklama", load=True)
        ia = plan["intent_analysis"]
        self.assertEqual(ia["detected_market"], "uz")
        self.assertEqual(ia["detected_language"], "uz_latin")
        self.assertIn("rules/30-ozbekiston-konteksti.md", plan["rules_to_load"])
        self.assertIn("markets/uz/README.md", plan["rules_to_load"])

    def test_v6_06_router_progressive_disclosure_within_15kb_budget(self) -> None:
        for q in (
            "My Shopify store in Germany has low ROAS on Meta",
            "Audit my Google Ads Performance Max campaign in the UK",
            "Toshkentda ko'chmas mulk uchun Meta reklama",
        ):
            plan = self.ss.route_task(q, load=True)
            self.assertEqual(plan["context_mode"], "progressive")
            used = plan["loaded_context"]["context_budget"]["used_bytes"]
            self.assertLessEqual(used, 15_000, f"Query {q!r} exceeded 15KB progressive budget: {used}")

    def test_v6_07_iso4217_currency_formatting_and_zero_decimal_currencies(self) -> None:
        self.assertEqual(self.mloc.format_currency(12500.7, "JPY"), "¥12,501")
        self.assertEqual(self.mloc.format_currency(1500000, "UZS"), "1,500,000 UZS")
        self.assertEqual(self.mloc.format_currency(99.5, "EUR"), "€99.50")
        self.assertEqual(self.mloc.format_currency(99.5, "GBP"), "£99.50")
        self.assertEqual(self.mloc.format_currency(250, "BRL"), "R$250.00")
        self.assertEqual(self.mloc.format_currency(1499, "INR"), "₹1,499.00")

        be_jpy = self.calc.calc_breakeven(price=15000, cogs=5000, shipping=800, currency="JPY")
        self.assertEqual(be_jpy["currency"], "JPY")
        self.assertIsInstance(be_jpy["price"], int)
        self.assertEqual(be_jpy["formatted_price"], "¥15,000")

        arch_eur = self.ma.build_architecture(niche="ecom", daily_budget=200.0, geo="DE", currency="EUR", market="eu")
        self.assertEqual(arch_eur["currency"], "EUR")
        self.assertEqual(arch_eur["formatted_daily_budget"], "€200.00")
        self.assertIn("budget_share", arch_eur["audience_layers"][0])

    def test_v6_08_capi_consent_gate_blocks_pii_when_no_consent_and_sets_consent_mode_v2_and_ldu(self) -> None:
        denied = self.cu.build_capi_payload(
            event_name="Purchase",
            phone="+4915123456789",
            email="customer@berlin.de",
            first_name="Hans",
            city="Berlin",
            country="de",
            market="eu",
            value=180.0,
            currency="EUR",
            consent_granted=False,
        )
        self.assertEqual(denied["consent_gate_status"], "BLOCKED_PII_NO_CONSENT")
        self.assertTrue(denied["pii_stripped_due_to_no_consent"])
        ud = denied["capi_payload"]["data"][0]["user_data"]
        for pii_key in ("ph", "em", "fn", "ct", "fbp", "fbc"):
            self.assertNotIn(pii_key, ud, f"PII field {pii_key} must never be hashed/sent when consent_granted=False")
        cm_v2 = denied["regulatory_compliance"]["google_consent_mode_v2"]
        self.assertEqual(cm_v2["ad_user_data"], "denied")
        self.assertEqual(cm_v2["ad_personalization"], "denied")
        self.assertEqual(denied["capi_payload"]["data"][0]["data_processing_options"], ["LDU"])

    def test_v6_09_creative_matrix_market_bnpl_anchors_and_bcp47_rtl_hooks(self) -> None:
        m_eu = self.cm.build_matrix("ecom", "Ergonomic Chair", price=300.0, market="eu", currency="EUR")
        self.assertIn("Klarna", m_eu["price_anchor"])
        self.assertIn("€100.00", m_eu["price_anchor"])

        m_mena = self.cm.build_matrix("ecom", "Luxury Perfume", price=400.0, market="mena", currency="AED")
        self.assertIn("Tabby", m_mena["price_anchor"])

        m_uz = self.cm.build_matrix("ecom", "Konditsioner", price=500.0, market="uz", currency="USD")
        self.assertIn("Uzum Nasiya", m_uz["price_anchor"])

        hooks = self.cm.generate_hooks("ecom", "24h Delivery", languages=["en", "de", "fr", "ar"])
        for lang_code in ("en", "de", "fr", "ar"):
            self.assertIn(lang_code, hooks["hooks_by_language"])
        self.assertIn("ar", hooks.get("rtl_formatting_notes", {}))

    def test_v6_10_english_commands_and_uzbek_aliases_present_and_synced(self) -> None:
        pairs = [
            ("audience", "auditoriya"),
            ("creative", "kreativ"),
            ("funnel", "voronka"),
            ("export", "eksport"),
            ("report", "hisobot"),
            ("client", "mijoz"),
            ("competitors", "raqobatchi"),
            ("ask", "savol"),
        ]
        for en_name, uz_name in pairs:
            self.assertTrue((VAULT / "commands" / f"{en_name}.md").is_file(), f"Missing commands/{en_name}.md")
            self.assertTrue((VAULT / "commands" / f"{uz_name}.md").is_file(), f"Missing alias commands/{uz_name}.md")
            self.assertTrue((VAULT / ".claude" / "commands" / f"{en_name}.md").is_file())

    def test_v6_11_regional_platform_skills_and_verified_sources(self) -> None:
        expected_skills = [
            "markets/uz/skills/ads-yandex-direct/SKILL.md",
            "markets/uz/skills/ads-vk/SKILL.md",
            "markets/sea/skills/ads-line/SKILL.md",
            "markets/global/skills/ads-naver-kakao/SKILL.md",
            "markets/global/skills/ads-china-ecosystem/SKILL.md",
            "markets/global/skills/ads-native-taboola-outbrain/SKILL.md",
        ]
        for rel in expected_skills:
            p = VAULT / rel
            self.assertTrue(p.is_file(), f"Missing regional platform skill: {rel}")
            txt = p.read_text(encoding="utf-8")
            self.assertIn("2026-10-21", txt)
            self.assertIn("https://", txt)

    def test_v6_12_no_personal_paths_and_upstream_mit_attribution_present(self) -> None:
        cat_json = json.loads((VAULT / "manifests" / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(cat_json["vault"], ".", "catalog.json must not contain an absolute machine path")

        for doc in ("LICENSE", "NOTICE", "THIRD_PARTY.md", "README.md", "README.uz.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md"):
            self.assertTrue((VAULT / doc).is_file(), f"Missing {doc}")

        lic_txt = (VAULT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("AgriciDaniel", lic_txt)
        self.assertIn("Affaan Mustafa", lic_txt)

        ci_txt = (VAULT / ".github" / "workflows" / "tyrion-ci.yml").read_text(encoding="utf-8")
        self.assertIn("macos-latest", ci_txt)
        self.assertIn("'3.13'", ci_txt)


if __name__ == "__main__":
    unittest.main()
