"""VaultAuditTests, CharterBaselineAndGateTests, AiAdsSyncAndVaultAuditCITests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from tests._helpers import VAULT, run_tool_inproc as _run_tool_inproc

import catalog  # noqa: E402



class VaultAuditTests(unittest.TestCase):
    def test_vault_audit_runs(self) -> None:
        proc = _run_tool_inproc("vault-audit.py", str(VAULT))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("JAMI MUAMMO", proc.stdout)


class CharterBaselineAndGateTests(unittest.TestCase):
    """70-charter-baseline, vault-audit --gate va hook pre:guard."""

    def test_charter_baseline_rule_exists(self) -> None:
        rule = VAULT / "rules" / "70-charter-baseline.md"
        self.assertTrue(rule.is_file())
        text = rule.read_text(encoding="utf-8")
        self.assertIn("Prompt Defense Baseline", text)
        self.assertIn("Zero Findings", text)

    def test_all_35_agents_have_skills_attached(self) -> None:
        import importlib
        ss = importlib.import_module("skill-search")
        agents = ss.load_agents()
        self.assertEqual(len(agents), 38)
        unattached = [name for name, a in agents.items() if not a["skills"]]
        self.assertEqual(unattached, [], f"Skillsiz qolgan agentlar: {unattached}")

    def test_vault_audit_gate_passes(self) -> None:
        proc = _run_tool_inproc("vault-audit.py", str(VAULT), "--gate")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("JAMI MUAMMO (bilim qatlami): 0", proc.stdout)

    def test_hook_guard_protects_generated_catalog(self) -> None:
        env = dict(**os.environ, TYRION_HOOK_PROFILE="strict")
        proc = subprocess.run(
            [sys.executable, str(VAULT / "hooks" / "tyrion-hook.py"), "guard", "--target", "manifests/catalog.json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("HIMOYA (pre:guard)", proc.stdout)


class AiAdsSyncAndVaultAuditCITests(unittest.TestCase):
    """Tyrion v5.0 — ai-ads Sync & Vault Audit CI Fix Tests (Template syntax vs broken links, LOG.md gate, non-force push)."""

    def test_ci_01_obsidian_template_syntax_allowed_but_real_broken_links_in_templates_caught(self) -> None:
        # 1. Clean vault-audit --gate passes with 0 broken links and 0 dangling template links
        proc_clean = _run_tool_inproc("vault-audit.py", str(VAULT), "--gate")
        self.assertEqual(proc_clean.returncode, 0, proc_clean.stdout)
        self.assertIn("JAMI MUAMMO (bilim qatlami): 0 | xom manbadagi dangling havola: 0", proc_clean.stdout)

        # 2. If a template in templates/ has a REAL broken wikilink (not `<% ... %>` or `{{ ... }}`), vault-audit --gate MUST catch it and exit 1
        bad_tpl = VAULT / "templates" / "_temp_broken_link_test.md"
        try:
            bad_tpl.write_text("# Test Template\n\nValid: [[<% tp.file.cursor(1) %>]]\nBroken: [[haqiqiy-buzilgan-wikilink-xyz-999]]\n", encoding="utf-8")
            proc_bad = _run_tool_inproc("vault-audit.py", str(VAULT), "--gate")
            self.assertEqual(proc_bad.returncode, 1, "Real broken wikilink inside templates/ must fail --gate")
            self.assertIn("templates/_temp_broken_link_test.md: haqiqiy-buzilgan-wikilink-xyz-999", proc_bad.stdout)
            self.assertNotIn("tp.file.cursor(1)", proc_bad.stdout)
        finally:
            if bad_tpl.exists():
                bad_tpl.unlink()

    def test_ci_02_log_md_delivery_gate_handles_2026_10_21_and_detects_unlogged_wiki_updates(self) -> None:
        log_text = (VAULT / "LOG.md").read_text(encoding="utf-8")
        self.assertIn("2026-10-21", log_text)

        # Simulate 3 wiki notes updated on a date missing from LOG.md in a temp vault copy
        with tempfile.TemporaryDirectory() as tmp:
            troot = Path(tmp)
            (troot / "wiki").mkdir()
            (troot / "INDEX.md").write_text("| [[n1]] | [[n2]] | [[n3]] |\n", encoding="utf-8")
            (troot / "CLAUDE.md").write_text("# CLAUDE\n", encoding="utf-8")
            (troot / "LOG.md").write_text("# LOG\n\n| Sana | Nima | Natija |\n|---|---|---|\n| 2026-10-20 | Eski | OK |\n", encoding="utf-8")
            today_iso = datetime.now().date().isoformat()
            for idx_n in (1, 2, 3):
                other = 2 if idx_n == 1 else 1
                third = 3 if idx_n != 3 else 2
                (troot / "wiki" / f"n{idx_n}.md").write_text(
                    f"---\nname: n{idx_n}\ndescription: d\ntags: [a]\nsource: s\nupdated: {today_iso}\n---\n\n[[n{other}]] [[n{third}]]\n",
                    encoding="utf-8",
                )
            proc_fail = _run_tool_inproc("vault-audit.py", str(troot), "--gate")
            self.assertEqual(proc_fail.returncode, 1)
            self.assertIn("Delivery Gate:", proc_fail.stdout)

            # Once today's date is added to LOG.md, --gate passes!
            (troot / "LOG.md").write_text(
                f"# LOG\n\n| Sana | Nima | Natija |\n|---|---|---|\n| {today_iso} | Yangi | OK |\n| 2026-10-20 | Eski | OK |\n",
                encoding="utf-8",
            )
            proc_ok = _run_tool_inproc("vault-audit.py", str(troot), "--gate")
            self.assertEqual(proc_ok.returncode, 0, proc_ok.stdout)

    def test_ci_03_ai_ads_repo_urls_and_no_force_push_in_scripts(self) -> None:
        for rel in ("package.json", "plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            content = (VAULT / rel).read_text(encoding="utf-8")
            self.assertIn("salohiddinayydigital-sudo/ai-ads", content, f"{rel} missing ai-ads URL")

        for script_rel in ("push.sh", "push.ps1"):
            script_txt = (VAULT / script_rel).read_text(encoding="utf-8")
            self.assertIn("salohiddinayydigital-sudo/ai-ads.git", script_txt)
            self.assertNotIn("--force", script_txt, f"{script_rel} must not use git push --force")


if __name__ == "__main__":
    unittest.main()
