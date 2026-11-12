"""skill-search.py: scope-darvoza (out_of_scope / needs_clarification), til aniqlash, mintaqaviy platformalar."""

from __future__ import annotations

import importlib
import json
import unittest

from tests._helpers import run_tool_inproc

ss = importlib.import_module("skill-search")


class ScopeGateTests(unittest.TestCase):
    def _route(self, q: str) -> dict:
        return ss.route_task(q, load=True)

    def test_greetings_are_out_of_scope(self) -> None:
        for q in ("salom", "Assalomu alaykum", "hello", "Привет", "hi!"):
            plan = self._route(q)
            self.assertEqual(plan["status"], "out_of_scope", q)
            self.assertEqual(plan["primary_agent"], "", q)
            self.assertEqual(plan["required_skills"], [], q)
            self.assertFalse(plan["loaded_context"]["actually_loaded"], q)

    def test_non_marketing_requests_are_out_of_scope(self) -> None:
        for q in ("write me a python script to sort a list", "bugungi ob-havo qanday", "напиши рецепт борща", "how do I fix a leaking tap"):
            self.assertEqual(self._route(q)["status"], "out_of_scope", q)

    def test_generic_query_needs_clarification(self) -> None:
        for q in ("reklama", "реклама", "ads", "marketing"):
            plan = self._route(q)
            self.assertEqual(plan["status"], "needs_clarification", q)
            self.assertGreaterEqual(len(plan["clarifying_questions"]), 3, q)
            self.assertEqual(plan["primary_agent"], "", q)

    def test_clarification_questions_follow_language(self) -> None:
        self.assertIn("platforma", " ".join(self._route("reklama")["clarifying_questions"]).lower())
        self.assertIn("платформ", " ".join(self._route("реклама")["clarifying_questions"]).lower())
        self.assertIn("platform", " ".join(self._route("ads")["clarifying_questions"]).lower())

    def test_real_marketing_queries_still_route(self) -> None:
        for q in ("Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top",
                  "Audit my Google Ads Performance Max and search terms negative keywords",
                  "Telegram Ads kampaniyam va Telegram bot voronkasini tekshir",
                  "pixel ishlamayapti purchase event kelmayapti",
                  "instagram da sotuv yoq"):
            self.assertIn(self._route(q)["status"], ("ready", "fallback_ready"), q)

    def test_low_confidence_with_rich_query_keeps_fallback_contract(self) -> None:
        plan = self._route("zzz qqq unknown holographic billboard telemetry xyz")
        self.assertEqual(plan["status"], "fallback_ready")

    def test_execute_task_short_circuits(self) -> None:
        for q, want in (("salom", "out_of_scope"), ("reklama", "needs_clarification")):
            rep = ss.execute_task(q)
            self.assertEqual(rep["execution_status"], want)
            self.assertEqual(rep["worker_executions"], [])
            self.assertEqual(rep["deterministic_tool_outputs"], [])

    def test_cli_json_and_text_modes(self) -> None:
        proc = run_tool_inproc("skill-search.py", "route", "salom", "--json")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)["status"], "out_of_scope")
        proc = run_tool_inproc("skill-search.py", "route", "reklama")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("needs_clarification", proc.stdout)


class LanguageDetectionTests(unittest.TestCase):
    def test_uzbek_latin_with_english_brand_words(self) -> None:
        for q in ("instagram da sotuv yoq", "pixel ishlamayapti purchase event kelmayapti",
                  "Meta Ads kampaniyam uchun retargeting audience kerak",
                  "Google Ads CPA oshib ketdi, nima qilish kerak",
                  "tiktok ads dan lid kelmayapti", "facebook pixel purchase event yo'q"):
            self.assertEqual(ss.detect_language(q), "uz_latin", q)

    def test_english_stays_english(self) -> None:
        for q in ("write me a python script to sort a list", "I need data for ads", "audit my Google Ads account",
                  "why is my CPA going up", "hello"):
            self.assertEqual(ss.detect_language(q), "en", q)

    def test_cyrillic_variants(self) -> None:
        self.assertEqual(ss.detect_language("Нужна стратегия для Яндекс Директ"), "ru")
        self.assertEqual(ss.detect_language("мижозлар учун реклама"), "uz_cyrillic")


class RegionalPlatformTests(unittest.TestCase):
    def test_yandex_direct_russian_query_routes_to_own_skill(self) -> None:
        plan = ss.route_task("Нужна стратегия для Яндекс Директ, стоматология в Ташкенте", load=True)
        self.assertIn("ads-yandex", plan["required_skills"] + plan["supporting_skills"])
        self.assertEqual(plan["intent_analysis"]["detected_language"], "ru")
        self.assertEqual(plan["required_skills"][0], "ads-yandex")

    def test_yandex_audit_routes_to_audit_agent(self) -> None:
        plan = ss.route_task("Проверь аудит Яндекс Директ: РСЯ и минус-слова", load=True)
        self.assertEqual(plan["required_skills"][0], "ads-yandex")
        self.assertEqual(plan["primary_agent"], "audit-google")

    def test_registry_valid_with_new_skill(self) -> None:
        problems, _ = ss.validate_registry()
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()


class EnglishMutationGateTests(unittest.TestCase):
    def test_english_live_mutations_are_blocked(self) -> None:
        for q in ("Increase my Meta Ads budget by 300% now and delete the old ads",
                  "pause all campaigns right now", "double the Google budget by 100%"):
            self.assertEqual(ss.route_task(q, load=False)["status"], "blocked_mutation_approval", q)

    def test_english_advisory_questions_are_not_blocked(self) -> None:
        for q in ("why is my CPA going up on Google Ads", "how does Meta budget pacing work"):
            self.assertNotEqual(ss.route_task(q, load=False)["status"], "blocked_mutation_approval", q)
