"""DetailedTargetingUpgradeTests, DetailedTargetingAccuracyTests, LiveMetaSmokeTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from tests._helpers import VAULT



class DetailedTargetingUpgradeTests(unittest.TestCase):
    """Comprehensive automated acceptance tests for the upgraded Detailed Targeting Engine (Query Expansion, 5-Factor Relevance Ranking, Live Workflow & Targetologist Report)."""

    def setUp(self) -> None:
        self.mte = importlib.import_module("meta-targeting-engine")
        self.ma = importlib.import_module("meta-audience")
        self.mcp = importlib.import_module("tyrion-mcp-server")

    def _with_mock_server(self, handler_cls):
        import http.server
        import threading
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server

    def test_dt_upg_01_explicit_queries_never_dropped_by_query_limits_or_synonym_expansion(self) -> None:
        # First two queries have multiple synonyms in MULTILINGUAL_QUERY_SYNONYMS; even with max_queries=3, all 4 explicit queries must be preserved!
        explicit = ["ko'chmas mulk", "stomatologiya", "Custom Niche Query Alpha", "Custom Niche Query Beta"]
        expanded = self.mte.expand_search_queries(
            product="Toshkentda xonadonlar",
            niche="real-estate",
            extra_queries=explicit,
            max_queries=3,
        )
        q_list = [x["query"] for x in expanded]
        for eq in explicit:
            self.assertIn(eq, q_list, f"Explicit query {eq!r} was silently dropped!")
        # Verify explicit queries come first with P1 priority
        for idx, eq in enumerate(explicit):
            self.assertEqual(expanded[idx]["query"], eq)
            self.assertEqual(expanded[idx]["origin"], "explicit_user_query")
            self.assertEqual(expanded[idx]["priority_tier"], "P1_EXPLICIT_USER_QUERY")

    def test_dt_upg_02_uzbek_and_russian_inputs_generate_useful_relevant_search_candidates(self) -> None:
        # Uzbek Latin medical / dental input with problem and intent
        uz_lat = self.mte.expand_search_queries(
            product="Tish implantatsiyasi va breket qo'yish klinikasi",
            problem_solved="Tish og'rig'i va estetik tabassum tiklash",
            purchase_intent="Bepul 3D diagnostika va konsultatsiya",
            complementary_products="Oral hygiene",
            niche="medical",
            max_queries=12,
        )
        uz_lat_qs = {x["query"] for x in uz_lat}
        self.assertTrue({"Dental implant", "Orthodontics", "Dentistry", "Cosmetic dentistry"} & uz_lat_qs, uz_lat_qs)

        # Uzbek Cyrillic real estate input
        uz_cyr = self.mte.expand_search_queries(
            product="Тошкентда кўчмас мулк ва хонадон ипотека асосида",
            niche="real-estate",
            max_queries=10,
        )
        uz_cyr_qs = {x["query"] for x in uz_cyr}
        self.assertIn("Real estate", uz_cyr_qs)
        self.assertIn("Mortgage loan", uz_cyr_qs)

        # Russian auto detailing input
        ru_auto = self.mte.expand_search_queries(
            product="Детейлинг автомобиля, автосервис и запчасти",
            niche="auto",
            max_queries=10,
        )
        ru_auto_qs = {x["query"] for x in ru_auto}
        self.assertIn("Auto detailing", ru_auto_qs)
        self.assertIn("Automotive repair shop", ru_auto_qs)
        self.assertIn("Car parts", ru_auto_qs)

    def test_dt_upg_03_irrelevant_api_results_do_not_outrank_strongly_relevant_results_arriving_later(self) -> None:
        import http.server

        class NoisyFirstHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                if "targetingvalidation" in self.path:
                    body = {
                        "data": [
                            {"id": "9001", "name": "Freebies & Funny Memes", "valid": True},
                            {"id": "9002", "name": "Music", "valid": True},
                            {"id": "9003", "name": "The Implants (rock band)", "valid": True},
                            {"id": "1001", "name": "Dental implant", "valid": True},
                            {"id": "1002", "name": "Cosmetic dentistry", "valid": True},
                        ]
                    }
                else:
                    # API returns 3 irrelevant/broad items FIRST and the 2 genuinely relevant items LAST
                    body = {
                        "data": [
                            {
                                "id": "9001",
                                "name": "Freebies & Funny Memes",
                                "type": "interests",
                                "path": ["Interests", "Entertainment", "Humor"],
                                "audience_size_lower_bound": 50000000,
                                "audience_size_upper_bound": 60000000,
                            },
                            {
                                "id": "9002",
                                "name": "Music",
                                "type": "interests",
                                "path": ["Interests", "Entertainment", "Music"],
                                "audience_size_lower_bound": 800000000,
                                "audience_size_upper_bound": 950000000,
                            },
                            {
                                "id": "9003",
                                "name": "The Implants (rock band)",
                                "type": "interests",
                                "path": ["Interests", "Entertainment", "Music", "Rock music"],
                                "audience_size_lower_bound": 12000,
                                "audience_size_upper_bound": 15000,
                            },
                            {
                                "id": "1001",
                                "name": "Dental implant",
                                "type": "interests",
                                "path": ["Interests", "Fitness and wellness", "Dentistry"],
                                "audience_size_lower_bound": 320000,
                                "audience_size_upper_bound": 390000,
                            },
                            {
                                "id": "1002",
                                "name": "Cosmetic dentistry",
                                "type": "interests",
                                "path": ["Interests", "Fitness and wellness", "Dentistry"],
                                "audience_size_lower_bound": 410000,
                                "audience_size_upper_bound": 480000,
                            },
                        ]
                    }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(NoisyFirstHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_ranking_test"
            rep = self.mte.search_and_validate_targeting(
                product="Tish implantatsiyasi va vinirlar",
                problem_solved="Tish yo'qotilishi va estetik tabassum",
                niche="medical",
                queries=["Dental implant"],
                ad_account_id="act_999111",
                max_queries=1,
            )
            prim = rep["primary_recommended_interests"]
            # Only the 2 genuinely relevant verified interests should be in primary_recommended_interests (never padded to 5!)
            self.assertEqual(len(prim), 2, f"Expected exactly 2 relevant interests, got: {[x['name'] for x in prim]}")
            self.assertEqual({x["id"] for x in prim}, {"1001", "1002"})
            # And they must be ranked #1 and #2 in verified_targeting_options ahead of the noisy first API results
            self.assertIn(rep["verified_targeting_options"][0]["id"], ("1001", "1002"))
            self.assertIn(rep["verified_targeting_options"][1]["id"], ("1001", "1002"))

            # Verify irrelevant items are captured in excluded_low_relevance_options for diagnostic transparency
            excl_ids = {x["id"] for x in rep["excluded_low_relevance_options"]}
            self.assertEqual(excl_ids, {"9001", "9002", "9003"})

            # Verify score disclaimer is attached to every candidate
            for it in prim:
                self.assertEqual(it["score_disclaimer"], "SYSTEM_RELEVANCE_ESTIMATE_NOT_META_SCORE_OR_PERFORMANCE_GUARANTEE")
                self.assertGreaterEqual(it["relevance_score"], 70.0)
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_upg_04_offline_ideas_never_enter_verified_list_even_with_max_relevance(self) -> None:
        old_tok = os.environ.pop("META_ACCESS_TOKEN", None)
        try:
            rep = self.mte.search_and_validate_targeting(
                product="Real estate",
                problem_solved="Property investment and apartment buying",
                niche="real-estate",
                queries=["Real estate", "Apartment"],
            )
            self.assertEqual(rep["verified_targeting_options"], [])
            self.assertEqual(rep["primary_recommended_interests"], [])
            self.assertEqual(rep["recommended_audience_combinations"]["combinations"], [])
            # Offline ideas have high relevance scores (>70), yet remain strictly RELATED_UNVERIFIED
            self.assertTrue(any(x["relevance_score"] >= 70.0 for x in rep["related_unverified_ideas"]))
            self.assertTrue(all(x["validation_status"] == "RELATED_UNVERIFIED" for x in rep["related_unverified_ideas"]))
            self.assertTrue(all(x["is_verified_meta_option"] is False for x in rep["related_unverified_ideas"]))
        finally:
            if old_tok is not None:
                os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_upg_05_live_meta_audience_integration_and_8_section_targetologist_report(self) -> None:
        import http.server

        class LiveAudHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                if "targetingvalidation" in self.path:
                    body = {"data": [{"id": "7001", "name": "Real estate", "valid": True}, {"id": "7002", "name": "Mortgage loan", "valid": True}]}
                else:
                    body = {
                        "data": [
                            {"id": "7001", "name": "Real estate", "type": "interests", "path": ["Interests", "Business and industry", "Real estate"]},
                            {"id": "7002", "name": "Mortgage loan", "type": "interests", "path": ["Interests", "Business and industry", "Personal finance", "Mortgage loan"]},
                        ]
                    }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(LiveAudHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_live_aud"

            # 1. meta-audience.py get_interests automatically performs live search when META_ACCESS_TOKEN is present
            info = self.ma.get_interests(niche="real-estate", product="Novostroyka xonadonlar", ad_account_id="act_12345")
            self.assertEqual(info["live_verification_status"], "LIVE_SEARCH_AND_VALIDATION_COMPLETED")
            self.assertEqual(len(info["live_api_results"]), 2)

            # 2. meta-audience.py build_architecture automatically populates Layer 2 with live verified options when product/account is passed
            arch = self.ma.build_architecture(
                niche="real-estate",
                daily_budget=120.0,
                product="Novostroyka xonadonlar",
                ad_account_id="act_12345",
            )
            layer2 = arch["audience_layers"][1]
            self.assertEqual(layer2["targeting_verification_status"], "VERIFIED_AVAILABLE")
            self.assertEqual(len(layer2["verified_interests"]), 2)

            # 3. Verify 8-section targetologist_report structure
            tr = info["detailed_targeting_accuracy_report"]["targetologist_report"]
            expected_sections = [
                "1_business_and_audience_understanding",
                "2_ranked_verified_interests",
                "3_validation_status_and_official_ids",
                "4_offer_fit_explanations",
                "5_related_alternatives_by_status",
                "6_suggested_test_groups",
                "7_broad_targeting_alternatives",
                "8_missing_inputs_limitations_and_next_steps",
            ]
            for sec in expected_sections:
                self.assertIn(sec, tr, f"Missing targetologist report section: {sec}")
            self.assertGreaterEqual(len(tr["6_suggested_test_groups"]), 1)
            self.assertIn("anti_stacking_rule", tr["7_broad_targeting_alternatives"])

            # 4. Verify commands/audience.md invokes meta-targeting-engine.py search rather than --help
            cmd_txt = (VAULT / "commands" / "audience.md").read_text(encoding="utf-8")
            self.assertIn("meta-targeting-engine.py search", cmd_txt)
            self.assertNotIn("meta-audience.py --help", cmd_txt)
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok


class DetailedTargetingAccuracyTests(unittest.TestCase):
    """Tyrion v5.0 — Detailed Targeting Accuracy Engine uchun 12 ta majburiy avtomatlashtirilgan test."""

    def setUp(self) -> None:
        self.mte = importlib.import_module("meta-targeting-engine")
        self.ma = importlib.import_module("meta-audience")
        self.mcp = importlib.import_module("tyrion-mcp-server")

    def _with_mock_server(self, handler_cls):
        import http.server
        import threading
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server

    def test_dt_01_official_api_exact_match_preserves_original_name_and_id(self) -> None:
        import http.server

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                if "targetingvalidation" in self.path:
                    body = {"data": [{"id": "6003107902433", "name": "Online shopping", "valid": True}]}
                else:
                    body = {
                        "data": [
                            {
                                "id": "6003107902433",
                                "name": "Online shopping",
                                "type": "interests",
                                "path": ["Interests", "Shopping and fashion", "Online shopping"],
                                "audience_size_lower_bound": 450000,
                                "audience_size_upper_bound": 520000,
                            }
                        ]
                    }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(Handler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "valid_test_token_12345"
            rep = self.mte.search_and_validate_targeting(
                queries=["Online shopping"], ad_account_id="act_123456", limit_per_query=5
            )
            self.assertEqual(len(rep["verified_targeting_options"]), 1)
            item = rep["verified_targeting_options"][0]
            self.assertEqual(item["id"], "6003107902433")
            self.assertEqual(item["name"], "Online shopping")
            self.assertEqual(item["validation_status"], "VERIFIED_AVAILABLE")
            self.assertEqual(item["audience_size_lower_bound"], 450000)
            self.assertEqual(item["audience_size_upper_bound"], 520000)
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_02_empty_api_response_never_hallucinates_interests(self) -> None:
        import http.server

        class EmptyHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                raw = json.dumps({"data": []}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(EmptyHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "valid_test_token_12345"
            rep = self.mte.search_and_validate_targeting(queries=["nonexistent_xyz_interest_999"], niche="ecom")
            self.assertEqual(rep["verified_targeting_options"], [])
            self.assertEqual(rep["recommended_audience_combinations"]["status"], "NO_VERIFIED_OPTIONS_AVAILABLE")
            self.assertEqual(rep["recommended_audience_combinations"]["combinations"], [])
            self.assertTrue(any(q["validation_status"] == "NOT_FOUND" for q in rep["not_found_queries"]))
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_03_missing_token_never_marks_static_names_verified(self) -> None:
        old_tok = os.environ.pop("META_ACCESS_TOKEN", None)
        try:
            rep = self.mte.search_and_validate_targeting(product="Kiyim do'koni", niche="ecom")
            self.assertFalse(rep["live_check_status"]["executed"])
            self.assertEqual(rep["live_check_status"]["status"], "API_UNAVAILABLE")
            self.assertEqual(rep["verified_targeting_options"], [])
            self.assertTrue(all(x["validation_status"] == "RELATED_UNVERIFIED" for x in rep["related_unverified_ideas"]))
            self.assertTrue(all(x["is_verified_meta_option"] is False for x in rep["related_unverified_ideas"]))
        finally:
            if old_tok is not None:
                os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_04_http_401_and_403_handled_as_api_unavailable(self) -> None:
        import http.server

        for code, expected_cat in ((401, "AUTH_401"), (403, "PERMISSION_403")):
            class AuthErrHandler(http.server.BaseHTTPRequestHandler):
                def log_message(self, format: str, *args: object) -> None:
                    pass
                def do_GET(self) -> None:
                    raw = json.dumps({"error": {"message": "OAuthException", "code": 190}}).encode("utf-8")
                    self.send_response(code)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(raw)

            srv = self._with_mock_server(AuthErrHandler)
            old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
            try:
                os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
                os.environ["META_ACCESS_TOKEN"] = "expired_token_test"
                rep = self.mte.search_and_validate_targeting(queries=["Real estate"], niche="real-estate")
                self.assertEqual(rep["live_check_status"]["status"], "API_UNAVAILABLE")
                self.assertEqual(rep["live_check_status"]["error_category"], expected_cat)
                self.assertEqual(rep["verified_targeting_options"], [])
            finally:
                srv.shutdown()
                srv.server_close()
                if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
                else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
                if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
                else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_05_http_429_and_5xx_retry_backoff_and_recovery(self) -> None:
        import http.server
        attempts = {"count": 0}

        class FlakyHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                attempts["count"] += 1
                if attempts["count"] == 1:
                    self.send_response(429)
                    self.send_header("Retry-After", "0.05")
                    self.end_headers()
                    self.wfile.write(b'{"error": "rate limit"}')
                elif attempts["count"] == 2:
                    self.send_response(503)
                    self.end_headers()
                    self.wfile.write(b'{"error": "server busy"}')
                else:
                    raw = json.dumps({"data": [{"id": "777", "name": "Dentistry", "type": "adinterest"}]}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(raw)

        srv = self._with_mock_server(FlakyHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_retry_test"
            rep = self.mte.search_and_validate_targeting(queries=["Dentistry"], niche="medical", validate_results=False)
            self.assertGreaterEqual(attempts["count"], 3)
            self.assertEqual(len(rep["verified_targeting_options"]), 1)
            self.assertEqual(rep["verified_targeting_options"][0]["validation_status"], "FOUND_NOT_VALIDATED")
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_06_consolidated_or_invalid_interest_status_and_replacement_link(self) -> None:
        import http.server

        class ConsolidatedHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                if "targetingvalidation" in self.path:
                    body = {
                        "data": [
                            {
                                "id": "111_old",
                                "name": "Boutique",
                                "valid": False,
                                "status": "CONSOLIDATED",
                                "replacements": [{"id": "222_new", "name": "Shopping and fashion", "type": "interests"}],
                            },
                            {
                                "id": "222_new",
                                "name": "Shopping and fashion",
                                "valid": True,
                            },
                        ]
                    }
                else:
                    body = {
                        "data": [
                            {"id": "111_old", "name": "Boutique", "type": "interests"},
                            {"id": "222_new", "name": "Shopping and fashion", "type": "interests"},
                        ]
                    }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(ConsolidatedHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_cons_test"
            rep = self.mte.search_and_validate_targeting(queries=["Boutique"], ad_account_id="act_555")
            self.assertEqual(len(rep["verified_targeting_options"]), 1)
            self.assertEqual(rep["verified_targeting_options"][0]["id"], "222_new")
            self.assertEqual(len(rep["unavailable_or_consolidated_options"]), 1)
            old_it = rep["unavailable_or_consolidated_options"][0]
            self.assertEqual(old_it["validation_status"], "UNAVAILABLE_OR_CONSOLIDATED")
            self.assertEqual(old_it["validation_details"]["consolidated_into"]["id"], "222_new")
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_07_same_name_different_ids_preserved_without_collision(self) -> None:
        import http.server

        class HomonymHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                body = {
                    "data": [
                        {"id": "600111", "name": "Real estate", "type": "interests"},
                        {"id": "600222", "name": "Real estate", "type": "interests"},
                    ]
                }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(HomonymHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_homonym"
            rep = self.mte.search_and_validate_targeting(queries=["Real estate"], validate_results=False)
            ids = [x["id"] for x in rep["verified_targeting_options"] if x["name"] == "Real estate"]
            self.assertEqual(ids, ["600111", "600222"])
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_08_pagination_collects_all_pages(self) -> None:
        import http.server

        class PaginatedSearchHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                base = f"http://127.0.0.1:{self.server.server_port}"
                if "page=2" in self.path:
                    body = {"data": [{"id": "p2_id", "name": "Luxury real estate", "type": "adinterest"}], "paging": {}}
                else:
                    body = {
                        "data": [{"id": "p1_id", "name": "Property investment", "type": "adinterest"}],
                        "paging": {"next": f"{base}/v26.0/search?type=adinterest&q=Property&page=2"},
                    }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(PaginatedSearchHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_page"
            rep = self.mte.search_and_validate_targeting(queries=["Property"], max_pages_per_query=3, validate_results=False)
            ids = {x["id"] for x in rep["verified_targeting_options"]}
            self.assertIn("p1_id", ids)
            self.assertIn("p2_id", ids)
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_09_multilingual_queries_uz_latin_cyrillic_ru_en(self) -> None:
        self.assertEqual(self.mte.detect_query_language("Toshkentda ko'chmas mulk va xonadon"), "uz_latin")
        self.assertEqual(self.mte.detect_query_language("Тошкентда кўчмас мулк ва хонадон"), "uz_cyrillic")
        self.assertEqual(self.mte.detect_query_language("Недвижимость и квартира в Ташкенте"), "ru")
        self.assertEqual(self.mte.detect_query_language("Luxury real estate investment"), "en")

        for phrase in ("ko'chmas mulk", "кўчмас мулк", "недвижимость"):
            expanded = self.mte.expand_search_queries(product=phrase, niche="real-estate")
            q_strings = [x["query"] for x in expanded]
            self.assertIn("Real estate", q_strings)
            self.assertTrue(all(x["role"] == "SEARCH_QUERY_ONLY_NOT_VERIFIED_INTEREST" for x in expanded))

    def test_dt_10_malformed_json_empty_fields_and_unexpected_shapes_never_crash(self) -> None:
        import http.server
        mode = {"state": "bad_json"}

        class WeirdHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                if mode["state"] == "bad_json":
                    self.wfile.write(b"{not valid json")
                else:
                    body = {"data": [{"id": "", "name": ""}, {"id": "901", "name": "IELTS"}]}
                    self.wfile.write(json.dumps(body).encode("utf-8"))

        srv = self._with_mock_server(WeirdHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_weird"
            rep_bad = self.mte.search_and_validate_targeting(queries=["IELTS"], validate_results=False)
            self.assertEqual(rep_bad["live_check_status"]["status"], "API_UNAVAILABLE")
            self.assertEqual(rep_bad["live_check_status"]["error_category"], "INVALID_JSON")

            mode["state"] = "partial_empty"
            rep_ok = self.mte.search_and_validate_targeting(queries=["IELTS"], validate_results=False)
            self.assertEqual(len(rep_ok["verified_targeting_options"]), 1)
            it = rep_ok["verified_targeting_options"][0]
            self.assertEqual(it["id"], "901")
            self.assertIsNone(it["audience_size_lower_bound"])
            self.assertIsNone(it["audience_size_upper_bound"])
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_11_mcp_tool_preserves_statuses_and_provenance(self) -> None:
        old_tok = os.environ.pop("META_ACCESS_TOKEN", None)
        try:
            resp = self.mcp.handle_request({
                "jsonrpc": "2.0",
                "id": 77,
                "method": "tools/call",
                "params": {
                    "name": "tyrion_meta_detailed_targeting",
                    "arguments": {"product": "Стоматология", "niche": "medical", "special_ad_category": "NONE"},
                },
            })
            payload = json.loads(resp["result"]["content"][0]["text"])
            self.assertEqual(payload["schema"], "tyrion.detailed_targeting_accuracy/v5")
            self.assertEqual(payload["live_check_status"]["status"], "API_UNAVAILABLE")
            self.assertEqual(payload["verified_targeting_options"], [])
            self.assertTrue(len(payload["related_unverified_ideas"]) > 0)
        finally:
            if old_tok is not None:
                os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_12_relevance_reason_and_expired_cache_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfile = Path(tmp) / "targeting_cache.json"
            expired_data = {
                "schema": "tyrion.targeting_cache/v5",
                "entries": {
                    "test_key": {
                        "api_version": "v26.0",
                        "fetched_at_utc": "2026-01-01T00:00:00Z",
                        "fetched_epoch": 1000.0,
                        "ttl_seconds": 60,
                        "query_params": {},
                        "payload": {"fake": True},
                    }
                },
            }
            cfile.write_text(json.dumps(expired_data), encoding="utf-8")
            loaded, cstat, warn = self.mte._load_valid_cache(cfile, "test_key", {"api_version": "v26.0"}, 60)
            self.assertIsNone(loaded)
            self.assertEqual(cstat, "EXPIRED")
            self.assertIn("Kesh muddati tugagan", warn)

            loaded_ver, cstat_ver, warn_ver = self.mte._load_valid_cache(cfile, "test_key", {"api_version": "v25.0"}, 60)
            self.assertIsNone(loaded_ver)
            self.assertEqual(cstat_ver, "VERSION_MISMATCH")
            self.assertIn("Kesh versiyasi eskirgan", warn_ver)


@unittest.skipUnless(
    os.environ.get("TYRION_RUN_LIVE_META_SMOKE") == "1" and os.environ.get("META_ACCESS_TOKEN"),
    "Ixtiyoriy live Meta API smoke testi: faqat TYRION_RUN_LIVE_META_SMOKE=1 va META_ACCESS_TOKEN berilganda ishlaydi.",
)
class LiveMetaSmokeTests(unittest.TestCase):
    def test_live_meta_targeting_smoke(self) -> None:
        mte = importlib.import_module("meta-targeting-engine")
        rep = mte.search_and_validate_targeting(queries=["Online shopping"], limit_per_query=5)
        self.assertTrue(rep["live_check_status"]["executed"])
        self.assertGreater(len(rep["verified_targeting_options"]), 0)


if __name__ == "__main__":
    unittest.main()
