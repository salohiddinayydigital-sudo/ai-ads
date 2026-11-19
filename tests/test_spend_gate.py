"""Spend-Guard PreToolUse darvozasi: deny / ask / allow holatlari (sintetik packet'lar)."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._helpers import VAULT

import spend_gate as sg  # noqa: E402

NOW = dt.datetime(2026, 11, 19, 12, 0, tzinfo=dt.timezone.utc)
WRITE = "mcp__target__ads_update_entity"


def packet(**over) -> dict:
    p = {
        "schema": "change-packet.v1", "synthetic": True, "entity": "123456", "proposed_tool": "ads_update_entity",
        "kind": "budget", "proposal": {"current_daily": 100, "proposed_daily": 115},
        "risk": "past", "stop_loss": "Agar CPA 2x oshsa to'xtatish taklif qilinadi",
        "rollback": "Byudjetni 100 ga qaytarish (ads_update_entity)", "baseline": {"cpa": 10},
        "approved_by_user": True, "approved_at": (NOW - dt.timedelta(hours=2)).isoformat(),
    }
    p.update(over)
    return p


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.clients = Path(self.td.name) / "clients"
        (self.clients / "demo" / "changes").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def put(self, pk: dict, name: str = "c1.json") -> None:
        (self.clients / "demo" / "changes" / name).write_text(json.dumps(pk), encoding="utf-8")

    def ev(self, tool=WRITE, tinput=None, profile="standard"):
        payload = {"tool_name": tool, "tool_input": tinput if tinput is not None else {"entity_id": "123456", "daily_budget": 115}}
        return sg.evaluate(payload, profile, now=NOW, clients_dir=self.clients)


class DecisionTests(Base):
    def test_no_packet_strict_denies_standard_asks(self) -> None:
        self.assertEqual(self.ev(profile="strict")["decision"], "deny")
        self.assertEqual(self.ev(profile="standard")["decision"], "ask")

    def test_valid_packet_allows(self) -> None:
        self.put(packet())
        r = self.ev(profile="strict")
        self.assertEqual(r["decision"], "allow")
        self.assertIn("c1.json", r["reason"])

    def test_read_tools_pass_through(self) -> None:
        for t in ("mcp__target__ads_get_ad_entities", "mcp__target__ads_insights_performance_trend", "mcp__target__ads_library_search",
                  "mcp__target__ads_catalog_list_products", "mcp__target__ads_pixel_event_read"):
            self.assertFalse(sg.is_write_tool(t), t)
            self.assertEqual(self.ev(tool=t, profile="strict")["decision"], "allow")

    def test_write_tools_detected(self) -> None:
        for t in ("mcp__target__ads_create_campaign", "mcp__target__ads_activate_entity", "mcp__target__ads_duplicate_entity",
                  "mcp__target__ads_delete_custom_audience", "mcp__target__ads_creative_upload_media", "mcp__plugin_x_meta__ads_update_entity",
                  "mcp__target__ads_experiment_abtest_create_test", "mcp__g__assets_create_asset", "mcp__g__labels_manage_labels"):
            self.assertTrue(sg.is_write_tool(t), t)

    def test_official_meta_write_tools_all_gated_and_reads_pass(self) -> None:
        """Meta rasmiy hujjatidagi (2026-11-19) yozish asboblari ushlanadi, o'qish asboblari o'tadi."""
        writes = ("ads_create_campaign", "ads_create_ad_set", "ads_create_ad", "ads_update_entity", "ads_activate_entity",
                  "ads_create_creative", "ads_boost_ig_post", "ads_create_custom_audience", "ads_update_custom_audience",
                  "ads_update_custom_audience_users", "ads_delete_custom_audience")
        reads = ("ads_get_ad_accounts", "ads_get_ad_account_pages", "ads_get_pages_for_business", "ads_get_user_pages", "ads_get_field_context",
                 "ads_get_creatives", "ads_get_creative_ads", "ads_get_ad_images", "ads_get_ad_videos", "ads_get_ad_preview",
                 "ads_get_ad_entities", "ads_library_search", "ads_get_ig_accounts", "ads_get_ig_media",
                 "ads_get_ad_account_custom_audiences", "ads_get_custom_audience", "ads_get_custom_audience_adsets")
        for n in writes:
            self.assertTrue(sg.is_write_tool("mcp__plugin_tyrion_meta__" + n), n)
        for n in reads:
            self.assertFalse(sg.is_write_tool("mcp__plugin_tyrion_meta__" + n), n)

    def test_minimal_profile_disables_gate(self) -> None:
        self.assertEqual(self.ev(profile="minimal")["decision"], "allow")

    def test_unapproved_expired_future_and_no_rollback_rejected(self) -> None:
        cases = {
            "unapproved": packet(approved_by_user=False),
            "expired": packet(approved_at=(NOW - dt.timedelta(hours=25)).isoformat()),
            "future": packet(approved_at=(NOW + dt.timedelta(hours=3)).isoformat()),
            "no_rollback": packet(rollback=""),
            "wrong_entity": packet(entity="999"),
            "bad_schema": packet(schema="x"),
        }
        for name, pk in cases.items():
            with self.subTest(case=name):
                self.put(pk)
                r = self.ev(profile="strict")
                self.assertEqual(r["decision"], "deny", name)

    def test_budget_over_20pct_in_packet_is_rejected(self) -> None:
        self.put(packet(proposal={"current_daily": 100, "proposed_daily": 160}))
        self.assertEqual(self.ev(profile="strict")["decision"], "deny")

    def test_create_tool_matches_by_proposed_tool(self) -> None:
        self.put(packet(entity="new:campaign-1", proposed_tool="ads_create_campaign", proposal={}))
        self.assertEqual(self.ev(tool="mcp__target__ads_create_campaign", tinput={"name": "X"}, profile="strict")["decision"], "allow")
        # update asbobi uchun id'siz moslik yo'q
        self.assertEqual(self.ev(tool=WRITE, tinput={"name": "X"}, profile="strict")["decision"], "deny")

    def test_experiment_packet_from_experiments_tool_matches(self) -> None:
        sys.path.insert(0, str(VAULT / "tools"))
        pk = packet(entity="EXP-1", proposed_tool="ads_experiment_abtest_create_test", proposal={})
        self.put(pk)
        r = self.ev(tool="mcp__target__ads_experiment_abtest_create_test", tinput={"ad_account_id": "act_1"}, profile="strict")
        self.assertEqual(r["decision"], "allow")


class HookOutputTests(Base):
    def test_hook_output_format(self) -> None:
        out = sg.hook_output({"decision": "deny", "reason": "r"})
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PreToolUse")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIsNone(sg.hook_output({"decision": "allow", "reason": ""}))

    def _run_hook(self, payload: dict, profile: str) -> str:
        env = {**os.environ, "TYRION_HOOK_PROFILE": profile, "TYRION_CLIENTS_DIR": str(self.clients), "CLAUDE_PLUGIN_ROOT": str(VAULT)}
        env.pop("TYRION_DISABLED_HOOKS", None)
        return subprocess.run([sys.executable, str(VAULT / "hooks" / "tyrion-hook.py"), "spend"], input=json.dumps(payload),
                              capture_output=True, text=True, env=env, timeout=30).stdout

    def test_hook_cli_deny_ask_allow(self) -> None:
        pl = {"tool_name": WRITE, "tool_input": {"entity_id": "123456"}}
        self.assertEqual(json.loads(self._run_hook(pl, "strict"))["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(json.loads(self._run_hook(pl, "standard"))["hookSpecificOutput"]["permissionDecision"], "ask")
        self.put(packet(approved_at=dt.datetime.now(dt.timezone.utc).isoformat()))
        self.assertEqual(self._run_hook(pl, "strict").strip(), "")

    def test_hooks_json_matcher_covers_write_tools_only(self) -> None:
        hooks = json.loads((VAULT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
        entry = [h for h in hooks if h["hooks"][0]["command"].rstrip().endswith(" spend")][0]
        rx = re.compile(entry["matcher"])
        for t in ("mcp__target__ads_create_ad", "mcp__plugin_tyrion_meta__ads_update_entity", "mcp__x__ads_activate_entity",
                  "mcp__x__ads_duplicate_entity", "mcp__x__ads_delete_custom_audience", "mcp__x__ads_creative_update"):
            self.assertTrue(rx.search(t), t)
        for t in ("mcp__target__ads_get_ad_entities", "mcp__target__ads_insights_anomaly_signal", "Edit", "Bash"):
            self.assertFalse(rx.search(t), t)

    def test_spend_guard_cli_accepts_json_packet(self) -> None:
        f = Path(self.td.name) / "p.json"
        f.write_text(json.dumps(packet()), encoding="utf-8")
        p = subprocess.run([sys.executable, str(VAULT / "tools" / "spend-guard.py"), "packet", str(f), "--json"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        f.write_text(json.dumps(packet(rollback="")), encoding="utf-8")
        p = subprocess.run([sys.executable, str(VAULT / "tools" / "spend-guard.py"), "packet", str(f), "--json"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)


if __name__ == "__main__":
    unittest.main()
