"""Tyrion v7.0.1 "Ishonch hotfix" — B01..B07, B11, B14 regressiya testlari.

Har bir test v7.0.0 da bag'ni ushlaydi (UPDATE-PLAN-v7.1.md, 3-bo'lim). Haqiqiy formatdagi
eksport fixture'lari: tests/fixtures/.
"""

from __future__ import annotations

import importlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TESTS = Path(__file__).resolve().parent
VAULT = TESTS.parent
TOOLS = VAULT / "tools"
FIXTURES = TESTS / "fixtures"
sys.path.insert(0, str(TOOLS))

import tyrion_core as tcore  # noqa: E402

ae = importlib.import_module("ad-export-analyzer")
sg = importlib.import_module("spend-guard")
cu = importlib.import_module("capi-utm-builder")
calc = importlib.import_module("calculator")
doctor = importlib.import_module("doctor")


def run_tool(script: str, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOLS / script), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, cwd=str(VAULT),
    )


def analyze(name: str, **kw) -> dict:
    return ae.analyze_export(FIXTURES / name, target_cpa=kw.pop("target_cpa", 20.0), **kw)


class NumberParsingTests(unittest.TestCase):
    """B02 — o'nlik/minglik ajratgichlar."""

    def test_localized_numbers(self) -> None:
        cases = {
            "499,90": 499.90,        # RU/EU o'nlik vergul (v7.0.0: 49990)
            "1 234,56": 1234.56,     # bo'shliq minglik (v7.0.0: 123456)
            "1 234,56": 1234.56,
            "1.234,56": 1234.56,     # EU (v7.0.0: 1.23456)
            "1,234.56": 1234.56,
            "$1,240.50": 1240.50,
            "1,234,567": 1234567.0,
            "0,123": 0.123,
            "12.5": 12.5,
        }
        for raw, want in cases.items():
            self.assertAlmostEqual(tcore.safe_float(raw), want, places=6, msg=raw)

    def test_ambiguous_comma_is_error_without_locale(self) -> None:
        with self.assertRaises(tcore.AmbiguousNumberError):
            tcore.safe_float("1,234")
        self.assertEqual(tcore.safe_float("61,230", decimal="dot"), 61230.0)
        self.assertEqual(tcore.safe_float("1,234", decimal="comma"), 1.234)

    def test_garbage_still_defaults(self) -> None:
        self.assertEqual(tcore.safe_float("abc", default=7.0), 7.0)
        self.assertEqual(tcore.safe_float("nan", default=0.0), 0.0)

    def test_locale_detection(self) -> None:
        self.assertEqual(tcore.detect_number_locale(["499,90", "1 234,56"])[0], "comma")
        self.assertEqual(tcore.detect_number_locale(["1,240.50", "61,230"])[0], "dot")
        self.assertEqual(tcore.detect_number_locale(["61,230"], "Spend")[0], "dot")
        self.assertEqual(tcore.detect_number_locale(["61,230"], "Показы")[0], "comma")
        with self.assertRaises(ValueError):
            tcore.detect_number_locale(["1,240.50", "499,90"])


class ExportFixtureTests(unittest.TestCase):
    """B01 — haqiqiy formatdagi eksportlar."""

    def assert_no_zero_spend_verdicts(self, res: dict) -> None:
        for d in res["decisions"]:
            self.assertGreater(d["spend"], 0, d)
            self.assertFalse(d["name"].startswith("Row_"), d["name"])
            self.assertNotEqual(d["verdict"], "NO_VERDICT_ZERO_SPEND")

    def test_meta_en(self) -> None:
        res = analyze("meta_ads_manager_en.csv")
        self.assert_no_zero_spend_verdicts(res)
        by = {d["name"]: d for d in res["decisions"]}
        win = by["Winner_Reels_Broad"]
        self.assertEqual((win["spend"], win["conversions"], win["revenue"]), (1020.0, 62, 3980.0))
        self.assertEqual(win["impressions"] if "impressions" in win else None, None)  # ichki maydon emas
        self.assertTrue(win["verdict"].startswith("SCALE"))
        # v7.0.0: $310 sarflab 0 konversiya bergan qator KEEP edi
        self.assertEqual(by["Loser_FB_Feed"]["verdict"], "KILL_ZERO_CONV")
        self.assertEqual(by["Loser_FB_Feed"]["spend"], 310.0)
        self.assertEqual(res["currency"], "USD")
        self.assertEqual(res["summary"]["total_spend"], 2570.5)
        self.assertEqual(res["input_format"]["number_format"], "dot")

    def test_meta_ru_decimal_comma(self) -> None:
        res = analyze("meta_ads_manager_ru.csv")
        self.assert_no_zero_spend_verdicts(res)
        by = {d["name"]: d for d in res["decisions"]}
        self.assertEqual(by["Победитель Reels"]["spend"], 499.90)       # 49990 emas
        self.assertEqual(by["Крупный"]["spend"], 1234.56)
        self.assertEqual(by["Победитель Reels"]["revenue"], 2100.50)
        self.assertEqual(res["currency"], "USD")
        self.assertEqual(res["input_format"]["number_format"], "comma")

    def test_google_ads_with_report_preamble(self) -> None:
        res = analyze("google_ads.csv")
        self.assert_no_zero_spend_verdicts(res)
        by = {d["name"]: d for d in res["decisions"]}
        self.assertEqual(by["Search_Brand"]["spend"], 1150.25)
        self.assertEqual(by["Search_Brand"]["revenue"], 7400.0)
        self.assertEqual(by["DSA_Old"]["verdict"], "KILL_ZERO_CONV")
        self.assertEqual(len(res["decisions"]), 3)

    def test_telegram_ads_currency_from_header(self) -> None:
        res = analyze("telegram_ads.csv")
        self.assert_no_zero_spend_verdicts(res)
        self.assertEqual(res["currency"], "TON")
        by = {d["name"]: d for d in res["decisions"]}
        self.assertEqual(by["Kanal_Aksiya_1"]["spend"], 182.5)
        self.assertEqual(by["Bot_Start_2"]["verdict"], "KILL_ZERO_CONV")

    def test_utf16_tab_separated_google_export(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "g.csv"
            p.write_text("Campaign\tCost\tConversions\nA\t1,000.50\t10\n", encoding="utf-16")
            res = ae.analyze_export(p)
        self.assertEqual(res["decisions"][0]["spend"], 1000.5)

    def test_missing_spend_column_stops_with_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "nospend.csv"
            p.write_text("Ad set name,Impressions,Purchases\nA,1000,62\n", encoding="utf-8")
            with self.assertRaises(ValueError) as cm:
                ae.analyze_export(p)
            self.assertIn("Sarf ustuni topilmadi", str(cm.exception))
            proc = run_tool("ad-export-analyzer.py", "analyze", "--file", str(p), "--json")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Sarf ustuni topilmadi", proc.stderr)
        self.assertEqual(proc.stdout.strip(), "")  # hukm jadvali chiqmaydi

    def test_zero_spend_with_conversions_gives_no_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "zero.csv"
            p.write_text("Ad set name,Amount spent (USD),Purchases\nA,0,62\nB,0,0\n", encoding="utf-8")
            res = ae.analyze_export(p)
        for d in res["decisions"]:
            self.assertEqual(d["verdict"], "NO_VERDICT_ZERO_SPEND")
            self.assertNotIn("SCALE", d["verdict"])
        self.assertEqual(res["zero_spend_items"], 2)

    def test_misaligned_header_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.csv"
            p.write_text("Ad set name,Amount spent (USD),CPM (cost per 1,000 impressions),Purchases\n"
                         "A,100,5,3\nB,200,6,4\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                ae.analyze_export(p)

    def test_cli_exit_zero_on_fixture(self) -> None:
        proc = run_tool("ad-export-analyzer.py", "analyze", "--file", str(FIXTURES / "meta_ads_manager_en.csv"), "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["decisions"][0]["spend"], 1020.0)


class SpendGuardBudgetTests(unittest.TestCase):
    """B03."""

    def test_nan_inf_negative_blocked(self) -> None:
        for bad in (float("nan"), float("inf"), float("-inf"), -50.0, -0.01):
            res = sg.check_budget_change(100.0, bad)
            self.assertFalse(res["passed"], bad)
            self.assertTrue(res["errors"], bad)
            json.dumps(res, allow_nan=False)  # JSON NaN chiqmasin

    def test_zero_is_pause_needs_explicit_approval(self) -> None:
        res = sg.check_budget_change(100.0, 0.0)
        self.assertFalse(res["passed"])
        self.assertEqual(res["action"], "pause")
        self.assertTrue(res["requires_explicit_approval"])
        ok = sg.check_budget_change(100.0, 0.0, pause_approved=True)
        self.assertTrue(ok["passed"])
        self.assertEqual(ok["action"], "pause")

    def test_bad_current_blocked(self) -> None:
        self.assertFalse(sg.check_budget_change(float("nan"), 10.0)["passed"])
        self.assertFalse(sg.check_budget_change(-5.0, 10.0)["passed"])

    def test_normal_changes_unchanged(self) -> None:
        self.assertTrue(sg.check_budget_change(100.0, 115.0)["passed"])
        self.assertFalse(sg.check_budget_change(100.0, 130.0)["passed"])

    def test_cli_exit_codes(self) -> None:
        for prop in ("nan", "inf", "-50", "0"):
            proc = run_tool("spend-guard.py", "budget", "--current", "100", f"--proposed={prop}")
            self.assertEqual(proc.returncode, 1, f"{prop}: {proc.stdout}")
            self.assertIn("BLOCKED", proc.stdout)
        proc = run_tool("spend-guard.py", "budget", "--current", "100", "--proposed=0", "--approve-pause")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        proc = run_tool("spend-guard.py", "budget", "--current", "100", "--proposed=nan", "--json")
        self.assertEqual(proc.returncode, 1)
        self.assertFalse(json.loads(proc.stdout)["passed"])  # yaroqli JSON


class ChangePacketTests(unittest.TestCase):
    """B04 — tuzilmaviy tekshiruv."""

    FULL = (
        "# Change Packet\n"
        "## Rollback\nByudjetni $100 ga qaytarish, kampaniyani eski nusxaga almashtirish.\n"
        "## Stop-loss\nAgar CPA > $20 va 0 xarid bo'lsa, 48 soatda to'xtatish.\n"
        "## Boshlang'ich ko'rsatkichlar\nCPA $15, ROAS 3.1 (so'nggi 7 kun).\n"
        "## Xavf\nO'rta — learning phase qayta boshlanishi mumkin.\n"
        "## Tasdiq\nOperator: Ali, 2026-11-11\n"
    )

    def test_complete_packet_passes(self) -> None:
        res = sg.check_change_packet(self.FULL)
        self.assertTrue(res["passed"], res)
        self.assertTrue(all(res["checks"].values()))

    def test_keyword_only_file_fails(self) -> None:
        # v7.0.0: ichida faqat "qaytarish chegara" yozilgan fayl o'tgan
        self.assertFalse(sg.check_change_packet("qaytarish chegara")["passed"])
        self.assertFalse(sg.check_change_packet("rollback stop-loss baseline risk approval")["passed"])

    def test_missing_approval_is_error(self) -> None:
        text = self.FULL.split("## Tasdiq")[0]
        res = sg.check_change_packet(text)
        self.assertFalse(res["passed"])
        self.assertFalse(res["checks"]["human_approval"])
        self.assertTrue(any("tasdig" in e.lower() for e in res["errors"]))

    def test_empty_or_placeholder_values_fail(self) -> None:
        for repl in ("", "`[Operator nomi]`", "[ ] Operator", "TBD"):
            text = self.FULL.replace("Operator: Ali, 2026-11-11", repl)
            self.assertFalse(sg.check_change_packet(text)["passed"], repr(repl))
        self.assertFalse(sg.check_change_packet(self.FULL.replace("Agar CPA > $20 va 0 xarid bo'lsa, 48 soatda to'xtatish.", "$0.00"))["passed"])

    def test_inline_field_format(self) -> None:
        text = ("Teskari qadam: eski byudjetga qaytarish\nStop-loss: CPA > $20\n"
                "Boshlang'ich holat: CPA $15\nXavf: past\nOperator tasdig'i: Ali")
        self.assertTrue(sg.check_change_packet(text)["passed"])

    def test_unfilled_template_fails_and_cli_exit(self) -> None:
        tpl = VAULT / "templates" / "campaign-launch-packet-template.md"
        self.assertFalse(sg.check_change_packet(tpl.read_text(encoding="utf-8"))["passed"])
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "p.md"
            bad.write_text("qaytarish chegara\n", encoding="utf-8")
            proc = run_tool("spend-guard.py", "packet", str(bad))
            self.assertEqual(proc.returncode, 1)
            self.assertNotIn("6 ta xavfsizlik darvozasi", proc.stdout)
            good = Path(td) / "g.md"
            good.write_text(self.FULL, encoding="utf-8")
            self.assertEqual(run_tool("spend-guard.py", "packet", str(good)).returncode, 0)


@unittest.skipUnless(shutil.which("node"), "node o'rnatilmagan")
class McpProbeTests(unittest.TestCase):
    """B05 — MCP server haqiqatda ishga tushishi."""

    def test_mcp_json_has_default_for_plugin_root(self) -> None:
        cfg = json.loads((VAULT / ".mcp.json").read_text(encoding="utf-8"))
        arg = cfg["mcpServers"]["tyrion-core"]["args"][0]
        self.assertIn("${CLAUDE_PLUGIN_ROOT:-.}", arg)

    def test_repo_mcp_server_starts_without_plugin_root(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
            res = doctor.probe_mcp_server(VAULT / ".mcp.json", VAULT)
        self.assertTrue(res["ok"], res)
        self.assertGreaterEqual(res["tools"], 10)

    def test_old_config_without_default_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / ".mcp.json"
            cfg.write_text(json.dumps({"mcpServers": {"tyrion-core": {
                "command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cjs", "--mcp"]}}}), encoding="utf-8")
            res = doctor.probe_mcp_server(cfg, VAULT)
        self.assertFalse(res["ok"], res)

    def test_doctor_reports_failure_when_server_cannot_start(self) -> None:
        report = doctor.Report()
        with mock.patch.object(doctor, "probe_mcp_server", return_value={"ok": False, "detail": "boom", "tools": 0}) as probe:
            doctor.check_mcp_and_evals(report)
        probe.assert_called_once()
        entry = next(r for r in report.rows if r["check"].startswith("MCP Server"))
        self.assertEqual(entry["status"], doctor.FAIL)


class CapiPayloadTests(unittest.TestCase):
    """B06 — payload'ga faqat foydalanuvchi bergan qiymatlar."""

    def event(self, **kw) -> dict:
        return cu.build_capi_payload("Lead", **kw)

    def test_no_invented_values(self) -> None:
        res = self.event(phone="+998901234567", email="a@b.uz")
        ev = res["capi_payload"]["data"][0]
        self.assertEqual(set(ev["user_data"]), {"ph", "em"})
        for forbidden in ("fbp", "fbc", "country", "ct", "fn", "client_user_agent", "client_ip_address"):
            self.assertNotIn(forbidden, ev["user_data"])
        for forbidden in ("event_source_url", "custom_data", "event_id", "data_processing_options"):
            self.assertNotIn(forbidden, ev, forbidden)
        blob = json.dumps(res["capi_payload"])
        for fake in ("fb.1.1729200000", "tashkent", "LEAD_001", "CRM_1001", "brand.uz"):
            self.assertNotIn(fake, blob)

    def test_missing_fields_are_reported(self) -> None:
        res = self.event(phone="+998901234567")
        self.assertIn("client_user_agent", res["missing_fields"])
        self.assertIn("event_source_url", res["missing_fields"])
        self.assertIn("event_id", res["missing_fields"])
        self.assertTrue(res["warnings"])
        self.assertEqual(res["system_generated_fields"], ["event_time"])

    def test_user_supplied_values_pass_through(self) -> None:
        res = cu.build_capi_payload(
            "Purchase", email="a@b.de", fbp="fb.1.1.2", fbc="fb.1.1.abc", user_agent="UA/1.0", ip="1.2.3.4",
            value=150, currency="EUR", order_id="A55", event_source_url="https://s.de/x", country="de",
            action_source="website", event_time=1700000000, market="eu",
        )
        ev = res["capi_payload"]["data"][0]
        ud = ev["user_data"]
        self.assertEqual((ud["fbp"], ud["fbc"], ud["client_user_agent"], ud["client_ip_address"]), ("fb.1.1.2", "fb.1.1.abc", "UA/1.0", "1.2.3.4"))
        self.assertEqual(ev["custom_data"], {"currency": "EUR", "value": 150.0, "order_id": "A55"})
        self.assertEqual(ev["event_time"], 1700000000)
        self.assertEqual(ev["event_id"], "evt_purchase_A55")
        self.assertEqual(res["missing_fields"], [])
        self.assertEqual(res["system_generated_fields"], [])

    def test_action_source_for_non_web_flows(self) -> None:
        res = cu.build_capi_payload("Lead", phone="+998901234567", action_source="business_messaging", event_id="e1")
        self.assertEqual(res["capi_payload"]["data"][0]["action_source"], "business_messaging")
        self.assertNotIn("client_user_agent", res["missing_fields"])
        with self.assertRaises(ValueError):
            cu.build_capi_payload("Lead", action_source="telepathy")

    def test_value_without_currency_is_error(self) -> None:
        with self.assertRaises(ValueError):
            cu.build_capi_payload("Purchase", value=10)

    def test_emq_is_labelled_heuristic_and_ignores_missing_fbp(self) -> None:
        sparse = self.event(phone="+998901234567", email="a@b.uz")
        self.assertEqual(sparse["emq_basis"], "HEURISTIC_PRIOR_MODEL")
        full = self.event(phone="+998901234567", email="a@b.uz", fbp="fb.1.1.2", fbc="fb.1.1.abc")
        self.assertEqual(round(full["estimated_emq_score_10"] - sparse["estimated_emq_score_10"], 1), 2.1)

    def test_no_consent_strips_pii(self) -> None:
        res = self.event(phone="+998901234567", email="a@b.uz", fbp="fb.1.1.2", user_agent="UA", consent_granted=False)
        self.assertEqual(res["capi_payload"]["data"][0]["user_data"], {})

    def test_cli_flags(self) -> None:
        proc = run_tool("capi-utm-builder.py", "capi-payload", "--email", "a@b.de", "--fbp", "fb.1.1.2", "--user-agent", "UA",
                        "--ip", "1.2.3.4", "--action-source", "website", "--event-source-url", "https://s.de/", "--event-id", "e9", "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        ev = json.loads(proc.stdout)["capi_payload"]["data"][0]
        self.assertEqual(ev["user_data"]["fbp"], "fb.1.1.2")
        self.assertEqual(ev["event_id"], "e9")
        bad = run_tool("capi-utm-builder.py", "capi-payload", "--value", "5")
        self.assertEqual(bad.returncode, 2)


class UtmFragmentTests(unittest.TestCase):
    """B07."""

    def test_fragment_stays_after_query(self) -> None:
        url = cu.build_utm_links("https://shop.com/page#section", "meta", "q4")["full_tracked_url"]
        self.assertTrue(url.endswith("#section"), url)
        self.assertEqual(url.count("#"), 1)
        self.assertLess(url.index("?utm_source="), url.index("#section"))

    def test_existing_query_and_fragment(self) -> None:
        url = cu.build_utm_links("https://shop.com/p?a=1#x", "google", "q4")["full_tracked_url"]
        self.assertTrue(url.startswith("https://shop.com/p?a=1&utm_source=google"), url)
        self.assertTrue(url.endswith("#x"))
        self.assertIn("{campaignid}", url)  # makrolar kodlanmaydi

    def test_plain_url_unchanged_behavior(self) -> None:
        url = cu.build_utm_links("https://shop.com/p", "telegram", "Q4 Sale")["full_tracked_url"]
        self.assertTrue(url.startswith("https://shop.com/p?utm_source=telegram"))


class CalculatorGuardTests(unittest.TestCase):
    """B11."""

    def test_loss_exits_nonzero(self) -> None:
        proc = run_tool("calculator.py", "breakeven", "--price", "100", "--cogs", "120")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Zarardasiz", proc.stderr)
        proc = run_tool("calculator.py", "breakeven", "--price", "100", "--cogs", "120", "--json")
        self.assertEqual(proc.returncode, 1)
        self.assertTrue(json.loads(proc.stdout)["loss_making"])

    def test_nan_inf_rejected(self) -> None:
        for args in (("breakeven", "--price", "nan", "--cogs", "10"),
                     ("breakeven", "--price", "100", "--cogs", "inf"),
                     ("meta-155", "--daily-budget", "nan", "--target-cpa", "10"),
                     ("ladder", "--total-budget", "100", "--breakeven-cpa", "inf")):
            proc = run_tool("calculator.py", *args)
            self.assertEqual(proc.returncode, 2, args)
            self.assertNotIn("nan", proc.stdout.lower())

    def test_function_level_validation(self) -> None:
        with self.assertRaises(ValueError):
            calc.calc_breakeven(price=float("nan"), cogs=10)
        with self.assertRaises(ValueError):
            calc.calc_breakeven(price=100, cogs=-5)
        self.assertTrue(calc.calc_breakeven(price=100, cogs=120)["loss_making"])

    def test_profitable_exits_zero(self) -> None:
        proc = run_tool("calculator.py", "breakeven", "--price", "100", "--cogs", "40", "--json")
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(math.isfinite(json.loads(proc.stdout)["breakeven_cpa"]))


class GitignoreTests(unittest.TestCase):
    """B14."""

    def ignored(self, rel: str) -> bool:
        return subprocess.run(["git", "check-ignore", "-q", rel], cwd=str(VAULT)).returncode == 0

    def test_client_data_and_outputs_ignored(self) -> None:
        for rel in ("clients/acme/BRIEF.md", "clients/acme/outputs/report.md", "outputs/report.md", "outputs/a/b.csv"):
            self.assertTrue(self.ignored(rel), rel)

    def test_demo_and_templates_stay_tracked(self) -> None:
        for rel in ("examples/demo-brand/BRIEF.md", "examples/demo-brand/outputs/demo-audit-report.md",
                    "examples/demo-brand/assets/meta_performance.json", "templates/audit-report-template.md",
                    "templates/campaign-launch-packet-template.md", "clients/README.md"):
            self.assertFalse(self.ignored(rel), rel)

    def test_nothing_private_already_tracked(self) -> None:
        out = subprocess.run(["git", "ls-files", "clients", "outputs"], cwd=str(VAULT), capture_output=True, text=True).stdout
        self.assertEqual([l for l in out.splitlines() if l != "clients/README.md"], [])


if __name__ == "__main__":
    unittest.main()
