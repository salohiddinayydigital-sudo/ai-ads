"""Edge-case tests for tools/tyrion_core.py: path guards, secret redaction, numeric parsing, atomic I/O."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests._helpers import VAULT  # noqa: F401  (puts tools/ on sys.path)

import tyrion_core as tcore  # noqa: E402


class PathGuardTests(unittest.TestCase):
    def test_allowed_root_itself_and_children_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(tcore.validate_safe_path(root, root), root.resolve())
            (root / "a").mkdir()
            self.assertEqual(tcore.validate_safe_path(root / "a" / "f.txt", root), (root / "a" / "f.txt").resolve())

    def test_dotdot_escape_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "inner"
            root.mkdir()
            with self.assertRaises(PermissionError):
                tcore.validate_safe_path(root / ".." / "outside.txt", root)

    def test_sibling_with_common_prefix_is_blocked(self) -> None:
        """`/x/inner-evil` must not be treated as inside `/x/inner` (naive startswith bug)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "inner"
            evil = Path(tmp) / "inner-evil"
            root.mkdir()
            evil.mkdir()
            with self.assertRaises(PermissionError):
                tcore.validate_safe_path(evil / "f.txt", root)

    @unittest.skipUnless(hasattr(os, "symlink") and os.name != "nt", "symlinks need POSIX")
    def test_symlink_escape_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "inner"
            outside = Path(tmp) / "outside"
            root.mkdir()
            outside.mkdir()
            (root / "link").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(PermissionError):
                tcore.validate_safe_path(root / "link" / "secret.txt", root)

    def test_no_root_means_resolve_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(tcore.validate_safe_path(Path(tmp) / "x"), (Path(tmp) / "x").resolve())

    def test_safe_slug_edge_cases(self) -> None:
        self.assertEqual(tcore.safe_slug(""), "unnamed-project")
        self.assertEqual(tcore.safe_slug(None), "unnamed-project")  # type: ignore[arg-type]
        self.assertEqual(tcore.safe_slug("..\\..\\Windows\\System32"), "windows-system32")
        self.assertEqual(tcore.safe_slug("A" * 200), "a" * 48)
        self.assertNotIn("/", tcore.safe_slug("a/b/../c"))
        self.assertNotIn(".", tcore.safe_slug("a.b"))

    def test_sanitize_url_edge_cases(self) -> None:
        self.assertEqual(tcore.sanitize_url(" https://example.com/a?b=1 "), "https://example.com/a?b=1")
        # CR/LF/TAB are stripped so header injection is impossible.
        self.assertEqual(tcore.sanitize_url("https://exa\r\nmple.com/x"), "https://example.com/x")
        for bad in ("javascript:alert(1)", "data:text/html,x", "file:///etc/passwd", "ftp://x.com", "//example.com", ""):
            with self.assertRaises(ValueError, msg=bad):
                tcore.sanitize_url(bad)
        with self.assertRaises(ValueError):
            tcore.sanitize_url("https://")  # scheme but no host


class SecretRedactionTests(unittest.TestCase):
    def test_empty_and_none(self) -> None:
        self.assertEqual(tcore.redact_secrets(""), "")
        self.assertEqual(tcore.redact_secrets(None), "")  # type: ignore[arg-type]

    def test_all_token_families_redacted(self) -> None:
        tokens = [
            "EAA" + "B" * 30,
            "sk-" + "a1b2c3d4" * 4,
            "AIza" + "x" * 30,
            "123456789:AA" + "y" * 30,
            "ghp_" + "z" * 30,
            "Bearer abcdefghijklmnop123",
        ]
        for tok in tokens:
            out = tcore.redact_secrets(f"error calling api with {tok} failed")
            self.assertNotIn(tok, out)
            self.assertIn("[REDACTED_SECRET]", out)
            self.assertTrue(out.startswith("error calling api with"))

    def test_multiple_secrets_and_non_string_input(self) -> None:
        out = tcore.redact_secrets("a ghp_" + "q" * 25 + " b ghp_" + "r" * 25)
        self.assertEqual(out.count("[REDACTED_SECRET]"), 2)
        self.assertEqual(tcore.redact_secrets(12345), "12345")  # type: ignore[arg-type]

    def test_plain_text_is_untouched(self) -> None:
        text = "Budget 100 -> 115, CPA $12.50, sk-short"
        self.assertEqual(tcore.redact_secrets(text), text)


class NumericParsingTests(unittest.TestCase):
    def test_safe_float_inputs(self) -> None:
        self.assertEqual(tcore.safe_float(None, default=3.0), 3.0)
        self.assertEqual(tcore.safe_float(True, default=3.0), 3.0)  # bool is not a number here
        self.assertEqual(tcore.safe_float("garbage", default=2.0), 2.0)
        self.assertEqual(tcore.safe_float("", default=2.0), 2.0)
        self.assertEqual(tcore.safe_float("12%"), 12.0)
        self.assertEqual(tcore.safe_float(float("-inf"), default=1.0), 1.0)
        self.assertEqual(tcore.safe_float("1e3"), 1000.0)

    def test_safe_float_bounds_inclusive(self) -> None:
        self.assertEqual(tcore.safe_float(5, min_val=5, max_val=5), 5.0)
        with self.assertRaises(ValueError):
            tcore.safe_float(4.999, min_val=5)
        with self.assertRaises(ValueError):
            tcore.safe_float(5.001, max_val=5)

    def test_safe_int_rounding_and_bounds(self) -> None:
        self.assertEqual(tcore.safe_int("7.6"), 8)
        self.assertEqual(tcore.safe_int("nan", default=4), 4)
        self.assertEqual(tcore.safe_int(None, default=9), 9)
        with self.assertRaises(ValueError):
            tcore.safe_int(0, min_val=1, field_name="n")
        with self.assertRaises(ValueError):
            tcore.safe_int(101, max_val=100)

    def test_require_number_rejects_what_safe_float_would_default(self) -> None:
        for bad in (None, True, False, "abc", "", "nan", "NaN", "inf", "-inf", float("nan"), float("inf"), [], {}):
            with self.assertRaises(tcore.NumberValidationError, msg=repr(bad)):
                tcore.require_number(bad, "x")

    def test_require_number_sign_and_range_flags(self) -> None:
        self.assertEqual(tcore.require_number("0", "x", non_negative=True), 0.0)
        with self.assertRaises(tcore.NumberValidationError):
            tcore.require_number(0, "x", positive=True)
        with self.assertRaises(tcore.NumberValidationError):
            tcore.require_number(-0.01, "x", non_negative=True)
        self.assertEqual(tcore.require_number(10, "x", min_val=10, max_val=10), 10.0)
        with self.assertRaises(tcore.NumberValidationError):
            tcore.require_number(10.01, "x", max_val=10)

    def test_exit_code_policy(self) -> None:
        self.assertEqual(tcore.exit_code_for_result({"passed": True}), tcore.EXIT_OK)
        self.assertEqual(tcore.exit_code_for_result({"error": "boom", "passed": True}), tcore.EXIT_VALIDATION)
        self.assertEqual(tcore.exit_code_for_result({"passed": False}), tcore.EXIT_OK)
        self.assertEqual(tcore.exit_code_for_result({"passed": False}, gate=True), tcore.EXIT_GATE_BLOCKED)
        self.assertEqual(tcore.exit_code_for_result({}, gate=True), tcore.EXIT_GATE_BLOCKED)
        self.assertEqual(tcore.exit_code_for_result("not a dict"), tcore.EXIT_OK)

    def test_parse_localized_number_table(self) -> None:
        cases = {
            "1,234.50": 1234.5, "1 234,50": 1234.5, "1.234,50": 1234.5, "12,5": 12.5, "$1,234": 1234.0,
            "45%": 45.0, "1,234": 1234.0, "1.234": 1.234, "0,123": 0.123, "(500)": -500.0, "-12.5": -12.5,
            "1'234'567": 1234567.0, "1,234,567": 1234567.0, "1.234.567": 1234567.0, 7: 7.0, 2.5: 2.5,
        }
        for raw, want in cases.items():
            self.assertAlmostEqual(tcore.parse_localized_number(raw), want, places=6, msg=repr(raw))

    def test_parse_localized_number_invalid_is_none(self) -> None:
        for raw in (None, True, "", "   ", "abc", "-", "--", float("nan"), float("inf")):
            self.assertIsNone(tcore.parse_localized_number(raw), msg=repr(raw))


class AtomicIoTests(unittest.TestCase):
    def test_creates_parent_dirs_and_leaves_no_temp_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "a" / "b" / "state.json"
            tcore.atomic_write_json(target, {"ok": True})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"ok": True})
            self.assertEqual([p.name for p in target.parent.iterdir()], ["state.json"])

    def test_overwrite_replaces_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "f.txt"
            tcore.atomic_write_text(target, "one")
            tcore.atomic_write_text(target, "two")
            self.assertEqual(target.read_text(encoding="utf-8"), "two")

    def test_failed_json_serialisation_keeps_old_file_intact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "state.json"
            tcore.atomic_write_json(target, {"v": 1})
            for bad in ({"v": float("nan")}, {"v": float("inf")}):
                with self.assertRaises(ValueError):
                    tcore.atomic_write_json(target, bad)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"v": 1})
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["state.json"])

    def test_replace_failure_cleans_temp_and_preserves_original(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "f.txt"
            tcore.atomic_write_text(target, "original")
            with mock.patch("tyrion_core.os.replace", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    tcore.atomic_write_text(target, "new")
            self.assertEqual(target.read_text(encoding="utf-8"), "original")
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["f.txt"])

    def test_unicode_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "u.json"
            tcore.atomic_write_json(target, {"t": "Toshkent — reklama ёлка"})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["t"], "Toshkent — reklama ёлка")


class HttpBackoffTests(unittest.TestCase):
    def test_non_http_scheme_rejected_before_any_network(self) -> None:
        with mock.patch("tyrion_core.urllib.request.urlopen") as op:
            with self.assertRaises(ValueError):
                tcore.http_get_json_with_backoff("file:///etc/passwd")
            op.assert_not_called()

    def test_retries_on_503_then_reports_error_without_secrets(self) -> None:
        import urllib.error
        secret = "EAA" + "Z" * 30
        err = urllib.error.HTTPError("https://x.test", 503, f"bad {secret}", {}, None)  # type: ignore[arg-type]
        with mock.patch("tyrion_core.urllib.request.urlopen", side_effect=err) as op, mock.patch("tyrion_core.time.sleep"):
            res = tcore.http_get_json_with_backoff("https://x.test/api", max_retries=2)
        self.assertEqual(op.call_count, 3)
        self.assertEqual(res["error_category"], "SERVER_5XX")
        self.assertEqual(res["retries_attempted"], 2)
        self.assertNotIn(secret, json.dumps(res))

    def test_no_retry_on_401(self) -> None:
        import urllib.error
        err = urllib.error.HTTPError("https://x.test", 401, "unauthorized", {}, None)  # type: ignore[arg-type]
        with mock.patch("tyrion_core.urllib.request.urlopen", side_effect=err) as op, mock.patch("tyrion_core.time.sleep"):
            res = tcore.http_get_json_with_backoff("https://x.test/api")
        self.assertEqual(op.call_count, 1)
        self.assertEqual(res["error_category"], "AUTH_401")

    def test_timeout_is_classified(self) -> None:
        with mock.patch("tyrion_core.urllib.request.urlopen", side_effect=TimeoutError("slow")), mock.patch("tyrion_core.time.sleep"):
            res = tcore.http_get_json_with_backoff("https://x.test/api", max_retries=1)
        self.assertEqual(res["error_category"], "TIMEOUT_ERROR")
        self.assertEqual(res["retries_attempted"], 1)


if __name__ == "__main__":
    unittest.main()
