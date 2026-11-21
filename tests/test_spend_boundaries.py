"""Boundary and invalid-input tests for tools/spend-guard.py and tools/spend_gate.py."""

from __future__ import annotations

import datetime as dt
import importlib
import json
import unittest

from tests._helpers import run_tool_inproc

import spend_gate as sg  # noqa: E402

guard = importlib.import_module("spend-guard")
NOW = dt.datetime(2026, 11, 19, 12, 0, tzinfo=dt.timezone.utc)
TOOL = "mcp__target__ads_update_entity"


def pk(**over) -> dict:
    p = {
        "schema": "change-packet.v1", "entity": "42", "proposed_tool": "ads_update_entity", "kind": "budget",
        "proposal": {"current_daily": 100, "proposed_daily": 110}, "risk": "past",
        "stop_loss": "Agar CPA 2x oshsa to'xtatish", "rollback": "Byudjetni qaytarish", "baseline": {"cpa": 10},
        "approved_by_user": True, "approved_at": (NOW - dt.timedelta(hours=1)).isoformat(),
    }
    p.update(over)
    return p


class BudgetBoundaryTests(unittest.TestCase):
    def test_exactly_20_percent_passes_and_just_over_fails(self) -> None:
        self.assertTrue(guard.check_budget_change(100, 120, 500)["passed"])
        over = guard.check_budget_change(100, 120.01, 500)
        self.assertFalse(over["passed"])
        self.assertEqual(over["percent_change"], 20.01)

    def test_exact_20_percent_has_no_float_drift_for_awkward_bases(self) -> None:
        for cur in (0.1, 0.3, 3, 7, 11, 13, 33.33, 70, 99.99, 1234.56, 330):
            self.assertTrue(guard.check_budget_change(cur, cur * 1.2, 1e9)["passed"], msg=str(cur))

    def test_cap_boundary(self) -> None:
        self.assertTrue(guard.check_budget_change(400, 480, 480)["passed"])  # == cap -> allowed
        res = guard.check_budget_change(400, 480.01, 480)
        self.assertFalse(res["passed"])
        self.assertTrue(any("maksimal limit" in e for e in res["errors"]))

    def test_decreases_pass_and_deep_cut_only_warns(self) -> None:
        self.assertTrue(guard.check_budget_change(100, 50, 500)["passed"])
        self.assertEqual(guard.check_budget_change(100, 50, 500)["warnings"], [])
        cut = guard.check_budget_change(100, 49, 500)
        self.assertTrue(cut["passed"])
        self.assertEqual(len(cut["warnings"]), 1)

    def test_no_change_passes(self) -> None:
        res = guard.check_budget_change(100, 100, 500)
        self.assertTrue(res["passed"])
        self.assertEqual(res["percent_change"], 0.0)

    def test_learning_volume_warning_boundary(self) -> None:
        # target_cpa 14 -> healthy minimum = 14*50/7 = 100/day
        self.assertEqual(guard.check_budget_change(100, 100, 500, target_cpa=14)["warnings"], [])
        self.assertEqual(len(guard.check_budget_change(100, 99, 500, target_cpa=14)["warnings"]), 1)

    def test_invalid_inputs_block_with_error_field(self) -> None:
        bad_values = [float("nan"), float("inf"), float("-inf"), 0, -1, None, True, "abc", ""]
        for bad in bad_values:
            for args in ((bad, 100, 500), (100, bad, 500), (100, 110, bad)):
                res = guard.check_budget_change(*args)
                self.assertFalse(res["passed"], msg=repr(args))
                self.assertIn("error", res, msg=repr(args))
        res = guard.check_budget_change(100, 110, 500, target_cpa=float("nan"))
        self.assertFalse(res["passed"])
        self.assertIn("error", res)

    def test_string_numbers_are_parsed_not_crashed(self) -> None:
        self.assertTrue(guard.check_budget_change("100", "110", "500")["passed"])

    def test_cli_exit_codes(self) -> None:
        ok = run_tool_inproc("spend-guard.py", "budget", "--current", "100", "--proposed", "120", "--max-cap", "200")
        blocked = run_tool_inproc("spend-guard.py", "budget", "--current", "100", "--proposed", "121", "--max-cap", "200")
        invalid = run_tool_inproc("spend-guard.py", "budget", "--current", "nan", "--proposed", "120")
        self.assertEqual((ok.returncode, blocked.returncode, invalid.returncode), (0, 1, 2))


class TrackingAndCopyBoundaryTests(unittest.TestCase):
    def test_emq_bounds(self) -> None:
        for bad in (-0.1, 10.1, float("nan")):
            self.assertIn("error", guard.check_tracking_setup(True, True, emq_score=bad), msg=str(bad))
        self.assertTrue(guard.check_tracking_setup(True, True, emq_score=0.0)["passed"])
        self.assertTrue(guard.check_tracking_setup(True, True, emq_score=10.0)["passed"])
        self.assertEqual(guard.check_tracking_setup(True, True, emq_score=6.0)["warnings"], [])
        self.assertEqual(len(guard.check_tracking_setup(True, True, emq_score=5.9)["warnings"]), 1)

    def test_dedup_and_hashing_rules(self) -> None:
        self.assertFalse(guard.check_tracking_setup(False, False)["passed"])
        self.assertFalse(guard.check_tracking_setup(True, True, event_id_present=False)["passed"])
        self.assertTrue(guard.check_tracking_setup(True, False, event_id_present=False)["passed"])
        self.assertFalse(guard.check_tracking_setup(False, True, user_data_hashed=False)["passed"])

    def test_telegram_160_char_boundary(self) -> None:
        self.assertTrue(guard.check_ad_copy("telegram", "a" * 160)["passed"])
        self.assertFalse(guard.check_ad_copy("telegram", "a" * 161)["passed"])
        self.assertTrue(guard.check_ad_copy("tg", "")["passed"] in (True, False))  # empty text must not crash


class ChangePacketTextTests(unittest.TestCase):
    def test_empty_and_garbage_packets_fail_closed(self) -> None:
        for content in ("", "   ", "{not json", "[]", "null"):
            res = guard.check_change_packet(content)
            self.assertFalse(res["passed"], msg=repr(content))

    def test_missing_rollback_or_stop_loss_blocks(self) -> None:
        self.assertFalse(guard.check_change_packet("baseline joriy; xavf past; stop-loss: agar cpa oshsa")["passed"])
        self.assertFalse(guard.check_change_packet("baseline joriy; xavf past; rollback: qaytarish")["passed"])
        self.assertTrue(guard.check_change_packet("baseline joriy; xavf past; rollback; stop-loss")["passed"])


class GatePacketBoundaryTests(unittest.TestCase):
    def v(self, packet: dict, ids=frozenset({"42"}), tool=TOOL) -> list[str]:
        return sg.validate_packet(packet, tool, set(ids), NOW)

    def test_valid_packet_has_no_reasons(self) -> None:
        self.assertEqual(self.v(pk()), [])

    def test_age_boundary_24h(self) -> None:
        at = lambda delta: pk(approved_at=(NOW - delta).isoformat())  # noqa: E731
        self.assertEqual(self.v(at(dt.timedelta(hours=24))), [])
        self.assertTrue(self.v(at(dt.timedelta(hours=24, seconds=1))))

    def test_future_skew_boundary_5_minutes(self) -> None:
        at = lambda delta: pk(approved_at=(NOW + delta).isoformat())  # noqa: E731
        self.assertEqual(self.v(at(dt.timedelta(minutes=5))), [])
        self.assertTrue(self.v(at(dt.timedelta(minutes=5, seconds=1))))

    def test_timestamp_variants(self) -> None:
        self.assertEqual(self.v(pk(approved_at="2026-11-19T11:00:00Z")), [])
        self.assertEqual(self.v(pk(approved_at="2026-11-19T11:00:00")), [])  # naive -> UTC
        for bad in ("yesterday", "", None, 123, "2026-13-45"):
            p = pk(approved_at=bad)
            self.assertTrue(self.v(p), msg=repr(bad))  # no created_at fallback -> rejected
        p = pk(approved_at=None, created_at=(NOW - dt.timedelta(hours=1)).isoformat())
        self.assertEqual(self.v(p), [])  # created_at fallback works

    def test_approval_must_be_literal_true(self) -> None:
        for val in (False, None, "true", 1, "yes"):
            self.assertTrue(self.v(pk(approved_by_user=val)), msg=repr(val))

    def test_wrong_schema_or_blank_rollback_or_entity(self) -> None:
        self.assertEqual(self.v(pk(schema="change-packet.v0")), ["schema != change-packet.v1"])
        self.assertTrue(self.v(pk(rollback="   ")))
        self.assertTrue(self.v(pk(entity="")))
        self.assertTrue(self.v(pk(entity=None)))
        self.assertTrue(self.v(pk(entity="999")))  # not the entity being changed

    def test_entity_list_matches_any_member(self) -> None:
        self.assertEqual(self.v(pk(entity=["7", "42"])), [])

    def test_create_tool_matches_by_proposed_tool_only(self) -> None:
        create = "mcp__target__ads_create_campaign"
        self.assertEqual(self.v(pk(entity="new", proposed_tool="ads_create_campaign"), ids=set(), tool=create), [])
        self.assertTrue(self.v(pk(entity="new", proposed_tool="ads_update_entity"), ids=set(), tool=create))

    def test_budget_20_percent_boundary_in_packet(self) -> None:
        self.assertEqual(self.v(pk(proposal={"current_daily": 100, "proposed_daily": 120})), [])
        self.assertTrue(self.v(pk(proposal={"current_daily": 100, "proposed_daily": 120.5})))

    def test_invalid_budget_numbers_in_packet_fail_closed(self) -> None:
        """Regression: nan / zero / string / one-sided budgets used to skip the 20% rule entirely."""
        bad_proposals = [
            {"current_daily": float("nan"), "proposed_daily": 9999},
            {"current_daily": 0, "proposed_daily": 9999},
            {"current_daily": -100, "proposed_daily": 50},
            {"current_daily": 100, "proposed_daily": float("inf")},
            {"current_daily": "100", "proposed_daily": "9999"},
            {"current_daily": 100},
            {"proposed_daily": 9999},
            {"current_daily": True, "proposed_daily": 9999},
        ]
        for prop in bad_proposals:
            reasons = self.v(pk(proposal=prop))
            self.assertTrue(any(r.startswith("budget:") for r in reasons), msg=f"{prop} -> {reasons}")

    def test_packets_without_budget_fields_are_unaffected(self) -> None:
        self.assertEqual(self.v(pk(proposal={})), [])
        self.assertEqual(self.v(pk(proposal=None)), [])
        self.assertEqual(self.v(pk(proposal={"note": "pause ad"})), [])


class GateEvaluateTests(unittest.TestCase):
    def test_tool_name_classification(self) -> None:
        for t in ("mcp__target__ads_create_ads", "mcp__target__ads_update_entity", "ads_activate_entity",
                  "mcp__x__ads_pixel_event_delete", "mcp__g__assets_upload"):
            self.assertTrue(sg.is_write_tool(t), msg=t)
        for t in ("mcp__target__ads_get_ad_entities", "mcp__target__ads_library_search", "Bash", "", None):
            self.assertFalse(sg.is_write_tool(t), msg=repr(t))  # type: ignore[arg-type]

    def test_entity_ids_collected_from_nested_payloads(self) -> None:
        ids = sg.payload_entity_ids({"entity_id": 1, "ad_ids": [2, "3", {"x": 1}], "nested": {"campaign_id": "4"}, "name": "n"})
        self.assertEqual(ids, {"1", "2", "3", "4"})
        self.assertEqual(sg.payload_entity_ids(None), set())
        self.assertEqual(sg.payload_entity_ids("string"), set())

    def test_unknown_or_missing_payload_fields_fail_safely(self) -> None:
        self.assertEqual(sg.evaluate({}, "strict")["decision"], "allow")  # no tool name -> not a write tool
        res = sg.evaluate({"tool_name": TOOL, "tool_input": None, "cwd": "/nonexistent"}, "strict", now=NOW, clients_dir=None)
        self.assertEqual(res["decision"], "deny")

    def test_corrupt_packet_files_are_ignored_not_trusted(self) -> None:
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            changes = Path(tmp) / "demo" / "changes"
            changes.mkdir(parents=True)
            (changes / "bad.json").write_text("{not json", encoding="utf-8")
            (changes / "list.json").write_text("[1,2]", encoding="utf-8")
            res = sg.evaluate({"tool_name": TOOL, "tool_input": {"entity_id": "42"}}, "strict", now=NOW, clients_dir=Path(tmp))
            self.assertEqual(res["decision"], "deny")
            (changes / "good.json").write_text(json.dumps(pk()), encoding="utf-8")
            res = sg.evaluate({"tool_name": TOOL, "tool_input": {"entity_id": "42"}}, "strict", now=NOW, clients_dir=Path(tmp))
            self.assertEqual(res["decision"], "allow")

    def test_standard_asks_strict_denies_minimal_allows(self) -> None:
        payload = {"tool_name": TOOL, "tool_input": {"entity_id": "42"}, "cwd": "/nonexistent"}
        self.assertEqual(sg.evaluate(payload, "standard", now=NOW)["decision"], "ask")
        self.assertEqual(sg.evaluate(payload, "strict", now=NOW)["decision"], "deny")
        self.assertEqual(sg.evaluate(payload, "minimal", now=NOW)["decision"], "allow")

    def test_hook_output_none_for_allow(self) -> None:
        self.assertIsNone(sg.hook_output({"decision": "allow", "reason": "x"}))
        self.assertEqual(sg.hook_output({"decision": "deny", "reason": "r"})["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
