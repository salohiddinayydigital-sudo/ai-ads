#!/usr/bin/env python3
"""Tyrion Production Core (`tyrion_core.py`) — Atomic I/O, Input Sanitization, Safe Numeric Parsing,
Path Traversal Guards, Secret Redaction, and Exponential Backoff HTTP Client (0 external dependencies).
"""

from __future__ import annotations

import json
import math
import os
import random
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

# The Meta Graph API version every tool targets unless META_GRAPH_API_VERSION overrides it.
# Defined once: bumping it is a one-line change, checked by the test suite.
DEFAULT_GRAPH_API_VERSION: str = "v26.0"

MAX_FILE_BYTES: int = 25 * 1024 * 1024  # 25 MB hard ceiling for CSV/JSON imports
MAX_RPC_LINE_BYTES: int = 1 * 1024 * 1024  # 1 MB hard ceiling for STDIO JSON-RPC lines

SECRET_REDACT_RE = re.compile(
    r"(EAA[A-Za-z0-9]{12,}|sk-[A-Za-z0-9_\-]{16,}|AIza[0-9A-Za-z_\-]{20,}|\b\d{8,10}:AA[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9_\-\.]{12,})"
)
SAFE_SLUG_RE = re.compile(r"[^a-z0-9]+")
CONTROL_AND_TAG_RE = re.compile(r"[\x00-\x1f\x7f<>\"'`\\]")


# --------------------------------------------------------------------------- #
# Install layout: where the plugin lives, where operator state lives
# --------------------------------------------------------------------------- #

PLUGIN_ROOT_TOKEN = "${CLAUDE_PLUGIN_ROOT}"
STATE_DIR_ENV = "TYRION_HOME"
# kind -> (path inside a git checkout, path inside the personal state directory)
STATE_FILES: dict[str, tuple[str, str]] = {
    "memory": ("MEMORY.md", "MEMORY.md"),
    "instincts": ("manifests/instincts.json", "instincts.json"),
}


def plugin_version(vault: Path) -> str:
    """The release version. `.claude-plugin/plugin.json` is the only place it is written;
    every banner, manifest copy and MCP handshake reads it from there."""
    try:
        data = json.loads((Path(vault) / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        return str(data.get("version") or "0.0.0")
    except (OSError, json.JSONDecodeError):
        return "0.0.0"


def expand_plugin_root(text: str, root: Path) -> str:
    """Replace `${CLAUDE_PLUGIN_ROOT}` with the real root.

    Claude Code substitutes the token in skill, command and agent bodies it loads itself.
    Text that reaches the model any other way (the router's context package, another
    harness) still carries the token, and the Bash tool has no such variable.
    """
    if PLUGIN_ROOT_TOKEN not in text:
        return text
    return text.replace(PLUGIN_ROOT_TOKEN, Path(root).resolve().as_posix())


_QUOTED_ROOT_RE = re.compile(r'"\$\{CLAUDE_PLUGIN_ROOT\}/([^"\n]*)"')


def to_project_relative(text: str) -> str:
    """`python3 "${CLAUDE_PLUGIN_ROOT}/tools/x.py"` -> `python3 tools/x.py`.

    Used for the `.claude/commands/` mirror: when the repository itself is the open
    project, cwd is the root and no substitution happens, so paths must be relative.
    """
    if PLUGIN_ROOT_TOKEN not in text:
        return text
    text = _QUOTED_ROOT_RE.sub(lambda m: m.group(1) if " " not in m.group(1) else f'"{m.group(1)}"', text)
    return text.replace(PLUGIN_ROOT_TOKEN + "/", "").replace(PLUGIN_ROOT_TOKEN, ".")


def is_installed_plugin(vault: Path) -> bool:
    """True when this copy sits in Claude Code's plugin cache, which is replaced on every update."""
    parts = Path(vault).resolve().parts
    return any(a == "plugins" and b == "cache" for a, b in zip(parts, parts[1:]))


def state_dir(vault: Path) -> Path:
    """Directory that holds operator state (memory, instincts).

    A git checkout keeps state in the repository, as before. An installed plugin must not:
    its directory is swapped for a new one on update, so state goes to `~/.tyrion`
    (override with TYRION_HOME). The answer never depends on variables that only some
    processes receive, so hooks, the MCP server and Bash-run tools all agree.
    """
    override = os.environ.get(STATE_DIR_ENV, "").strip()
    if override:
        return Path(override).expanduser()
    if is_installed_plugin(vault):
        return Path.home() / ".tyrion"
    return Path(vault)


def state_path(vault: Path, kind: str) -> Path:
    """Path of one state file, seeded from the shipped template on first use."""
    in_repo, in_state = STATE_FILES[kind]
    base = state_dir(vault)
    template = Path(vault) / in_repo
    if base.resolve() == Path(vault).resolve():
        return template
    target = base / in_state
    if not target.exists() and template.is_file():
        try:
            atomic_write_bytes(target, template.read_bytes())
        except OSError:
            return template  # read-only home: fall back to the shipped copy rather than fail
    return target


def work_root(vault: Path) -> Path:
    """Where client workspaces and outputs are created: the user's project for an installed
    plugin (cwd), the repository itself for a checkout."""
    return Path.cwd() if is_installed_plugin(vault) else Path(vault)


# --------------------------------------------------------------------------- #
# Settings: one place decides where a credential comes from
# --------------------------------------------------------------------------- #

# Only these keys are ever read from a `.env` file. A project's `.env` often holds
# unrelated secrets; none of them is loaded into a Tyrion process.
SETTING_KEYS = (
    "META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID", "META_GRAPH_API_VERSION", "META_GRAPH_API_BASE_URL",
    "TYRION_MARKET", "TYRION_DEFAULT_MARKET", "TYRION_HOOK_PROFILE",
)
# Plugin settings (userConfig) arrive under their own names so that an empty or unset
# option can never blank out a variable the operator exported in the shell.
PLUGIN_SETTING_ENV = {
    "TYRION_CFG_META_ACCESS_TOKEN": "META_ACCESS_TOKEN",
    "TYRION_CFG_META_AD_ACCOUNT_ID": "META_AD_ACCOUNT_ID",
    "TYRION_CFG_DEFAULT_MARKET": "TYRION_DEFAULT_MARKET",
}
_PLACEHOLDER_RE = re.compile(r"\$\{|^your_|_here$|^act_1234567890$|^<.*>$", re.I)
_ENV_LINE_RE = re.compile(r"^\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=\s*(.*?)\s*$")


def usable_setting(value: Any) -> str:
    """The value, or "" when it is empty, an unsubstituted `${...}` or a template placeholder."""
    text = str(value or "").strip().strip('"').strip("'").strip()
    return "" if not text or _PLACEHOLDER_RE.search(text) else text


def read_env_file(path: Path) -> dict[str, str]:
    """KEY=VALUE pairs for SETTING_KEYS from one `.env` file (comments and other keys ignored)."""
    found: dict[str, str] = {}
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return found
    for line in lines:
        match = _ENV_LINE_RE.match(line)
        if not match or match.group(1) not in SETTING_KEYS:
            continue
        value = usable_setting(match.group(2).split(" #", 1)[0])
        if value:
            found[match.group(1)] = value
    return found


def load_settings(vault: Path) -> dict[str, str]:
    """Fill missing settings in os.environ and report where each one came from.

    Precedence, highest first — a later source never overrides an earlier one:
      1. the process environment (what the operator exported);
      2. the plugin settings (`/plugin configure tyrion`), which Claude Code passes to the
         MCP server as TYRION_CFG_*;
      3. `.env` in the current project, then in the state directory (~/.tyrion), then in a checkout.
    Placeholder values are dropped everywhere, so a template token reads as "missing"
    instead of being sent to an API. TYRION_NO_DOTENV=1 skips step 3 (used by the tests).
    """
    sources: dict[str, str] = {}
    for key in SETTING_KEYS:
        if key in os.environ:
            if usable_setting(os.environ[key]):
                sources[key] = "environment"
            else:
                del os.environ[key]
    for cfg_key, key in PLUGIN_SETTING_ENV.items():
        value = usable_setting(os.environ.get(cfg_key))
        if value and key not in os.environ:
            os.environ[key] = value
            sources[key] = "plugin settings"
    if os.environ.get("TYRION_NO_DOTENV", "").strip() not in ("1", "true", "yes"):
        seen: set[Path] = set()
        for folder in (Path.cwd(), state_dir(vault), Path(vault)):
            try:
                env_file = (Path(folder) / ".env").resolve()
            except OSError:
                continue
            if env_file in seen or not env_file.is_file():
                continue
            seen.add(env_file)
            for key, value in read_env_file(env_file).items():
                if key not in os.environ:
                    os.environ[key] = value
                    sources[key] = str(env_file)
    return sources


def redact_secrets(text: str) -> str:
    """Har qanday xato xabari yoki log ichidan API tokenlarni to'liq yashiradi."""
    if not text:
        return ""
    return SECRET_REDACT_RE.sub("[REDACTED_SECRET]", str(text))


def safe_float(
    value: Any,
    default: float = 0.0,
    min_val: float | None = None,
    max_val: float | None = None,
    field_name: str = "value",
) -> float:
    """NaN, Infinity, manfiy yoki buzilgan satrlardan himoyalangan float parser."""
    if value is None or isinstance(value, bool):
        res = default
    elif isinstance(value, (int, float)):
        res = float(value)
    else:
        cleaned = str(value).replace("$", "").replace(",", "").replace("%", "").replace(" ", "").strip()
        try:
            res = float(cleaned) if cleaned else default
        except ValueError:
            res = default

    if not math.isfinite(res):
        res = default
    if min_val is not None and res < min_val:
        raise ValueError(f"'{field_name}' kamida {min_val} bo'lishi shart (berildi: {res})")
    if max_val is not None and res > max_val:
        raise ValueError(f"'{field_name}' ko'pi bilan {max_val} bo'lishi shart (berildi: {res})")
    return res


def safe_int(
    value: Any,
    default: int = 0,
    min_val: int | None = None,
    max_val: int | None = None,
    field_name: str = "value",
) -> int:
    """NaN, Infinity va diapazondan tashqari qiymatlardan himoyalangan int parser."""
    fval = safe_float(value, default=float(default), field_name=field_name)
    res = int(round(fval))
    if min_val is not None and res < min_val:
        raise ValueError(f"'{field_name}' kamida {min_val} bo'lishi shart (berildi: {res})")
    if max_val is not None and res > max_val:
        raise ValueError(f"'{field_name}' ko'pi bilan {max_val} bo'lishi shart (berildi: {res})")
    return res


def safe_slug(value: str, fallback: str = "unnamed-project", max_len: int = 48) -> str:
    """Path traversal (`../`) va bo'sh slug'lardan 100% himoyalangan identifikator."""
    raw = SAFE_SLUG_RE.sub("-", str(value or "").lower()).strip("-")[:max_len].strip("-")
    return raw if raw else fallback


def sanitize_url(url: str) -> str:
    """XSS (`javascript:`, `data:`) va CRLF injection'dan himoyalangan URL tekshiruvi."""
    cleaned = re.sub(r"[\r\n\t\x00-\x1f]", "", str(url or "").strip())
    parsed = urllib.parse.urlsplit(cleaned)
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError(f"Xavfsiz bo'lmagan URL sxemasi: '{parsed.scheme}'. Faqat http/https ruxsat etiladi.")
    if not parsed.netloc:
        raise ValueError("URL domeni (netloc) ko'rsatilmagan.")
    return cleaned


def validate_safe_path(target: Path, allowed_root: Path | None = None) -> Path:
    """Symlink yoki `..` orqali ruxsat etilgan papkadan chiqib ketishni (Path Traversal) bloklaydi."""
    resolved = target.resolve()
    if allowed_root is not None:
        root_resolved = allowed_root.resolve()
        if resolved != root_resolved and root_resolved not in resolved.parents:
            raise PermissionError(f"Xavfsizlik xatosi: '{target}' ruxsat etilgan '{root_resolved}' hududidan tashqarida!")
    return resolved


def atomic_write_bytes(target: Path, data: bytes) -> None:
    """Jarayonlararo poyga (race condition) va yarim yozilgan fayllarni oldini oluvchi atomik yozish."""
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except OSError:
                pass
        try:
            os.chmod(str(tmp_path), 0o644)
        except OSError:
            pass
        os.replace(str(tmp_path), str(target))
    except Exception:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise


def atomic_write_text(target: Path, text: str, encoding: str = "utf-8") -> None:
    """Matnli faylni atomik tarzda (`temp -> fsync -> os.replace`) yozadi."""
    atomic_write_bytes(target, text.encode(encoding))


def atomic_write_json(target: Path, payload: Any) -> None:
    """JSON faylni NaN/Infinity'siz tekshirib, atomik tarzda yozadi."""
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    atomic_write_text(target, serialized, encoding="utf-8")


def _classify_http_status(status: int) -> str:
    if status == 400:
        return "BAD_REQUEST_400"
    if status == 401:
        return "AUTH_401"
    if status == 403:
        return "PERMISSION_403"
    if status == 404:
        return "NOT_FOUND_404"
    if status == 429:
        return "RATE_LIMIT_429"
    if 500 <= status <= 599:
        return "SERVER_5XX"
    return f"HTTP_{status}"


def http_get_json_with_backoff(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 8.0,
    max_retries: int = 3,
    base_delay: float = 0.25,
) -> dict[str, Any]:
    """HTTP 429 (Rate Limit), 5xx va vaqtinchalik tarmoq xatolarida eksponensial backoff + jitter bilan so'rov yuboradi.
    400/401/403/404 va noto'g'ri JSON xatolarida qayta urinmaydi. Maxfiy tokenlarni hech qachon oshkor qilmaydi.
    """
    clean_url = sanitize_url(url)
    req_headers = {"Accept": "application/json", "User-Agent": "Tyrion-OS"}
    if headers:
        req_headers.update(headers)

    last_err: str = "Noma'lum tarmoq xatosi"
    last_status: int | None = None
    last_category: str = "NETWORK_ERROR"
    attempts_made = 0

    for attempt in range(max_retries + 1):
        attempts_made = attempt + 1
        req = urllib.request.Request(clean_url, headers=req_headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status_code = getattr(resp, "status", 200) or 200
                raw = resp.read(MAX_FILE_BYTES).decode("utf-8", errors="replace")
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError as jexc:
                    return {
                        "error": f"Invalid JSON response: {jexc.msg}",
                        "http_status": status_code,
                        "error_category": "INVALID_JSON",
                        "retries_attempted": attempt,
                    }
                if isinstance(data, dict):
                    return data
                if isinstance(data, list):
                    return {"data": data}
                return {
                    "error": f"Unexpected JSON root type: {type(data).__name__}",
                    "http_status": status_code,
                    "error_category": "UNEXPECTED_PAYLOAD_SHAPE",
                    "retries_attempted": attempt,
                }
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            last_status = status
            last_category = _classify_http_status(status)
            body_preview = ""
            try:
                body_preview = redact_secrets(exc.read(2048).decode("utf-8", errors="replace"))
            except Exception:
                pass
            last_err = f"HTTP {status}: {redact_secrets(str(exc.reason))} {body_preview[:200]}".strip()
            if status in (429, 500, 502, 503, 504) and attempt < max_retries:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                delay = safe_float(retry_after, default=base_delay * (2 ** attempt)) + random.uniform(0.02, 0.12)
                time.sleep(min(delay, 2.5))
                continue
            break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_status = None
            last_category = "TIMEOUT_ERROR" if isinstance(exc, TimeoutError) else "NETWORK_ERROR"
            last_err = redact_secrets(str(exc))
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt) + random.uniform(0.02, 0.12)
                time.sleep(min(delay, 2.5))
                continue
            break

    return {
        "error": last_err,
        "http_status": last_status,
        "error_category": last_category,
        "retries_attempted": max(0, attempts_made - 1),
    }
