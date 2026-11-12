"""spend-guard.py: son validatsiyasi, chiqish kodi siyosati (2 = validatsiya, 1 = darvoza bloklandi, 0 = o'tdi)."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc

sg = importlib.import_module("spend-guard")


class SpendGuardNumericValidationTests(unittest.TestCase):
    def _run(self, *args: str):
        return run_tool_inproc("spend-guard.py", *args)

    def test_nan_proposed_is_blocked_with_nonzero_exit(self) -> None:
        proc = self._run("budget", "--current", "100", "--proposed", "nan")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("BLOCKED", proc.stdout + proc.stderr)

    def test_negative_proposed_is_blocked_with_nonzero_exit(self) -> None:
        proc = self._run("budget", "--current", "100", "--proposed", "-5")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("BLOCKED", proc.stdout + proc.stderr)

    def test_inf_and_nan_in_every_numeric_arg(self) -> None:
        for bad in (("--current", "inf"), ("--max-cap", "nan"), ("--target-cpa", "-inf"), ("--current", "0")):
            args = ["budget", "--current", "100", "--proposed", "110"]
            idx = args.index(bad[0]) if bad[0] in args else None
            if idx is not None:
                args[idx + 1] = bad[1]
            else:
                args += list(bad)
            proc = self._run(*args)
            self.assertNotEqual(proc.returncode, 0, bad)

    def test_function_level_rejects_nan_without_passing(self) -> None:
        for proposed in (float("nan"), float("inf"), -5.0, 0.0):
            res = sg.check_budget_change(100.0, proposed)
            self.assertFalse(res["passed"], proposed)
            self.assertTrue(res["errors"], proposed)
        self.assertFalse(sg.check_budget_change(float("nan"), 100.0)["passed"])
        self.assertFalse(sg.check_budget_change(100.0, 110.0, max_daily_cap=float("nan"))["passed"])

    def test_exit_code_policy(self) -> None:
        self.assertEqual(self._run("budget", "--current", "100", "--proposed", "115").returncode, 0)
        self.assertEqual(self._run("budget", "--current", "100", "--proposed", "150").returncode, 1)  # darvoza bloklandi
        self.assertEqual(self._run("budget", "--current", "100", "--proposed", "nan").returncode, 2)  # validatsiya
        self.assertEqual(self._run("packet", "/nonexistent/packet.md").returncode, 2)

    def test_json_output_and_exit_code_match(self) -> None:
        proc = self._run("budget", "--current", "100", "--proposed", "nan", "--json")
        self.assertEqual(proc.returncode, 2)
        data = json.loads(proc.stdout)
        self.assertFalse(data["passed"])
        self.assertTrue(data.get("error"))

    def test_tracking_emq_must_be_in_range(self) -> None:
        self.assertEqual(self._run("tracking", "--pixel", "--capi", "--emq", "nan").returncode, 2)
        self.assertEqual(self._run("tracking", "--pixel", "--capi", "--emq", "11").returncode, 2)
        self.assertEqual(self._run("tracking", "--pixel", "--capi", "--emq", "8").returncode, 0)


class SpendGuardDirectGateTests(unittest.TestCase):
    """Darvozalarning to'g'ridan-to'g'ri testlari (CLI'siz)."""

    def test_budget_exactly_20_pct_passes_and_21_fails(self) -> None:
        self.assertTrue(sg.check_budget_change(100.0, 120.0)["passed"])
        self.assertFalse(sg.check_budget_change(100.0, 121.0)["passed"])

    def test_sharp_decrease_warns_but_passes(self) -> None:
        res = sg.check_budget_change(100.0, 40.0)
        self.assertTrue(res["passed"])
        self.assertTrue(res["warnings"])

    def test_low_budget_vs_target_cpa_warns(self) -> None:
        res = sg.check_budget_change(10.0, 11.0, target_cpa=20.0)
        self.assertTrue(any("50 ta konversiya" in w for w in res["warnings"]))

    def test_meta_copy_banned_phrase_blocks(self) -> None:
        res = sg.check_ad_copy("meta", "Bu 100% kafolat beradi")
        self.assertFalse(res["passed"])

    def test_google_rsa_limits(self) -> None:
        res = sg.check_ad_copy("google", "d" * 91, headline="h" * 31)
        self.assertEqual(len(res["errors"]), 2)

    def test_tracking_requires_some_tool_and_hashing(self) -> None:
        self.assertFalse(sg.check_tracking_setup(False, False)["passed"])
        self.assertFalse(sg.check_tracking_setup(False, True, user_data_hashed=False)["passed"])
        self.assertTrue(sg.check_tracking_setup(True, True, event_id_present=True)["passed"])

    def test_packet_cli_roundtrip(self) -> None:
        good = "Baseline: CPA $15. Xavf: past. Teskari qadam: qaytarish. Stop-loss: CPA > $20 bo'lsa to'xtatish. Operator tasdiqi."
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "packet.md"
            p.write_text(good, encoding="utf-8")
            self.assertEqual(run_tool_inproc("spend-guard.py", "packet", str(p)).returncode, 0)
            p.write_text("Byudjetni oshiramiz", encoding="utf-8")
            self.assertEqual(run_tool_inproc("spend-guard.py", "packet", str(p)).returncode, 1)


if __name__ == "__main__":
    unittest.main()
