"""Tyrion — v7.0.1 dan keyingi tuzatishlar: B08, B09, B10, B12, B13, B15, B16, B17, B18, B19, B20 va
v7.2 eksport/Spend-Guard jurnali ishlari. Rasmiy tasdiqlanmagan bozor faktlari testlanmaydi."""

from __future__ import annotations

import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
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
ss = importlib.import_module("skill-search")
mcp = importlib.import_module("tyrion-mcp-server")
mis = importlib.import_module("meta-insights-sync")
doctor = importlib.import_module("doctor")
mloc = importlib.import_module("market_locale")
VERSION = (VAULT / "VERSION").read_text(encoding="utf-8").strip()


class TelegramCopyTests(unittest.TestCase):  # B13
    def test_star_and_flag_emojis_counted(self) -> None:
        self.assertFalse(sg.check_ad_copy("telegram", "Kanal ⭐⭐⭐⭐⭐ bor")["passed"])
        self.assertFalse(sg.check_ad_copy("telegram", "Salom 🇺🇿 dunyo 🇩🇪")["passed"])
        self.assertTrue(sg.check_ad_copy("telegram", "Yaxshi xabar ⭐")["passed"])

    def test_uzbek_cyrillic_caps(self) -> None:
        for word in ("ҚИЗИҒ", "ЎЗБЕКИСТОН", "ҒАЛАБА", "ҲАММА"):
            res = sg.check_ad_copy("telegram", f"{word} taklif")
            self.assertFalse(res["passed"], word)

    def test_meta_banned_phrases_ru_en(self) -> None:
        self.assertFalse(sg.check_ad_copy("meta", "get rich quick with us")["passed"])
        self.assertFalse(sg.check_ad_copy("meta", "Гарантированный доход каждый месяц")["passed"])

    def test_docstring_flags_exist(self) -> None:
        doc = sg.__doc__ or ""
        for bad in ("--event-id", "--has-pixel", "--has-capi"):
            self.assertNotIn(bad, doc)


class PhoneTests(unittest.TestCase):  # B17
    def test_e164_with_country_code(self) -> None:
        self.assertEqual(cu.normalize_phone("0151 23456789", "49"), "4915123456789")
        self.assertEqual(cu.normalize_phone("+49 151 23456789", "49"), "4915123456789")
        self.assertEqual(cu.normalize_phone("07700 900123", "44"), "447700900123")
        self.assertEqual(cu.normalize_phone("0044 7700 900123", ""), "447700900123")
        self.assertEqual(cu.normalize_phone("90 123-45-67", "998"), "998901234567")

    def test_unknown_country_code_left_untouched_and_warned(self) -> None:
        self.assertEqual(cu.normalize_phone("5551234567", ""), "5551234567")
        res = cu.build_capi_payload("Lead", phone="5551234567", event_id="e1", market="global")
        self.assertTrue(any("mamlakat kodisiz" in w for w in res["warnings"]))

    def test_country_drives_hash(self) -> None:
        a = cu.build_capi_payload("Lead", phone="0151 23456789", country="de", event_id="e")
        b = cu.build_capi_payload("Lead", phone="+49 151 23456789", event_id="e")
        self.assertEqual(a["capi_payload"]["data"][0]["user_data"]["ph"], b["capi_payload"]["data"][0]["user_data"]["ph"])
        c = cu.build_capi_payload("Lead", phone="0151 23456789", phone_country_code="49", event_id="e")
        self.assertEqual(c["capi_payload"]["data"][0]["user_data"]["ph"], b["capi_payload"]["data"][0]["user_data"]["ph"])


class BreakdownEffectTests(unittest.TestCase):  # B10
    def test_no_unsourced_projection(self) -> None:
        res = ae.analyze_breakdown_effect("Reels", 750, 50, "Feed", 150, 12)
        self.assertTrue(res["breakdown_effect_trap_detected"])
        self.assertIsNone(res["projected_cpa_if_dominant_paused_usd"])
        self.assertEqual(res["evidence_label"], "HEURISTIC_PRIOR_MODEL")
        self.assertNotIn("1.38", json.dumps(res))
        for html in ("tyrion-studio.html", "calculator.html"):
            self.assertNotIn("1.38", (TOOLS / html).read_text(encoding="utf-8"))


class McpProtocolTests(unittest.TestCase):  # B12
    def call(self, method: str, params: dict | None = None, rid: int = 1) -> dict:
        req = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            req["params"] = params
        return mcp.handle_request(req)

    def test_ping(self) -> None:
        self.assertEqual(self.call("ping")["result"], {})

    def test_protocol_version_negotiation(self) -> None:
        for v in mcp.SUPPORTED_PROTOCOL_VERSIONS:
            self.assertEqual(self.call("initialize", {"protocolVersion": v})["result"]["protocolVersion"], v)
        self.assertIn(self.call("initialize", {"protocolVersion": "1999-01-01"})["result"]["protocolVersion"],
                      mcp.SUPPORTED_PROTOCOL_VERSIONS)
        self.assertEqual(self.call("initialize")["result"]["serverInfo"]["version"], VERSION)

    def test_tool_failure_is_iserror_result(self) -> None:
        r = self.call("tools/call", {"name": "tyrion_media_calculator", "arguments": {"price": -5, "cogs": 1}})
        self.assertTrue(r["result"]["isError"])
        self.assertNotIn("error", r)
        r = self.call("tools/call", {"name": "tyrion_spend_guard", "arguments": {}})
        self.assertTrue(r["result"]["isError"])  # majburiy argument yo'q
        r = self.call("tools/call", {"name": "does_not_exist", "arguments": {}})
        self.assertEqual(r["error"]["code"], -32602)

    def test_schema_covers_every_argument_call_tool_reads(self) -> None:
        src = (TOOLS / "tyrion-mcp-server.py").read_text(encoding="utf-8")
        body = src[src.index("def call_tool"):src.index("def handle_request")]
        for block in re.split(r'\n    if name == "', body)[1:]:
            name = block.split('"')[0]
            keys = set(re.findall(r'args(?:\.get\(|\[)"(\w+)"', block))
            props = set(next(t for t in mcp.MCP_TOOLS if t["name"] == name)["inputSchema"]["properties"])
            self.assertEqual(keys - props, set(), f"{name}: sxemada yo'q parametrlar")

    def test_spend_guard_tool_pause_and_capi_mode(self) -> None:
        r = self.call("tools/call", {"name": "tyrion_spend_guard", "arguments": {"current_daily": 100, "proposed_daily": 0}})
        self.assertFalse(json.loads(r["result"]["content"][0]["text"])["passed"])
        r = self.call("tools/call", {"name": "tyrion_capi_utm", "arguments": {
            "mode": "capi-payload", "email": "a@b.de", "event_id": "e1", "user_agent": "UA", "event_source_url": "https://s.de"}})
        payload = json.loads(r["result"]["content"][0]["text"])
        self.assertEqual(payload["capi_payload"]["data"][0]["event_id"], "e1")


class UzbekDetectionTests(unittest.TestCase):  # B08
    def test_plan_examples(self) -> None:
        for q in ("TikTok reklamani qanday boshlayman", "Google Ads PMax kampaniyam CPA oshib ketdi",
                  "kampaniyam ishlamayapti", "Meta reklama byudjetim kerak"):
            self.assertEqual(ss.detect_language(q), "uz_latin", q)

    def test_english_and_russian_unchanged(self) -> None:
        self.assertEqual(ss.detect_language("Meta ads audit for my store"), "en")
        self.assertEqual(ss.detect_language("How do I scale a human campaign"), "en")
        self.assertEqual(ss.detect_language("Проверь рекламу в Meta"), "ru")

    def test_uzbek_query_selects_uz_market(self) -> None:
        plan = ss.build_execution_plan("TikTok reklamani qanday boshlayman") if hasattr(ss, "build_execution_plan") else None
        info = mloc.detect_market(text="TikTok reklamani qanday boshlayman", detected_lang=ss.detect_language("TikTok reklamani qanday boshlayman"))
        self.assertEqual(info["market_id"], "uz")
        self.assertEqual(info["currency"], "UZS")
        del plan


@unittest.skipUnless(shutil.which("node"), "node o'rnatilmagan")
class PluginOptionsTests(unittest.TestCase):  # B09
    def run_hook(self, env_extra: dict, mode: str = "guard") -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as td:  # hook skripti yo'q ildiz: yoqilgan bo'lsa stderr/strict xato beradi
            env = {k: v for k, v in os.environ.items() if not k.startswith(("TYRION_", "CLAUDE_PLUGIN_"))}
            env.update({"CLAUDE_PLUGIN_ROOT": td}); env.update(env_extra)
            return subprocess.run(["node", str(VAULT / "hooks" / "run-hook.cjs"), mode], capture_output=True, text=True,
                                  env=env, timeout=30, input="")

    def test_hooks_disabled_option_is_honoured(self) -> None:
        on = self.run_hook({"TYRION_HOOK_PROFILE": "strict"})
        self.assertEqual(on.returncode, 2, on.stderr)  # sozlama bo'lmasa: skript yo'q -> strict xato
        off = self.run_hook({"TYRION_HOOK_PROFILE": "strict", "CLAUDE_PLUGIN_OPTION_HOOKS_ENABLED": "false"})
        self.assertEqual(off.returncode, 0)
        self.assertEqual(off.stderr, "")

    def test_minimal_profile_skips_guard_but_not_brief(self) -> None:
        g = self.run_hook({"CLAUDE_PLUGIN_OPTION_HOOK_PROFILE": "minimal"}, "guard")
        self.assertEqual((g.returncode, g.stderr), (0, ""))
        b = self.run_hook({"CLAUDE_PLUGIN_OPTION_HOOK_PROFILE": "minimal"}, "brief")
        self.assertIn("hook script not found", b.stderr)
        s = self.run_hook({"CLAUDE_PLUGIN_OPTION_HOOK_PROFILE": "standard"}, "guard")
        self.assertIn("hook script not found", s.stderr)

    def test_default_market_option(self) -> None:
        env = {k: v for k, v in os.environ.items() if k not in ("TYRION_MARKET", "CLAUDE_PLUGIN_OPTION_DEFAULT_MARKET")}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(mloc.detect_market("Meta audit")["market_id"], "uz")  # qaror: asosiy auditoriya uz
            os.environ["CLAUDE_PLUGIN_OPTION_DEFAULT_MARKET"] = "eu"
            self.assertEqual(mloc.detect_market("Meta audit")["market_id"], "eu")
            os.environ["TYRION_MARKET"] = "us"   # aniq o'zgaruvchi ustun
            self.assertEqual(mloc.configured_default_market(), "us")
            os.environ["CLAUDE_PLUGIN_OPTION_DEFAULT_MARKET"] = "narnia"
            os.environ.pop("TYRION_MARKET")
            self.assertEqual(mloc.configured_default_market(), "uz")

    def test_plugin_manifests_default_to_uz(self) -> None:
        for rel in ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            cfg = json.loads((VAULT / rel).read_text(encoding="utf-8"))
            self.assertEqual(cfg["userConfig"]["default_market"]["default"], "uz", rel)


class ApiRegistryTests(unittest.TestCase):  # B19
    def test_single_source_of_truth(self) -> None:
        default = tcore.graph_api_default()
        self.assertRegex(default, r"^v\d+\.\d+$")
        for modname in ("capi-utm-builder", "meta-insights-sync", "meta-targeting-engine", "meta-audience"):
            self.assertEqual(importlib.import_module(modname).DEFAULT_GRAPH_API_VERSION, default, modname)
        for f in ("capi-utm-builder.py", "meta-insights-sync.py", "meta-targeting-engine.py", "meta-audience.py"):
            self.assertNotRegex((TOOLS / f).read_text(encoding="utf-8"), r'DEFAULT_GRAPH_API_VERSION\s*=\s*"v\d')

    def test_registry_marks_unverified_facts(self) -> None:
        reg = json.loads((VAULT / "manifests" / "api-versions.json").read_text(encoding="utf-8"))["meta_graph"]
        by = {v["version"]: v for v in reg["versions"]}
        self.assertIn(reg["default"], by)
        self.assertTrue(by[reg["default"]]["verified"])
        self.assertFalse(by["v27.0"]["verified"])  # rasmiy tasdiqsiz default bo'lmaydi
        self.assertNotEqual(reg["default"], "v27.0")

    def test_deprecation_threshold_comes_from_registry(self) -> None:
        with mock.patch.dict(os.environ, {"META_GRAPH_API_VERSION": "v21.0"}):
            info = mloc.get_configured_api_version()
        self.assertTrue(info["is_deprecated"])
        self.assertIn(tcore.graph_api_default(), info["warning"])


class InsightsAttributionTests(unittest.TestCase):  # B16
    def test_parse_windows(self) -> None:
        self.assertEqual(mis.parse_attribution_windows(""), mis.DEFAULT_ATTRIBUTION_WINDOWS)
        self.assertIsNone(mis.parse_attribution_windows("account_default"))
        self.assertEqual(mis.parse_attribution_windows("1d_click, 7d_click"), ("1d_click", "7d_click"))
        with self.assertRaises(ValueError):
            mis.parse_attribution_windows("forever")

    def test_live_request_pins_attribution_window(self) -> None:
        seen: list[str] = []

        def fake(url, **kw):
            seen.append(url)
            return {"data": [{"spend": "1", "account_currency": "UZS"}]}
        with mock.patch.dict(os.environ, {"META_ACCESS_TOKEN": "tok_real_123456"}), \
                mock.patch.object(tcore, "http_get_json_with_backoff", side_effect=fake):
            res = mis.fetch_live_meta_insights("act_1")
            self.assertIn("action_attribution_windows=", seen[0])
            self.assertIn("7d_click", seen[0])
            self.assertEqual(res["attribution_windows"], ["7d_click", "1d_view"])
            mis.fetch_live_meta_insights("act_1", attribution_windows=None)
            self.assertNotIn("action_attribution_windows", seen[1])

    def test_report_states_attribution_basis(self) -> None:
        raw = FIXTURES.parent.parent / "examples" / "demo-brand" / "assets" / "meta_graph_insights_raw.json"
        res = mis.sync_and_analyze(from_raw_json=raw)
        self.assertEqual(res["attribution"]["basis"], "ACCOUNT_DEFAULT_OR_IMPORTED_FILE")
        self.assertIn("solishtirmang", res["attribution"]["warning"])

    def test_non_usd_currency_flags_legacy_keys(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "u.csv"
            p.write_text("Ad set name,Amount spent (UZS),Purchases\nA,\"1,500,000\",5\n", encoding="utf-8")
            res = ae.analyze_export(p)
        self.assertEqual(res["currency"], "UZS")
        self.assertIn("UZS", res["legacy_usd_keys_note"])


class SpendGuardLedgerTests(unittest.TestCase):  # v7.2: 24 soatlik oyna
    def test_stacked_changes_blocked_within_24h(self) -> None:
        now = 1_800_000_000.0
        hist = [{"ts": now - 3600, "entity": "c1", "from": 100.0, "to": 118.0}]
        res = sg.check_budget_change(118.0, 140.0, history=hist, now=now)  # +18.6% qadam, jami +40%
        self.assertFalse(res["passed"])
        self.assertTrue(any("24 soat" in e for e in res["errors"]))
        self.assertEqual(res["window_24h"]["baseline"], 100.0)

    def test_old_history_ignored_and_small_total_ok(self) -> None:
        now = 1_800_000_000.0
        old = [{"ts": now - 90000, "entity": "c1", "from": 50.0, "to": 100.0}]
        self.assertTrue(sg.check_budget_change(100.0, 118.0, history=old, now=now)["passed"])
        recent = [{"ts": now - 60, "entity": "c1", "from": 100.0, "to": 105.0}]
        self.assertTrue(sg.check_budget_change(105.0, 118.0, history=recent, now=now)["passed"])

    def test_cli_record_requires_operator_and_persists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            led = Path(td) / "l.jsonl"
            base = [sys.executable, str(TOOLS / "spend-guard.py"), "budget", "--entity", "c1", "--ledger", str(led),
                    "--current", "100", "--proposed", "118"]
            bad = subprocess.run(base + ["--record"], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertFalse(led.exists())
            ok = subprocess.run(base + ["--record", "--approved-by", "Ali"], capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stdout)
            entry = json.loads(led.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual((entry["entity"], entry["approved_by"], entry["to"]), ("c1", "Ali", 118.0))
            nxt = subprocess.run(base[:-4] + ["--current", "118", "--proposed", "140"], capture_output=True, text=True)
            self.assertEqual(nxt.returncode, 1)
            self.assertIn("24 soat", nxt.stdout)

    def test_blocked_change_not_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            led = Path(td) / "l.jsonl"
            r = subprocess.run([sys.executable, str(TOOLS / "spend-guard.py"), "budget", "--entity", "c1", "--ledger", str(led),
                                "--current", "100", "--proposed", "200", "--record", "--approved-by", "Ali"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertFalse(led.exists())

    def test_ledger_ignored_by_git(self) -> None:
        rel = sg.DEFAULT_LEDGER.relative_to(VAULT).as_posix()
        self.assertEqual(subprocess.run(["git", "check-ignore", "-q", rel], cwd=str(VAULT)).returncode, 0)


class ExportTotalRowTests(unittest.TestCase):  # v7.2: jami qator
    def test_totals_not_double_counted(self) -> None:
        meta = ae.analyze_export(FIXTURES / "meta_ads_manager_en.csv")
        self.assertEqual(len(meta["decisions"]), 3)
        self.assertEqual(meta["summary"]["total_spend"], 2570.5)
        self.assertEqual(meta["input_format"]["skipped_total_rows"], 1)
        google = ae.analyze_export(FIXTURES / "google_ads.csv")
        self.assertEqual(len(google["decisions"]), 3)
        self.assertEqual(google["summary"]["total_spend"], 2320.25)
        self.assertEqual(google["input_format"]["skipped_total_rows"], 1)
        self.assertIn("November 1, 2026 - November 10, 2026", " ".join(google["input_format"]["preamble"]))

    def test_blank_name_row_kept_when_not_a_total(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.csv"
            p.write_text("Ad set name,Amount spent (USD),Purchases\nA,100,5\nB,200,6\n,50,1\n", encoding="utf-8")
            res = ae.analyze_export(p)
        self.assertEqual(res["input_format"]["skipped_total_rows"], 0)
        self.assertEqual(res["summary"]["total_spend"], 350.0)


class UzCreditWarningTests(unittest.TestCase):
    def test_credit_copy_warns_and_labels_unverified(self) -> None:
        res = sg.check_ad_copy("meta", "Oyiga atigi 99 000 so'm (Nasiya orqali)")
        self.assertTrue(res["passed"])
        self.assertTrue(any("moliyaviy xatar" in w for w in res["warnings"]))
        self.assertEqual(res["evidence"]["uz_credit_warning_rule"], "UNVERIFIED_SECONDARY_SOURCE")
        self.assertEqual(sg.check_ad_copy("meta", "Yangi kolleksiya")["evidence"], {})


class DoctorFollowupTests(unittest.TestCase):  # B15, B18, freshness
    def test_version_single_source(self) -> None:
        rep = doctor.Report()
        doctor.check_version(rep)
        self.assertEqual(rep.rows[0]["status"], doctor.OK, rep.rows)
        self.assertEqual(tcore.project_version(), VERSION)
        self.assertEqual(mcp.SERVER_VERSION, VERSION)

    def test_version_drift_detected(self) -> None:
        rep = doctor.Report()
        with mock.patch.object(doctor, "VAULT", Path(tempfile.mkdtemp())) as v:
            (v / "VERSION").write_text("9.9.9", encoding="utf-8")
            (v / "package.json").write_text(json.dumps({"version": "1.0.0"}), encoding="utf-8")
            doctor.check_version(rep)
        self.assertEqual(rep.rows[0]["status"], doctor.FAIL)

    def test_freshness_flags_overdue(self) -> None:
        rep = doctor.Report()
        doctor.check_freshness(rep, today=datetime(2026, 11, 11, tzinfo=timezone.utc))
        self.assertEqual(rep.rows[0]["status"], doctor.WARN)
        self.assertIn("2026-08-10", rep.rows[0]["detail"])
        rep2 = doctor.Report()
        doctor.check_freshness(rep2, today=datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(rep2.rows[0]["status"], doctor.OK)

    def test_graph_staleness_uses_commit_time_not_mtime(self) -> None:
        with mock.patch.object(doctor, "_git_commit_time", side_effect=lambda paths: 1000.0):
            rep = doctor.Report()
            data = {"items": {"wiki": [{"path": "wiki/ab-test-mexanikasi.md"}]}}
            os.utime(VAULT / "wiki" / "ab-test-mexanikasi.md", None)  # mtime hozir — commit vaqti teng
            doctor.check_graph(rep, data)
        self.assertEqual(rep.rows[0]["status"], doctor.OK)
        self.assertNotIn("gy.cmd", rep.rows[0]["detail"])
        with mock.patch.object(doctor, "_git_commit_time", side_effect=lambda paths: 2000.0 if paths == ["wiki"] else 1000.0):
            rep = doctor.Report()
            doctor.check_graph(rep, data)
        self.assertEqual(rep.rows[0]["status"], doctor.WARN)
        self.assertNotIn("gy.cmd", rep.rows[0]["detail"])

    def test_wiki_sources_reported(self) -> None:
        rep = doctor.Report()
        doctor.check_wiki_sources(rep, {"items": {"wiki": [{"path": "wiki/ab-test-mexanikasi.md"}]}})
        self.assertEqual(rep.rows[0]["status"], doctor.WARN)

    def test_ci_runs_on_every_branch(self) -> None:
        ci = (VAULT / ".github" / "workflows" / "tyrion-ci.yml").read_text(encoding="utf-8")
        self.assertRegex(ci, r'push:\s*\n\s*branches:\s*\[\s*"\*\*"\s*\]')
        count = re.search(r"\((\d+) Tests", ci)
        self.assertIsNotNone(count)


if __name__ == "__main__":
    unittest.main()
