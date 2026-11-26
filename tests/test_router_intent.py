"""Router niyat va scope regressiyalari (v8.3.2): A/B test, landing CRO, qurish niyati, agent-trigger scope-darvozasi."""

from __future__ import annotations

import importlib
import unittest

from tests._helpers import VAULT  # noqa: F401  (tools/ ni sys.path ga qo'shadi)

ss = importlib.import_module("skill-search")

# (so'rov, kutilgan primary agent, kutilgan birinchi skill yoki None)
CASES = [
    ("A/B test natijasi statistik ahamiyatli mi", "data-analyst", "experiments"),
    ("test natijasi qaysi variant yutdi", "data-analyst", "experiments"),
    ("landing sahifa konversiyasi past", "funnel-cro-doctor", "funnel"),
    ("Telegram Ads kampaniya tuz", "campaign-launcher", "strategy"),
    ("сделай план запуска для интернет-магазина", "campaign-launcher", "strategy"),
    ("CBO yoki ABO tanlash naming", "campaign-launcher", None),
    ("bozor tadqiqoti va custdev savollari", "research-verifier", None),
    ("release tekshir skill sifati", "release-verifier", None),
    ("ads ban appeal rus tilida", "account-recovery-specialist", None),
    ("reklamalarim charchadi frequency 4.5", "creative-strategist", None),
    ("dm qualification script", "funnel-cro-doctor", None),
    # audit niyati saqlanadi: qurish fe'li yo'q yoki audit fe'li bor
    ("Google Ads search terms wasted spend", "platform-auditor", "audit"),
    ("Telegram Ads kampaniya audit qil", "platform-auditor", "audit"),
]


class RouterIntentTests(unittest.TestCase):
    def test_cases(self) -> None:
        for query, agent, skill in CASES:
            with self.subTest(query=query):
                plan = ss.route_task(query, load=False, context_mode="manifest")
                self.assertIn(plan["status"], ("ready", "fallback_ready"))
                self.assertEqual(plan["primary_agent"], agent)
                if skill:
                    self.assertEqual(plan["required_skills"][0], skill)

    def test_short_uzbek_sentences_detected_as_uzbek(self) -> None:
        for q in ("akkauntim bloklandi apellyatsiya yoz", "landing sahifa konversiyasi past", "UZS byudjet 5 mln break-even ROAS"):
            with self.subTest(query=q):
                self.assertEqual(ss.detect_language(q), "uz_latin")

    def test_out_of_scope_still_blocked(self) -> None:
        for q in ("python kod yozib ber", "bugun ob-havo qanday", "salom"):
            with self.subTest(query=q):
                plan = ss.route_task(q, load=False, context_mode="manifest")
                self.assertEqual(plan["status"], "out_of_scope")
                self.assertEqual(plan["primary_agent"], "")

    def test_every_agent_trigger_routes_to_its_owner(self) -> None:
        """Butun trigger iborasi bo'lgan so'rov boshqa agentga ketmasligi kerak (gate'dan o'tmagan juda qisqa iboralar bundan mustasno)."""
        for name, agent in ss.load_agents().items():
            for trig in agent["triggers"]:
                with self.subTest(agent=name, trigger=trig):
                    got = ss.route_task(trig, load=False, context_mode="manifest")["primary_agent"]
                    self.assertIn(got, (name, ""))

    def test_explicit_agent_hint_beats_build_bias(self) -> None:
        plan = ss.route_task("Meta Ads strategiya tuz", agent_hint="platform-auditor", load=False, context_mode="manifest")
        self.assertEqual(plan["primary_agent"], "platform-auditor")


if __name__ == "__main__":
    unittest.main()
