"""VideoRunTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import ast
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from tests._helpers import run_tool_inproc as _run_tool_inproc



class VideoRunTests(unittest.TestCase):
    """video-run — video ishi uchun ish maydoni (scaffold, dry-run, idempotent)."""

    def _run(self, *args):
        return _run_tool_inproc("video-run.py", *args)

    def test_dry_run_creates_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("new", "--client", "test", "--topic", "demo",
                             "--root", tmp, "--dry-run")
            self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
            self.assertIn("REJA (dry-run)", proc.stdout)
            self.assertEqual(list(Path(tmp).rglob("*.py")), [], "dry-run fayl yozmasligi shart")
            self.assertEqual(list(Path(tmp).rglob("props.json")), [])

    def test_new_creates_standard_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("new", "--client", "dilobar", "--topic", "kuz aksiya", "--root", tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
            base = Path(tmp) / f"{datetime.now():%Y-%m-%d}-dilobar-kuz-aksiya" / "workers" / "video-editor"
            for name in ("props.json", "build.py", "MANIFEST.md", "qa.md"):
                self.assertTrue((base / name).is_file(), f"yetishmayapti: {name}")
            self.assertTrue((base / "assets").is_dir())
            self.assertTrue((base / "renders").is_dir())
            props = json.loads((base / "props.json").read_text(encoding="utf-8"))
            self.assertEqual((props["output"]["width"], props["output"]["height"]), (1080, 1920))

    def test_generated_build_py_is_valid_python(self) -> None:
        """Skelet sintaksis xatosi bilan berilmasligi shart (BOM/escape tuzoqlari)."""
        with tempfile.TemporaryDirectory() as tmp:
            self._run("new", "--client", "test", "--topic", "sintaksis", "--root", tmp)
            build = next(Path(tmp).rglob("build.py"))
            raw = build.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), "build.py BOM'siz bo'lishi shart")
            ast.parse(raw.decode("utf-8"))  # xato bo'lsa test yiqiladi

    def test_existing_files_are_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._run("new", "--client", "test", "--topic", "takror", "--root", tmp)
            base = next(Path(tmp).rglob("build.py")).parent
            marker = base / "props.json"
            marker.write_text('{"custom": true}', encoding="utf-8")
            proc = self._run("new", "--client", "test", "--topic", "takror", "--root", tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
            self.assertEqual(marker.read_text(encoding="utf-8"), '{"custom": true}',
                             "mavjud props.json tegilmasligi shart")

    def test_force_archives_old_skeletons(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._run("new", "--client", "test", "--topic", "force", "--root", tmp)
            base = next(Path(tmp).rglob("build.py")).parent
            marker = base / "props.json"
            marker.write_text('{"custom": true}', encoding="utf-8")
            proc = self._run("new", "--client", "test", "--topic", "force",
                             "--root", tmp, "--force")
            self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
            self.assertTrue(list((base / "_archive").glob("build.py.*")), "eskisi arxivga olinmagan")
            self.assertEqual(marker.read_text(encoding="utf-8"), '{"custom": true}')

    def test_unknown_format_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("new", "--client", "t", "--topic", "t", "--root", tmp,
                             "--format", "21x9")
            self.assertEqual(proc.returncode, 2)

    def test_status_of_missing_run_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("status", "yoq-run", "--root", tmp)
            self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
