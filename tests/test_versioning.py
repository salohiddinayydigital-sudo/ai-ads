"""Versiya va raqamlar uchun yagona manba (VERSION) va drift nazorati."""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from tests._helpers import VAULT

import catalog  # noqa: E402
import doctor  # noqa: E402

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _tmp_repo(tmp: str, files: dict[str, str]) -> Path:
    root = Path(tmp)
    (root / "VERSION").write_text("7.0.0\n", encoding="utf-8")
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


class VersionSourceTests(unittest.TestCase):
    def test_version_file_is_semver(self) -> None:
        self.assertRegex(catalog.read_version(), SEMVER)

    def test_manifests_match_version_file(self) -> None:
        want = catalog.read_version()
        for rel, path in catalog.VERSION_JSON_FIELDS:
            data = json.loads((VAULT / rel).read_text(encoding="utf-8"))
            cur = data
            for key in path:
                cur = cur[key]
            self.assertEqual(cur, want, f"{rel}:{path}")

    def test_repo_has_no_version_drift(self) -> None:
        self.assertEqual(catalog.version_scan(VAULT), [])

    def test_no_stale_hardcoded_strings_remain(self) -> None:
        stale = re.compile(r"(?<![/\w])v5\.[01]\b|(?<![/\w])v6\.0\b|\b62 (ta )?skill|\b26 (ta )?(buyruq|slash)|14 qatlam|15 qatlam")
        exempt_dirs = {".git", "graphify-out", "archive", "tests", "__pycache__", "node_modules"}
        exempt_files = {"CHANGELOG.md", "LOG.md", "catalog.json"}
        offenders = []
        for p in VAULT.rglob("*"):
            if not p.is_file() or exempt_dirs & set(p.relative_to(VAULT).parts) or p.name in exempt_files:
                continue
            if p.suffix.lower() not in {".md", ".py", ".json", ".sh", ".ps1", ".html", ".svg", ".cjs", ".yml", ".txt", ".example"}:
                continue
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if stale.search(line):
                    offenders.append(f"{p.relative_to(VAULT)}:{n}: {line.strip()[:90]}")
        self.assertEqual(offenders, [])


class VersionDriftDetectionTests(unittest.TestCase):
    def test_text_drift_detected_and_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tmp_repo(tmp, {
                "README.md": "# Tyrion v5.0 — OS\n",
                "skills/x/SKILL.md": "run the relevant Tyrion v5.0 deterministic checks\n",
                "tools/studio.html": '<span class="badge">v5.0 ECC Ultimate</span>\n',
                "CHANGELOG.md": "## v5.0 history stays\n",
                "LOG.md": "Tyrion v5.0 old log\n",
            })
            found = catalog.version_scan(root)
            self.assertEqual({f["file"] for f in found}, {"README.md", "skills/x/SKILL.md", "tools/studio.html"})
            catalog.version_sync(root)
            self.assertEqual(catalog.version_scan(root), [])
            self.assertIn("Tyrion v7.0", (root / "README.md").read_text(encoding="utf-8"))
            self.assertIn("v5.0", (root / "CHANGELOG.md").read_text(encoding="utf-8"))
            self.assertIn("v5.0", (root / "LOG.md").read_text(encoding="utf-8"))

    def test_json_manifest_drift_detected_and_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tmp_repo(tmp, {"plugin.json": json.dumps({"version": "6.0.0", "description": "36 agents, 99 skills"})})
            found = catalog.version_scan(root)
            self.assertTrue(any(f["file"] == "plugin.json" for f in found))
            catalog.version_sync(root)
            self.assertEqual(json.loads((root / "plugin.json").read_text())["version"], "7.0.0")

    def test_doctor_flags_future_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tmp_repo(tmp, {"README.md": "Tyrion v6.0 here\n"})
            report = doctor.Report()
            doctor.check_version(report, root=root)
            self.assertEqual(report.rows[-1]["status"], doctor.FAIL)
        report = doctor.Report()
        doctor.check_version(report)
        self.assertEqual(report.rows[-1]["status"], doctor.OK, report.rows[-1])


class StatusOutputTests(unittest.TestCase):
    def test_status_split_adds_up_to_total(self) -> None:
        from tests._helpers import run_tool_inproc
        counts = catalog.scan()["counts"]
        out = run_tool_inproc("tyrion.py", "status").stdout
        m = re.search(r"Skilllar\s*:\s*(\d+) ta \((\d+) platforma \+ (\d+) operator", out)
        self.assertIsNotNone(m, out)
        total, plat, oper = map(int, m.groups())
        self.assertEqual(total, counts["skills"])
        self.assertEqual(plat + oper, total)


if __name__ == "__main__":
    unittest.main()
