"""Jarayon ichidagi (in-proc) testlar: coverage_gate.py subprocess kodini o'lchamaydi, shuning uchun hook/CLI yo'llari shu yerda."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

from tests._helpers import VAULT, run_tool_inproc


def _load_hook():
    spec = importlib.util.spec_from_file_location("tyrion_hook_inproc", VAULT / "hooks" / "tyrion-hook.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hook = _load_hook()


def _run(fn, args: Namespace, stdin: str = "", env: dict | None = None):
    out = io.StringIO()
    with mock.patch.dict(os.environ, env or {}, clear=False), mock.patch.object(sys, "stdin", io.StringIO(stdin)), contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        rc = fn(args)
    return rc, out.getvalue()


class HookInProcTests(unittest.TestCase):
    def test_spend_denies_in_strict_and_asks_in_standard(self) -> None:
        payload = json.dumps({"tool_name": "mcp__x__ads_update_entity", "tool_input": {"entity_id": "1"}, "cwd": tempfile.gettempdir()})
        with tempfile.TemporaryDirectory() as td:
            for profile, want in (("strict", "deny"), ("standard", "ask")):
                rc, out = _run(hook.cmd_spend, Namespace(), payload, {"TYRION_HOOK_PROFILE": profile, "TYRION_CLIENTS_DIR": td, "TYRION_DISABLED_HOOKS": ""})
                self.assertEqual(rc, 0)
                self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], want)

    def test_spend_passes_read_tools_and_respects_disable(self) -> None:
        rc, out = _run(hook.cmd_spend, Namespace(), json.dumps({"tool_name": "mcp__x__ads_get_ad_entities"}), {"TYRION_HOOK_PROFILE": "strict", "TYRION_DISABLED_HOOKS": ""})
        self.assertEqual((rc, out), (0, ""))
        rc, out = _run(hook.cmd_spend, Namespace(), json.dumps({"tool_name": "mcp__x__ads_update_entity"}), {"TYRION_DISABLED_HOOKS": "pre:spend"})
        self.assertEqual((rc, out), (0, ""))

    def test_guard_blocks_secret_files_in_strict(self) -> None:
        args = Namespace(target=".env", warn_only=True, quiet=True)
        rc, _ = _run(hook.cmd_guard, args, "", {"TYRION_HOOK_PROFILE": "strict", "TYRION_DISABLED_HOOKS": ""})
        self.assertEqual(rc, 2)
        rc, _ = _run(hook.cmd_guard, Namespace(target="notes.md", warn_only=True, quiet=True), "", {"TYRION_HOOK_PROFILE": "standard", "TYRION_DISABLED_HOOKS": ""})
        self.assertEqual(rc, 0)

    def test_brief_runs(self) -> None:
        rc, out = _run(hook.cmd_brief, Namespace(), "", {"TYRION_DISABLED_HOOKS": ""})
        self.assertEqual(rc, 0)


class CliInProcTests(unittest.TestCase):
    def test_brain_graph_stats(self) -> None:
        p = run_tool_inproc("brain-graph.py", "stats")
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_tyrion_demo_inproc(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = run_tool_inproc("tyrion.py", "demo", "--out", td)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertTrue((Path(td) / "demo-brand-report.html").is_file())

    def test_tyrion_unknown_command(self) -> None:
        self.assertEqual(run_tool_inproc("tyrion.py", "nope").returncode, 2)

    def test_token_budget_and_spend_gate_main(self) -> None:
        self.assertEqual(run_tool_inproc("token-budget.py", "--max-tokens", "3500").returncode, 0)
        with mock.patch.object(sys, "stdin", io.StringIO("{}")):
            self.assertEqual(run_tool_inproc("spend_gate.py").returncode, 0)


if __name__ == "__main__":
    unittest.main()
