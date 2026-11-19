"""v7.1 -> v8 migratsiya: har eski nom mavjud yangi faylga ishora qiladi va router uni taniydi."""

from __future__ import annotations

import importlib
import json
import unittest

from tests._helpers import VAULT

ss = importlib.import_module("skill-search")
MIG = json.loads((VAULT / "manifests" / "migration-v8.json").read_text(encoding="utf-8"))


class MigrationTests(unittest.TestCase):
    def test_inventory_covers_every_v71_name(self) -> None:
        self.assertEqual(len(MIG["skills"]), 61)
        self.assertEqual(len(MIG["agents"]), 36)

    def test_every_old_skill_points_to_existing_file_and_new_skill(self) -> None:
        skills = {s["name"] for s in ss.load_skills()}
        for old, ent in MIG["skills"].items():
            with self.subTest(skill=old):
                self.assertTrue((VAULT / ent["path"]).is_file(), ent["path"])
                if not ent["new"].startswith("market:"):
                    self.assertIn(ent["new"], skills)

    def test_every_old_agent_points_to_existing_file_and_new_agent(self) -> None:
        agents = set(ss.load_agents())
        for old, ent in MIG["agents"].items():
            with self.subTest(agent=old):
                self.assertTrue((VAULT / ent["path"]).is_file(), ent["path"])
                self.assertIn(ent["new"], agents)

    def test_router_resolves_old_agent_names(self) -> None:
        self.assertEqual(ss.resolve_legacy_agent("audit-meta"), "platform-auditor")
        self.assertEqual(ss.resolve_legacy_agent("video-editor"), "video-producer")
        self.assertEqual(ss.resolve_legacy_agent("strategist"), "strategist")
        plan = ss.route_task("Meta lidlar sifatsiz", agent_hint="audit-meta", load=False, context_mode="manifest")
        self.assertEqual(plan["primary_agent"], "platform-auditor")

    def test_old_skill_names_resolve_and_are_aliases(self) -> None:
        self.assertEqual(ss.resolve_legacy_skill("ads-meta"), "audit")
        self.assertEqual(ss.resolve_legacy_skill("uzbekistan-market-intel"), "uzbekistan-market-intel")
        aliases = {a for s in ss.load_skills() for a in s["aliases"]}
        for old, ent in MIG["skills"].items():
            if not ent["new"].startswith("market:"):
                self.assertIn(old, aliases, old)

    def test_command_aliases_are_hidden_from_model(self) -> None:
        for name in MIG["hidden_commands"]:
            txt = (VAULT / "commands" / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn("disable-model-invocation: true", txt.split("\n---\n")[0], name)

    def test_uz_market_pack_loads_only_for_uz(self) -> None:
        uz = ss.route_task("Toshkentda stomatologiya uchun Meta reklama", load=False, context_mode="manifest")
        self.assertIn("markets/uz/market-intel.md", uz["references_to_load"])
        eu = ss.route_task("My Shopify store in Germany has low ROAS on Meta", load=False, context_mode="manifest")
        self.assertNotIn("markets/uz/market-intel.md", eu["references_to_load"])


if __name__ == "__main__":
    unittest.main()
