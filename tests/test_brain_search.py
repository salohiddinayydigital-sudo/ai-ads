"""BrainSearchTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import unittest

from tests._helpers import run_tool_inproc as _run_tool_inproc



class BrainSearchTests(unittest.TestCase):
    """brain-search — LLM'siz (deterministik) qidiruv, token tejamkor."""

    def _run(self, *args):
        return _run_tool_inproc("brain-search.py", *args)

    def test_search_finds_known_note(self) -> None:
        proc = self._run("search", "meta katta byudjet scaling", "--top", "3")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        self.assertIn("meta-katta-byudjet-scaling", proc.stdout)

    def test_stats_reports_no_orphans(self) -> None:
        proc = self._run("stats")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        self.assertIn("orphan wiki: 0", proc.stdout)

    def test_show_unknown_returns_error(self) -> None:
        proc = self._run("show", "bu-qayd-mavjud-emas-xyz")
        self.assertEqual(proc.returncode, 1)

    def test_links_of_hub(self) -> None:
        proc = self._run("links", "sop-xarita")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        self.assertIn("chiquvchi", proc.stdout)
        self.assertIn("kiruvchi", proc.stdout)


if __name__ == "__main__":
    unittest.main()
