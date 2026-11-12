"""Testlar uchun umumiy yordamchilar (tools/ ni sys.path ga qo'shadi va CLI'ni jarayon ichida ishga tushiradi)."""

from __future__ import annotations

import contextlib
import importlib
import inspect
import io
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
VAULT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

_CLI_MOD_CACHE: dict[str, object] = {}


def run_tool_inproc(script_name: str, *args: str) -> subprocess.CompletedProcess:
    """`tools/<script>` ning `main()` ini jarayon ichida ishga tushirib, (rc, stdout, stderr) qaytaradi."""
    mod_name = script_name[:-3] if script_name.endswith(".py") else script_name
    if mod_name not in _CLI_MOD_CACHE:
        _CLI_MOD_CACHE[mod_name] = importlib.import_module(mod_name)
    mod = _CLI_MOD_CACHE[mod_name]
    out_buf, err_buf = io.StringIO(), io.StringIO()
    old_argv = sys.argv[:]
    sys.argv = [script_name, *args]
    rc = 0
    try:
        with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
            main_fn = getattr(mod, "main")
            res = main_fn(list(args)) if len(inspect.signature(main_fn).parameters) >= 1 else main_fn()
            rc = int(res) if res is not None else 0
    except SystemExit as exc:
        rc = int(exc.code) if isinstance(exc.code, int) else (1 if exc.code else 0)
    finally:
        sys.argv = old_argv
    return subprocess.CompletedProcess(args=[script_name, *args], returncode=rc, stdout=out_buf.getvalue(), stderr=err_buf.getvalue())
