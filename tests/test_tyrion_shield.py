"""TyrionShieldTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import json
import unittest

from tests._helpers import run_tool_inproc as _run_tool_inproc



class TyrionShieldTests(unittest.TestCase):
    """tyrion-shield — ECC AgentShield xavfsizlik va governance skaneri."""

    def test_shield_scan_passes_with_zero_errors(self) -> None:
        proc = _run_tool_inproc("tyrion-shield.py", "scan", "--json")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["summary"]["errors"], 0, payload)
        self.assertEqual(payload["summary"]["warnings"], 0, payload)
        self.assertEqual(payload["summary"]["ok"], 6, payload)


if __name__ == "__main__":
    unittest.main()
