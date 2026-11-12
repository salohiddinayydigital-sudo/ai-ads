"""Wiki `source:` / `source_status:` tekshiruvi (vault-audit) va platforma qaydlarining eskirishi (doctor)."""

from __future__ import annotations

import importlib
import re
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from tests._helpers import VAULT, run_tool_inproc

import doctor  # noqa: E402

va = importlib.import_module("vault-audit")

NOTE = """---
name: {name}
description: test
tags: [{tags}]
source: {source}
{status}updated: {updated}
---

# {name}

[[a]] va [[b]]
"""


def _vault(tmp: str, source: str, status: str = "", tags: str = "local", updated: str | None = None) -> Path:
    root = Path(tmp)
    (root / "wiki").mkdir()
    (root / "docs").mkdir()
    (root / "docs" / "ref.md").write_text("ok", encoding="utf-8")
    upd = updated or date.today().isoformat()
    for name, other in (("a", "b"), ("b", "a")):
        (root / "wiki" / f"{name}.md").write_text(
            NOTE.format(name=name, tags=tags, source=source if name == "a" else "docs/ref.md", status=(status if name == "a" else "source_status: verified\n"),
                        updated=upd), encoding="utf-8")
    (root / "INDEX.md").write_text("a b", encoding="utf-8")
    (root / "LOG.md").write_text("", encoding="utf-8")
    return root


def _audit(root: Path) -> str:
    return run_tool_inproc("vault-audit.py", str(root)).stdout


class SourceAuditTests(unittest.TestCase):
    def test_classify_source(self) -> None:
        c = va.classify_source('"vedio bilimlar/youtubedagilar/X Y.md (https://www.youtube.com/watch?v=abc)"', VAULT)
        self.assertEqual(c["urls"], ["https://www.youtube.com/watch?v=abc"])
        self.assertEqual(len(c["missing"]), 1)
        c = va.classify_source("tools/meta-audience.py + wiki/meta-kampaniya-tuzilmalari.md (2026-10-18)", VAULT)
        self.assertEqual(c["missing"], [])
        self.assertEqual(len(c["existing"]), 2)
        self.assertEqual(va.classify_source("amaliyot (tyrion vault bilimlari asosida)", VAULT)["local"], [])

    def test_missing_local_source_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _vault(tmp, '"raw/gone/transcript.md"', status="source_status: verified\n")
            self.assertIn("MANBA YO'Q", _audit(root))
            self.assertRegex(_audit(root), r"JAMI MUAMMO \(bilim qatlami\): [1-9]")

    def test_unverified_status_acknowledges_missing_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _vault(tmp, '"raw/gone/transcript.md"', status="source_status: unverified\n")
            self.assertIn("JAMI MUAMMO (bilim qatlami): 0", _audit(root))

    def test_existing_local_source_ok_and_invalid_status_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _vault(tmp, "docs/ref.md", status="source_status: verified\n")
            self.assertIn("JAMI MUAMMO (bilim qatlami): 0", _audit(root))
        with tempfile.TemporaryDirectory() as tmp:
            root = _vault(tmp, "docs/ref.md", status="source_status: maybe\n")
            self.assertIn("MANBA HOLATI", _audit(root))
            self.assertRegex(_audit(root), r"JAMI MUAMMO \(bilim qatlami\): [1-9]")

    def test_missing_status_with_dead_path_flagged_but_not_with_existing_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _vault(tmp, '"raw/gone.md"', status="")
            self.assertIn("MANBA YO'Q", _audit(root))
        with tempfile.TemporaryDirectory() as tmp:
            root = _vault(tmp, "docs/ref.md", status="")
            self.assertIn("JAMI MUAMMO (bilim qatlami): 0", _audit(root))

    def test_summary_counts_printed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _vault(tmp, "docs/ref.md", status="source_status: verified\n")
            self.assertRegex(_audit(root), r"MANBA HOLATI SANOG'I: verified=2")


class RepoSourceTests(unittest.TestCase):
    def test_every_note_has_valid_status_and_no_dead_unacknowledged_paths(self) -> None:
        counts = {"verified": 0, "url_cited": 0, "unverified": 0}
        for p in sorted((VAULT / "wiki").glob("*.md")):
            text = p.read_text(encoding="utf-8")
            status = re.search(r"(?m)^source_status:\s*(\S+)\s*$", text)
            self.assertIsNotNone(status, p.name)
            self.assertIn(status.group(1), counts, p.name)
            counts[status.group(1)] += 1
            src = re.search(r"(?m)^source:\s*(.*)$", text).group(1)
            if status.group(1) != "unverified":
                self.assertEqual(va.classify_source(src, VAULT)["missing"], [], p.name)
        self.assertEqual(sum(counts.values()), 100)

    def test_no_invented_urls(self) -> None:
        """URL'lar faqat ilgari qaydda bo'lgan YouTube havolalari yoki tekshirilgan rasmiy manbalar bo'lishi mumkin."""
        for p in sorted((VAULT / "wiki").glob("*.md")):
            src = re.search(r"(?m)^source:\s*(.*)$", p.read_text(encoding="utf-8")).group(1)
            for url in re.findall(r"https?://[^\s)\"']+", src):
                self.assertTrue(url.startswith("https://www.youtube.com/watch?v="), f"{p.name}: kutilmagan URL {url}")


class FreshnessTests(unittest.TestCase):
    def test_old_platform_note_warns(self) -> None:
        old = (date.today() - timedelta(days=400)).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            root = _vault(tmp, "docs/ref.md", status="source_status: verified\n", tags="meta-ads, api", updated=old)
            report = doctor.Report()
            doctor.check_wiki_freshness(report, root=root, max_age_days=180)
        self.assertEqual(report.rows[-1]["status"], doctor.WARN)
        self.assertIn("a.md", report.rows[-1]["detail"])

    def test_old_non_platform_and_fresh_notes_do_not_warn(self) -> None:
        old = (date.today() - timedelta(days=400)).isoformat()
        for tags, upd in (("sop, kopirayting", old), ("meta-ads", date.today().isoformat())):
            with tempfile.TemporaryDirectory() as tmp:
                root = _vault(tmp, "docs/ref.md", status="source_status: verified\n", tags=tags, updated=upd)
                report = doctor.Report()
                doctor.check_wiki_freshness(report, root=root, max_age_days=180)
            self.assertEqual(report.rows[-1]["status"], doctor.OK, (tags, upd))

    def test_real_vault_not_stale(self) -> None:
        report = doctor.Report()
        doctor.check_wiki_freshness(report)
        self.assertEqual(report.rows[-1]["status"], doctor.OK, report.rows[-1])


if __name__ == "__main__":
    unittest.main()
