""".mcp.json dagi aynan o'sha buyruq bilan haqiqiy stdio handshake — plagin va ombor-loyiha rejimlarida."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests._helpers import VAULT

import doctor  # noqa: E402

HAVE_NODE = shutil.which("node") is not None


@unittest.skipUnless(HAVE_NODE, "node o'rnatilmagan")
class McpHandshakeTests(unittest.TestCase):
    def test_project_mode_without_plugin_root(self) -> None:
        """CLAUDE_PLUGIN_ROOT yo'q, CLAUDE_PROJECT_DIR bor (Claude Code shuni beradi), cwd boshqa joy."""
        with tempfile.TemporaryDirectory() as other_cwd:
            res = doctor.mcp_handshake(VAULT / ".mcp.json", "tyrion-core", env={"CLAUDE_PROJECT_DIR": str(VAULT)}, cwd=Path(other_cwd))
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["tool_count"], 10)

    def test_project_mode_cwd_only(self) -> None:
        """Hech qanday CLAUDE_* o'zgaruvchisiz, cwd = ombor ildizi."""
        res = doctor.mcp_handshake(VAULT / ".mcp.json", "tyrion-core", env={}, cwd=VAULT)
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["tool_count"], 10)

    def test_plugin_mode_with_plugin_root(self) -> None:
        with tempfile.TemporaryDirectory() as other_cwd:
            res = doctor.mcp_handshake(
                VAULT / ".mcp.json", "tyrion-core",
                env={"CLAUDE_PLUGIN_ROOT": str(VAULT), "CLAUDE_PROJECT_DIR": other_cwd}, cwd=Path(other_cwd),
            )
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["tool_count"], 10)

    def test_broken_command_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / ".mcp.json"
            cfg.write_text(json.dumps({"mcpServers": {"tyrion-core": {"command": "node", "args": ["/nonexistent/x.cjs"]}}}), encoding="utf-8")
            res = doctor.mcp_handshake(cfg, "tyrion-core", env={}, cwd=Path(tmp), timeout=8)
            self.assertFalse(res["ok"])
            report = doctor.Report()
            doctor.check_mcp(report, cfg_path=cfg, env={}, cwd=Path(tmp))
        self.assertEqual(report.rows[-1]["status"], doctor.FAIL)

    def test_missing_server_entry_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / ".mcp.json"
            cfg.write_text(json.dumps({"mcpServers": {}}), encoding="utf-8")
            self.assertFalse(doctor.mcp_handshake(cfg, "tyrion-core", env={}, cwd=Path(tmp))["ok"])

    def test_real_repo_doctor_check_ok(self) -> None:
        report = doctor.Report()
        doctor.check_mcp(report)
        self.assertEqual(report.rows[-1]["status"], doctor.OK, report.rows[-1])


if __name__ == "__main__":
    unittest.main()
