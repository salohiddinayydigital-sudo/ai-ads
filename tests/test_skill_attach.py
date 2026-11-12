"""SkillAttachTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import re
import subprocess
import sys
import unittest

from tests._helpers import TOOLS, VAULT, run_tool_inproc as _run_tool_inproc



class SkillAttachTests(unittest.TestCase):
    """skill-attach — skill ↔ agent ulash (ikki tomonlama, idempotent, dry-run)."""

    def _run(self, *args):
        return _run_tool_inproc("skill-attach.py", *args)

    def test_list_shows_operator_skills(self) -> None:
        proc = self._run("list")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        self.assertIn("video-editing", proc.stdout)
        self.assertRegex(proc.stdout, r"Operator skill: \d+")

    def test_dry_run_changes_nothing(self) -> None:
        skill = VAULT / "skills" / "copywriting" / "SKILL.md"
        before = skill.read_bytes()
        proc = self._run("set", "copywriting", "--agents", "copy-writer", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        self.assertIn("REJA (dry-run)", proc.stdout)
        self.assertEqual(skill.read_bytes(), before, "dry-run faylni o'zgartirmasligi shart")

    def test_set_is_idempotent(self) -> None:
        skill = VAULT / "skills" / "copywriting" / "SKILL.md"
        proc = self._run("set", "copywriting", "--agents", "copy-writer")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        after = skill.read_bytes()
        proc2 = self._run("set", "copywriting", "--agents", "copy-writer")
        self.assertEqual(proc2.returncode, 0, proc2.stderr[-300:])
        self.assertEqual(skill.read_bytes(), after, "qayta urinish faylni o'zgartirmasligi shart")

    def test_unknown_skill_exits_one(self) -> None:
        proc = self._run("set", "bunday-skill-yoq-xyz", "--agents", "copy-writer")
        self.assertEqual(proc.returncode, 1)

    def test_unknown_agent_exits_one(self) -> None:
        proc = self._run("set", "copywriting", "--agents", "bunday-agent-yoq-xyz")
        self.assertEqual(proc.returncode, 1)

    def test_missing_arguments_exit_two(self) -> None:
        proc = self._run("set", "copywriting")
        self.assertEqual(proc.returncode, 2)

    def test_agent_skills_are_bidirectional(self) -> None:
        """Har ulanish ikki tomonda ham yozilgan bo'lishi shart (check shuni tekshiradi)."""
        proc = self._run("list")
        names = re.findall(r"operator\s+(\S+)\s+→\s+(.+)", proc.stdout)
        listed = {name for name, state in names if state.strip() != "— ulanganmagan"}
        self.assertIn("video-editing", listed)
        check = subprocess.run(
            [sys.executable, str(TOOLS / "skill-search.py"), "check"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(check.returncode, 0, check.stdout[-400:])
        self.assertIn("butun", check.stdout)


if __name__ == "__main__":
    unittest.main()
