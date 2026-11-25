"""Targetolog Copilot Pack (v8.3): 7 yordamchi agent, 7 slash buyruq, 6 DAG workflow, routing va xavfsizlik chegaralari."""

from __future__ import annotations

import collections
import importlib
import json
import re
import unittest

from tests._helpers import VAULT  # noqa: F401  (tools/ ni sys.path ga qo'shadi)
from tests.test_agent_charters import read_agent, tool_list
from tests.test_agents_charter_v2 import CORE_AGENTS, PATH_RE, REQUIRED_SECTIONS, TARGETOLOG_AGENTS, section

PLUGIN = "mcp__plugin_tyrion_tyrion-core__"

COMMANDS = {
    "onboard": "client-onboarder",
    "ad-spy": "ad-spy-analyst",
    "launch-plan": "campaign-launcher",
    "morning-triage": "daily-optimizer",
    "cro-dm": "funnel-cro-doctor",
    "appeal": "account-recovery-specialist",
    "client-update": "client-comms-lead",
}

WORKFLOWS = {
    "new_client_onboarding": "client-onboarder",
    "campaign_build_to_launch": "campaign-launcher",
    "morning_media_buyer_triage": "daily-optimizer",
    "lead_quality_and_dm_fix": "funnel-cro-doctor",
    "competitor_ad_spy": "ad-spy-analyst",
    "account_restriction_recovery": "account-recovery-specialist",
}

PACKETS = {
    "client-onboarder": "client_onboarding_packet",
    "ad-spy-analyst": "ad_spy_packet",
    "campaign-launcher": "launch_blueprint_packet",
    "daily-optimizer": "daily_triage_packet",
    "funnel-cro-doctor": "cro_fix_packet",
    "account-recovery-specialist": "recovery_action_packet",
    "client-comms-lead": "client_comms_packet",
}

# UZ / RU / EN so'rov -> kutilgan primary_agent (birinchi 7 tasi — reja §5 dagi namunalar)
ROUTING_MATRIX = (
    ("yangi mijoz brif", "client-onboarder"),
    ("ertalabki optimizatsiya kill scale", "daily-optimizer"),
    ("direct skript lid sifati", "funnel-cro-doctor"),
    ("reklama rejected apellyatsiya", "account-recovery-specialist"),
    ("mijozga telegram hisobot", "client-comms-lead"),
    ("raqobatchi ad library tahlil", "ad-spy-analyst"),
    ("kampaniya cbo abo launch reja", "campaign-launcher"),
    ("бриф нового клиента онбординг", "client-onboarder"),
    ("client onboarding checklist for a new client", "client-onboarder"),
    ("реклама конкурентов библиотека рекламы", "ad-spy-analyst"),
    ("spy competitor ads teardown", "ad-spy-analyst"),
    ("структура кампании cbo или abo", "campaign-launcher"),
    ("campaign structure blueprint naming convention", "campaign-launcher"),
    ("утренняя оптимизация почему вырос cpl", "daily-optimizer"),
    ("morning triage kill hold iterate scale", "daily-optimizer"),
    ("скрипт для директа заявки есть продаж нет", "funnel-cro-doctor"),
    ("dm qualification script lead form", "funnel-cro-doctor"),
    ("аккаунт заблокирован апелляция", "account-recovery-specialist"),
    ("ad account restricted request review", "account-recovery-specialist"),
    ("отчет клиенту в телеграм", "client-comms-lead"),
    ("client objection reply why no sales", "client-comms-lead"),
    # v8.3.1 regressiyalari: keng workflow'lar (meta_strategy, weekly_review) bu so'rovlarni egallamasligi kerak
    ("Meta reklama rejected bo'ldi, apellyatsiya matnini tayyorla", "account-recovery-specialist"),
    ("Mijozga telegram hisobot yoz: bu hafta lidlar soni va keyingi qadamlar", "client-comms-lead"),
)


class TargetologCharterTests(unittest.TestCase):
    def test_seven_agents_exist_with_charter_v2_sections(self) -> None:
        self.assertEqual(len(TARGETOLOG_AGENTS), 7)
        self.assertEqual(len(CORE_AGENTS | TARGETOLOG_AGENTS), 19)
        for name in sorted(TARGETOLOG_AGENTS):
            with self.subTest(agent=name):
                fm, body = read_agent(name)
                self.assertTrue(fm["description"].strip('"').startswith("Use this agent"))
                for title in REQUIRED_SECTIONS:
                    self.assertIn(title, body)
                for rel in PATH_RE.findall(body):
                    self.assertTrue((VAULT / rel).is_file(), f"{name}: diskda yo'q: {rel}")
                self.assertIn(PACKETS[name], fm["output_contract"])
                self.assertIn(f"`{PACKETS[name]}`", section(body, "## Handoff Kontrakti"))

    def test_triggers_are_multilingual(self) -> None:
        for name in sorted(TARGETOLOG_AGENTS):
            with self.subTest(agent=name):
                text = (VAULT / "agents" / f"{name}.md").read_text(encoding="utf-8")
                trig = re.search(r"(?ms)^triggers:\n((?:- .*\n)+)", text).group(1)
                self.assertRegex(trig, r"[a-z]", "lotin (UZ/EN) trigger yo'q")
                self.assertRegex(trig, r"[а-яё]", "kirill (RU/UZ) trigger yo'q")
                self.assertGreaterEqual(trig.count("\n- ") + 1, 10)

    def test_no_duplicate_triggers_across_all_19_agents(self) -> None:
        ss = importlib.import_module("skill-search")
        owners: dict[str, list[str]] = collections.defaultdict(list)
        for name, info in ss.load_agents(force_reload=True).items():
            for trig in info["triggers"]:
                owners[trig.strip().lower()].append(name)
        dups = {t: a for t, a in owners.items() if len(a) > 1}
        self.assertEqual(dups, {}, "trigger to'qnashuvi")

    def test_skill_links_are_bidirectional(self) -> None:
        ss = importlib.import_module("skill-search")
        problems, _ = ss.validate_registry()
        self.assertEqual(problems, [])
        agents = ss.load_agents(force_reload=True)
        for name in sorted(TARGETOLOG_AGENTS):
            self.assertTrue(agents[name]["skills"], name)


class SafetyBoundaryTests(unittest.TestCase):
    def test_account_recovery_is_strictly_white_hat(self) -> None:
        fm, body = read_agent("account-recovery-specialist")
        boundary = fm["authority_boundary"].lower()
        for needle in ("white-hat", "cloaking", "fake documents", "farmed"):
            self.assertIn(needle, boundary)
        for needle in ("Cloaking", "Soxta hujjat", "white-hat", "rules/40-xavfsizlik-va-hisob.md", "white_hat_only: true",
                       "qat'iyan taqiqlanadi"):
            self.assertIn(needle, body)
        gate = section(body, "## Self-Audit Sifat Darvozasi")
        self.assertIn("100% white-hat", gate)
        playbook = (VAULT / "skills/audit/references/account-recovery-whitehat.md").read_text(encoding="utf-8")
        self.assertIn("faqat white-hat", playbook)
        self.assertIn("hech qachon", playbook)
        schema = json.loads((VAULT / "schemas/agent-handoff.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$defs"]["recovery_action_packet"]["properties"]["white_hat_only"], {"const": True})
        self.assertIn("white_hat_only", schema["$defs"]["recovery_action_packet"]["required"])

    def test_spend_guard_enforced_for_launcher_and_optimizer(self) -> None:
        for name in ("campaign-launcher", "daily-optimizer"):
            with self.subTest(agent=name):
                fm, body = read_agent(name)
                self.assertIn(PLUGIN + "tyrion_spend_guard", tool_list(fm))
                self.assertIn("Spend-Guard", fm["authority_boundary"])
                self.assertIn("spend_guard_required", fm["output_contract"])
                self.assertRegex(body, r"\+20%")
                self.assertIn("`tyrion_spend_guard`", body)
                self.assertNotIn("Write", tool_list(fm))

    def test_no_new_agent_has_write_or_spawn_tools(self) -> None:
        for name in sorted(TARGETOLOG_AGENTS):
            with self.subTest(agent=name):
                tools = set(tool_list(read_agent(name)[0]))
                self.assertFalse(tools & {"Write", "Edit", "MultiEdit", "NotebookEdit", "Agent", "Task"})


class TargetologCommandTests(unittest.TestCase):
    def test_seven_commands_exist_point_to_agents_and_are_mirrored(self) -> None:
        for cmd, agent in COMMANDS.items():
            with self.subTest(command=cmd):
                src = VAULT / "commands" / f"{cmd}.md"
                self.assertTrue(src.is_file())
                text = src.read_text(encoding="utf-8")
                head = text.split("\n---\n")[0]
                self.assertIn("disable-model-invocation: true", head)
                self.assertIn("description:", head)
                self.assertIn("$ARGUMENTS", text)
                self.assertIn(f"`{agent}`", text)
                self.assertIn(f"agents/{agent}.md", text)
                self.assertTrue((VAULT / "agents" / f"{agent}.md").is_file())
                self.assertEqual(text, (VAULT / ".claude" / "commands" / f"{cmd}.md").read_text(encoding="utf-8"))
                for rel in PATH_RE.findall(text):
                    self.assertTrue((VAULT / rel).is_file(), f"/{cmd}: diskda yo'q: {rel}")


class TargetologWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.twf = importlib.import_module("tyrion_workflows")
        cls.ss = importlib.import_module("skill-search")

    def test_six_workflows_pass_validation(self) -> None:
        errors, warnings = self.twf.validate_workflows(self.ss.load_agents(force_reload=True), self.ss.load_skills(force_reload=True))
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        by_id = {w["id"]: w for w in self.twf.load_workflows(force=True)["workflows"]}
        for wid, primary in WORKFLOWS.items():
            with self.subTest(workflow=wid):
                self.assertIn(wid, by_id)
                wf = by_id[wid]
                self.assertEqual(wf["primary_agent"], primary)
                levels = self.twf._levels(wf["stages"])
                self.assertGreaterEqual(len(levels), 2, "DAG kamida 2 daraja")
                self.assertEqual(len({s["output"] for s in wf["stages"]}), len(wf["stages"]))

    def test_workflow_dag_shapes_match_plan(self) -> None:
        by_id = {w["id"]: w for w in self.twf.load_workflows(force=True)["workflows"]}
        agents_in = lambda wid: [s["agent"] for s in by_id[wid]["stages"]]  # noqa: E731
        self.assertEqual(agents_in("new_client_onboarding")[0], "client-onboarder")
        self.assertEqual(agents_in("new_client_onboarding")[-1], "strategist")
        self.assertEqual(agents_in("campaign_build_to_launch")[-2:], ["campaign-launcher", "compliance-reviewer"])
        self.assertEqual(agents_in("morning_media_buyer_triage")[0], "data-analyst")
        self.assertTrue(by_id["morning_media_buyer_triage"]["stages"][0].get("optional_when"))
        self.assertEqual(agents_in("morning_media_buyer_triage")[-1], "client-comms-lead")
        self.assertEqual(agents_in("lead_quality_and_dm_fix")[-2:], ["creative-strategist", "client-comms-lead"])
        self.assertEqual(agents_in("competitor_ad_spy"), ["ad-spy-analyst", "creative-strategist", "video-producer"])
        self.assertTrue(by_id["competitor_ad_spy"]["stages"][-1].get("optional_when"))
        self.assertEqual(agents_in("account_restriction_recovery"),
                         ["account-recovery-specialist", "compliance-reviewer", "client-comms-lead"])
        lvl = self.twf._levels(by_id["campaign_build_to_launch"]["stages"])
        self.assertEqual(set(lvl[0]), {"audience", "creative", "tracking"}, "parallel daraja")

    def test_handoff_schema_has_targetolog_packets(self) -> None:
        defs = json.loads((VAULT / "schemas/agent-handoff.schema.json").read_text(encoding="utf-8"))["$defs"]
        for pkt in PACKETS.values():
            self.assertIn(pkt, defs)


class TargetologRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ss = importlib.import_module("skill-search")

    def test_routing_matrix(self) -> None:
        for query, expected in ROUTING_MATRIX:
            with self.subTest(query=query):
                plan = self.ss.route_task(query, load=False, context_mode="manifest")
                self.assertEqual(plan["primary_agent"], expected)

    def test_new_triggers_never_route_to_another_agent(self) -> None:
        """Trigger yo'qolishi (gate: out_of_scope / needs_clarification) mumkin, boshqa agentga ketishi — yo'q."""
        agents = self.ss.load_agents(force_reload=True)
        own = total = 0
        for name in sorted(TARGETOLOG_AGENTS):
            for trig in agents[name]["triggers"]:
                total += 1
                with self.subTest(agent=name, trigger=trig):
                    got = self.ss.route_task(trig, load=False, context_mode="manifest")["primary_agent"]
                    self.assertIn(got, (name, ""), f"to'qnashuv: '{trig}' -> {got}")
                    own += got == name
        self.assertGreaterEqual(own / total, 0.70)


if __name__ == "__main__":
    unittest.main()
