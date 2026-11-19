"""ChatGPT Ads reference: fayl, manba/unverified belgisi va routerga ta'siri."""

from __future__ import annotations

import importlib
import unittest

from tests._helpers import VAULT

ss = importlib.import_module("skill-search")
REF = VAULT / "skills/audit/references/platforms/chatgpt-ads.md"


class ChatGptAdsTests(unittest.TestCase):
    def test_reference_has_source_and_unverified_marks(self) -> None:
        txt = REF.read_text(encoding="utf-8")
        self.assertIn("https://openai.com/index/new-ways-to-buy-chatgpt-ads", txt)
        self.assertIn("unverified", txt)
        for cid in ("CG01", "CG02", "CG09"):
            self.assertIn(cid, txt)

    def test_reference_declared_in_audit_skill(self) -> None:
        audit = next(s for s in ss.load_skills() if s["name"] == "audit")
        self.assertIn("skills/audit/references/platforms/chatgpt-ads.md", audit["declared_references"])

    def test_triggers_route_to_platform_auditor(self) -> None:
        for q in ("ChatGPT Ads audit", "openai reklama auditi", "реклама в chatgpt аудит"):
            plan = ss.route_task(q, load=False, context_mode="manifest")
            self.assertEqual(plan["primary_agent"], "platform-auditor", q)
            self.assertIn("audit", plan["required_skills"], q)


if __name__ == "__main__":
    unittest.main()
