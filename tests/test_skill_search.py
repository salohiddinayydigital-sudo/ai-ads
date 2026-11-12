"""SkillSearchTests, UniversalAutoRouterTests, AutoRouterExecutionGapTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._helpers import VAULT, run_tool_inproc as _run_tool_inproc

import catalog  # noqa: E402



class SkillSearchTests(unittest.TestCase):
    """skill-search — skill reyestri va agentga ulash (0 token, LLM'siz)."""

    def _run(self, *args):
        return _run_tool_inproc("skill-search.py", *args)

    def test_check_reports_healthy_registry(self) -> None:
        proc = self._run("check")
        self.assertEqual(proc.returncode, 0, proc.stdout[-500:] + proc.stderr[-300:])
        self.assertIn("butun", proc.stdout)

    def test_agent_reports_attached_skills(self) -> None:
        proc = self._run("agent", "video-editor")
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        self.assertIn("video-editing", proc.stdout)
        self.assertIn("video-motion-graphics", proc.stdout)

    def test_brief_routes_editing_task(self) -> None:
        proc = self._run("brief", "shu videoni montaj qilib ber", "--agent", "video-editor")
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        self.assertIn("Tanlandi: video-editing", proc.stdout)
        self.assertIn("SKILL.md", proc.stdout)

    def test_routing_matrix(self) -> None:
        """Routing aniqligi: umumiy so'zlar ("reels", "ber") skillni chalkashtirmasin.

        Regressiya: "animatsion reels yasab ber" bir paytlar video-editing ga ketgan edi —
        IDF (so'z noyobligi) va stop-so'zlar tufayli endi to'g'ri taqsimlanadi.
        """
        cases = [
            ("animatsion reels yasab ber", "video-motion-graphics"),
            ("animatsion video kerak", "video-motion-graphics"),
            ("after effects uslubida logo animatsiya", "video-motion-graphics"),
            ("kinetik tipografiya bilan video", "video-motion-graphics"),
            ("motion graphics qilib ber", "video-motion-graphics"),
            ("mijoz videoni montaj qilib ber", "video-editing"),
            ("shu videoni kesib ber", "video-editing"),
            ("bergan videomni edit qilib ber", "video-editing"),
            ("reels qilib ber", "video-editing"),
            ("videoimga subtitr qo'sh", "video-editing"),
            ("materialimni tahrirla", "video-editing"),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                proc = self._run("brief", query, "--agent", "video-editor")
                self.assertEqual(proc.returncode, 0, proc.stdout[-300:])
                self.assertIn(f"Tanlandi: {expected}", proc.stdout)

    def test_brief_routes_animation_task(self) -> None:
        proc = self._run("brief", "kinetik tipografiya animatsion video after effects", "--agent", "video-editor")
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        self.assertIn("Tanlandi: video-motion-graphics", proc.stdout)

    def test_brief_without_match_exits_one(self) -> None:
        proc = self._run("brief", "zzz qqq www", "--agent", "video-editor")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("mos skill topilmadi", proc.stdout)

    def test_unknown_agent_exits_two(self) -> None:
        proc = self._run("agent", "bunday-agent-yoq-xyz")
        self.assertEqual(proc.returncode, 2)

    def test_attached_skills_exist_on_disk(self) -> None:
        proc = self._run("agent", "video-editor")
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        for rel in re.findall(r"(skills/\S+/SKILL\.md)", proc.stdout):
            self.assertTrue((VAULT / rel).is_file(), f"skill fayli yo'q: {rel}")


class UniversalAutoRouterTests(unittest.TestCase):
    """Part 2: 18 Mandatory Automated Tests for Universal Auto-Router & Autonomous Agent Orchestration."""

    def setUp(self) -> None:
        self.ss = importlib.import_module("skill-search")
        self.mcp = importlib.import_module("tyrion-mcp-server")
        self.ss.SESSION_CACHE.reset()

    def test_01_simple_task_selects_single_agent_and_skill_automatically(self) -> None:
        plan = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=True)
        self.assertEqual(plan["primary_agent"], "tracking-specialist")
        self.assertEqual(plan["supporting_agents"], [])
        self.assertEqual(plan["required_skills"], ["ads-server-side-tracking"])
        self.assertEqual(plan["intent_analysis"]["complexity"], "single_step")

    def test_02_multistep_marketing_task_selects_complementary_skills_and_supporting_agents(self) -> None:
        plan = self.ss.route_task("Yangi mijoz uchun to'liq marketing strategiyasi tuz.", load=True)
        self.assertEqual(plan["primary_agent"], "launch-planner")
        self.assertEqual(plan["intent_analysis"]["complexity"], "multi_step")
        self.assertGreaterEqual(len(plan["required_skills"]), 2)
        self.assertIn("ads-plan", plan["required_skills"])
        self.assertGreaterEqual(len(plan["supporting_agents"]), 1)

    def test_03_global_registry_fallback_when_agent_hint_skills_insufficient(self) -> None:
        # Hinting `video-editor` for a CAPI server-side tracking query must automatically discover `ads-server-side-tracking` from the global registry
        plan = self.ss.route_task("Meta CAPI va event_id deduplikatsiya xatolarini tekshir", agent_hint="video-editor", load=True)
        self.assertTrue(plan["global_registry_fallback_used"])
        self.assertIn("ads-server-side-tracking", plan["required_skills"])
        self.assertEqual(plan["primary_agent"], "tracking-specialist")

    def test_04_multilingual_tasks_uz_latin_uz_cyrillic_ru_en_routed_accurately(self) -> None:
        cases = [
            ("Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top", "uz_latin", "audit-meta", "ads-meta"),
            ("Мета рекламада CAPI ишлашини текшир ва пиксель хатоларини топ", "uz_cyrillic", "tracking-specialist", "ads-server-side-tracking"),
            ("Подбери детальный таргетинг и интересы в Мета для недвижимости", "ru", "meta-audience-architect", "ads-meta-audience"),
            ("Audit my Google Ads Performance Max and search terms negative keywords", "en", "audit-google", "ads-google"),
        ]
        for query, exp_lang, exp_agent, exp_skill in cases:
            with self.subTest(lang=exp_lang):
                plan = self.ss.route_task(query, load=True)
                self.assertEqual(plan["intent_analysis"]["detected_language"], exp_lang)
                self.assertEqual(plan["primary_agent"], exp_agent)
                self.assertIn(exp_skill, plan["required_skills"])

    def test_05_generic_common_words_do_not_trigger_wrong_specialist_agent(self) -> None:
        plan = self.ss.route_task("iltimos menga hozir tez yordam qilib ber", load=True)
        self.assertEqual(plan["status"], "fallback_ready")
        self.assertTrue(plan["fallback_plan"]["triggered"])
        self.assertNotIn(plan["primary_agent"], ("audit-amazon", "audit-apple", "video-editor"))

    def test_06_universal_fallback_works_when_no_skill_matches(self) -> None:
        plan = self.ss.route_task("zzz qqq unknown holographic billboard telemetry xyz", load=True)
        self.assertEqual(plan["status"], "fallback_ready")
        self.assertTrue(plan["fallback_plan"]["triggered"])
        self.assertEqual(plan["fallback_plan"]["conductor"], "ads")
        self.assertIn("ads", plan["required_skills"])
        self.assertGreaterEqual(len(plan["fallback_plan"]["steps"]), 2)

    def test_07_only_dangerous_or_missing_critical_input_blocks_execution(self) -> None:
        safe_plan = self.ss.route_task("Instagram uchun bir oylik kontent reja tayyorla", load=True)
        self.assertEqual(safe_plan["status"], "ready")
        self.assertFalse(safe_plan["mutation_gate"]["blocked"])

        dangerous_plan = self.ss.route_task("Meta kampaniyamda byudjetni 300% oshir va reklamalarni hoziroq o'chir", load=True)
        self.assertEqual(dangerous_plan["status"], "blocked_mutation_approval")
        self.assertTrue(dangerous_plan["mutation_gate"]["blocked"])
        self.assertTrue(len(dangerous_plan["missing_inputs"]) > 0)

    def test_08_mid_task_dynamic_rerouting_adds_specialist_skill_and_agent(self) -> None:
        initial = self.ss.route_task("Instagram uchun bir oylik kontent reja tayyorla", load=True)
        self.assertEqual(initial["primary_agent"], "social-content-writer")
        self.assertNotIn("tracking-specialist", [initial["primary_agent"]] + initial["supporting_agents"])

        rerouted = self.ss.reroute_task(initial, "CAPI ishlashini tekshir va event_id deduplikatsiya xatolarini top", load=True)
        self.assertTrue(rerouted.get("rerouted"))
        self.assertIn("tracking-specialist", rerouted["supporting_agents"])
        self.assertIn("ads-server-side-tracking", rerouted["supporting_skills"] + rerouted["required_skills"])
        self.assertIn("ads-server-side-tracking", rerouted["loaded_context"]["loaded_skill_names"])

    def test_09_skill_references_loaded_selectively_only_when_needed(self) -> None:
        plan = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=True)
        refs = plan["references_to_load"]
        self.assertIn("skills/ads/references/conversion-tracking.md", refs)
        self.assertLessEqual(len(refs), 4, "Should never dump all 39 references into context")
        for r in refs:
            self.assertTrue((VAULT / r).is_file(), f"Reference does not exist: {r}")

    def test_10_no_duplicate_or_redundant_agents_selected(self) -> None:
        for q in (
            "Yangi mijoz uchun to'liq marketing strategiyasi tuz",
            "Raqobatchilarimni o'rganib, menga reklama strategiyasi tuz",
            "Saytimni SEO va konversiya bo'yicha yaxshila",
        ):
            plan = self.ss.route_task(q, load=True)
            all_agents = [plan["primary_agent"]] + plan["supporting_agents"]
            self.assertEqual(len(all_agents), len(set(all_agents)), f"Duplicate agent in {all_agents}")
            all_skills = plan["required_skills"] + plan["supporting_skills"]
            self.assertEqual(len(all_skills), len(set(all_skills)), f"Duplicate skill in {all_skills}")

    def test_11_validator_detects_broken_reference_links_in_skill_metadata(self) -> None:
        skills = self.ss.load_skills()
        agents = self.ss.load_agents()
        tampered = [dict(s) for s in skills]
        tampered[0]["declared_references"] = ["skills/non_existent_broken_ref_xyz.md"]
        problems, _warnings = self.ss.validate_registry(tampered, agents)
        self.assertTrue(any("non_existent_broken_ref_xyz.md" in p for p in problems))

    def test_12_bidirectional_skill_agent_links_100pct_consistent(self) -> None:
        problems, _warnings = self.ss.validate_registry()
        self.assertEqual(problems, [], f"Registry validation problems found: {problems}")

    def test_13_conductor_and_worker_packets_comply_with_contract_schema(self) -> None:
        plan = self.ss.route_task("Raqobatchilarimni o'rganib, menga reklama strategiyasi tuz.", load=True)
        self.assertGreaterEqual(len(plan["worker_packets"]), 1)
        required_packet_keys = {
            "step", "role", "agent", "goal", "scope_boundary", "assigned_skills",
            "references_to_load", "input_data", "expected_output_format",
            "evidence_requirements", "safety_constraints", "verification_criteria",
        }
        for wp in plan["worker_packets"]:
            self.assertTrue(required_packet_keys.issubset(set(wp.keys())))

    def test_14_existing_slash_commands_audit_auditoriya_kreativ_budget_hisobot_intact(self) -> None:
        for cmd_name in ("audit", "auditoriya", "kreativ", "budget", "hisobot", "tracking", "voronka", "mijoz"):
            cmd_path = VAULT / "commands" / f"{cmd_name}.md"
            mirror_path = VAULT / ".claude" / "commands" / f"{cmd_name}.md"
            self.assertTrue(cmd_path.is_file(), f"Missing command: {cmd_path}")
            self.assertTrue(mirror_path.is_file(), f"Missing command mirror: {mirror_path}")
            self.assertEqual(
                cmd_path.read_bytes().replace(b"\r\n", b"\n"),
                mirror_path.read_bytes().replace(b"\r\n", b"\n"),
            )

    def test_15_router_never_asks_user_to_choose_skill_or_agent_name(self) -> None:
        for q in (
            "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top",
            "zzz qqq unknown holographic billboard telemetry xyz",
            "Meta kampaniyamda byudjetni 300% oshir",
        ):
            plan = self.ss.route_task(q, load=True)
            self.assertFalse(plan["asks_user_for_skill_or_agent"])
            for msg in plan["missing_inputs"]:
                self.assertNotIn("skill tanlang", msg.lower())
                self.assertNotIn("agent tanlang", msg.lower())

    def test_16_mcp_and_cli_router_share_identical_agent_and_skill_metadata(self) -> None:
        query = "Saytimni SEO va konversiya bo'yicha yaxshila."
        cli_plan = self.ss.route_task(query, load=True)
        mcp_resp = self.mcp.handle_request({
            "jsonrpc": "2.0",
            "id": 901,
            "method": "tools/call",
            "params": {"name": "tyrion_universal_router", "arguments": {"query": query, "load": True}},
        })
        mcp_plan = json.loads(mcp_resp["result"]["content"][0]["text"])
        self.assertEqual(cli_plan["primary_agent"], mcp_plan["primary_agent"])
        self.assertEqual(cli_plan["required_skills"], mcp_plan["required_skills"])
        self.assertEqual(cli_plan["supporting_skills"], mcp_plan["supporting_skills"])
        self.assertEqual(cli_plan["rules_to_load"], mcp_plan["rules_to_load"])

    def test_17_router_never_claims_unloaded_skill_was_loaded_or_applied(self) -> None:
        plan_no_load = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=False)
        self.assertFalse(plan_no_load["loaded_context"]["actually_loaded"])
        self.assertEqual(plan_no_load["loaded_context"]["loaded_skill_names"], [])
        self.assertEqual(plan_no_load["loaded_context"]["loaded_skills"], [])

        # When load=True, verify every claimed loaded skill was read from disk and session cache works on 2nd read
        cache = self.ss.SessionContextCache()
        plan_loaded_1 = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=True, session_cache=cache)
        self.assertTrue(plan_loaded_1["loaded_context"]["actually_loaded"])
        self.assertIn("ads-server-side-tracking", plan_loaded_1["loaded_context"]["loaded_skill_names"])
        self.assertFalse(plan_loaded_1["loaded_context"]["loaded_skills"][0]["from_session_cache"])

        plan_loaded_2 = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=True, session_cache=cache)
        self.assertTrue(plan_loaded_2["loaded_context"]["loaded_skills"][0]["from_session_cache"])
        self.assertGreater(cache.hits, 0)

    def test_18_mutation_gate_blocks_unapproved_account_changes_until_approved(self) -> None:
        q = "Meta kampaniyamda byudjetni 50% oshir va reklamalarni hoziroq o'chir"
        blocked = self.ss.route_task(q, mutation_approved=False, load=True)
        self.assertEqual(blocked["status"], "blocked_mutation_approval")
        self.assertTrue(blocked["mutation_gate"]["blocked"])
        self.assertIn("rules/40-xavfsizlik-va-hisob.md", blocked["rules_to_load"])

        approved = self.ss.route_task(q, mutation_approved=True, load=True)
        self.assertEqual(approved["status"], "ready")
        self.assertFalse(approved["mutation_gate"]["blocked"])
        self.assertTrue(approved["mutation_gate"]["approved"])


class AutoRouterExecutionGapTests(unittest.TestCase):
    """Tyrion v5.0 — Auto-Router Execution Gap Audit & Fix: 10 End-to-End Acceptance Tests."""

    def setUp(self) -> None:
        self.ss = importlib.import_module("skill-search")
        self.mcp = importlib.import_module("tyrion-mcp-server")
        self.he = importlib.import_module("harness-export")
        self.ss.SESSION_CACHE.reset()

    def test_gap_01_router_returns_full_text_of_selected_skills_charters_and_references(self) -> None:
        plan = self.ss.route_task("Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top.", load=True, context_mode="full")
        lc = plan["loaded_context"]
        self.assertEqual(plan["context_mode"], "full")
        self.assertTrue(lc["actually_loaded"])
        self.assertTrue(lc["full_instructions_loaded"])
        self.assertIn("ads-meta", lc["applied_skills_verified"])

        # Verify full text (`content` and `body_markdown`) is present and much longer than the 360-char excerpt
        sk_entry = lc["loaded_skills"][0]
        self.assertIn("content", sk_entry)
        self.assertIn("body_markdown", sk_entry)
        self.assertGreater(len(sk_entry["content"]), 1000)
        self.assertGreater(len(sk_entry["content"]), len(sk_entry["instructions_excerpt"]))

        ch_entry = lc["loaded_agent_charters"][0]
        self.assertGreater(len(ch_entry["content"]), 1000)

        # Verify compiled_context_package contains the full markdown bundle
        bundle = lc["compiled_context_package"]["full_markdown_bundle"]
        self.assertIn("<!-- AGENT_CHARTER: audit-meta", bundle)
        self.assertIn("<!-- SKILL_INSTRUCTIONS: ads-meta", bundle)
        self.assertGreater(lc["compiled_context_package"]["total_bytes"], 3000)

    def test_gap_02_worker_packet_receives_full_skill_and_reference_content_and_manifest_mode_is_distinct(self) -> None:
        plan_full = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=True, context_mode="full")
        wp = plan_full["worker_packets"][0]
        self.assertTrue(wp["full_instructions_attached"])
        self.assertIsNotNone(wp["full_charter_markdown"])
        self.assertIn("ads-server-side-tracking", wp["full_skill_instructions"])
        self.assertGreater(len(wp["full_skill_instructions"]["ads-server-side-tracking"]), 800)
        self.assertIn("skills/ads/references/conversion-tracking.md", wp["full_reference_contents"])

        # In manifest mode, router must NOT claim full instructions were loaded or applied
        plan_manifest = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=False, context_mode="manifest")
        self.assertEqual(plan_manifest["context_mode"], "manifest")
        self.assertFalse(plan_manifest["loaded_context"]["actually_loaded"])
        self.assertFalse(plan_manifest["loaded_context"]["full_instructions_loaded"])
        self.assertEqual(plan_manifest["loaded_context"]["applied_skills_verified"], [])
        self.assertFalse(plan_manifest["worker_packets"][0]["full_instructions_attached"])

    def test_gap_03_execute_task_runs_tools_and_honestly_distinguishes_subagent_vs_single_conductor(self) -> None:
        # 1. Without native subagent_runner (CLI / single-conductor environment): must honestly report subagents_actually_spawned=False
        rep_single = self.ss.execute_task("Yangi mijoz uchun to'liq marketing strategiyasi tuz.")
        self.assertEqual(rep_single["execution_status"], "completed")
        self.assertEqual(rep_single["execution_mode"], "single_conductor_fallback")
        self.assertFalse(rep_single["subagents_actually_spawned"])
        self.assertGreaterEqual(len(rep_single["worker_executions"]), 2)
        for we in rep_single["worker_executions"]:
            self.assertFalse(we["subagent_spawned"])
            self.assertGreater(we["full_skill_chars_loaded"], 500)
        self.assertGreaterEqual(len(rep_single["deterministic_tool_outputs"]), 1)

        # 2. With native subagent_runner callback: dispatches workers with full instructions and collects results
        dispatched_agents: list[str] = []
        def mock_subagent_runner(packet: dict) -> dict:
            dispatched_agents.append(packet["agent"])
            self.assertTrue(packet["full_instructions_attached"])
            return {"agent": packet["agent"], "status": "ok", "findings": []}

        rep_native = self.ss.execute_task(
            "Yangi mijoz uchun to'liq marketing strategiyasi tuz.",
            subagent_runner=mock_subagent_runner,
        )
        self.assertEqual(rep_native["execution_mode"], "native_subagent_dispatch")
        self.assertTrue(rep_native["subagents_actually_spawned"])
        self.assertIn("launch-planner", dispatched_agents)
        self.assertGreaterEqual(len(dispatched_agents), 2)

    def test_gap_04_context_budget_defers_overflow_references_honestly(self) -> None:
        # Set a tight budget (e.g., 16,000 bytes) so charter + skill fit, but large reference is deferred
        plan = self.ss.route_task(
            "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top.",
            load=True,
            context_mode="full",
            max_context_bytes=16_000,
        )
        lc = plan["loaded_context"]
        self.assertTrue(lc["full_instructions_loaded"])
        self.assertGreaterEqual(len(lc["deferred_references"]), 1)
        self.assertFalse(lc["deferred_references"][0]["full_instructions_loaded"])

    def test_gap_05_missing_file_utf8_error_path_traversal_and_agent_error_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_vault = Path(tmp)
            cache = self.ss.SessionContextCache(vault_root=tmp_vault)

            # Missing file
            rec_missing, err_missing = cache.read_verified_with_error("skills/non_existent/SKILL.md")
            self.assertIsNone(rec_missing)
            self.assertEqual(err_missing["error_code"], "FILE_NOT_FOUND")

            # Path traversal outside vault
            rec_trav, err_trav = cache.read_verified_with_error("../../etc/passwd")
            self.assertIsNone(rec_trav)
            self.assertEqual(err_trav["error_code"], "PATH_TRAVERSAL_BLOCKED")

            # Invalid UTF-8 file
            bad_utf8 = tmp_vault / "bad.md"
            bad_utf8.write_bytes(b"---\nname: bad\n---\n\xff\xfeinvalid utf8")
            rec_utf8, err_utf8 = cache.read_verified_with_error("bad.md")
            self.assertIsNone(rec_utf8)
            self.assertEqual(err_utf8["error_code"], "UTF8_DECODE_ERROR")

        # Sub-agent runtime failure -> graceful recovery via conductor fallback
        def failing_subagent_runner(packet: dict) -> dict:
            raise RuntimeError("Simulated sub-agent timeout")

        rep_err = self.ss.execute_task("CAPI ishlashini tekshir, xatolarni top.", subagent_runner=failing_subagent_runner)
        self.assertEqual(rep_err["execution_status"], "completed_with_warnings")
        self.assertEqual(rep_err["worker_executions"][0]["status"], "recovered_via_conductor_fallback")
        self.assertEqual(rep_err["execution_errors"][0]["error_code"], "SUBAGENT_EXECUTION_ERROR")

    def test_gap_06_persistent_session_cache_and_sha256_invalidation_on_file_edit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_vault = Path(tmp)
            sample_md = tmp_vault / "sample_skill.md"
            sample_md.write_text("---\nname: s1\n---\nVersion 1 content", encoding="utf-8")
            cache_file = tmp_vault / "session_cache.json"

            # Process 1 writes to persistent cache
            cache1 = self.ss.SessionContextCache(persist_path=cache_file, vault_root=tmp_vault)
            r1, e1 = cache1.read_verified_with_error("sample_skill.md")
            self.assertIsNone(e1)
            self.assertFalse(r1["from_session_cache"])
            self.assertTrue(cache_file.is_file())

            # Process 2 loads from persistent cache -> cache hit!
            cache2 = self.ss.SessionContextCache(persist_path=cache_file, vault_root=tmp_vault)
            r2, e2 = cache2.read_verified_with_error("sample_skill.md")
            self.assertIsNone(e2)
            self.assertTrue(r2["from_session_cache"])
            self.assertEqual(r2["content"], "---\nname: s1\n---\nVersion 1 content")

            # Modify file on disk -> Process 2 immediately invalidates stale cache and reads Version 2!
            sample_md.write_text("---\nname: s1\n---\nVersion 2 updated content", encoding="utf-8")
            r3, e3 = cache2.read_verified_with_error("sample_skill.md")
            self.assertIsNone(e3)
            self.assertFalse(r3["from_session_cache"])
            self.assertTrue(r3["cache_invalidated"])
            self.assertGreaterEqual(cache2.invalidations, 1)
            self.assertIn("Version 2 updated content", r3["content"])

    def test_gap_07_multi_harness_integration_paths_verified_for_claude_codex_cursor_windsurf(self) -> None:
        for h_name in ("claude_code", "codex", "cursor", "windsurf"):
            cap = self.ss.detect_harness_capabilities(VAULT, harness_override=h_name)
            self.assertEqual(cap["active_harness"], h_name)
            self.assertTrue(cap["active_harness_capabilities"]["supported"], f"{h_name} not supported")
            self.assertTrue(cap["active_harness_capabilities"]["supports_mcp_stdio"])

        # Verify harness-export.py exports all 4 targets cleanly into a temp directory
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run_tool_inproc("harness-export.py", "--target", "all", "--out", tmp, "--json")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            res = json.loads(proc.stdout)
            self.assertGreaterEqual(res["exported_count"], 28)
            self.assertTrue((Path(tmp) / ".cursor" / "rules").is_dir())
            self.assertTrue((Path(tmp) / ".windsurfrules").is_file())
            self.assertTrue((Path(tmp) / ".claude" / "commands").is_dir())
            self.assertTrue((Path(tmp) / ".codex-plugin" / "plugin.json").is_file())

    def test_gap_08_strict_hook_profile_never_silenced_by_warn_only(self) -> None:
        env = dict(**os.environ, TYRION_HOOK_PROFILE="strict")
        proc = subprocess.run(
            [sys.executable, str(VAULT / "hooks" / "tyrion-hook.py"), "guard", "--target", "manifests/catalog.json", "--warn-only"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
        )
        self.assertEqual(proc.returncode, 2, "strict profile must block protected file edits even when --warn-only is passed")

    def test_gap_09_mcp_universal_router_supports_execute_and_full_context(self) -> None:
        resp = self.mcp.handle_request({
            "jsonrpc": "2.0",
            "id": 950,
            "method": "tools/call",
            "params": {
                "name": "tyrion_universal_router",
                "arguments": {
                    "query": "Instagram uchun bir oylik kontent reja tayyorla.",
                    "execute": True,
                    "harness": "cursor",
                },
            },
        })
        payload = json.loads(resp["result"]["content"][0]["text"])
        self.assertEqual(payload["schema"], "tyrion.auto_router_execution/v5")
        self.assertEqual(payload["execution_status"], "completed")
        self.assertEqual(payload["harness"]["active_harness"], "cursor")
        self.assertFalse(payload["subagents_actually_spawned"])
        self.assertIn("social", payload["conductor_synthesis"]["applied_skills_verified"])

    def test_gap_10_unapproved_mutation_blocked_in_execute_task(self) -> None:
        rep = self.ss.execute_task("Meta kampaniyamda byudjetni 300% oshir va reklamalarni hoziroq o'chir", mutation_approved=False)
        self.assertEqual(rep["execution_status"], "blocked_mutation_approval")
        self.assertEqual(rep["worker_executions"], [])
        self.assertEqual(rep["deterministic_tool_outputs"], [])


if __name__ == "__main__":
    unittest.main()
