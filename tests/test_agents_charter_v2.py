"""Charter v2 (v8.2+): har kanonik agent charteri 6 majburiy blokka, rolga xos chiqish shartnomasiga,
Self-Audit darvozasiga va typed handoff'ga ega; boilerplate faqat rules/70-charter-baseline.md da.
"""

from __future__ import annotations

import importlib
import json
import re
import unittest

from tests._helpers import VAULT  # noqa: F401  (tools/ ni sys.path ga qo'shadi)
from tests.test_agent_charters import read_agent

AGENTS_DIR = VAULT / "agents"
SCHEMA_PATH = VAULT / "schemas" / "agent-handoff.schema.json"
BASELINE = VAULT / "rules" / "70-charter-baseline.md"

CORE_AGENTS = frozenset({
    "strategist", "platform-auditor", "creative-strategist", "video-producer", "budget-analyst",
    "audience-architect", "data-analyst", "tracking-specialist", "content-planner",
    "compliance-reviewer", "research-verifier", "release-verifier",
})
TARGETOLOG_AGENTS = frozenset({
    "client-onboarder", "ad-spy-analyst", "campaign-launcher", "daily-optimizer", "funnel-cro-doctor",
    "account-recovery-specialist", "client-comms-lead",
})
CANONICAL_AGENTS = CORE_AGENTS | TARGETOLOG_AGENTS

# Self-Audit turi: generativ/strategik -> rubrika >= 85/100; qolganlari -> Pass/Fail
SCORE_GATE = frozenset({"strategist", "creative-strategist", "video-producer", "content-planner",
                        "client-onboarder", "funnel-cro-doctor", "client-comms-lead"})
# Audit-format (`control_id` findings) faqat shu agentlarda ruxsat etiladi
AUDIT_FORMAT = frozenset({"platform-auditor", "compliance-reviewer", "tracking-specialist"})

MAX_TURNS = {
    **{a: 28 for a in ("strategist", "platform-auditor", "creative-strategist")},
    **{a: 24 for a in ("budget-analyst", "data-analyst", "tracking-specialist", "audience-architect",
                       "video-producer", "content-planner")},
    **{a: 18 for a in ("compliance-reviewer", "research-verifier", "release-verifier")},
    # Targetolog Copilot Pack (v8.3)
    "client-onboarder": 20, "ad-spy-analyst": 20, "campaign-launcher": 24, "daily-optimizer": 24,
    "funnel-cro-doctor": 24, "account-recovery-specialist": 18, "client-comms-lead": 18,
}

REQUIRED_SECTIONS = (
    "## Rejimlar", "## Qaror tartibi", "## Anti-Patternlar va Qat'iy Taqiqlar", "## Output contract",
    "## Self-Audit Sifat Darvozasi", "## Handoff Kontrakti", "## Rol bilimlari", "## Agent sikli",
)
REQUIRED_FM = ("name", "description", "role", "model", "maxTurns", "tools", "skills",
               "authority_boundary", "output_contract")
PATH_RE = re.compile(r"(?<![\w/.\-])((?:skills|wiki|rules|playbooks|contexts|templates|markets|manifests|docs|schemas|tools)/[\w\-./]*\.(?:md|json|py))")
ROLE_SUFFIXES = ("-analyst", "-specialist", "-verifier", "-reviewer", "-strategist", "-producer", "-planner",
                 "-architect", "-auditor", "-onboarder", "-launcher", "-optimizer", "-doctor", "-lead")
PACKET_RE = re.compile(r"`([a-z_]+_packet|strategic_brief)`")

# Routing regressiyasi: UZ/RU/EN so'rov -> kutilgan primary_agent
ROUTING_MATRIX = (
    ("offer tuzish lead magnet g'oya", "strategist"),
    ("полная маркетинговая стратегия", "strategist"),
    ("meta ads audit qilib ber", "platform-auditor"),
    ("google ads pmax search terms", "platform-auditor"),
    ("kreativ charchoq hook rate past", "creative-strategist"),
    ("продающий текст для рекламы", "creative-strategist"),
    ("reels skript yozib ber", "video-producer"),
    ("break-even roas hisobla", "budget-analyst"),
    ("detailed targeting lookalike overlap", "audience-architect"),
    ("capi tekshir pixel sozla", "tracking-specialist"),
    ("контент-план на месяц", "content-planner"),
    ("special ad category policy violation", "compliance-reviewer"),
    ("raqobatchilarni o'rganish bozor tahlili", "research-verifier"),
    ("Meta reklama ab test natijasi statistik ahamiyatlimi", "data-analyst"),
    ("результаты a/b теста рекламы статистическая значимость", "data-analyst"),
    ("ad experiment readout sample size check", "data-analyst"),
)


def section(body: str, title: str) -> str:
    start = body.index(title)
    nxt = body.find("\n## ", start + len(title))
    return body[start: nxt if nxt != -1 else len(body)]


class CharterV2InventoryTests(unittest.TestCase):
    def test_canonical_agents_match_disk_and_catalog(self) -> None:
        on_disk = {p.stem for p in AGENTS_DIR.glob("*.md")}
        self.assertEqual(on_disk, set(CANONICAL_AGENTS))
        catalog = json.loads((VAULT / "manifests" / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["counts"]["agents"], len(CANONICAL_AGENTS))
        self.assertEqual({i["name"] for i in catalog["items"]["agents"]}, set(CANONICAL_AGENTS))

    def test_mirror_has_every_canonical_agent(self) -> None:
        mirrored = {p.stem for p in (VAULT / ".claude" / "agents").glob("*.md")}
        self.assertEqual(mirrored, set(CANONICAL_AGENTS))

    def test_baseline_has_no_stale_agent_count(self) -> None:
        text = BASELINE.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\b36\s+(ta\s+)?agent", text), "70-charter-baseline: eskirgan '36 agent'")
        self.assertIn(f"**{len(CANONICAL_AGENTS)} ta kanonik agent charteri**", text)
        for needle in ("Charter v2", "Self-Audit", "Handoff", "needs_input", "blocked_mutation_approval",
                       "execution_evidence", "Prompt Defense Baseline", "Zero Findings"):
            self.assertIn(needle, text)


class CharterV2StructureTests(unittest.TestCase):
    def test_frontmatter_fields_and_max_turns(self) -> None:
        for name in sorted(CANONICAL_AGENTS):
            with self.subTest(agent=name):
                fm, _ = read_agent(name)
                for key in REQUIRED_FM:
                    self.assertTrue(fm.get(key, "").strip(), f"{name}: frontmatter `{key}` bo'sh")
                self.assertEqual(fm["name"], name)
                self.assertEqual(int(fm["maxTurns"]), MAX_TURNS[name], f"{name}: maxTurns tabaqasi")

    def test_required_sections_present(self) -> None:
        for name in sorted(CANONICAL_AGENTS):
            with self.subTest(agent=name):
                _, body = read_agent(name)
                for title in REQUIRED_SECTIONS:
                    self.assertIn(title, body, f"{name}: `{title}` yo'q")
                self.assertIn("[[70-charter-baseline]]", body)
                self.assertNotIn("## Procedure", body, f"{name}: boilerplate baseline'ga ko'chirilmagan")

    def test_modes_and_anti_patterns_are_substantive(self) -> None:
        for name in sorted(CANONICAL_AGENTS):
            with self.subTest(agent=name):
                _, body = read_agent(name)
                modes = [ln for ln in section(body, "## Rejimlar").splitlines() if ln.startswith("| `")]
                self.assertGreaterEqual(len(modes), 3, f"{name}: kamida 3 rejim kerak")
                bullets = [ln for ln in section(body, "## Anti-Patternlar").splitlines() if ln.startswith("- ")]
                self.assertGreaterEqual(len(bullets), 4, f"{name}: kamida 4 anti-pattern kerak")
                steps = re.findall(r"(?m)^\d\. ", section(body, "## Qaror tartibi"))
                self.assertGreaterEqual(len(steps), 4, f"{name}: qaror tartibi kamida 4 qadam")

    def test_self_audit_gate_type_and_rewrite_rule(self) -> None:
        for name in sorted(CANONICAL_AGENTS):
            with self.subTest(agent=name):
                _, body = read_agent(name)
                gate = section(body, "## Self-Audit Sifat Darvozasi")
                if name in SCORE_GATE:
                    self.assertIn("85/100", gate, f"{name}: >= 85/100 rubrika kerak")
                else:
                    self.assertIn("Pass/Fail", gate, f"{name}: Pass/Fail darvoza kerak")
                self.assertRegex(gate, r"1 marta|qayta yoz|2 aylanish", f"{name}: qayta yozish qoidasi yo'q")

    def test_role_native_output_contract(self) -> None:
        for name in sorted(CANONICAL_AGENTS):
            with self.subTest(agent=name):
                fm, body = read_agent(name)
                if name not in AUDIT_FORMAT:
                    self.assertNotIn("control_id", fm["output_contract"], f"{name}: audit shablon nusxalangan")
                    self.assertNotIn("control_id", body, f"{name}: audit-only `control_id` boilerplate")
                self.assertRegex(fm["output_contract"].lower(), r"self[_-]audit")
                self.assertIn("execution_evidence", fm["output_contract"])

    def test_handoff_packets_exist_in_schema(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        packets = set(schema["$defs"])
        for name in sorted(CANONICAL_AGENTS):
            with self.subTest(agent=name):
                _, body = read_agent(name)
                handoff = section(body, "## Handoff Kontrakti")
                self.assertIn("Upstream", handoff)
                self.assertIn("Downstream", handoff)
                for pkt in PACKET_RE.findall(body):
                    self.assertIn(pkt, packets, f"{name}: `{pkt}` schemas/agent-handoff.schema.json da yo'q")
                for other in re.findall(r"`([a-z]+(?:-[a-z]+)+)`", handoff):
                    if (VAULT / "agents" / f"{other}.md").exists() or other.endswith(ROLE_SUFFIXES):
                        self.assertIn(other, CANONICAL_AGENTS, f"{name}: handoff noma'lum agentga: {other}")

    def test_every_referenced_path_exists(self) -> None:
        for name in sorted(CANONICAL_AGENTS):
            with self.subTest(agent=name):
                _, body = read_agent(name)
                for rel in PATH_RE.findall(body):
                    self.assertTrue((VAULT / rel).is_file(), f"{name}: diskda yo'q: {rel}")

    def test_charter_body_stays_concise(self) -> None:
        for name in sorted(CANONICAL_AGENTS):
            with self.subTest(agent=name):
                _, body = read_agent(name)
                self.assertLessEqual(body.count("\n"), 140, f"{name}: charter tanasi juda uzun (token gigiyena)")


class HandoffSchemaTests(unittest.TestCase):
    def test_schema_is_valid_and_consistent(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema"]["const"], "tyrion.agent_handoff/v1")
        enum = set(schema["properties"]["packet_type"]["enum"])
        self.assertEqual(enum, set(schema["$defs"]))
        self.assertEqual({c["if"]["properties"]["packet_type"]["const"] for c in schema["allOf"]}, enum)
        for req in ("status", "payload", "execution_evidence", "self_audit"):
            self.assertIn(req, schema["required"])
        self.assertEqual(set(schema["properties"]["status"]["enum"]),
                         {"completed", "needs_input", "blocked_mutation_approval"})

    def test_core_packets_present(self) -> None:
        defs = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))["$defs"]
        for pkt in ("strategic_brief", "audit_findings_packet", "analytics_readout_packet", "budget_guard_packet",
                    "tracking_spec_packet", "compliance_clearance_packet", "verified_research_packet"):
            self.assertIn(pkt, defs)

    def test_rubrics_and_playbook_exist(self) -> None:
        for rel in ("skills/strategy/references/quality-rubric.md", "skills/creative/references/quality-rubric.md",
                    "skills/budget/references/quality-rubric.md", "skills/analyze/references/quality-rubric.md",
                    "skills/content/references/quality-rubric.md", "skills/analyze/references/data-analyst-playbook.md"):
            self.assertTrue((VAULT / rel).is_file(), rel)


class CharterV2RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ss = importlib.import_module("skill-search")

    def test_routing_matrix_has_no_regressions(self) -> None:
        for query, expected in ROUTING_MATRIX:
            with self.subTest(query=query):
                plan = self.ss.route_task(query, load=False, context_mode="manifest")
                self.assertEqual(plan["primary_agent"], expected)

    def test_router_registry_knows_every_canonical_agent(self) -> None:
        agents = self.ss.load_agents(force_reload=True)
        self.assertEqual(set(agents), set(CANONICAL_AGENTS))
        for name in sorted(CANONICAL_AGENTS):
            with self.subTest(agent=name):
                fm, _ = read_agent(name)
                self.assertEqual(self.ss.resolve_legacy_agent(name), name)
                self.assertTrue(agents[name]["skills"], f"{name}: skill ulanmagan")
                self.assertEqual(agents[name]["output_contract"], fm["output_contract"].strip('"'))
        problems, _warnings = self.ss.validate_registry()
        self.assertEqual(problems, [])

if __name__ == "__main__":
    unittest.main()
