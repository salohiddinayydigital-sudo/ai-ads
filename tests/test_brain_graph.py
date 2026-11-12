"""BrainGraphTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from tests._helpers import TOOLS, VAULT



class BrainGraphTests(unittest.TestCase):
    """brain-graph — wikilinklardan deterministik graf (0 token, lahzali)."""

    def test_build_and_stats(self) -> None:
        g_json = VAULT / "graphify-out" / "graph.json"
        g_rep = VAULT / "graphify-out" / "GRAPH_REPORT.md"
        before_json = g_json.read_bytes() if g_json.is_file() else None
        before_rep = g_rep.read_bytes() if g_rep.is_file() else None
        try:
            build = subprocess.run(
                [sys.executable, str(TOOLS / "brain-graph.py"), "build"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            self.assertEqual(build.returncode, 0, build.stderr[-300:])
            self.assertIn("0 token", build.stdout)
            stats = subprocess.run(
                [sys.executable, str(TOOLS / "brain-graph.py"), "stats"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            self.assertEqual(stats.returncode, 0)
            self.assertIn("tugun", stats.stdout)
        finally:
            if before_json is not None:
                g_json.write_bytes(before_json)
            if before_rep is not None:
                g_rep.write_bytes(before_rep)

    def test_graph_has_nodes_and_links(self) -> None:
        graph = VAULT / "graphify-out" / "graph.json"
        self.assertTrue(graph.is_file(), "graph.json yo'q")
        data = json.loads(graph.read_text(encoding="utf-8"))
        self.assertGreater(data["stats"]["nodes"], 50)
        self.assertGreater(data["stats"]["links"], 50)
        self.assertIn("community", data["nodes"][0])


if __name__ == "__main__":
    unittest.main()
