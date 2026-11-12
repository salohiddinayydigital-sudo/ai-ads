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

    def test_vk_ads_russian_queries_route_to_own_skill(self) -> None:
        for q in ("Нужна стратегия для VK Ads, стоматология в Ташкенте",
                  "Проверь аудит рекламы ВКонтакте: VK Реклама и ретаргетинг",
                  "Настрой таргет во ВК для интернет-магазина"):
            plan = ss.route_task(q, load=True)
            self.assertEqual(plan["required_skills"][0], "ads-vk", q)
            self.assertEqual(plan["intent_analysis"]["detected_language"], "ru", q)

    def test_vk_does_not_hijack_other_platforms(self) -> None:
        plan = ss.route_task("Audit my Google Ads Performance Max and search terms negative keywords", load=True)
        self.assertNotIn("ads-vk", plan["required_skills"] + plan["supporting_skills"])

    def test_registry_valid_with_new_skill(self) -> None:
        problems, _ = ss.validate_registry()
        self.assertEqual(problems, [])


class RealQueryRegressionTests(unittest.TestCase):
    """5-qadam: 34 real operator so'rovi — UZ lotin/kirill, RU, EN. Niyat -> platforma routingi.

    Har satr (so'rov, kutgan primary_agent, kutgan birinchi skill) — joriy ishlaydigan
    xulq qayd etilgan; regressiya buzilishi darhol ko'rinadi."""

    EXPECTED = [
        ("Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top", "audit-meta", "ads-meta"),
        ("Telegram Ads kanalga obunachi yig'ish 500 dollar byudjet", "audit-telegram", "ads-telegram"),
        ("yangi mijoz o'quv markazi, oyiga 1000$ byudjet, nimadan boshlaymiz", "launch-planner", "ads-plan"),
        ("Таргет для стоматологии в Ташкенте, бюджет 300 долларов", "audit-budget", "ads-budget"),
        ("Audit my Google Ads Performance Max and search terms", "audit-google", "ads-google"),
        ("meta ads 4 qatlamli auditoriya overlap va exclusion qur", "meta-audience-architect", "ads-meta-audience"),
        ("кинстик типография аниматсион рилс", "video-editor", "video-motion-graphics"),
        ("креатив хохлашга", "audit-creative", "ads-creative"),
        ("CPA qimmatlab ketdi, qayerda pul ketmoqda", "performance-analyst", "ads-math"),
        ("weekly performance report for my meta campaigns", "performance-analyst", "orch-weekly-review"),
        (".pixel va CAPI event_id deduplikatsiya tekshir", "tracking-specialist", "ads-server-side-tracking"),
        ("Instagram reels skript yozib ber kiyim do'koni uchun", "reels-scriptwriter", "reels-scripting"),
        ("некачественные лиды мета", "audit-meta", "ads-meta"),
        ("YouTube kanal uchun reklama videosi montaj qil", "video-editor", "video-editing"),
        ("Snapchat Ads kampaniyam tekshir", "audit-platform", "ads-snapchat"),
        ("LinkedIn B2B lidlar kampaniya qurish", "audit-platform", "ads-linkedin"),
        ("Amazon PPC sponsored products audit", "audit-platform", "ads-amazon"),
        ("Google qidiruv so'rovlarida salbiy kalit so'zlar kerak", "audit-google", "ads-google"),
        ("продвижение нового магазина одежды с нуля", "launch-planner", "ads-plan"),
        ("online store uchun to'liq marketing strategiya", "launch-planner", "ads-plan"),
        ("конверсия трекинг событие не работает", "audit-tracking", "ads-server-side-tracking"),
        ("Telegram bot voronka kechikish muammosi", "audit-telegram", "ads-telegram"),
        ("ROAS past, kampaniyani qanday optimizatsiya qilamiz", "audit-budget", "ads-optimize"),
        ("mijoz uchun haftalik hisobot tayyorla", "release-verifier", "ads-report"),
        ("AUD my tiktok campaign creative fatigue", "audit-creative", "ads-creative"),
        ("landing sahifa konversiya past, CRO tekshiruv", "seo-auditor", "ads-landing"),
        ("boshlang'ich byudjet bilan kampaniya ochkazish rejasi", "media-buyer", "ads-plan"),
        ("Instagram'da brend xabardorligi kampaniyasi", "creative-strategist", "ads-dna"),
        ("недвижимость в Ташкенте лиды", "meta-audience-architect", "ads-meta"),
        ("IELTS kurslari uchun lidlar yig'ish", "meta-audience-architect", "ads-meta"),
        ("куда уходит бюджет в гугл рекламе", "audit-budget", "ads-budget"),
        ("EMQ oshirish uchun maydonlarni hashla", "tracking-specialist", "ads-server-side-tracking"),
        ("повышение конверсии лендинга", "launch-planner", "cro"),
        ("Meta reklamamdan kelayotgan lidlar sifatsiz, CPA 20 dollarga chiqdi, sababi nima", "audit-meta", "ads-meta"),
    ]

    def test_real_queries_route_to_expected_primary_agent(self) -> None:
        self.assertGreaterEqual(len(self.EXPECTED), 30)
        for q, agent, skill in self.EXPECTED:
            plan = ss.route_task(q, load=False)
            self.assertEqual(plan["status"], "ready", f"{q} -> {plan['status']}")
            self.assertEqual(plan["primary_agent"], agent, q)
            self.assertTrue(plan["required_skills"], q)
            self.assertIn(skill, plan["required_skills"], q)

    def test_intent_before_platform_for_start_from_scratch(self) -> None:
        """'nimadan boshlaymiz' niyati byudjet skillidan ustun turadi (niyat -> platforma)."""
        plan = ss.route_task("yangi mijoz o'quv markazi, oyiga 1000$ byudjet, nimadan boshlaymiz", load=False)
        self.assertEqual(plan["primary_agent"], "launch-planner")
        self.assertIn("ads-plan", plan["required_skills"])
        self.assertEqual(plan["intent_analysis"]["niche"], "edu")

    def test_channel_growth_intent_routes_with_platform(self) -> None:
        plan = ss.route_task("Telegram Ads kanalga obunachi yig'ish 500 dollar byudjet", load=False)
        self.assertIn("telegram", plan["intent_analysis"]["domains"])
        self.assertIn("ads-telegram", plan["required_skills"])

    def test_budget_intent_extracted_from_required_queries(self) -> None:
        import tyrion_core as tcore
        b1 = tcore.extract_budget_from_query("Telegram Ads kanalga obunachi yig'ish 500 dollar byudjet")
        self.assertEqual((b1["amount"], b1["currency"]), (500.0, "USD"))
        b2 = tcore.extract_budget_from_query("yangi mijoz o'quv markazi, oyiga 1000$ byudjet, nimadan boshlaymiz")
        self.assertEqual((b2["amount"], b2["period"]), (1000.0, "monthly"))

    def test_mutation_requests_are_gated_multilingual(self) -> None:
        for q in ("byudjetni 50% oshirish kerak",
                  "oylik byudjetni oshirish kerak 500 dollar",
                  "budget +40% and pause campaigns",
                  "увеличить бюджет на 60%"):
            self.assertEqual(ss.route_task(q, load=False)["status"], "blocked_mutation_approval", q)

    def test_advisory_budget_requests_are_not_blocked(self) -> None:
        for q in ("byudjet oshirish rejasi tuz", "budget increase advice please", "byudjet taqsimlash qanday qilinadi"):
            self.assertEqual(ss.route_task(q, load=False)["status"], "ready", q)

    def test_default_market_is_uz(self) -> None:
        """v8: standart bozor uz (O'zbekiston/MDH maqsadi)."""
        plan = ss.route_task("new campaign for a coffee shop in my city", load=False)
        self.assertEqual(plan["market_context"]["market_id"], "uz")

    def test_language_detection_on_required_queries(self) -> None:
        self.assertEqual(ss.route_task("Telegram Ads kanalga obunachi yig'ish 500 dollar byudjet", load=False)["intent_analysis"]["detected_language"], "uz_latin")
        self.assertEqual(ss.route_task("Таргет для стоматологии в Ташкенте", load=False)["intent_analysis"]["detected_language"], "ru")
        self.assertEqual(ss.route_task("Audit my Google Ads campaign", load=False)["intent_analysis"]["detected_language"], "en")


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
