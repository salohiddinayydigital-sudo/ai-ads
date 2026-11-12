"""ProductionHardeningTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path



class ProductionHardeningTests(unittest.TestCase):
    """Tyrion v4.1 — Atomic I/O, Secret Redaction, NaN/Inf Guards, Path Traversal & JSON-RPC Edge Cases."""

    def setUp(self) -> None:
        import importlib
        self.tcore = importlib.import_module("tyrion_core")
        self.mcp = importlib.import_module("tyrion-mcp-server")

    def test_redact_secrets_masks_meta_openai_and_telegram_tokens(self) -> None:
        raw = "Failed with token " + "EAA" + "bcdefghijklmnopqrstuvwxyz0123456789" + " and " + "sk-" + "proj1234567890abcdefghijkl"
        cleaned = self.tcore.redact_secrets(raw)
        self.assertNotIn("EAAbcdef", cleaned)
        self.assertNotIn("sk-proj", cleaned)
        self.assertIn("[REDACTED_SECRET]", cleaned)

    def test_safe_float_rejects_nan_infinity_and_negative_bounds(self) -> None:
        self.assertEqual(self.tcore.safe_float("nan", default=12.5), 12.5)
        self.assertEqual(self.tcore.safe_float("inf", default=5.0), 5.0)
        self.assertEqual(self.tcore.safe_float("$1,250.50"), 1250.50)
        with self.assertRaises(ValueError):
            self.tcore.safe_float(-5.0, min_val=0.0, field_name="budget")

    def test_safe_slug_prevents_empty_and_path_traversal(self) -> None:
        self.assertEqual(self.tcore.safe_slug("../../../etc/passwd"), "etc-passwd")
        self.assertEqual(self.tcore.safe_slug("---", fallback="default-client"), "default-client")

    def test_validate_safe_path_blocks_directory_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            safe = self.tcore.validate_safe_path(root / "client-a", allowed_root=root)
            self.assertTrue(str(safe).startswith(str(root.resolve())))
            with self.assertRaises(PermissionError):
                self.tcore.validate_safe_path(root / ".." / "escaped", allowed_root=root)

    def test_sanitize_url_blocks_javascript_and_data_uris(self) -> None:
        with self.assertRaises(ValueError):
            self.tcore.sanitize_url("javascript:alert(1)")
        with self.assertRaises(ValueError):
            self.tcore.sanitize_url("data:text/html,<script>alert(1)</script>")
        self.assertEqual(self.tcore.sanitize_url("https://brand.uz/offer\r\n"), "https://brand.uz/offer")

    def test_atomic_write_json_rejects_nan_and_writes_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "state.json"
            self.tcore.atomic_write_json(target, {"status": "ok", "count": 42})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["count"], 42)
            with self.assertRaises(ValueError):
                self.tcore.atomic_write_json(target, {"bad": float("nan")})

    def test_mcp_server_returns_32700_on_malformed_json(self) -> None:
        resp = self.mcp.process_raw_line("{invalid json")
        self.assertEqual(resp["error"]["code"], -32700)

    def test_mcp_server_returns_32601_on_unknown_method(self) -> None:
        resp = self.mcp.handle_request({"jsonrpc": "2.0", "id": 99, "method": "unknown/method"})
        self.assertEqual(resp["error"]["code"], -32601)

    def test_mcp_server_returns_32602_on_negative_budget(self) -> None:
        resp = self.mcp.handle_request({
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {"name": "tyrion_meta_audience", "arguments": {"niche": "ecom", "daily_budget": -50}},
        })
        self.assertEqual(resp["error"]["code"], -32602)


if __name__ == "__main__":
    unittest.main()
