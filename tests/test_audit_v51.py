"""TyrionV51AuditTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path



class TyrionV51AuditTests(unittest.TestCase):
    """Tyrion v5.1 — Ikkinchi auditdagi 4 ta asosiy kamchilik va real HTTP server integratsiyasi testlari."""

    def setUp(self) -> None:
        self.ma = importlib.import_module("meta-audience")
        self.mis = importlib.import_module("meta-insights-sync")
        self.ae = importlib.import_module("ad-export-analyzer")

    def test_v51_1_live_http_pagination_account_currency_and_ssrf_guard(self) -> None:
        import http.server
        import threading

        received_auth_headers: list[str] = []

        class MockMetaGraphHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass

            def do_GET(self) -> None:
                received_auth_headers.append(self.headers.get("Authorization", ""))
                base_url = f"http://127.0.0.1:{self.server.server_port}"
                if self.path.startswith("/v26.0/act_777888999?"):
                    body = {
                        "id": "act_777888999",
                        "name": "Tashkent Ecom UZS Account",
                        "account_status": 1,
                        "currency": "UZS",
                        "timezone_name": "Asia/Tashkent",
                    }
                elif "after=cursor_page_2" in self.path:
                    body = {
                        "data": [
                            {
                                "adset_id": "adset_p2",
                                "adset_name": "Page2_Broad_Tashkent",
                                "account_currency": "UZS",
                                "spend": "1800000",
                                "impressions": "45000",
                                "reach": "30000",
                                "frequency": "1.50",
                                "actions": [{"action_type": "purchase", "value": "18"}],
                                "action_values": [{"action_type": "purchase", "value": "7200000"}],
                            }
                        ],
                        "paging": {"next": f"{base_url}/v26.0/act_777888999/insights?after=cursor_page_3"},
                    }
                elif "after=cursor_page_3" in self.path:
                    body = {
                        "data": [
                            {
                                "adset_id": "adset_p3",
                                "adset_name": "Page3_ZeroConv_Bleeder",
                                "account_currency": "UZS",
                                "spend": "950000",
                                "impressions": "15000",
                                "reach": "5000",
                                "frequency": "3.00",
                                "actions": [],
                                "action_values": [],
                            }
                        ],
                        "paging": {},
                    }
                else:
                    body = {
                        "data": [
                            {
                                "adset_id": "adset_p1",
                                "adset_name": "Page1_Winner_Set",
                                "account_currency": "UZS",
                                "spend": "2000000",
                                "impressions": "60000",
                                "reach": "40000",
                                "frequency": "1.50",
                                "actions": [{"action_type": "purchase", "value": "25"}],
                                "action_values": [{"action_type": "purchase", "value": "9000000"}],
                            }
                        ],
                        "paging": {"next": f"{base_url}/v26.0/act_777888999/insights?after=cursor_page_2"},
                    }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), MockMetaGraphHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        old_base = os.environ.get("META_GRAPH_API_BASE_URL")
        old_tok = os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{server.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "test_live_bearer_token_v51"

            ver = self.mis.verify_live_connection("777888999")
            self.assertTrue(ver["authenticated"])
            self.assertEqual(ver["account_currency"], "UZS")

            synced = self.mis.sync_and_analyze(
                account_id="act_777888999",
                level="adset",
                date_preset="last_7d",
                target_cpa=120000.0,
                breakeven_roas=2.0,
                max_pages=10,
            )
            self.assertEqual(synced["data_source_type"], "LIVE_META_GRAPH_API")
            self.assertEqual(synced["pagination"]["pages_fetched"], 3)
            self.assertFalse(synced["pagination"]["is_truncated"])
            self.assertEqual(synced["normalized_rows_count"], 3)
            self.assertEqual(synced["account_currency"], "UZS")
            self.assertEqual(synced["currency_source"], "META_ACCOUNT_CURRENCY")
            self.assertEqual(synced["audit_report"]["currency"], "UZS")
            self.assertEqual(synced["audit_report"]["summary"]["total_conversions"], 43)
            self.assertTrue(all(h == "Bearer test_live_bearer_token_v51" for h in received_auth_headers))

            with self.assertRaises(PermissionError):
                self.mis._validate_same_origin("https://evil.attacker.com/v26.0/steal", "https://graph.facebook.com")
        finally:
            server.shutdown()
            server.server_close()
            if old_base is None:
                os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else:
                os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None:
                os.environ.pop("META_ACCESS_TOKEN", None)
            else:
                os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_v51_2_mixed_conversion_families_never_silently_blended(self) -> None:
        raw_mixed = [
            {
                "adset_id": "1",
                "adset_name": "Ecom_Purchase_Set",
                "account_currency": "USD",
                "spend": "200.0",
                "impressions": "20000",
                "reach": "10000",
                "actions": [{"action_type": "purchase", "value": "10"}],
                "action_values": [{"action_type": "purchase", "value": "600.0"}],
            },
            {
                "adset_id": "2",
                "adset_name": "B2B_LeadGen_Set",
                "account_currency": "USD",
                "spend": "150.0",
                "impressions": "15000",
                "reach": "8000",
                "actions": [{"action_type": "lead", "value": "30"}],
                "action_values": [],
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "mixed_insights.json"
            p.write_text(json.dumps({"account_id": "act_111", "data": raw_mixed}), encoding="utf-8")

            res_auto = self.mis.sync_and_analyze(from_raw_json=p, target_cpa=15.0, primary_conversion="auto")
            rep_auto = res_auto["audit_report"]
            self.assertTrue(rep_auto["mixed_conversion_types_detected"])
            self.assertEqual(rep_auto["active_conversion_families"], ["LEAD", "PURCHASE"])
            self.assertIsNone(rep_auto["summary"]["blended_cpa"])
            self.assertIsNone(rep_auto["summary"]["total_conversions"])
            self.assertEqual(rep_auto["summary_by_conversion_family"]["PURCHASE"]["cpa"], 20.0)
            self.assertEqual(rep_auto["summary_by_conversion_family"]["LEAD"]["cpa"], 5.0)

            res_purch = self.mis.sync_and_analyze(from_raw_json=p, target_cpa=15.0, primary_conversion="purchase")
            rep_purch = res_purch["audit_report"]
            self.assertFalse(rep_purch["mixed_conversion_types_detected"])
            self.assertEqual(rep_purch["summary"]["total_conversions"], 10)
            self.assertEqual(rep_purch["summary"]["blended_cpa"], 35.0)

    def test_v51_3_saturation_scenario_sensitivity_band_not_statistical_ci(self) -> None:
        sat = self.ma.calc_saturation(audience_size=200000, daily_budget=80.0, measured_freq_7d=1.75)
        win = sat["scenario_sensitivity_window_days"]
        self.assertFalse(win["is_statistical_confidence_interval"])
        self.assertIn("NOT_A_STATISTICAL_CONFIDENCE_INTERVAL", sat["model_disclosure"]["interval_methodology"])
        self.assertIn("MODERATE_CALIBRATED_LINEAR_PROJECTION", sat["model_disclosure"]["confidence_level"])
        self.assertNotEqual(sat["model_disclosure"]["confidence_level"], "HIGH")

    def test_v51_4_unit_economics_bounds_and_unverified_target_cpa_label(self) -> None:
        with self.assertRaises(ValueError):
            self.ma.build_architecture(niche="ecom", daily_budget=150.0, aov=100.0, margin_pct=150.0)
        with self.assertRaises(ValueError):
            self.ma.build_architecture(niche="ecom", daily_budget=150.0, aov=100.0, margin_pct=40.0, lead_to_sale_cvr=250.0)
        with self.assertRaises(ValueError):
            self.ma.build_architecture(niche="ecom", daily_budget=150.0, aov=100.0)

        goal_arch = self.ma.build_architecture(niche="ecom", daily_budget=150.0, target_cpa=15.0)
        self.assertEqual(goal_arch["evidence_and_assumptions"]["cpa_source"], "USER_SPECIFIED_TARGET_GOAL")
        self.assertEqual(goal_arch["evidence_and_assumptions"]["confidence_level"], "UNVERIFIED_USER_TARGET")

        meas_arch = self.ma.build_architecture(niche="ecom", daily_budget=150.0, measured_cpa=14.2)
        self.assertEqual(meas_arch["evidence_and_assumptions"]["cpa_source"], "MEASURED_HISTORICAL_CPA")
        self.assertEqual(meas_arch["evidence_and_assumptions"]["confidence_level"], "MODERATE_HISTORICAL_BASELINE")


if __name__ == "__main__":
    unittest.main()
