"""HookTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._helpers import TOOLS, VAULT, run_tool_inproc as _run_tool_inproc

import catalog  # noqa: E402



class HookTests(unittest.TestCase):
    """Hook qatlami — deterministik nazorat."""

    def _module(self):
        sys.path.insert(0, str(TOOLS))
        import importlib
        return importlib.import_module("install-hooks")

    def test_vault_path_substitution_has_no_control_chars(self) -> None:
        """Yo'l almashtirilganda TAB kabi belgi paydo bo'lmasligi shart.

        Regressiya: xom JSON matnida almashtirilsa `vault\\tyrion` ichidagi `\\t`
        TAB belgisiga aylanib, hook umuman ishlamay qolardi (dry-run tutgan).
        """
        module = self._module()
        config = module.build_config(VAULT, VAULT)
        commands = [
            hook["command"]
            for group in config["hooks"].values()
            for hook in group[0]["hooks"]
        ]
        self.assertTrue(commands)
        for command in commands:
            self.assertNotIn("\t", command, f"TAB belgisi: {command!r}")
            self.assertIn(str(VAULT), command)

    def test_merge_is_idempotent(self) -> None:
        module = self._module()
        canonical = module.build_config(VAULT, VAULT)
        settings: dict = {}
        settings, first = module.merge(settings, canonical)
        self.assertTrue(first, "birinchi merge hech narsa qo'shmadi")
        _settings, second = module.merge(settings, canonical)
        self.assertEqual(second, [], "ikkinchi merge takror qo'shdi")

    def test_merge_preserves_existing_hooks(self) -> None:
        module = self._module()
        canonical = module.build_config(VAULT, VAULT)
        existing = {"hooks": {"SessionStart": [
            {"matcher": "", "hooks": [{"type": "command", "command": "echo boshqa-hook"}]}
        ]}}
        merged, _added = module.merge(existing, canonical)
        commands = [
            h["command"] for g in merged["hooks"]["SessionStart"] for h in g["hooks"]
        ]
        self.assertIn("echo boshqa-hook", commands, "mavjud hook o'chib ketdi")

    def test_command_sync_is_byte_exact_and_idempotent(self) -> None:
        """Buyruq nusxasi bayt-aniq bo'lishi va ikkinchi urinishda tegmasligi shart.

        Regressiya: `write_text` Windows'da satr oxirini o'zgartirib, nusxa
        "drift" bo'lib ko'rinardi.
        """
        module = self._module()
        module.sync_commands(VAULT, dry_run=False)
        source = VAULT / "commands"
        for path in sorted(source.glob("*.md")):
            mirror = VAULT / ".claude" / "commands" / path.name
            self.assertTrue(mirror.is_file(), f"nusxa yo'q: {path.name}")
            self.assertEqual(path.read_bytes(), mirror.read_bytes(), f"baytlar farqli: {path.name}")
        self.assertEqual(module.sync_commands(VAULT, dry_run=False), [],
                         "ikkinchi sinxronizatsiya keraksiz nusxa qildi")

    def test_brief_and_ingest_run(self) -> None:
        g_json = VAULT / "graphify-out" / "graph.json"
        g_rep = VAULT / "graphify-out" / "GRAPH_REPORT.md"
        c_json = catalog.MANIFEST
        saved = {
            f: f.read_bytes() for f in (g_json, g_rep, c_json) if f.is_file()
        }
        try:
            cases = {
                "brief": [],
                "ingest": ["--warn-only", "--quiet"],
            }
            for mode, flags in cases.items():
                proc = subprocess.run(
                    [sys.executable, str(VAULT / "hooks" / "tyrion-hook.py"), mode, *flags],
                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
                )
                self.assertEqual(proc.returncode, 0, f"{mode}: {proc.stderr[-300:]}")
        finally:
            for f, raw in saved.items():
                f.write_bytes(raw)


class InstallHooksDirectTests(unittest.TestCase):
    """install-hooks.py main()/detect_python_launcher()/sync_commands() ning to'g'ridan-to'g'ri testlari (haqiqiy .claude/ ga tegmaydi)."""

    def setUp(self) -> None:
        self.ih = importlib.import_module("install-hooks")

    def _run(self, *args: str):
        return _run_tool_inproc("install-hooks.py", *args)

    def test_fresh_install_writes_settings_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("--target", tmp, "--no-commands")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            settings = json.loads((Path(tmp) / ".claude" / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(set(settings["hooks"]), {"SessionStart", "PreToolUse", "PostToolUse", "Stop"})
            again = self._run("--target", tmp, "--no-commands")
            self.assertEqual(again.returncode, 0)
            self.assertIn("allaqachon joyida", again.stdout)
            self.assertEqual(json.loads((Path(tmp) / ".claude" / "settings.json").read_text(encoding="utf-8")), settings)

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("--target", tmp, "--dry-run")
            self.assertEqual(proc.returncode, 0)
            self.assertIn("--dry-run", proc.stdout)
            self.assertFalse((Path(tmp) / ".claude" / "settings.json").exists())
            self.assertFalse((Path(tmp) / ".claude" / "commands").exists())

    def test_existing_settings_are_backed_up_and_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sp = Path(tmp) / ".claude" / "settings.json"
            sp.parent.mkdir(parents=True)
            sp.write_text(json.dumps({"model": "x", "hooks": {"Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "echo mine"}]}]}}), encoding="utf-8")
            self.assertEqual(self._run("--target", tmp, "--no-commands").returncode, 0)
            self.assertTrue(sp.with_suffix(".json.bak").is_file())
            merged = json.loads(sp.read_text(encoding="utf-8"))
            self.assertEqual(merged["model"], "x")
            commands = [h["command"] for g in merged["hooks"]["Stop"] for h in g["hooks"]]
            self.assertIn("echo mine", commands)
            self.assertTrue(any("run-hook.cjs" in c for c in commands))

    def test_corrupt_settings_json_is_refused_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sp = Path(tmp) / ".claude" / "settings.json"
            sp.parent.mkdir(parents=True)
            sp.write_text("{not json", encoding="utf-8")
            proc = self._run("--target", tmp, "--no-commands")
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(sp.read_text(encoding="utf-8"), "{not json")

    def test_commands_are_copied_and_no_commands_flag_skips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._run("--target", tmp, "--no-commands")
            self.assertFalse((Path(tmp) / ".claude" / "commands").exists())
            changed = self.ih.sync_commands(Path(tmp), dry_run=False)
            self.assertEqual(len(changed), len(list((VAULT / "commands").glob("*.md"))))
            self.assertEqual(self.ih.sync_commands(Path(tmp), dry_run=False), [])

    def test_python_launcher_detection_by_platform(self) -> None:
        from unittest import mock
        with mock.patch.object(self.ih.sys, "platform", "win32"), mock.patch.object(self.ih.shutil, "which", lambda n: "x" if n == "py" else None):
            self.assertEqual(self.ih.detect_python_launcher(), "py -3")
        with mock.patch.object(self.ih.sys, "platform", "win32"), mock.patch.object(self.ih.shutil, "which", lambda n: None):
            self.assertEqual(self.ih.detect_python_launcher(), "python")
        with mock.patch.object(self.ih.sys, "platform", "linux"), mock.patch.object(self.ih.shutil, "which", lambda n: "x" if n == "python3" else None):
            self.assertEqual(self.ih.detect_python_launcher(), "python3")
        with mock.patch.object(self.ih.sys, "platform", "linux"), mock.patch.object(self.ih.shutil, "which", lambda n: None):
            self.assertEqual(self.ih.detect_python_launcher(), "py -3")

    def test_substitute_is_applied_after_parsing(self) -> None:
        out = self.ih._substitute({"a": ["${X}/y", {"b": "${X}"}], "n": 3}, "${X}", "C:\\tyrion\\vault")
        self.assertEqual(out["a"][0], "C:\\tyrion\\vault/y")
        self.assertNotIn("\t", out["a"][1]["b"].replace("\\t", ""))
        self.assertEqual(out["n"], 3)


if __name__ == "__main__":
    unittest.main()
