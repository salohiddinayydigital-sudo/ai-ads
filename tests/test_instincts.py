"""InstinctsTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import unittest

from tests._helpers import VAULT, run_tool_inproc as _run_tool_inproc



class InstinctsTests(unittest.TestCase):
    """instincts — ECC continuous learning va marketing instinktlari reestri."""

    def _run(self, *args):
        return _run_tool_inproc("instincts.py", *args)

    def test_check_passes(self) -> None:
        proc = self._run("check")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("butun", proc.stdout)

    def test_list_by_domain(self) -> None:
        proc = self._run("list", "--domain", "meta")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("meta-asc-existing-cap-25", proc.stdout)

    def test_add_dry_run_changes_nothing(self) -> None:
        manifest = VAULT / "manifests" / "instincts.json"
        before = manifest.read_bytes()
        proc = self._run(
            "add", "--id", "test-instinct-dry", "--domain", "meta",
            "--trigger", "Sinov holati", "--action", "Sinov qoidasi",
            "--evidence", "wiki/learning-phase-qoidalari.md", "--confidence", "4", "--dry-run"
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(manifest.read_bytes(), before)

    def test_promote_dry_run(self) -> None:
        proc = self._run("promote", "kreativ-ftir-fatigue-radar", "--dry-run")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("REJA (dry-run)", proc.stdout)


if __name__ == "__main__":
    unittest.main()
