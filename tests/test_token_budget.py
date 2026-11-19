"""token-budget.py: o'lchash, darvoza va yashirin buyruqlar."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc




def _mk(root: Path, rel: str, fm: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\n{fm}\n---\nbody\n", encoding="utf-8")


class TokenBudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)
        _mk(self.root, "skills/a/SKILL.md", "name: a\ndescription: " + "x" * 400)
        _mk(self.root, "agents/b.md", "name: b\ndescription: " + "y" * 40)
        _mk(self.root, "commands/c.md", "description: " + "z" * 80)
        _mk(self.root, "commands/d.md", "description: " + "w" * 200 + "\ndisable-model-invocation: true")

    def tearDown(self) -> None:
        self.td.cleanup()

    def _run(self, *a: str):
        return run_tool_inproc("token-budget.py", "--root", str(self.root), *a)

    def test_counts_visible_only(self) -> None:
        p = self._run("--json")
        self.assertEqual(p.returncode, 0)
        rep = json.loads(p.stdout)
        self.assertEqual(rep["total_chars"], 400 + 40 + 80)
        self.assertEqual(rep["total_tokens"], 100 + 10 + 20)
        self.assertEqual(rep["by_kind"]["command"]["count"], 2)
        self.assertEqual(rep["by_kind"]["command"]["model_visible"], 1)
        self.assertEqual(rep["over_300_chars"], ["skills/a/SKILL.md"])
        self.assertEqual(rep["top"][0]["name"], "a")

    def test_gate(self) -> None:
        self.assertEqual(self._run("--max-tokens", "130").returncode, 0)
        self.assertEqual(self._run("--max-tokens", "129").returncode, 1)

    def test_missing_root(self) -> None:
        p = run_tool_inproc("token-budget.py", "--root", str(self.root / "nope"))
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
