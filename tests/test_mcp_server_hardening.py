"""Edge-case tests for tools/tyrion-mcp-server.py: malformed JSON-RPC, NaN/Inf, payload cap, timeouts."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import unittest
from unittest import mock

from tests._helpers import TOOLS  # also puts tools/ on sys.path

import tyrion_core as tcore  # noqa: E402

mcp = importlib.import_module("tyrion-mcp-server")


def call(name: str, arguments, req_id=1) -> dict:
    return mcp.handle_request({"jsonrpc": "2.0", "id": req_id, "method": "tools/call", "params": {"name": name, "arguments": arguments}})


class MalformedRpcTests(unittest.TestCase):
    def test_non_object_json_roots_are_invalid_requests(self) -> None:
        for raw in ("[]", "[1,2]", '"str"', "42", "null", "true"):
            resp = mcp.process_raw_line(raw)
            self.assertEqual(resp["error"]["code"], -32600, msg=raw)
            self.assertIsNone(resp["id"])

    def test_truncated_and_garbage_json_is_parse_error(self) -> None:
        for raw in ("{", '{"jsonrpc": "2.0", "id": 1,', "not json", "{'a': 1}", "\x00\x01"):
            resp = mcp.process_raw_line(raw)
            self.assertEqual(resp["error"]["code"], -32700, msg=repr(raw))
            self.assertTrue(resp["error"]["message"].startswith("Parse error"))

    def test_params_must_be_object(self) -> None:
        for bad in (None, [], "x", 5):
            resp = mcp.handle_request({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": bad})
            self.assertEqual(resp["error"]["code"], -32602, msg=repr(bad))
            self.assertEqual(resp["id"], 7)

    def test_tool_arguments_must_be_object(self) -> None:
        for bad in ([], [1], "abc", 3):
            resp = call("tyrion_media_calculator", bad)
            self.assertEqual(resp["error"]["code"], -32602, msg=repr(bad))

    def test_unknown_tool_is_invalid_params_not_crash(self) -> None:
        resp = call("does_not_exist", {})
        self.assertEqual(resp["error"]["code"], -32602)
        self.assertIn("Unknown MCP tool", resp["error"]["message"])

    def test_missing_required_argument_is_32602(self) -> None:
        resp = call("tyrion_breakdown_effect", {})
        self.assertEqual(resp["error"]["code"], -32602)

    def test_notifications_get_no_response(self) -> None:
        self.assertIsNone(mcp.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        self.assertIsNone(mcp.handle_request({"jsonrpc": "2.0", "method": "some/unknown-notification"}))

    def test_unknown_method_with_id_is_32601_and_echoes_id(self) -> None:
        for rid in (0, "abc", 12):
            resp = mcp.handle_request({"jsonrpc": "2.0", "id": rid, "method": "nope"})
            self.assertEqual(resp["error"]["code"], -32601)
            self.assertEqual(resp["id"], rid)

    def test_initialize_and_tools_list_shape(self) -> None:
        init = mcp.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(init["result"]["serverInfo"]["name"], "tyrion-mcp-server")
        tools = mcp.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual(len(tools), 10)
        for t in tools:
            self.assertIn("name", t)
            self.assertEqual(t["inputSchema"]["type"], "object")


class NanInfRejectionTests(unittest.TestCase):
    def test_json_nan_and_infinity_literals_are_rejected_not_defaulted(self) -> None:
        # Python's json.loads accepts bare NaN / Infinity; the tools must still refuse them.
        for lit in ("NaN", "Infinity", "-Infinity"):
            raw = '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"tyrion_spend_guard",' \
                  f'"arguments":{{"current_daily":{lit},"proposed_daily":100}}}}}}'
            resp = mcp.process_raw_line(raw)
            self.assertEqual(resp["error"]["code"], -32602, msg=lit)

    def test_string_nan_inf_rejected_for_every_numeric_tool(self) -> None:
        cases = [
            ("tyrion_spend_guard", {"current_daily": "nan", "proposed_daily": 10}),
            ("tyrion_spend_guard", {"current_daily": 10, "proposed_daily": "inf"}),
            ("tyrion_spend_guard", {"current_daily": 10, "proposed_daily": 11, "max_daily_cap": "inf"}),
            ("tyrion_media_calculator", {"price": "nan", "cogs": 1}),
            ("tyrion_media_calculator", {"price": 10, "cogs": float("inf")}),
            ("tyrion_breakdown_effect", {"seg_a_name": "a", "seg_a_spend": "nan", "seg_a_conv": 1,
                                         "seg_b_name": "b", "seg_b_spend": 1, "seg_b_conv": 1}),
        ]
        for name, args in cases:
            resp = call(name, args)
            self.assertEqual(resp["error"]["code"], -32602, msg=f"{name} {args}")

    def test_zero_and_negative_money_rejected(self) -> None:
        for args in ({"current_daily": 0, "proposed_daily": 10}, {"current_daily": -5, "proposed_daily": 10},
                     {"current_daily": 10, "proposed_daily": 0}):
            self.assertEqual(call("tyrion_spend_guard", args)["error"]["code"], -32602, msg=str(args))

    def test_responses_never_contain_nan_tokens(self) -> None:
        resp = call("tyrion_spend_guard", {"current_daily": 100, "proposed_daily": 110})
        text = resp["result"]["content"][0]["text"]
        json.loads(text, parse_constant=lambda c: self.fail(f"non-finite constant {c} in response"))

    def test_non_finite_tool_output_is_not_serialised(self) -> None:
        with mock.patch.object(mcp, "call_tool", return_value={"x": float("nan")}):
            resp = call("anything", {})
        self.assertIn("error", resp)  # allow_nan=False -> ValueError -> -32602, never "NaN" on the wire
        self.assertNotIn("NaN", json.dumps(resp))


class PayloadCapTests(unittest.TestCase):
    def test_line_just_over_cap_is_rejected(self) -> None:
        raw = "x" * (tcore.MAX_RPC_LINE_BYTES + 1)
        resp = mcp.process_raw_line(raw)
        self.assertEqual(resp["error"]["code"], -32600)
        self.assertIn("1 MB", resp["error"]["message"])

    def test_cap_is_measured_in_bytes_not_characters(self) -> None:
        raw = "я" * (tcore.MAX_RPC_LINE_BYTES // 2 + 1)  # 2 bytes each in UTF-8 -> just over the cap
        self.assertLessEqual(len(raw), tcore.MAX_RPC_LINE_BYTES)
        self.assertEqual(mcp.process_raw_line(raw)["error"]["code"], -32600)

    def test_line_at_cap_is_not_rejected_for_size(self) -> None:
        raw = "x" * tcore.MAX_RPC_LINE_BYTES
        resp = mcp.process_raw_line(raw)
        self.assertEqual(resp["error"]["code"], -32700)  # parsed (and failed) as JSON, not size-rejected

    def test_oversized_line_over_real_stdio_does_not_kill_server(self) -> None:
        big = "x" * (tcore.MAX_RPC_LINE_BYTES + 10)
        ok = json.dumps({"jsonrpc": "2.0", "id": 5, "method": "tools/list"})
        proc = subprocess.run([sys.executable, str(TOOLS / "tyrion-mcp-server.py")], input=big + "\n" + ok + "\n",
                              capture_output=True, text=True, timeout=60)
        lines = [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(lines[0]["error"]["code"], -32600)
        self.assertEqual(lines[1]["id"], 5)
        self.assertIn("tools", lines[1]["result"])

    def test_blank_lines_and_eof_exit_cleanly(self) -> None:
        proc = subprocess.run([sys.executable, str(TOOLS / "tyrion-mcp-server.py")], input="\n\n  \n",
                              capture_output=True, text=True, timeout=60)
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))


class TimeoutAndErrorHandlingTests(unittest.TestCase):
    def test_subprocess_timeout_becomes_clean_rpc_error(self) -> None:
        with mock.patch.object(mcp.subprocess, "run", side_effect=subprocess.TimeoutExpired(cmd="brain-search", timeout=15)):
            resp = call("tyrion_brain_search", {"query": "andromeda"})
        self.assertEqual(resp["error"]["code"], -32000)
        self.assertEqual(resp["id"], 1)

    def test_subprocess_is_invoked_with_a_timeout(self) -> None:
        fake = mock.Mock(stdout="ok\n")
        with mock.patch.object(mcp.subprocess, "run", return_value=fake) as run:
            resp = call("tyrion_brain_search", {"query": "x" * 1000})
        self.assertEqual(run.call_args.kwargs["timeout"], 15)
        self.assertLessEqual(len(run.call_args.args[0][-3]), 200)  # query clipped to 200 chars
        self.assertEqual(json.loads(resp["result"]["content"][0]["text"]), {"output": "ok"})

    def test_empty_query_is_rejected(self) -> None:
        self.assertEqual(call("tyrion_brain_search", {"query": "   "})["error"]["code"], -32602)
        self.assertEqual(call("tyrion_universal_router", {"query": ""})["error"]["code"], -32602)

    def test_unexpected_exception_is_redacted(self) -> None:
        secret = "ghp_" + "k" * 30
        with mock.patch.object(mcp, "call_tool", side_effect=RuntimeError(f"upstream said {secret}")):
            resp = call("x", {})
        self.assertEqual(resp["error"]["code"], -32000)
        self.assertNotIn(secret, resp["error"]["message"])
        self.assertIn("[REDACTED_SECRET]", resp["error"]["message"])

    def test_path_traversal_in_raw_json_path_is_blocked(self) -> None:
        resp = call("tyrion_meta_live_insights", {"from_raw_json": "../../../../etc/passwd"})
        self.assertIn("error", resp)
        self.assertNotIn("result", resp)

    def test_numeric_bounds_on_context_bytes(self) -> None:
        for bad in (0, 10, 5_000_000):
            self.assertEqual(call("tyrion_universal_router", {"query": "meta ads", "max_context_bytes": bad})["error"]["code"],
                             -32602, msg=str(bad))


if __name__ == "__main__":
    unittest.main()
