"""Tyrion Universal: workflow routing, honest skill reading, delegation fallback, anti-recursion, token efficiency,
Meta economics and creative-intelligence regression tests."""

from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from tests._helpers import VAULT, run_tool_inproc

ss = importlib.import_module("skill-search")
twf = importlib.import_module("tyrion_workflows")
cm = importlib.import_module("creative-matrix")
calc = importlib.import_module("calculator")

CLAUDE_CAPS = {"supports_native_subagents": True, "active_harness": "claude_code"}
CLI_CAPS = {"supports_native_subagents": False, "active_harness": "cli_standalone"}

NL_CASES = [
    # (query, workflow_id, primary_agent)
    ("Shu biznes uchun Meta Ads strategiya tuz", "meta_strategy", "launch-planner"),
    ("Build a complete Meta Ads strategy for this business", "meta_strategy", "launch-planner"),
    ("Сделай стратегию Meta Ads для моего бизнеса", "meta_strategy", "launch-planner"),
    ("Mijoz uchun reklama strategiyasini tayyorla", "meta_strategy", "launch-planner"),
    ("Raqobatchilarimni o'rganib menga reklama strategiyasi tuz", "competitor_strategy", "positioning-strategist"),
    ("Raqobatchilarimni tahlil qil", "competitor_research", "research-worker"),
    ("Menga professional Reels ssenariysi yoz", "video_script", "reels-scriptwriter"),
    ("Мне нужен сценарий рилс", "video_script", "reels-scriptwriter"),
    ("Meta Ads kampaniyam nima sababdan yaxshi ishlamayapti?", "campaign_diagnosis", "audit-meta"),
    ("Google Ads kampaniyam yaxshi ishlamayapti", "campaign_diagnosis", "audit-google"),
    ("Kreativlarimni yaxshilash kerak", "creative_improve", "creative-strategist"),
    ("Улучши мои креативы", "creative_improve", "creative-strategist"),
    ("Ushbu reklama natijalarini tahlil qil", "results_analysis", "audit-meta"),
    ("Menga to'liq marketing rejasi kerak", "marketing_plan_full", "launch-planner"),
]


class NaturalLanguageRoutingTests(unittest.TestCase):
    def test_user_examples_route_to_expected_workflow_and_primary_agent(self) -> None:
        for q, wf, agent in NL_CASES:
            plan = ss.route_task(q, load=False, context_mode="manifest")
            self.assertEqual(plan["status"], "ready", q)
            self.assertEqual(plan["execution_plan"]["workflow_id"], wf, q)
            self.assertEqual(plan["primary_agent"], agent, q)
            self.assertFalse(plan["asks_user_for_skill_or_agent"], q)

    def test_non_meta_platform_strategy_does_not_hijack_to_meta(self) -> None:
        for q in ("Нужна стратегия для VK Ads, стоматология в Ташкенте", "Google Ads strategiya tuz", "TikTok Ads strategiya tuz"):
            plan = ss.route_task(q, load=False, context_mode="manifest")
            self.assertNotEqual((plan.get("execution_plan") or {}).get("workflow_id"), "meta_strategy", q)

    def test_content_plan_is_not_an_ad_strategy(self) -> None:
        plan = ss.route_task("Instagram uchun bir oylik kontent reja tayyorla", load=False, context_mode="manifest")
        self.assertEqual(plan["primary_agent"], "social-content-writer")

    def test_greeting_and_off_topic_stay_out_of_scope(self) -> None:
        for q in ("salom", "ob-havo qanday bo'ladi?"):
            self.assertEqual(ss.route_task(q, load=True)["status"], "out_of_scope", q)

    def test_single_specialist_task_keeps_ranker_and_spawns_no_team(self) -> None:
        plan = ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=True)
        self.assertEqual(plan["primary_agent"], "tracking-specialist")
        self.assertEqual(plan["supporting_agents"], [])


class WorkflowManifestTests(unittest.TestCase):
    def test_manifest_validates_against_real_agents_skills_tools(self) -> None:
        errors, _warn = twf.validate_workflows(ss.load_agents(force_reload=True), ss.load_skills(force_reload=True))
        self.assertEqual(errors, [])

    def test_dag_dependencies_precede_dependents_and_synthesis_is_last(self) -> None:
        for wf in twf.load_workflows(force=True)["workflows"]:
            levels = twf._levels(wf["stages"])
            pos = {sid: i for i, lvl in enumerate(levels) for sid in lvl}
            for st in wf["stages"]:
                for n in st.get("needs", []):
                    self.assertLess(pos[n], pos[st["id"]], f"{wf['id']}: {n} -> {st['id']}")
            self.assertEqual(len({s["output"] for s in wf["stages"]}), len(wf["stages"]), wf["id"])

    def test_meta_strategy_dependency_order_is_professional(self) -> None:
        plan = twf.build_execution_plan("Meta Ads strategiya tuz", CLI_CAPS, ss.load_agents())
        lvl = {s["id"]: s["level"] for s in plan["stages"]}
        self.assertLess(lvl["intake"], lvl["economics"])
        self.assertLess(lvl["positioning"], lvl["audience"])
        self.assertLess(lvl["economics"], lvl["audience"])
        self.assertLess(lvl["creative"], lvl["video"])
        self.assertLess(max(lvl[s] for s in ("audience", "architecture", "creative", "tracking", "video")), lvl["validate"])
        self.assertEqual(lvl["synthesize"], max(lvl.values()))
        self.assertEqual(lvl["economics"], lvl["tracking"])  # mustaqil: parallel

    def test_only_necessary_agents_are_activated(self) -> None:
        plan = twf.build_execution_plan("Meta Ads strategiya tuz", CLI_CAPS, ss.load_agents())
        agents = {s["agent"] for s in plan["stages"] if s["agent"] != "conductor"}
        self.assertLessEqual(len(agents), 9)
        self.assertLess(len(agents), len(ss.load_agents()) / 3)
        self.assertNotIn("audit-tiktok", agents)
        video = twf.build_execution_plan("Reelsga skript yoz", CLI_CAPS, ss.load_agents())
        self.assertLessEqual({s["agent"] for s in video["stages"]}, {"conductor", "reels-scriptwriter", "copy-writer"})

    def test_cycle_and_orchestrator_recursion_are_rejected(self) -> None:
        cfg = json.loads(json.dumps(twf.load_workflows()))
        wf = cfg["workflows"][0]
        wf["stages"][0]["needs"] = [wf["stages"][-1]["id"]]
        with self.assertRaises(ValueError):
            twf._levels(wf["stages"])
        bad = json.loads(json.dumps(twf.load_workflows()))
        bad["workflows"][0]["stages"][1]["skills"] = ["tyrion-universal"]
        orig = twf.load_workflows
        twf.load_workflows = lambda force=False: bad  # type: ignore[assignment]
        try:
            errs, _ = twf.validate_workflows(ss.load_agents(), ss.load_skills())
        finally:
            twf.load_workflows = orig  # type: ignore[assignment]
        self.assertTrue(any("rekursiya" in e for e in errs))


class DelegationHonestyTests(unittest.TestCase):
    def test_cli_harness_declares_single_conductor_fallback(self) -> None:
        plan = twf.build_execution_plan("Meta Ads strategiya tuz", CLI_CAPS, ss.load_agents())
        self.assertEqual(plan["delegation"]["mode"], "single_conductor_fallback")
        self.assertFalse(plan["delegation"]["subagents_actually_spawned"])
        self.assertTrue(all(s["execution"] in ("conductor", "conductor_inline_as_specialist") for s in plan["stages"]))

    def test_claude_code_harness_plans_native_subagents_but_router_never_claims_spawn(self) -> None:
        plan = twf.build_execution_plan("Meta Ads strategiya tuz", CLAUDE_CAPS, ss.load_agents())
        self.assertEqual(plan["delegation"]["mode"], "native_subagents")
        self.assertFalse(plan["delegation"]["subagents_actually_spawned"])
        self.assertIn("native_subagent", {s["execution"] for s in plan["stages"]})
        self.assertEqual({s["execution"] for s in plan["stages"] if s["agent"] == "conductor"}, {"conductor"})

    def test_execute_task_reports_no_spawn_without_runner(self) -> None:
        rep = ss.execute_task("Shu biznes uchun Meta Ads strategiya tuz")
        self.assertFalse(rep["subagents_actually_spawned"])
        self.assertEqual(rep["execution_mode"], "single_conductor_fallback")

    def test_platform_swap_uses_matching_audit_agent(self) -> None:
        plan = twf.build_execution_plan("TikTok reklamam nega ishlamayapti", CLI_CAPS, ss.load_agents())
        self.assertEqual(plan["primary_agent"], "audit-tiktok")
        self.assertNotIn("audit-meta", {s["agent"] for s in plan["stages"]})


class AntiRecursionTests(unittest.TestCase):
    def test_specialist_caller_gets_no_workflow_or_delegation(self) -> None:
        plan = ss.route_task("Meta Ads strategiya tuz", load=False, context_mode="manifest", caller="specialist")
        self.assertIsNone(plan["execution_plan"])
        self.assertFalse(plan["delegation_allowed"])

    def test_agent_hint_means_specialist_already_chosen(self) -> None:
        plan = ss.route_task("Meta Ads strategiya tuz", agent_hint="audit-meta", load=False, context_mode="manifest")
        self.assertIsNone(plan["execution_plan"])
        self.assertEqual(plan["primary_agent"], "audit-meta")

    def test_env_flag_marks_specialist(self) -> None:
        os.environ["TYRION_SPECIALIST"] = "1"
        try:
            plan = ss.route_task("Meta Ads strategiya tuz", load=False, context_mode="manifest")
        finally:
            os.environ.pop("TYRION_SPECIALIST")
        self.assertIsNone(plan["execution_plan"])

    def test_universal_skill_is_not_routable_and_not_attached_to_agents(self) -> None:
        for q in ("tyrion universal", "orchestrate marketing tasks automatically", "Meta Ads strategiya tuz"):
            hits = [s["name"] for _sc, s in ss.rank(ss.load_skills(), q)]
            self.assertNotIn("tyrion-universal", hits, q)
        for name, ag in ss.load_agents().items():
            self.assertNotIn("tyrion-universal", ag.get("skills", []), name)
            self.assertNotIn("tyrion-universal", (VAULT / "agents" / f"{name}.md").read_text(encoding="utf-8"), name)

    def test_duplicate_stage_work_flagged_in_plan(self) -> None:
        for q, _wf, _a in NL_CASES:
            plan = twf.build_execution_plan(q, CLI_CAPS, ss.load_agents())
            self.assertFalse(any(s["duplicate_of_previous"] for s in plan["stages"]), q)


class SkillReadingHonestyAndTokenTests(unittest.TestCase):
    def test_progressive_slice_is_reported_truncated_not_verified(self) -> None:
        plan = ss.route_task("Shu biznes uchun Meta Ads strategiya tuz", load=True, context_mode="progressive")
        lc = plan["loaded_context"]
        self.assertTrue(lc["read_in_full_before_claiming"])
        for sk in lc["loaded_skills"]:
            if sk["truncated"]:
                self.assertFalse(sk["full_instructions_loaded"])
                self.assertNotIn(sk["name"], lc["applied_skills_verified"])
        self.assertTrue(lc["context_budget"]["within_budget"])

    def test_full_mode_verifies_required_skills(self) -> None:
        plan = ss.route_task("Shu biznes uchun Meta Ads strategiya tuz", load=True, context_mode="full")
        lc = plan["loaded_context"]
        self.assertTrue(set(plan["required_skills"]) <= set(lc["applied_skills_verified"]))
        self.assertEqual(lc["read_in_full_before_claiming"], [])

    def test_manifest_mode_loads_nothing_and_defers_skills(self) -> None:
        plan = ss.route_task("Shu biznes uchun Meta Ads strategiya tuz", load=False, context_mode="manifest")
        self.assertEqual(plan["loaded_context"]["context_budget"]["used_bytes"], 0)
        self.assertTrue(plan["stage_skills_deferred"])
        self.assertEqual(plan["loaded_context"]["applied_skills_verified"], [])

    def test_workflow_route_is_far_smaller_than_loading_everything(self) -> None:
        plan = ss.route_task("Shu biznes uchun Meta Ads strategiya tuz", load=True)
        used = plan["loaded_context"]["context_budget"]["used_bytes"]
        self.assertLess(used, 40_000)
        self.assertGreater(plan["loaded_context"]["token_telemetry"]["token_savings_pct"], 90)

    def test_compact_mode_keeps_a_single_skill(self) -> None:
        plan = ss.route_task("Meta reklamamdan lidlar sifatsiz", load=True, context_mode="compact")
        self.assertEqual(len(plan["required_skills"]), 1)
        self.assertLessEqual(plan["loaded_context"]["context_budget"]["used_bytes"], 4500)

    def test_universal_skill_is_an_orchestrator_not_a_copy_of_everything(self) -> None:
        text = (VAULT / "skills/tyrion-universal/SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(text.splitlines()), 160)
        for ref in ("orchestration-protocol.md", "workflow-recipes.md"):
            self.assertTrue((VAULT / "skills/tyrion-universal/references" / ref).is_file())
        self.assertIn("## 3. Read before you claim", text)
        errs, _w = ss.validate_registry()
        self.assertEqual(errs, [])


class HookEntryPointTests(unittest.TestCase):
    def _hook(self, prompt: str) -> str:
        env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(VAULT)}
        node = shutil.which("node")
        cmd = [node, str(VAULT / "hooks/run-hook.cjs"), "route"] if node else [sys.executable, str(VAULT / "hooks/tyrion-hook.py"), "route"]
        return subprocess.run(cmd, input=json.dumps({"prompt": prompt}), capture_output=True, text=True, env=env, timeout=30).stdout

    def test_marketing_prompt_gets_route_hint_pointing_to_universal_skill(self) -> None:
        out = self._hook("Shu biznes uchun Meta Ads strategiya tuz")
        self.assertIn("workflow=meta_strategy", out)
        self.assertIn("tyrion-universal", out)

    def test_non_marketing_and_slash_prompts_stay_silent(self) -> None:
        self.assertEqual(self._hook("salom").strip(), "")
        self.assertEqual(self._hook("/doctor now please").strip(), "")

    def test_hooks_manifest_registers_prompt_route_and_session_brief_mentions_entry_point(self) -> None:
        hooks = json.loads((VAULT / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
        self.assertIn("UserPromptSubmit", hooks)
        brief = subprocess.run([sys.executable, str(VAULT / "hooks/tyrion-hook.py"), "brief"], capture_output=True, text=True, timeout=30).stdout
        self.assertIn("tyrion-universal", brief)


class McpIntegrationTests(unittest.TestCase):
    def _call(self, name: str, args: dict) -> dict:
        srv = importlib.import_module("tyrion-mcp-server")
        return srv.call_tool(name, args) if hasattr(srv, "call_tool") else srv.handle_tool_call(name, args)

    def test_router_tool_schema_exposes_caller_and_creative_tool_exposes_iterate(self) -> None:
        srv = importlib.import_module("tyrion-mcp-server")
        tools = {t["name"]: t for t in srv.MCP_TOOLS}
        self.assertIn("caller", tools["tyrion_universal_router"]["inputSchema"]["properties"])
        self.assertIn("iterate", tools["tyrion_creative_matrix"]["inputSchema"]["properties"]["mode"]["enum"])


class MetaEconomicsTests(unittest.TestCase):
    def test_breakeven_target_cpl_and_scenarios_are_arithmetically_correct(self) -> None:
        r = calc.calc_funnel_economics("1200000", "500000", processing_fee_pct="1.5", target_profit_pct="20",
                                        lead_to_sale_cvr_pct="12", daily_budget="500000", assumed_cpl="60000",
                                        cpl_low="40000", cpl_high="90000", currency="UZS")
        self.assertEqual(r["breakeven_cpa"], 682000.0)
        self.assertEqual(r["target_cpa"], 442000.0)
        self.assertEqual(r["breakeven_cpl"], 81840.0)
        base = next(s for s in r["scenarios"] if s["scenario"] == "base")
        self.assertEqual(base["implied_cpa"], 500000.0)
        self.assertTrue(base["profitable_at_breakeven"])
        self.assertFalse(base["meets_target_profit"])
        self.assertAlmostEqual(base["daily_gross_profit_after_ads"], 182000.0, places=0)
        pess = next(s for s in r["scenarios"] if s["scenario"] == "pessimistic")
        self.assertFalse(pess["profitable_at_breakeven"])
        self.assertTrue(all(s["label"] == "ASSUMPTION" for s in r["scenarios"]))

    def test_no_volume_forecast_without_user_assumed_cpl_and_no_universal_target(self) -> None:
        r = calc.calc_funnel_economics("100", "40")
        self.assertNotIn("scenarios", r)
        self.assertIn("scenarios_note", r)
        self.assertEqual(r["evidence_labels"]["decision_conversions"].split()[0], "HEURISTIC_PRIOR_MODEL")

    def test_scaling_constraint_follows_spend_guard_20pct(self) -> None:
        r = calc.calc_funnel_economics("100", "40")
        self.assertEqual(r["scaling_constraints"]["max_step_per_change_pct"], 20)
        self.assertEqual(r["scaling_constraints"]["steps_to_double_budget"], 4)

    def test_unprofitable_unit_economics_reports_error(self) -> None:
        self.assertIn("error", calc.calc_funnel_economics("100", "120"))

    def test_cli_funnel_economics_json(self) -> None:
        proc = run_tool_inproc("calculator.py", "funnel-economics", "--price", "100", "--cogs", "40", "--json")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)["breakeven_cpa"], 58.0)


class CreativeIntelligenceTests(unittest.TestCase):
    def test_video_script_has_no_invented_statistics_or_prices(self) -> None:
        res = cm.generate_video_script(product="Ingliz tili kursi", problem="gapira olmaslik", duration_sec=30)
        blob = json.dumps(res, ensure_ascii=False)
        for bad in ("90%", "10 tadan 9", "14 kunda", "Yuzlab mijoz", "Kрупniy"):
            self.assertNotIn(bad, blob)
        self.assertIn("NARX KIRITILMAGAN", res["price_anchor"])

    def test_known_price_still_produces_anchor(self) -> None:
        mat = cm.build_matrix("ecom", "Kostyum", 150.0, market="eu", currency="EUR")
        self.assertTrue(mat["price_known"])
        self.assertNotIn("NARX", mat["price_anchor"])

    def test_claim_linter_flags_unverified_claims_but_not_placeholders(self) -> None:
        self.assertTrue(cm.lint_unverified_claims({"hook": "90% of clients win in 14 days with guarantee"})["needs_verification"])
        clean = cm.lint_unverified_claims({"hook": "[ADD VERIFIED RESULT AND TIMEFRAME HERE]"})
        self.assertFalse(clean["needs_verification"])
        self.assertTrue(clean["placeholders_present"])

    def test_cli_outputs_claim_safety(self) -> None:
        proc = run_tool_inproc("creative-matrix.py", "video-script", "--product", "Kurs", "--problem", "x", "--json")
        self.assertIn("claim_safety", json.loads(proc.stdout))

    def test_iterate_prioritizes_first_funnel_loss_and_keeps_rest_constant(self) -> None:
        r = cm.diagnose_creative_iteration(
            {"hook_rate": 31.0, "hold_rate": 8.0, "outbound_ctr": 0.4},
            {"hook_rate": 27.0, "hold_rate": 14.0, "outbound_ctr": 1.0}, impressions=5000)
        self.assertEqual(r["priority_fix"]["stage"], "RETENTION")
        self.assertIn("hook", r["priority_fix"]["keep_constant"].lower())
        self.assertEqual(r["nature"].split()[0], "DIAGNOSTIC_HYPOTHESES")

    def test_iterate_attention_failure_changes_only_opening(self) -> None:
        r = cm.diagnose_creative_iteration({"hook_rate": 12.0}, {"hook_rate": 28.0})
        self.assertEqual(r["priority_fix"]["stage"], "ATTENTION")
        self.assertIn("0-3s", r["priority_fix"]["change_next"])

    def test_iterate_labels_priors_and_small_samples(self) -> None:
        r = cm.diagnose_creative_iteration({"hook_rate": 10.0}, None, impressions=300)
        self.assertEqual(r["findings"][0]["baseline_source"], "HEURISTIC_PRIOR_MODEL")
        self.assertEqual(len(r["warnings"]), 2)

    def test_iterate_without_any_baseline_for_non_prior_metric_says_so(self) -> None:
        r = cm.diagnose_creative_iteration({"lp_cvr": 1.0})
        self.assertEqual(r["findings"][0]["status"], "NO_BASELINE")
        self.assertIsNone(r["priority_fix"])

    def test_cheap_leads_poor_sales_points_to_qualification(self) -> None:
        r = cm.diagnose_creative_iteration({"qualified_lead_rate": 5.0}, {"qualified_lead_rate": 20.0})
        self.assertEqual(r["priority_fix"]["stage"], "LEAD_QUALITY")

    def test_meta_audience_help_does_not_crash(self) -> None:
        for args in (["--help"], ["overlap", "--help"], ["lookalike", "--help"]):
            proc = subprocess.run([sys.executable, str(VAULT / "tools/meta-audience.py"), *args], capture_output=True, text=True, timeout=30)
            self.assertEqual(proc.returncode, 0, proc.stderr[-300:])


class PluginSyncTests(unittest.TestCase):
    def test_workflow_references_and_legacy_orchestrators_are_gone_without_dangling_refs(self) -> None:
        for gone in ("tyrion", "orch-audit", "orch-campaign-launch", "orch-creative-sprint", "orch-weekly-review"):
            self.assertFalse((VAULT / "skills" / gone).exists(), gone)
        gone = {"tyrion", "orch-audit", "orch-campaign-launch", "orch-creative-sprint", "orch-weekly-review"}
        for s in ss.load_skills():
            self.assertFalse(gone & set(s.get("related_skills", [])), s["name"])
        for p in list((VAULT / "agents").glob("*.md")) + list((VAULT / "skills").glob("*/SKILL.md")):
            txt = p.read_text(encoding="utf-8")
            for g in gone - {"tyrion"}:
                self.assertNotIn(g, txt, f"{p}: {g}")

    def test_claude_agent_mirror_matches_canonical_after_edits(self) -> None:
        proc = subprocess.run([sys.executable, str(VAULT / "tools/install-hooks.py"), "--agents-only", "--dry-run"], capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
