"""hooks/tyrion-hook.py pre:guard — sir fayllariga yozish: strict = blok (exit 2), standard = ogohlantirish, minimal = o'chirilgan."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

from tests._helpers import VAULT

HOOK = VAULT / "hooks" / "tyrion-hook.py"


def _guard(profile: str, target: str = "", stdin: str | None = None, extra: tuple[str, ...] = ("--warn-only", "--quiet")) -> subprocess.CompletedProcess:
    env = {**os.environ, "TYRION_HOOK_PROFILE": profile}
    env.pop("TYRION_DISABLED_HOOKS", None)
    args = [sys.executable, str(HOOK), "guard", *extra]
    if target:
        args += ["--target", target]
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, input=stdin if stdin is not None else "", timeout=30)


class SecretFileGuardTests(unittest.TestCase):
    SECRET_TARGETS = (".env", ".env.production", "config/.env.local", "keys/server.pem", "id_rsa", "deploy.key",
                      "credentials.json", "service-account-prod.json", ".netrc", "secrets.yaml")
    SAFE_TARGETS = (".env.example", ".env.sample", "README.md", "tools/calculator.py", "environment.md", "id_rsa.pub", "keyboard.txt")

    def test_strict_blocks_secret_writes_even_with_warn_only(self) -> None:
        for t in self.SECRET_TARGETS:
            proc = _guard("strict", t)
            self.assertEqual(proc.returncode, 2, f"{t}: {proc.stdout}{proc.stderr}")
            self.assertIn("sir", (proc.stdout + proc.stderr).lower())

    def test_standard_warns_but_allows(self) -> None:
        for t in self.SECRET_TARGETS:
            proc = _guard("standard", t)
            self.assertEqual(proc.returncode, 0, t)
            self.assertIn("sir", (proc.stdout + proc.stderr).lower(), f"ogohlantirish yo'q: {t}")

    def test_safe_targets_are_silent_and_allowed(self) -> None:
        for profile in ("standard", "strict"):
            for t in self.SAFE_TARGETS:
                proc = _guard(profile, t)
                self.assertEqual(proc.returncode, 0, f"{profile} {t}: {proc.stdout}{proc.stderr}")
                self.assertNotIn("sir", (proc.stdout + proc.stderr).lower(), f"{profile} {t}")

    def test_minimal_profile_disables_guard(self) -> None:
        self.assertEqual(_guard("minimal", ".env").returncode, 0)

    def test_stdin_payload_from_claude_code_is_parsed(self) -> None:
        payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": "/work/project/.env", "content": "X=1"}})
        self.assertEqual(_guard("strict", stdin=payload).returncode, 2)
        self.assertEqual(_guard("standard", stdin=payload).returncode, 0)

    def test_secret_outside_vault_is_still_guarded(self) -> None:
        self.assertEqual(_guard("strict", "/tmp/another-project/.env").returncode, 2)

    def test_generated_files_behaviour_unchanged(self) -> None:
        self.assertEqual(_guard("strict", "manifests/catalog.json").returncode, 2)
        self.assertEqual(_guard("standard", "manifests/catalog.json").returncode, 0)  # --warn-only
        self.assertEqual(_guard("standard", "manifests/catalog.json", extra=("--quiet",)).returncode, 2)


if __name__ == "__main__":
    unittest.main()
