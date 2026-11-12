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


if __name__ == "__main__":
    unittest.main()
