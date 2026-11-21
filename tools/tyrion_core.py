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

MAX_FILE_BYTES: int = 25 * 1024 * 1024  # 25 MB hard ceiling for CSV/JSON imports
MAX_RPC_LINE_BYTES: int = 1 * 1024 * 1024  # 1 MB hard ceiling for STDIO JSON-RPC lines

SECRET_REDACT_RE = re.compile(
    r"(EAA[A-Za-z0-9]{12,}|sk-[A-Za-z0-9_\-]{16,}|AIza[0-9A-Za-z_\-]{20,}|\b\d{8,10}:AA[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9_\-\.]{12,})"
)
SAFE_SLUG_RE = re.compile(r"[^a-z0-9]+")
CONTROL_AND_TAG_RE = re.compile(r"[\x00-\x1f\x7f<>\"'`\\]")


def redact_secrets(text: str) -> str:
    """Fully mask API tokens/secrets inside any error message or log text."""
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
    """Float parser that is safe against NaN, Infinity and malformed strings (falls back to `default`)."""
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
    """Int parser that is safe against NaN, Infinity and out-of-range values."""
    fval = safe_float(value, default=float(default), field_name=field_name)
    res = int(round(fval))
    if min_val is not None and res < min_val:
        raise ValueError(f"'{field_name}' kamida {min_val} bo'lishi shart (berildi: {res})")
    if max_val is not None and res > max_val:
        raise ValueError(f"'{field_name}' ko'pi bilan {max_val} bo'lishi shart (berildi: {res})")
    return res


# ---------------------------------------------------------------------------
# Unified number validation and exit-code policy (Tyrion v7)
# ---------------------------------------------------------------------------
# Exit-code policy (shared by every CLI tool):
#   0 = success (no `error` field in the result, gate passed)
#   1 = gate BLOCKED (spend-guard `passed: false`, doctor FAIL, ...) - input was valid, but the decision is "no"
#   2 = VALIDATION error (nan/inf, negative/zero value, missing file, bad header, argparse error)
EXIT_OK: int = 0
EXIT_GATE_BLOCKED: int = 1
EXIT_VALIDATION: int = 2


class NumberValidationError(ValueError):
    """Raised when a numeric argument is not finite (nan/inf) or has the wrong sign/range."""


def require_number(
    value: Any,
    field_name: str = "value",
    *,
    positive: bool = False,
    non_negative: bool = False,
    min_val: float | None = None,
    max_val: float | None = None,
) -> float:
    """Strictly validate a money/budget argument: must be a number, finite (not nan/inf) and, if requested, positive.

    Unlike `safe_float`, a malformed value is never silently replaced by a default; it raises `NumberValidationError`.
    """
    if value is None or isinstance(value, bool):
        raise NumberValidationError(f"'{field_name}' son bo'lishi shart (berildi: {value!r}).")
    try:
        res = float(value) if isinstance(value, (int, float)) else float(str(value).strip())
    except (TypeError, ValueError):
        raise NumberValidationError(f"'{field_name}' son bo'lishi shart (berildi: {value!r}).") from None
    if not math.isfinite(res):
        raise NumberValidationError(f"'{field_name}' chekli son bo'lishi shart — nan/inf qabul qilinmaydi (berildi: {value!r}).")
    if positive and res <= 0:
        raise NumberValidationError(f"'{field_name}' 0 dan katta bo'lishi shart (berildi: {res:g}).")
    if non_negative and res < 0:
        raise NumberValidationError(f"'{field_name}' manfiy bo'lishi mumkin emas (berildi: {res:g}).")
    if min_val is not None and res < min_val:
        raise NumberValidationError(f"'{field_name}' kamida {min_val:g} bo'lishi shart (berildi: {res:g}).")
    if max_val is not None and res > max_val:
        raise NumberValidationError(f"'{field_name}' ko'pi bilan {max_val:g} bo'lishi shart (berildi: {res:g}).")
    return res


def _argparse_number(positive: bool, non_negative: bool):
    import argparse

    def _conv(text: str) -> float:
        try:
            return require_number(text, "qiymat", positive=positive, non_negative=non_negative)
        except NumberValidationError as exc:
            raise argparse.ArgumentTypeError(str(exc)) from None

    return _conv


# Ready-made converters for argparse `type=`: on invalid input argparse itself exits with code 2.
finite_float = _argparse_number(False, False)
positive_float = _argparse_number(True, False)
non_negative_float = _argparse_number(False, True)


def exit_code_for_result(result: Any, gate: bool = False) -> int:
    """Derive the exit code from a result dict: `error` present -> 2; in `gate` mode `passed` false -> 1."""
    if isinstance(result, dict):
        if result.get("error"):
            return EXIT_VALIDATION
        if gate and not result.get("passed", False):
            return EXIT_GATE_BLOCKED
    return EXIT_OK


def parse_localized_number(raw: Any) -> float | None:
    """Parse numbers found in ad-platform exports: "1,234.50", "1 234,50", "1.234,50", "12,5", "$1,234", "45%".

    Rules: spaces/apostrophes are always thousands separators; if both `,` and `.` appear the LAST one is the
    decimal mark; a separator that appears several times is a thousands separator; a single `,` is a thousands
    separator ONLY when followed by exactly 3 digits (and the head is not `0`): "1,234" -> 1234 but
    "1.234" -> 1.234. Returns `None` for invalid or empty input (never a silent 0)."""
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw) if math.isfinite(float(raw)) else None
    s = str(raw).strip()
    if not s:
        return None
    negative = s.startswith("-") or (s.startswith("(") and s.endswith(")"))
    s = re.sub(r"[^\d,.]", "", re.sub(r"[ \u00a0\u202f\u2009']", "", s))
    if not re.search(r"\d", s):
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif s.count(",") > 1:
        s = s.replace(",", "")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    elif "," in s:
        head, tail = s.split(",")
        s = head + tail if (len(tail) == 3 and head not in ("", "0")) else head + "." + tail
    try:
        val = float(s)
    except ValueError:
        return None
    if not math.isfinite(val):
        return None
    return -val if negative else val


def safe_slug(value: str, fallback: str = "unnamed-project", max_len: int = 48) -> str:
    """Build an identifier that cannot contain path traversal (`../`) and is never empty."""
    raw = SAFE_SLUG_RE.sub("-", str(value or "").lower()).strip("-")[:max_len].strip("-")
    return raw if raw else fallback


def sanitize_url(url: str) -> str:
    """Validate a URL, rejecting XSS schemes (`javascript:`, `data:`) and stripping CRLF/control characters."""
    cleaned = re.sub(r"[\r\n\t\x00-\x1f]", "", str(url or "").strip())
    parsed = urllib.parse.urlsplit(cleaned)
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError(f"Xavfsiz bo'lmagan URL sxemasi: '{parsed.scheme}'. Faqat http/https ruxsat etiladi.")
    if not parsed.netloc:
        raise ValueError("URL domeni (netloc) ko'rsatilmagan.")
    return cleaned


def validate_safe_path(target: Path, allowed_root: Path | None = None) -> Path:
    """Block escaping the allowed root via symlinks or `..` (path traversal)."""
    resolved = target.resolve()
    if allowed_root is not None:
        root_resolved = allowed_root.resolve()
        if resolved != root_resolved and root_resolved not in resolved.parents:
            raise PermissionError(f"Xavfsizlik xatosi: '{target}' ruxsat etilgan '{root_resolved}' hududidan tashqarida!")
    return resolved


def atomic_write_bytes(target: Path, data: bytes) -> None:
    """Atomic write that prevents cross-process races and half-written files."""
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
    """Write a text file atomically (`temp -> fsync -> os.replace`)."""
    atomic_write_bytes(target, text.encode(encoding))


def atomic_write_json(target: Path, payload: Any) -> None:
    """Write a JSON file atomically, rejecting NaN/Infinity."""
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
    """GET JSON with exponential backoff + jitter on HTTP 429 (rate limit), 5xx and transient network errors.

    Does not retry on 400/401/403/404 or malformed JSON. Never leaks secret tokens in error output.
    """
    clean_url = sanitize_url(url)
    req_headers = {"Accept": "application/json", "User-Agent": "Tyrion-OS/8.0.1"}
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
