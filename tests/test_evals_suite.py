"""Golden eval suite (`claude plugin eval`): tuzilma, til taqsimoti, graderlar. LLM chaqirmaydi."""

from __future__ import annotations

import re
import unittest
from collections import Counter

from tests._helpers import VAULT

EVALS = VAULT / "evals"
PROMPT_KEYS = {"name", "description", "tags", "plugins", "runs", "model", "max_turns", "timeout_seconds", "allowed_tools", "append_system_prompt", "env"}
GRADER_KEYS = {"type", "weight", "arm", "pattern", "flags", "match", "target", "tool", "input_match", "min", "max", "before", "after",
               "path", "exists", "criteria", "focus", "baseline_file"}
GRADER_TYPES = {"regex", "tool_used", "tool_order", "file_exists", "llm", "baseline"}


def fm(path):
    m = re.match(r"---\n(.*?)\n---\n(.*)", path.read_text(encoding="utf-8"), re.S)
    assert m, f"{path}: frontmatter yo'q"
    return {k: v for k, v in re.findall(r"(?m)^([A-Za-z_]+):\s*(.*)$", m.group(1))}, m.group(2)


CASES = sorted(p.parent for p in EVALS.glob("*/prompt.md"))


class EvalSuiteTests(unittest.TestCase):
    def test_case_count_and_language_mix(self) -> None:
        self.assertGreaterEqual(len(CASES), 25)
        langs = Counter()
        for c in CASES:
            tags, _ = fm(c / "prompt.md")
            langs[re.search(r"lang:([\w-]+)", tags["tags"]).group(1)] += 1
        self.assertGreaterEqual(langs["uz-latn"], 12)
        self.assertGreaterEqual(langs["ru"], 6)
        self.assertGreaterEqual(langs["en"], 5)
        self.assertGreaterEqual(langs["uz-cyrl"], 2)

    def test_frontmatter_keys_are_documented(self) -> None:
        for c in CASES:
            with self.subTest(case=c.name):
                keys, body = fm(c / "prompt.md")
                self.assertLessEqual(set(keys), PROMPT_KEYS)
                self.assertEqual(keys["name"], c.name)
                self.assertTrue(body.strip())
                graders = sorted((c / "graders").glob("*.md"))
                self.assertGreaterEqual(len(graders), 1)
                for g in graders:
                    gk, gb = fm(g)
                    self.assertLessEqual(set(gk), GRADER_KEYS, g)
                    self.assertIn(gk["type"], GRADER_TYPES, g)
                    self.assertTrue(gb.strip(), g)

    def test_mutation_cases_forbid_write_tools(self) -> None:
        muts = [c for c in CASES if c.name.startswith("mutation-")]
        self.assertGreaterEqual(len(muts), 2)
        for c in muts:
            g = [fm(p) for p in (c / "graders").glob("*.md")]
            hit = [k for k, _ in g if k["type"] == "tool_used" and k.get("max") == "0" and "ads_" in k["tool"]]
            self.assertTrue(hit, c.name)

    def test_cheap_graders_dominate(self) -> None:
        kinds = Counter(fm(p)[0]["type"] for c in CASES for p in (c / "graders").glob("*.md"))
        self.assertGreater(kinds["regex"] + kinds["tool_used"], kinds["llm"] * 2)

    def test_topics_covered(self) -> None:
        topics = {re.search(r"topic:([\w-]+)", fm(c / "prompt.md")[0]["tags"]).group(1) for c in CASES}
        need = {"meta-strategy", "csv-diagnosis", "lead-quality", "reels-script", "audience", "budget-math", "pulse-explain",
                "experiment", "competitor", "report", "out-of-scope", "mutation"}
        self.assertTrue(need <= topics, need - topics)

    def test_referenced_fixtures_exist(self) -> None:
        for c in CASES:
            for f in re.findall(r"tests/fixtures/[\w./-]+\.\w+", (c / "prompt.md").read_text(encoding="utf-8")):
                self.assertTrue((VAULT / f).is_file(), f"{c.name}: {f}")


if __name__ == "__main__":
    unittest.main()
