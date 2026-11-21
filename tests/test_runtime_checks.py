"""Runtime/packaging standardisation: doctor runtime check, pyproject/package.json metadata, PyYAML-free fallback."""

from __future__ import annotations

import importlib
import json
import tempfile
import re
import unittest
from pathlib import Path
from unittest import mock

from tests._helpers import VAULT

try:  # tomllib is 3.11+; the project also supports 3.10
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

import doctor  # noqa: E402


def _rows(report: "doctor.Report") -> dict[str, dict]:
    return {r["check"]: r for r in report.rows}


class DoctorRuntimeTests(unittest.TestCase):
    def run_check(self, py=(3, 12, 1), node_out="v20.11.0\n", node_present=True) -> dict[str, dict]:
        report = doctor.Report()
        fake = mock.Mock(stdout=node_out)
        with mock.patch.object(doctor.sys, "version_info", py + ("final", 0)), \
                mock.patch.object(doctor.shutil, "which", return_value="/usr/bin/node" if node_present else None), \
                mock.patch.object(doctor, "run", return_value=fake):
            doctor.check_runtime(report)
        return _rows(report)

    def test_supported_versions_are_ok(self) -> None:
        for py in ((3, 10, 0), (3, 11, 9), (3, 12, 1), (3, 13, 18)):
            rows = self.run_check(py=py)
            self.assertEqual(rows["Python versiyasi"]["status"], doctor.OK, msg=str(py))
        self.assertEqual(self.run_check()["Node versiyasi"]["status"], doctor.OK)

    def test_python_below_310_fails_and_314_warns(self) -> None:
        self.assertEqual(self.run_check(py=(3, 9, 18))["Python versiyasi"]["status"], doctor.FAIL)
        self.assertEqual(self.run_check(py=(3, 14, 0))["Python versiyasi"]["status"], doctor.WARN)

    def test_node_boundaries(self) -> None:
        self.assertEqual(self.run_check(node_out="v18.0.0")["Node versiyasi"]["status"], doctor.OK)
        self.assertEqual(self.run_check(node_out="v17.9.1")["Node versiyasi"]["status"], doctor.FAIL)
        self.assertEqual(self.run_check(node_out="v22.23.5\n")["Node versiyasi"]["status"], doctor.OK)

    def test_missing_or_garbled_node_only_warns(self) -> None:
        self.assertEqual(self.run_check(node_present=False)["Node versiyasi"]["status"], doctor.WARN)
        self.assertEqual(self.run_check(node_out="not-a-version")["Node versiyasi"]["status"], doctor.WARN)
        self.assertEqual(self.run_check(node_out="")["Node versiyasi"]["status"], doctor.WARN)

    def test_parse_node_version(self) -> None:
        self.assertEqual(doctor._parse_node_version("v18.19.1\n"), (18, 19, 1))
        self.assertEqual(doctor._parse_node_version("20.0.0"), (20, 0, 0))
        self.assertIsNone(doctor._parse_node_version("v20"))
        self.assertIsNone(doctor._parse_node_version(None))  # type: ignore[arg-type]


class PackagingMetadataTests(unittest.TestCase):
    def test_pyproject_is_zero_dependency_and_in_sync(self) -> None:
        text = (VAULT / "pyproject.toml").read_text(encoding="utf-8")
        version = (VAULT / "VERSION").read_text(encoding="utf-8").strip()
        if tomllib is not None:
            proj = tomllib.loads(text)["project"]
            self.assertEqual(proj["name"], "tyrion-ai")
            self.assertEqual(proj["requires-python"], ">=3.10,<3.14")
            self.assertEqual(proj["dependencies"], [])
            self.assertEqual(proj["version"], version)
        else:  # Python 3.10: no TOML parser in the stdlib, check the literal lines
            self.assertRegex(text, r'(?m)^name = "tyrion-ai"$')
            self.assertRegex(text, r'(?m)^requires-python = ">=3.10,<3.14"$')
            self.assertRegex(text, r'(?m)^dependencies = \[\]$')
            self.assertRegex(text, rf'(?m)^version = "{re.escape(version)}"$')

    def test_package_json_engines_and_scripts_preserved(self) -> None:
        pkg = json.loads((VAULT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg["engines"], {"node": ">=18.0.0"})
        for script in ("test", "doctor", "shield", "vault-audit", "skills:check", "catalog:check"):
            self.assertIn(script, pkg["scripts"])
        self.assertEqual(pkg["version"], (VAULT / "VERSION").read_text(encoding="utf-8").strip())


class FrontmatterFallbackTests(unittest.TestCase):
    def test_inline_lists_without_pyyaml(self) -> None:
        ss = importlib.import_module("skill-search")
        text = "---\nname: demo\nrelated_skills: []\ntriggers: [a, 'b']\n---\nbody\n"
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(ss, "yaml", None):
            p = Path(tmp) / "SKILL.md"
            p.write_text(text, encoding="utf-8")
            fm = ss.read_frontmatter(p)
        self.assertEqual(fm["name"], "demo")
        self.assertEqual(fm["related_skills"], [])
        self.assertEqual(fm["triggers"], ["a", "b"])
        self.assertEqual(ss.as_list(fm["related_skills"]), [])


if __name__ == "__main__":
    unittest.main()
