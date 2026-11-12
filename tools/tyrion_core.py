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


# ---------------------------------------------------------------------------
# Yagona son validatsiyasi va chiqish kodi siyosati (Tyrion v7)
# ---------------------------------------------------------------------------
# Chiqish kodi siyosati (barcha CLI asboblar uchun yagona):
#   0 = muvaffaqiyat (natijada `error` maydoni yo'q, darvoza o'tdi)
#   1 = darvoza BLOKLANDI (spend-guard `passed: false`, doctor FAIL va h.k.) — kirish to'g'ri, lekin qaror "yo'q"
#   2 = VALIDATSIYA xatosi (nan/inf, manfiy/nol qiymat, topilmagan fayl, noto'g'ri sarlavha, argparse xatosi)
EXIT_OK: int = 0
EXIT_GATE_BLOCKED: int = 1
EXIT_VALIDATION: int = 2


class NumberValidationError(ValueError):
    """Son argumenti chekli (nan/inf emas) yoki kerakli ishorada emasligi haqidagi xato."""


def require_number(
    value: Any,
    field_name: str = "value",
    *,
    positive: bool = False,
    non_negative: bool = False,
    min_val: float | None = None,
    max_val: float | None = None,
) -> float:
    """Pul/byudjet argumentini qat'iy tekshiradi: son bo'lishi, chekli (nan/inf emas) va kerak bo'lsa musbat.

    `safe_float` dan farqi: buzilgan qiymatni jimgina `default` ga aylantirmaydi, balki `NumberValidationError` ko'taradi.
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


# argparse `type=` uchun tayyor konvertorlar: xato bo'lsa argparse o'zi exit 2 beradi.
finite_float = _argparse_number(False, False)
positive_float = _argparse_number(True, False)
non_negative_float = _argparse_number(False, True)


def exit_code_for_result(result: Any, gate: bool = False) -> int:
    """Natija lug'atidan chiqish kodini chiqaradi: `error` maydoni bor -> 2; `gate` rejimida `passed` false -> 1."""
    if isinstance(result, dict):
        if result.get("error"):
            return EXIT_VALIDATION
        if gate and not result.get("passed", False):
            return EXIT_GATE_BLOCKED
    return EXIT_OK


def parse_localized_number(raw: Any) -> float | None:
    """Eksport hujjatlaridagi sonlarni o'qiydi: "1,234.50", "1 234,50", "1.234,50", "12,5", "$1,234", "45%".

    Qoidalar: bo'shliq/apostrof har doim ming ajratgich; ikkala `,` va `.` bo'lsa OXIRGISI o'nlik belgi;
    bitta tur bir necha marta kelsa ming ajratgich; bitta marta kelsa — o'nlik, FAQAT `,` + aynan 3 raqam
    (va boshi `0` emas) bo'lsa ming ajratgich ("1,234" -> 1234, lekin "1.234" -> 1.234).
    Yaroqsiz yoki bo'sh qiymat uchun `None` qaytaradi (jimgina 0 emas)."""
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
    req_headers = {"Accept": "application/json", "User-Agent": "Tyrion-OS/5.0"}
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
