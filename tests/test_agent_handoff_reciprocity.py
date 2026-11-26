"""Handoff o'zaro mosligi: A agent downstream'da B ni ko'rsatsa, B ning upstream'ida ham A bo'lishi shart."""

from __future__ import annotations

import re
import unittest

from tests._helpers import VAULT

AGENTS = {p.stem: p.read_text(encoding="utf-8") for p in (VAULT / "agents").glob("*.md")}
NAME = re.compile(r"`([a-z]+(?:-[a-z]+)+)`")


def _line(text: str, key: str) -> str:
    m = re.search(rf"- \*\*{key}:\*\*(.*)", text)
    return m.group(1) if m else ""


class HandoffReciprocityTests(unittest.TestCase):
    def test_downstream_agents_list_sender_upstream(self) -> None:
        missing = []
        for a, text in AGENTS.items():
            for b in set(NAME.findall(_line(text, "Downstream"))):
                if b in AGENTS and b != a and a not in _line(AGENTS[b], "Upstream"):
                    missing.append(f"{a} -> {b}")
        self.assertEqual(missing, [], "bir tomonlama handoff: qabul qiluvchi charter upstream'iga yuboruvchini qo'shing")


if __name__ == "__main__":
    unittest.main()
