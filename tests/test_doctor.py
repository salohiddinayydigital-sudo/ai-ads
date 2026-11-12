"""DoctorTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

from tests._helpers import VAULT, run_tool_inproc as _run_tool_inproc

import catalog  # noqa: E402
import doctor  # noqa: E402



class DoctorTests(unittest.TestCase):
    """Doctor — tizim sog'lig'i."""

    def test_required_files_exist(self) -> None:
        missing = [rel for rel in doctor.REQUIRED if not (VAULT / rel).is_file()]
        self.assertEqual(missing, [], f"majburiy fayllar yo'q: {missing}")

    def test_claim_marker_matches_catalog(self) -> None:
        """AGENTS.md dagi e'lon qilingan raqamlar katalogga mos bo'lishi shart."""
        data = catalog.scan()
        report = doctor.Report()
        doctor.check_claims(report, data)
        row = next(r for r in report.rows if r["check"].startswith("Raqamlar"))
        self.assertEqual(row["status"], doctor.OK, row["detail"])

    def test_all_claim_checks_are_ok(self) -> None:
        """Marker ham, oddiy matndagi raqamlar ham katalogga mos bo'lsin."""
        report = doctor.Report()
        doctor.check_claims(report, catalog.scan())
        rows = [r for r in report.rows if r["check"].startswith("Raqamlar")]
        self.assertGreaterEqual(len(rows), 2, "oddiy matn raqamlari tekshirilmadi")
        for row in rows:
            self.assertNotEqual(row["status"], doctor.FAIL, row["detail"])
            self.assertEqual(row["status"], doctor.OK, f"{row['check']}: {row['detail']}")

    def test_memory_within_limit(self) -> None:
        """memory.md o'zining ixchamlik shartini buzmasin (≤ 90 qator)."""
        report = doctor.Report()
        doctor.check_memory(report)
        row = next(r for r in report.rows if r["check"].startswith("Xotira"))
        self.assertEqual(row["status"], doctor.OK, row["detail"])

    def test_secret_scan_flags_fake_key(self) -> None:
        """Soxta kalit naqshi aniqlanishi kerak (kalit bo'laklab yasalgan — faylda sir yo'q)."""
        fake_key = "sk-" + "abcdefghijklmnopqrstuvwxyz" + "012345"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "leak.json"
            path.write_text('{"key": "%s"}' % fake_key, encoding="utf-8")
            text = path.read_text(encoding="utf-8")
            hits = [label for pattern, label in doctor.SECRET_PATTERNS if re.search(pattern, text)]
            self.assertTrue(hits, "soxta kalit aniqlanmadi")

    def test_run_returns_completed_process(self) -> None:
        proc = doctor.run([sys.executable, "-c", "print('ok')"])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("ok", proc.stdout)

    def test_quick_doctor_exits_cleanly(self) -> None:
        """doctor --quick ishga tushishi va 0/1 qaytarishi kerak (2 emas)."""
        proc = _run_tool_inproc("doctor.py", "--quick", "--json")
        self.assertIn(proc.returncode, (0, 1), f"kutilmagan kod: {proc.returncode}\n{proc.stderr}")
        payload = json.loads(proc.stdout)
        self.assertIn("checks", payload)
        self.assertGreater(len(payload["checks"]), 5)


class LinkCheckTests(unittest.TestCase):
    """doctor.check_links — buzilgan markdown va wikilink havolalar."""

    def _vault(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "docs").mkdir()
        (root / "wiki").mkdir()
        (root / "docs" / "target.md").write_text("ok", encoding="utf-8")
        return root

    def test_broken_md_link_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._vault(tmp)
            (root / "docs" / "a.md").write_text("[x](missing-file.md)", encoding="utf-8")
            self.assertEqual(doctor.find_broken_md_links(root), [("docs/a.md", "missing-file.md")])

    def test_relative_md_link_resolves_from_own_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._vault(tmp)
            (root / "docs" / "a.md").write_text("[x](target.md)", encoding="utf-8")
            self.assertEqual(doctor.find_broken_md_links(root), [])

    def test_code_span_links_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._vault(tmp)
            (root / "docs" / "a.md").write_text("Wikilink namunasi `[[...]]`", encoding="utf-8")
            self.assertEqual(doctor.find_broken_wikilinks(root), [])

    def test_broken_wikilink_detected_and_template_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._vault(tmp)
            (root / "wiki" / "a.md").write_text("[[nomavjud-qayd]]", encoding="utf-8")
            (root / "templates").mkdir()
            (root / "templates" / "t.md").write_text("[[<% tp.file.cursor(1) %>]]", encoding="utf-8")
            self.assertEqual(doctor.find_broken_wikilinks(root), [("wiki/a.md", "nomavjud-qayd")])

    def test_current_vault_links_are_zero(self) -> None:
        self.assertEqual(doctor.find_broken_md_links(VAULT), [])
        self.assertEqual(doctor.find_broken_wikilinks(VAULT), [])

    def test_doctor_links_row_ok(self) -> None:
        report = doctor.Report()
        doctor.check_links(report)
        row = next(r for r in report.rows if r["check"] == "Buzilgan havolalar")
        self.assertEqual(row["status"], doctor.OK, row["detail"])


class CharterHygieneTests(unittest.TestCase):
    """doctor.check_charter_hygiene — nom, MCP naqshi va URL ajratuvchilar."""

    def test_current_vault_clean(self) -> None:
        report = doctor.Report()
        doctor.check_charter_hygiene(report)
        row = next(r for r in report.rows if r["check"] == "Charter gigiyenasi")
        self.assertEqual(row["status"], doctor.OK, row["detail"])

    def test_detects_harness_specific_conductor_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agents").mkdir()
            (root / "agents" / "x.md").write_text(
                "---\nname: x\ntools: Read\n---\n\nSlice assigned by the Claude Ads conductor.\n",
                encoding="utf-8")
            issues = doctor.charter_hygiene_issues(root)
            self.assertTrue(any("Claude Ads conductor" in i for i in issues), issues)

    def test_detects_invalid_mcp_tool_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agents").mkdir()
            (root / "agents" / "x.md").write_text(
                "---\nname: x\ntools: Read, mcp__plugin_tyrion_tyrion-core__tyrion_not_real\n---\n\nbody\n",
                encoding="utf-8")
            issues = doctor.charter_hygiene_issues(root)
            self.assertTrue(any("yaroqsiz MCP" in i for i in issues), issues)

    def test_valid_mcp_tool_name_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agents").mkdir()
            (root / "agents" / "x.md").write_text(
                "---\nname: x\ntools: Read, mcp__plugin_tyrion_tyrion-core__tyrion_media_calculator\n---\n\nbody\n",
                encoding="utf-8")
            self.assertEqual([i for i in doctor.charter_hygiene_issues(root) if "MCP" in i], [])

    def test_detects_double_question_mark_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "u.md").write_text(
                "https://brand.uz/page?utm_source=meta?utm_medium=cpc\n", encoding="utf-8")
            issues = doctor.charter_hygiene_issues(root)
            self.assertTrue(any("'?' ajratuvchi" in i for i in issues), issues)

    def test_ampersand_separator_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "u.md").write_text(
                "https://brand.uz/page?utm_source=meta&utm_medium=cpc\n", encoding="utf-8")
            self.assertEqual(doctor.charter_hygiene_issues(root), [])


if __name__ == "__main__":
    unittest.main()
