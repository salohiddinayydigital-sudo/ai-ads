"""Barcha pul/son argumentli CLI asboblar nan/inf/manfiy qiymatni exit 2 bilan rad etadi (tyrion_core yordamchilari)."""

from __future__ import annotations

import argparse
import unittest

from tests._helpers import run_tool_inproc

import tyrion_core as tcore


class CoreHelpersTests(unittest.TestCase):
    def test_require_number(self) -> None:
        self.assertEqual(tcore.require_number("12.5", "x", positive=True), 12.5)
        for bad in (float("nan"), float("inf"), "nan", "abc", None, True):
            with self.assertRaises(tcore.NumberValidationError, msg=repr(bad)):
                tcore.require_number(bad, "x")
        with self.assertRaises(tcore.NumberValidationError):
            tcore.require_number(0, "x", positive=True)
        with self.assertRaises(tcore.NumberValidationError):
            tcore.require_number(-1, "x", non_negative=True)
        self.assertEqual(tcore.require_number(0, "x", non_negative=True), 0.0)
        with self.assertRaises(tcore.NumberValidationError):
            tcore.require_number(11, "x", max_val=10)

    def test_argparse_converters(self) -> None:
        self.assertEqual(tcore.positive_float("3"), 3.0)
        for conv, bad in ((tcore.finite_float, "nan"), (tcore.positive_float, "-1"), (tcore.non_negative_float, "-0.1"), (tcore.finite_float, "inf")):
            with self.assertRaises(argparse.ArgumentTypeError):
                conv(bad)

    def test_exit_code_for_result(self) -> None:
        self.assertEqual(tcore.exit_code_for_result({"passed": True}, gate=True), 0)
        self.assertEqual(tcore.exit_code_for_result({"passed": False}, gate=True), 1)
        self.assertEqual(tcore.exit_code_for_result({"passed": False, "error": "x"}, gate=True), 2)
        self.assertEqual(tcore.exit_code_for_result({"error": "x"}), 2)
        self.assertEqual(tcore.exit_code_for_result({"ok": 1}), 0)


class OtherToolsRejectNonFiniteTests(unittest.TestCase):
    def test_nan_args_exit_2(self) -> None:
        cases = [
            ("meta-audience.py", ["saturation", "--daily-budget", "nan"]),
            ("meta-audience.py", ["architect", "--daily-budget", "-5"]),
            ("creative-matrix.py", ["matrix", "--price", "nan"]),
            ("capi-utm-builder.py", ["capi", "--value", "inf"]),
            ("ad-export-analyzer.py", ["breakdown-effect", "--seg-a-name", "a", "--seg-a-spend", "nan", "--seg-a-conv", "1",
                                       "--seg-b-name", "b", "--seg-b-spend", "1", "--seg-b-conv", "1"]),
        ]
        for script, args in cases:
            proc = run_tool_inproc(script, *args)
            self.assertEqual(proc.returncode, 2, f"{script} {args}: {proc.stderr[-200:]}")


if __name__ == "__main__":
    unittest.main()


class McpNumericTests(unittest.TestCase):
    def test_mcp_tools_reject_nan_instead_of_defaulting(self) -> None:
        import importlib
        mcp = importlib.import_module("tyrion-mcp-server")
        bad_calls = [
            ("tyrion_spend_guard", {"current_daily": 100, "proposed_daily": "nan"}),
            ("tyrion_media_calculator", {"price": "nan", "cogs": 10}),
            ("tyrion_breakdown_effect", {"seg_a_name": "a", "seg_a_spend": "nan", "seg_a_conv": 1,
                                         "seg_b_name": "b", "seg_b_spend": 5, "seg_b_conv": 1}),
            ("tyrion_creative_matrix", {"product": "x", "price": "inf"}),
        ]
        for name, args in bad_calls:
            with self.assertRaises(ValueError, msg=name):
                mcp.call_tool(name, args)
