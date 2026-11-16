"""Agent charterlari <-> haqiqiy Claude Code sub-agentlari: asbob/protsedura mosligi, yo'llar, mirror.

1-bosqich (pilot): faqat `CONVERTED` dagi charterlar tekshiriladi; qolganlari
`PENDING_STAGE2` da va aniq sabab bilan o'tkazib yuboriladi (2-bosqichda `CONVERTED` = hammasi).
"""

from __future__ import annotations

import importlib
import re
import sys
import unittest
from pathlib import Path

from tests._helpers import VAULT  # noqa: F401  (tools/ ni sys.path ga qo'shadi)

AGENTS = VAULT / "agents"
PLUGIN_SERVER = "mcp__plugin_tyrion_tyrion-core__"
PROJECT_SERVER = "mcp__tyrion-core__"

CONVERTED = frozenset({"audit-meta", "meta-audience-architect", "copy-writer"})
ALL_AGENTS = sorted(p.stem for p in AGENTS.glob("*.md"))
PENDING_STAGE2 = [n for n in ALL_AGENTS if n not in CONVERTED]

# CLI qadami -> uni almashtiruvchi MCP asbobi (qoplanmagan qadam Bash talab qiladi).
CLI_TO_MCP = {
    "skill-search.py": "universal_router",
    "meta-targeting-engine.py": "meta_detailed_targeting",
    "spend-guard.py": "spend_guard",
    "calculator.py": "media_calculator",
    "creative-matrix.py": "creative_matrix",
    "capi-utm-builder.py": "capi_utm",
    "brain-search.py": "brain_search",
    "meta-insights-sync.py": "meta_live_insights",
}
MCP_COVERED_SUBCOMMANDS = {"meta-audience.py": {"architect"}}  # overlap/saturation/... uchun MCP yo'q

ROOTS = ("skills/", "wiki/", "rules/", "playbooks/", "contexts/", "templates/", "markets/", "manifests/")


def read_agent(name: str) -> tuple[dict[str, str], str]:
    text = (AGENTS / f"{name}.md").read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    assert m, f"{name}: frontmatter yo'q"
    fm: dict[str, str] = {}
    for line in m.group(1).split("\n"):
        k = re.match(r"([A-Za-z_]+):\s*(.*)", line)
        if k:
            fm[k.group(1)] = k.group(2)
    return fm, m.group(2)


def tool_list(fm: dict[str, str]) -> list[str]:
    return [t.strip() for t in fm.get("tools", "").split(",") if t.strip()]


def required_tools(body: str) -> set[str]:
    """Charter matnidagi CLI qadamlari uchun zarur asbob nomlari ("Bash" yoki MCP qisqa nomi)."""
    need: set[str] = set()
    for script, sub in re.findall(r"python3 tools/([\w\-]+\.py)(?:\s+([\w\-]+))?", body):
        if script in CLI_TO_MCP:
            need.add("mcp:" + CLI_TO_MCP[script] + "|Bash")
        elif script in MCP_COVERED_SUBCOMMANDS and sub in MCP_COVERED_SUBCOMMANDS[script]:
            need.add("mcp:meta_audience|Bash")
        else:
            need.add("Bash")
    return need


class AgentCharterTests(unittest.TestCase):
    def test_pending_list_is_explicit(self) -> None:
        self.assertEqual(len(ALL_AGENTS), 36)
        self.assertTrue(CONVERTED <= set(ALL_AGENTS))

    def test_converted_charters(self) -> None:
        mcp_server = importlib.import_module("tyrion-mcp-server")
        real_tools = {t["name"] for t in mcp_server.MCP_TOOLS}
        for name in sorted(CONVERTED):
            with self.subTest(agent=name):
                fm, body = read_agent(name)
                tools = tool_list(fm)

                # 1. Asbob = protsedura
                for need in required_tools(body):
                    if need == "Bash":
                        self.assertIn("Bash", tools, f"{name}: CLI qadami bor, Bash ham MCP ham yo'q")
                    else:
                        mcp_name = need.split(":")[1].split("|")[0]
                        self.assertTrue(
                            "Bash" in tools or PLUGIN_SERVER + "tyrion_" + mcp_name in tools,
                            f"{name}: `{mcp_name}` qadami uchun na MCP na Bash bor",
                        )
                for t in tools:
                    if t.startswith("mcp__"):
                        self.assertTrue(t.startswith(PLUGIN_SERVER), f"{name}: noto'g'ri MCP prefiks {t}")
                        self.assertIn(t[len(PLUGIN_SERVER):], real_tools, f"{name}: MCP serverda yo'q asbob {t}")
                for mcp_name in re.findall(r"`(tyrion_[a-z_]+)`", body):
                    self.assertIn(PLUGIN_SERVER + mcp_name, tools, f"{name}: matnda `{mcp_name}` bor, tools: da yo'q")

                # 2. Audit agentlariga Write/Edit yo'q; sub-agent ichida sub-agent yo'q
                if name.startswith("audit-"):
                    self.assertFalse({"Write", "Edit", "MultiEdit", "NotebookEdit"} & set(tools), f"{name}: audit agentida yozish asbobi")
                self.assertNotIn("Agent", tools)
                self.assertNotIn("Task", tools)

                # 3. description "qachon chaqiriladi"ni aytadi
                self.assertTrue(fm["description"].startswith("Use this agent"), f"{name}: description 'Use this agent ...' bilan boshlanmagan")
                self.assertIn("Invoke on", fm["description"])

                # 4. Agent sikli va to'xtash holatlari
                for needle in ("Agent sikli", "needs_input", "blocked_mutation_approval", "completed", "missing_inputs", "execution_evidence"):
                    self.assertIn(needle, body, f"{name}: '{needle}' yo'q")

    def test_converted_paths_exist_and_legacy_names_gone(self) -> None:
        for name in sorted(CONVERTED):
            with self.subTest(agent=name):
                _fm, body = read_agent(name)
                self.assertNotIn("Claude Ads conductor", body)
                self.assertNotIn("<plugin_root>", body)
                self.assertIsNone(re.search(r"(?<![\w/.])(?:\.\./wiki/|local/|ads/(?:SKILL|references))", body), f"{name}: eski yo'l qolgan")
                for p in re.findall(r"`((?:" + "|".join(re.escape(r) for r in ROOTS) + r")[\w\-./]*\.(?:md|json|py))`", body):
                    self.assertTrue((VAULT / p).is_file(), f"{name}: diskda yo'q: {p}")

    def test_pending_charters_are_tracked_not_hidden(self) -> None:
        # 2-bosqichgacha: kutilayotgan charterlar yuqoridagi tekshiruvlardan o'tmaydi; ro'yxat aniq.
        self.assertEqual(len(PENDING_STAGE2), 33)


class AgentMirrorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ih = importlib.import_module("install-hooks")

    def test_render_rewrites_mcp_prefix_and_drops_skills(self) -> None:
        for name in sorted(CONVERTED):
            with self.subTest(agent=name):
                src = (AGENTS / f"{name}.md").read_text(encoding="utf-8")
                out = self.ih.render_project_agent(src, "tyrion", f"{name}.md")
                self.assertNotIn("mcp__plugin_", out)
                self.assertIn(PROJECT_SERVER + "tyrion_", out)
                fm = out.split("---")[1]
                self.assertNotRegex(fm, r"(?m)^skills:")
                self.assertIn("GENERATED from agents/", out)
                self.assertEqual(re.search(r"(?m)^model: (\w+)", out).group(1), re.search(r"(?m)^model: (\w+)", src).group(1))

    def test_mirror_in_repo_matches_canonical_and_is_idempotent(self) -> None:
        self.assertEqual(self.ih.sync_agents(VAULT, dry_run=True), [], "agents/ va .claude/agents/ drift: `python3 tools/install-hooks.py --agents-only`")
        mirrored = {p.stem for p in (VAULT / ".claude" / "agents").glob("*.md")}
        self.assertEqual(mirrored, set(self.ih.MIRRORED_AGENTS or ALL_AGENTS))

    def test_sync_agents_into_temp_dir(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            changed = self.ih.sync_agents(Path(tmp), dry_run=False)
            self.assertEqual(len(changed), len(CONVERTED))
            self.assertEqual(self.ih.sync_agents(Path(tmp), dry_run=False), [])


if __name__ == "__main__":
    unittest.main()
