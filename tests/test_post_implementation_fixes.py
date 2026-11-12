"""PostImplementationFixTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc as _run_tool_inproc

import catalog  # noqa: E402



class PostImplementationFixTests(unittest.TestCase):
    """Part 1 Post-Implementation Verification: CRLF resilience, Pagination/Truncation, Malformed vs NOT_FOUND, Cache Isolation, CLI Docs."""

    def setUp(self) -> None:
        self.mte = importlib.import_module("meta-targeting-engine")
        self.ss = importlib.import_module("skill-search")

    def test_p1_crlf_vs_lf_sha256_and_bytes_resilience(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            f_lf = Path(tmp) / "sample_lf.md"
            f_crlf = Path(tmp) / "sample_crlf.md"
            content_lf = b"---\nname: test\ndescription: hello\n---\n\nLine 1\nLine 2\n"
            content_crlf = content_lf.replace(b"\n", b"\r\n")
            f_lf.write_bytes(content_lf)
            f_crlf.write_bytes(content_crlf)

            self.assertEqual(catalog._sha256(f_lf), catalog._sha256(f_crlf))
            self.assertEqual(len(catalog._normalized_bytes(f_lf)), len(catalog._normalized_bytes(f_crlf)))

    def _start_server(self, handler_cls):
        import http.server
        import threading
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        return srv, f"http://127.0.0.1:{srv.server_address[1]}"

    def test_p2_pagination_truncation_reported_and_not_marked_complete(self) -> None:
        import http.server
        holder = {"base": ""}

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                body = {
                    "data": [{"id": "600111", "name": "Real estate", "type": "adinterest"}],
                    "paging": {"next": f"{holder['base']}/v26.0/search?type=adinterest&q=Real+estate&after=cursor_p2"},
                }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        srv, base_url = self._start_server(Handler)
        holder["base"] = base_url
        old_base = os.environ.get("META_GRAPH_API_BASE_URL")
        old_tok = os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = base_url
            os.environ["META_ACCESS_TOKEN"] = "mock_tok_trunc"
            with tempfile.TemporaryDirectory() as tmp:
                cfile = Path(tmp) / "trunc_cache.json"
                rep = self.mte.search_and_validate_targeting(
                    queries=["Real estate"],
                    niche="real-estate",
                    max_pages_per_query=1,
                    cache_path=cfile,
                )
                lcs = rep["live_check_status"]
                self.assertTrue(lcs["is_truncated"])
                self.assertFalse(lcs["is_complete"])
                self.assertIn("TRUNCATED", lcs["status"])
                first_diag = rep["query_diagnostics"][0]
                self.assertEqual(first_diag["pages_fetched"], 1)
                self.assertTrue(first_diag["is_truncated"])
                self.assertEqual(first_diag["results_count"], 1)
                self.assertTrue(any("Pagination Truncated" in lim for lim in rep["limitations_and_disclosures"]))
                self.assertFalse(cfile.is_file())
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_p3_malformed_or_empty_shape_payload_never_classified_as_not_found(self) -> None:
        import http.server

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                raw = json.dumps({"data": [{"id": "", "name": ""}, {"foo": "bar"}]}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        srv, base_url = self._start_server(Handler)
        old_base = os.environ.get("META_GRAPH_API_BASE_URL")
        old_tok = os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = base_url
            os.environ["META_ACCESS_TOKEN"] = "mock_tok_malformed"
            rep = self.mte.search_and_validate_targeting(queries=["BrokenQuery"], niche="ecom")
            self.assertEqual(rep["live_check_status"]["status"], "API_UNAVAILABLE")
            self.assertEqual(rep["live_check_status"]["error_category"], "MALFORMED_ITEM_PAYLOAD")
            self.assertEqual(rep["not_found_queries"], [])
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_p4_cache_key_isolation_across_special_ad_category_country_objective_locale_and_corrupted_states(self) -> None:
        import http.server

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                raw = json.dumps({"data": [{"id": "600999", "name": "Mortgage loan", "type": "adinterest"}]}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        srv, base_url = self._start_server(Handler)
        old_base = os.environ.get("META_GRAPH_API_BASE_URL")
        old_tok = os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = base_url
            os.environ["META_ACCESS_TOKEN"] = "mock_tok_cache"
            with tempfile.TemporaryDirectory() as tmp:
                cfile = Path(tmp) / "isolated_cache.json"

                # 1. Cache miss on non-existent file
                r_none = self.mte.search_and_validate_targeting(
                    product="Ipoteka", niche="real-estate", special_ad_category="NONE",
                    country="UZ", objective="LEADS", locale="en_US", cache_path=cfile,
                )
                self.assertFalse(r_none["live_check_status"]["served_from_valid_cache"])
                self.assertEqual(r_none["live_check_status"]["cache_status"], "MISS_NO_FILE")

                # 2. Exact same context -> HIT_VALID
                r_hit = self.mte.search_and_validate_targeting(
                    product="Ipoteka", niche="real-estate", special_ad_category="NONE",
                    country="UZ", objective="LEADS", locale="en_US", cache_path=cfile,
                )
                self.assertTrue(r_hit["live_check_status"]["served_from_valid_cache"])
                self.assertEqual(r_hit["live_check_status"]["cache_status"], "HIT_VALID")

                # 3. Different special_ad_category (HOUSING) -> CONTEXT_MISMATCH, must NOT serve NONE cache and MUST include HOUSING warning
                r_housing = self.mte.search_and_validate_targeting(
                    product="Ipoteka", niche="real-estate", special_ad_category="HOUSING",
                    country="UZ", objective="LEADS", locale="en_US", cache_path=cfile,
                )
                self.assertFalse(r_housing["live_check_status"]["served_from_valid_cache"])
                self.assertEqual(r_housing["live_check_status"]["cache_status"], "CONTEXT_MISMATCH")
                self.assertNotEqual(r_none["query_context"]["cache_key"], r_housing["query_context"]["cache_key"])
                self.assertTrue(any("Special Ad Category = HOUSING" in lim for lim in r_housing["limitations_and_disclosures"]))

                # 4. Different country / objective / locale -> CONTEXT_MISMATCH
                r_kz = self.mte.search_and_validate_targeting(
                    product="Ipoteka", niche="real-estate", special_ad_category="HOUSING",
                    country="KZ", objective="SALES", locale="ru_RU", cache_path=cfile,
                )
                self.assertFalse(r_kz["live_check_status"]["served_from_valid_cache"])
                self.assertEqual(r_kz["live_check_status"]["cache_status"], "CONTEXT_MISMATCH")

                # 5. Corrupted cache file -> CORRUPTED
                cfile.write_text("{corrupted_json", encoding="utf-8")
                r_corrupt = self.mte.search_and_validate_targeting(
                    product="Ipoteka", niche="real-estate", special_ad_category="NONE",
                    country="UZ", objective="LEADS", locale="en_US", cache_path=cfile,
                )
                self.assertFalse(r_corrupt["live_check_status"]["served_from_valid_cache"])
                self.assertEqual(r_corrupt["live_check_status"]["cache_status"], "CORRUPTED")
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_p5_readme_and_docs_cli_examples_parse_and_smoke_test(self) -> None:
        old_tok = os.environ.pop("META_ACCESS_TOKEN", None)
        try:
            # Verify README.md command: python3 tools/meta-targeting-engine.py search --niche real-estate --query "interyer" --query "новостройки" --account-id act_123456789
            proc1 = _run_tool_inproc(
                "meta-targeting-engine.py", "search",
                "--niche", "real-estate", "--query", "interyer", "--query", "новостройки",
                "--account-id", "act_123456789", "--json",
            )
            self.assertEqual(proc1.returncode, 0, proc1.stderr)
            data1 = json.loads(proc1.stdout)
            self.assertEqual(data1["query_context"]["ad_account_id"], "act_123456789")

            # Verify --ad-account-id alias and implicit search subcommand also work
            proc2 = _run_tool_inproc(
                "meta-targeting-engine.py",
                "--niche", "real-estate", "--query", "interyer", "--ad-account-id", "act_123456789", "--json",
            )
            self.assertEqual(proc2.returncode, 0, proc2.stderr)

            # Verify README.md universal router command: python3 tools/tyrion.py route "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top"
            proc3 = _run_tool_inproc(
                "skill-search.py", "route", "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top", "--json",
            )
            self.assertEqual(proc3.returncode, 0, proc3.stderr)
            route_data = json.loads(proc3.stdout)
            self.assertEqual(route_data["primary_agent"], "audit-meta")
        finally:
            if old_tok is not None:
                os.environ["META_ACCESS_TOKEN"] = old_tok


if __name__ == "__main__":
    unittest.main()
