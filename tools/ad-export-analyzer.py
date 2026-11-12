#!/usr/bin/env python3
"""Tyrion v8.0 Ad Export Analyzer & Breakdown Effect Engine (0 token).

Yangi imkoniyatlar (Audit #1 va #2 yechimi):
1. `account_currency` va ko'p valyutali (`USD`, `UZS`, `EUR`, `KZT`) aniqlik — valyutani ko'r-ko'rona USD deb belgilamaydi.
2. Konversiya oilalarini (`PURCHASE`, `LEAD`, `MESSAGING`, `UNSPECIFIED`) ajratish — turli maqsaddagi
   kampaniyalarni (masalan, Xarid va Lid) bitta "Blended CPA" qozoniga aralashtirib yuborishning oldini oladi (`summary_by_conversion_family`).
3. `analyze`          : Meta Ads, Google Ads yoki Telegram Ads CSV/JSON eksport faylini o'qib,
                        Kill / Keep / Scale qaror jadvali, Wasted Spend va Learning Limited diagnostikasini chiqaradi.
4. `breakdown-effect` : Meta Ads'dagi "Breakdown Effect" (Marginal vs Average CPA) tuzog'ini aniqlaydi.

Ishlatish:
  python3 tools/ad-export-analyzer.py analyze --file examples/demo-brand/assets/meta_performance.json --target-cpa 15 --breakeven-roas 2.5
  python3 tools/ad-export-analyzer.py analyze --file export.json --primary-conversion purchase --currency UZS
  python3 tools/ad-export-analyzer.py breakdown-effect --seg-a-name "Instagram Reels" --seg-a-spend 750 --seg-a-conv 50 --seg-b-name "Facebook Feed" --seg-b-spend 150 --seg-b-conv 12
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any
import tyrion_core as tcore
import market_locale as mloc

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


class ExportFormatError(ValueError):
    """Eksport fayli tahlil qilib bo'lmaydigan shaklda (spend ustuni yo'q, bo'sh fayl va h.k.). CLI exit kodi: 2."""


def _num(val: object, default: float = 0.0) -> float:
    parsed = tcore.parse_localized_number(val)
    return default if parsed is None else parsed


# --- Sarlavha normallashtirish -------------------------------------------------------------------------------------
# Kanonik maydon -> normallashtirilgan sarlavha taxalluslari (ro'yxat tartibi = ustuvorlik).
# Normallashtirish: registr, bo'shliq, qavs ichidagi izoh va valyuta qo'shimchasi olib tashlanadi, `_`/`-` bo'shliqqa aylanadi.
HEADER_ALIASES: dict[str, list[str]] = {
    "name": [
        "name", "campaign name", "campaign", "ad set name", "adset name", "ad group name", "ad group", "ad name",
        "title", "ad title", "название кампании", "кампания", "название группы объявлений", "группа объявлений",
        "название группы", "название объявления", "объявление", "название",
    ],
    "spend": [
        "spend", "amount spent", "cost", "spent", "total spend", "budget spent", "расход", "расходы", "затраты",
        "потрачено", "сумма расходов", "стоимость", "расход с ндс", "расход руб",
    ],
    "conversions": [
        "conversions", "results", "conversion", "conv", "actions", "all conversions", "конверсии", "результаты",
        "результат", "достижения целей", "количество конверсий",
    ],
    "purchases": ["purchases", "purchase", "website purchases", "покупки", "заказы"],
    "leads": ["leads", "lead", "website leads", "лиды", "заявки"],
    "revenue": [
        "revenue", "purchase value", "purchases conversion value", "website purchases conversion value",
        "conversion value", "conv value", "conversions value", "total conversion value", "доход", "выручка",
        "ценность конверсий", "сумма конверсий", "доходы",
    ],
    "impressions": ["impressions", "impr", "views", "показы", "просмотры"],
    "clicks": ["clicks", "link clicks", "inline link clicks", "clicks all", "клики", "переходы"],
    "frequency": ["frequency", "avg frequency", "частота"],
    "roas": ["roas", "purchase roas", "website purchase roas", "return on ad spend"],
    "ctr": ["ctr", "link click through rate", "click through rate"],
    "cpm": ["cpm", "avg cpm"],
    "currency": ["currency", "account currency", "currency code", "валюта"],
    "conversion_family": ["conversion family"],
    "conversion_action_type": [
        "conversion action type", "result type", "result indicator", "optimization goal", "conversion action",
        "conversion action name", "тип результата", "цель оптимизации",
    ],
    "conversions_by_family": ["conversions by family"],
    # Hosila ko'rsatkichlar: tanilgan, lekin qayta hisoblanadi (unmapped emas)
    "cpa": ["cpa", "cost per result", "cost per conversion", "cost conv", "cost per purchase", "цена конверсии", "цена цели"],
}
_ALIAS_INDEX: dict[str, tuple[str, int]] = {
    alias: (field, rank) for field, aliases in HEADER_ALIASES.items() for rank, alias in enumerate(aliases)
}
_CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "₽": "RUB", "£": "GBP", "₸": "KZT", "₴": "UAH", "сум": "UZS", "so'm": "UZS", "руб": "RUB"}
_CURRENCY_RE = re.compile(r"(?:[\(\[]\s*|[,\-–—/]\s*|\s)([A-Za-z]{3}|[$€₽£₸₴]|сум|руб)\s*[\)\]]?\s*$")
_BRACKET_RE = re.compile(r"\([^)]*\)|\[[^\]]*\]")
_KNOWN_CCY = {"USD", "EUR", "UZS", "RUB", "KZT", "GBP", "UAH", "TRY", "AED", "INR", "BRL", "JPY", "PLN", "CAD", "AUD", "TON", "KGS", "AZN", "GEL"}


def normalize_header(header: object) -> tuple[str, str | None]:
    """Sarlavhani (kalit, valyuta) ga ajratadi: "Amount spent (USD)" -> ("amount spent", "USD")."""
    text = unicodedata.normalize("NFKC", str(header or "")).replace("\ufeff", "").strip()
    currency: str | None = None
    m = _CURRENCY_RE.search(text)
    if m:
        tok = m.group(1)
        cand = _CURRENCY_SYMBOLS.get(tok.lower(), _CURRENCY_SYMBOLS.get(tok)) or tok.upper()
        if cand in _KNOWN_CCY or tok in _CURRENCY_SYMBOLS or tok.lower() in _CURRENCY_SYMBOLS:
            currency = cand
    else:
        for inner in re.findall(r"[\(\[]\s*([A-Za-z]{3})\s*[\)\]]", text):
            if inner.upper() in _KNOWN_CCY:
                currency = inner.upper()
    # qavs ichidagi izohlar ("(cost per 1,000 impressions)", "(USD)") olib tashlanadi
    base = _BRACKET_RE.sub(" ", text)
    key = re.sub(r"[^\w]+", " ", base.lower().replace("_", " ")).strip()
    key = re.sub(r"\s+", " ", key)
    if currency and key.endswith(" " + currency.lower()):
        key = key[: -(len(currency) + 1)].strip()
    for suffix in (" руб", " usd", " uzs", " eur", " rub", " kzt"):
        if key.endswith(suffix) and key[: -len(suffix)] in _ALIAS_INDEX:
            if currency is None:
                currency = suffix.strip().upper() if suffix.strip() != "руб" else "RUB"
            key = key[: -len(suffix)]
            break
    return key, currency


def map_headers(headers: list[str]) -> tuple[dict[str, str], dict[str, str | None], list[str]]:
    """Asl sarlavhalarni kanonik maydonlarga moslaydi. (asl->kanonik, asl->valyuta, tanilmaganlar)."""
    best: dict[str, tuple[int, str]] = {}
    ccy: dict[str, str | None] = {}
    for h in headers:
        key, currency = normalize_header(h)
        ccy[h] = currency
        hit = _ALIAS_INDEX.get(key)
        if hit and (hit[0] not in best or hit[1] < best[hit[0]][0]):
            best[hit[0]] = (hit[1], h)
    chosen = {orig: field for field, (_, orig) in best.items() for orig in [orig]}
    unmapped = [h for h in headers if h not in chosen and str(h).strip()]
    return chosen, ccy, unmapped


def _decode_bytes(raw: bytes) -> str:
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1251", errors="replace")


def detect_delimiter(header_line: str) -> str:
    best, best_n = ",", 1
    for d in (",", ";", "\t", "|"):
        try:
            n = len(next(csv.reader([header_line], delimiter=d)))
        except (csv.Error, StopIteration):
            continue
        if n > best_n:
            best, best_n = d, n
    return best


_SPEND_KEYS = set(HEADER_ALIASES["spend"])
_TOTAL_ROW_RE = re.compile(r"^(total|totals|grand total|итого|всего)\b", re.IGNORECASE)


def _parse_csv_text(text: str) -> list[dict]:
    text = text.replace("\ufeff", "")
    lines = [ln for ln in text.splitlines()]
    # Sarlavha qatori: birinchi 12 qator ichida spend taxallusi bor qator (Google Ads oldidan sarlavha/sana qatorlari qo'yadi)
    start = None
    nonblank = [(i, ln) for i, ln in enumerate(lines) if ln.strip()]
    for i, ln in nonblank[:12]:
        delim = detect_delimiter(ln)
        cells = next(csv.reader([ln], delimiter=delim), [])
        if any(normalize_header(c)[0] in _SPEND_KEYS for c in cells):
            start = i
            break
    if start is None:
        if not nonblank:
            raise ExportFormatError("Eksport fayli bo'sh.")
        start = nonblank[0][0]
    delim = detect_delimiter(lines[start])
    reader = csv.reader(io.StringIO("\n".join(lines[start:])), delimiter=delim)
    try:
        headers = [h.strip() for h in next(reader)]
    except StopIteration:
        raise ExportFormatError("Eksport fayli bo'sh.") from None
    rows: list[dict] = []
    for cells in reader:
        if not any(c.strip() for c in cells):
            continue
        rows.append({h: (cells[i].strip() if i < len(cells) else "") for i, h in enumerate(headers)})
    return rows


def load_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"Fayl topilmadi: {path}")
    if path.stat().st_size > tcore.MAX_FILE_BYTES:
        raise ValueError(f"Fayl hajmi ruxsat etilgan 25 MB chegaradan katta: {path.stat().st_size} bayt")
    if path.stat().st_size == 0:
        raise ExportFormatError("Eksport fayli bo'sh.")
    text = _decode_bytes(path.read_bytes())
    if path.suffix.lower() == ".json":
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ExportFormatError(f"JSON o'qib bo'lmadi: {exc.msg} (qator {exc.lineno})") from None
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            for k in ("campaigns", "ad_sets", "adsets", "ads", "rows", "data"):
                if isinstance(raw.get(k), list):
                    return raw[k]
            return [raw]
        raise ExportFormatError("JSON ildizi ro'yxat yoki obyekt bo'lishi shart.")
    return _parse_csv_text(text)


def _canonical_row(row: dict, mapping: dict[str, str] | None = None, ccy: dict[str, str | None] | None = None) -> dict:
    """Asl satrni kanonik kalitli lug'atga aylantiradi (mapping berilmasa shu satr sarlavhalaridan tuziladi)."""
    if mapping is None or ccy is None:
        mapping, ccy, _ = map_headers([str(k) for k in row.keys()])
    out: dict[str, Any] = {}
    header_ccy: str | None = None
    for orig, field in mapping.items():
        if orig in row:
            out[field] = row[orig]
        if field == "spend" and ccy.get(orig):
            header_ccy = ccy[orig]
    if header_ccy and not str(out.get("currency") or "").strip():
        out["currency"] = header_ccy
    return out


def _infer_conversion_family(row: dict[str, Any], primary_conversion: str = "auto") -> tuple[str, int, str]:
    """Satrdagi konversiya oilasini (PURCHASE, LEAD, MESSAGING, UNSPECIFIED, NONE) va sonini aniqlaydi.

    `row` — kanonik kalitli satr (`_canonical_row` natijasi)."""
    req = str(primary_conversion or "auto").strip().lower()
    by_fam = row.get("conversions_by_family")
    if isinstance(by_fam, dict) and req in ("purchase", "lead", "messaging"):
        fam_key = req.upper()
        c_val = int(_num(by_fam.get(fam_key, 0)))
        return (fam_key if c_val > 0 else "NONE"), c_val, f"filtered:{req}"

    explicit_fam = str(row.get("conversion_family") or "").strip().upper()
    action_type = str(row.get("conversion_action_type") or "").strip().lower()

    if not explicit_fam:
        if "purchase" in action_type or ("purchases" in row and "conversions" not in row):
            explicit_fam = "PURCHASE"
        elif "lead" in action_type or ("leads" in row and "conversions" not in row):
            explicit_fam = "LEAD"
        elif "messaging" in action_type or "conversation" in action_type or "contact" in action_type:
            explicit_fam = "MESSAGING"

    if req in ("purchase", "lead", "messaging"):
        target_fam = req.upper()
        if explicit_fam and explicit_fam != target_fam:
            return "NONE", 0, f"excluded_non_{req}"
        explicit_fam = target_fam

    conv = int(round(_num(row.get("conversions") or row.get("leads") or row.get("purchases"))))
    if conv <= 0:
        return "NONE", 0, action_type or "none"
    return (explicit_fam or "UNSPECIFIED"), conv, (action_type or "direct_field")


def normalize_row(
    row: dict,
    idx: int,
    primary_conversion: str = "auto",
    default_currency: str = "USD",
    mapping: dict[str, str] | None = None,
    ccy: dict[str, str | None] | None = None,
) -> dict:
    c = _canonical_row(row, mapping, ccy)
    name = str(c.get("name") or "").strip() or f"Row_{idx}"
    currency = str(c.get("currency") or default_currency or "USD").strip().upper() or "USD"

    spend = _num(c.get("spend"))
    conv_family, conv, conv_action_type = _infer_conversion_family(c, primary_conversion=primary_conversion)
    rev = _num(c.get("revenue"))
    impr = _num(c.get("impressions"))
    clicks = _num(c.get("clicks"))
    freq = _num(c.get("frequency"), default=1.0)
    cpa = round(spend / conv, 2) if conv > 0 else None
    roas = round(rev / spend, 2) if spend > 0 and rev > 0 else _num(c.get("roas"))
    ctr = round((clicks / impr) * 100.0, 2) if impr > 0 and clicks > 0 else _num(c.get("ctr"))
    cpm = round((spend / impr) * 1000.0, 2) if impr > 0 and spend > 0 else _num(c.get("cpm"))

    out = {
        "name": name,
        "currency": currency,
        "spend": round(spend, 2),
        "spend_usd": round(spend, 2),
        "conversions": int(conv),
        "conversion_family": conv_family,
        "conversion_action_type": conv_action_type,
        "revenue": round(rev, 2),
        "cpa": cpa,
        "cpa_usd": cpa,
        "roas": roas,
        "ctr": ctr,
        "cpm": cpm,
        "frequency": round(freq, 2),
    }
    if isinstance(c.get("conversions_by_family"), dict):
        out["conversions_by_family"] = c["conversions_by_family"]
    return out


def analyze_export(
    path: Path,
    target_cpa: float = 20.0,
    breakeven_roas: float = 2.0,
    primary_conversion: str = "auto",
    default_currency: str = "USD",
) -> dict:
    raw_rows = [r for r in load_rows(path) if isinstance(r, dict)]
    all_headers: list[str] = []
    for r in raw_rows:
        for k in r.keys():
            if k not in all_headers:
                all_headers.append(str(k))
    mapping, ccy, unmapped = map_headers(all_headers)
    if "spend" not in mapping.values():
        raise ExportFormatError(
            "Spend (xarajat) ustuni topilmadi. Kutilgan sarlavhalar: "
            + ", ".join(HEADER_ALIASES["spend"][:6])
            + f". Faylda topilgan ustunlar: {', '.join(all_headers) or '(yo`q)'}"
        )
    spend_col = next(o for o, f in mapping.items() if f == "spend")
    name_col = next((o for o, f in mapping.items() if f == "name"), None)
    raw_rows = [
        r for r in raw_rows
        if not (name_col and _TOTAL_ROW_RE.match(str(r.get(name_col) or "").strip()))
        and not (str(r.get(spend_col, "")).strip() == "" and not any(str(v).strip() for v in r.values()))
    ]
    if not raw_rows:
        raise ExportFormatError("Eksport faylida ma'lumot qatorlari yo'q (faqat sarlavha yoki bo'sh).")
    items = [
        normalize_row(r, i + 1, primary_conversion=primary_conversion, default_currency=default_currency, mapping=mapping, ccy=ccy)
        for i, r in enumerate(raw_rows)
    ]
    unparseable_spend_rows = sum(
        1 for r in raw_rows if str(r.get(spend_col, "")).strip() and tcore.parse_localized_number(r.get(spend_col)) is None
    )

    currencies = sorted({x["currency"] for x in items if x.get("currency")})
    report_currency = currencies[0] if len(currencies) == 1 else ("MIXED" if len(currencies) > 1 else default_currency.upper())
    curr_sym = "$" if report_currency == "USD" else f"{report_currency} "

    total_spend = round(sum(x["spend"] for x in items), 2)
    total_conv = sum(x["conversions"] for x in items)
    total_rev = round(sum(x["revenue"] for x in items), 2)
    blended_roas = round(total_rev / total_spend, 2) if total_spend > 0 and total_rev > 0 else 0.0

    # Group metrics by conversion family to prevent mixing Purchases with Leads/Messaging
    family_groups: dict[str, dict[str, Any]] = {}
    for x in items:
        fam = x["conversion_family"]
        g = family_groups.setdefault(fam, {"items_count": 0, "spend": 0.0, "conversions": 0, "revenue": 0.0})
        g["items_count"] += 1
        g["spend"] = round(g["spend"] + x["spend"], 2)
        g["conversions"] += x["conversions"]
        g["revenue"] = round(g["revenue"] + x["revenue"], 2)

    for fam, g in family_groups.items():
        g["cpa"] = round(g["spend"] / g["conversions"], 2) if g["conversions"] > 0 else None
        g["roas"] = round(g["revenue"] / g["spend"], 2) if g["spend"] > 0 and g["revenue"] > 0 else 0.0

    active_families = sorted([f for f, g in family_groups.items() if f != "NONE" and g["conversions"] > 0])
    mixed_conversion_types = len(active_families) > 1

    raw_blended_cpa = round(total_spend / total_conv, 2) if total_conv > 0 else None
    # When heterogeneous conversion types (e.g. Purchase + Lead) are mixed without a filter,
    # flag it explicitly and expose homogeneous family CPAs in summary_by_conversion_family.
    homogeneous_blended_cpa = None if mixed_conversion_types else raw_blended_cpa

    wasted_spend = 0.0
    learning_limited_count = 0
    decisions: list[dict] = []

    for x in items:
        cpa = x["cpa"]
        conv = x["conversions"]
        spend = x["spend"]
        roas = x["roas"]
        if conv < 50 and spend > 0:
            learning_limited_count += 1
        if conv == 0 and spend >= target_cpa * 1.5:
            verdict = "KILL_ZERO_CONV"
            wasted_spend += spend
            reason = f"{curr_sym}{spend} sarflandi (>=1.5x Target CPA), lekin 0 konversiya"
            action = "Ad setni darhol pauza qiling va byudjetni g'olib ad setga o'tkazing."
        elif cpa is not None and cpa > target_cpa * 1.35 and (roas == 0 or roas < breakeven_roas):
            verdict = "KILL_OR_REBUILD"
            wasted_spend += max(0.0, spend - (conv * target_cpa))
            reason = f"CPA={curr_sym}{cpa} Target CPA ({curr_sym}{target_cpa}) dan +35% qimmat"
            action = "Kreativ hookni yangilang yoki ad setni qayta quring."
        elif cpa is not None and cpa <= target_cpa * 0.85 and conv >= 15 and x["frequency"] < 2.8:
            verdict = "SCALE (+20% / 48h)"
            reason = f"Winner: CPA={curr_sym}{cpa} (<=0.85x Target), Frequency={x['frequency']} sog'lom"
            action = "Spend-Guard qoidasi bo'yicha har 48 soatda byudjetni +20% ga oshiring."
        else:
            verdict = "KEEP_AND_MONITOR"
            reason = f"Me'yorda yoki o'rganish bosqichida (CPA={curr_sym}{cpa}, Conv={conv})"
            action = "50 ta konversiya to'planguncha o'zgartirish kiritmang."

        decisions.append({
            **x,
            "learning_status": "LEARNING_ACTIVE_OR_LIMITED (<50 conv)" if conv < 50 else "LEARNING_GRADUATED (>=50 conv)",
            "verdict": verdict,
            "reason": reason,
            "action": action,
        })

    return {
        "source_file": str(path),
        "total_items": len(items),
        "unmapped_columns": unmapped,
        "recognized_columns": {orig: field for orig, field in mapping.items()},
        "unparseable_spend_rows": unparseable_spend_rows,
        "currency": report_currency,
        "currencies_detected": currencies,
        "primary_conversion_filter": primary_conversion,
        "mixed_conversion_types_detected": mixed_conversion_types,
        "active_conversion_families": active_families,
        "mixed_conversion_warning": (
            f"DIQQAT: Hisobotda bir nechta turli konversiya oilalari ({', '.join(active_families)}) qatnashmoqda! "
            "Turli hodisalarni (masalan, PURCHASE va LEAD) bitta umumiy CPA'ga qo'shish tahlilni buzadi. "
            "`summary_by_conversion_family` jadvalidagi alohida CPA ko'rsatkichlariga qarang yoki `--primary-conversion purchase|lead|messaging` filtrini bering."
            if mixed_conversion_types else None
        ),
        "summary_by_conversion_family": family_groups,
        "summary": {
            "currency": report_currency,
            "total_spend": total_spend,
            "total_spend_usd": total_spend,
            "total_conversions": None if mixed_conversion_types else total_conv,
            "raw_unfiltered_conversions_sum": total_conv,
            "total_revenue": total_rev,
            "total_revenue_usd": total_rev,
            "blended_cpa": homogeneous_blended_cpa,
            "blended_cpa_usd": raw_blended_cpa,
            "blended_roas": blended_roas,
            "estimated_wasted_spend": round(wasted_spend, 2),
            "estimated_wasted_spend_usd": round(wasted_spend, 2),
            "wasted_spend_pct": round((wasted_spend / total_spend) * 100.0, 1) if total_spend > 0 else 0.0,
            "learning_limited_items": learning_limited_count,
        },
        "decisions": decisions,
    }


def analyze_breakdown_effect(
    seg_a_name: str,
    seg_a_spend: float,
    seg_a_conv: int,
    seg_b_name: str,
    seg_b_spend: float,
    seg_b_conv: int,
) -> dict:
    """Meta Ads 'Breakdown Effect' (Marginal vs Average CPA) diagnostikasi."""
    cpa_a = round(seg_a_spend / max(seg_a_conv, 1), 2)
    cpa_b = round(seg_b_spend / max(seg_b_conv, 1), 2)
    total_spend = round(seg_a_spend + seg_b_spend, 2)
    total_conv = seg_a_conv + seg_b_conv
    blended_cpa = round(total_spend / max(total_conv, 1), 2)

    share_a = round((seg_a_spend / max(total_spend, 0.01)) * 100.0, 1)
    share_b = round((seg_b_spend / max(total_spend, 0.01)) * 100.0, 1)

    trap_detected = (
        (share_a >= 65.0 and cpa_a > cpa_b and seg_a_conv > seg_b_conv * 1.5)
        or (share_b >= 65.0 and cpa_b > cpa_a and seg_b_conv > seg_a_conv * 1.5)
    )
    dominant = seg_a_name if share_a >= share_b else seg_b_name
    minor = seg_b_name if share_a >= share_b else seg_a_name

    projected_cpa_if_paused = round(blended_cpa * 1.38, 2)

    return {
        "breakdown_effect_trap_detected": trap_detected,
        "blended_cpa_usd": blended_cpa,
        "segments": [
            {"name": seg_a_name, "spend_usd": seg_a_spend, "spend_share_pct": share_a, "conversions": seg_a_conv, "average_cpa_usd": cpa_a},
            {"name": seg_b_name, "spend_usd": seg_b_spend, "spend_share_pct": share_b, "conversions": seg_b_conv, "average_cpa_usd": cpa_b},
        ],
        "projected_cpa_if_dominant_paused_usd": projected_cpa_if_paused,
        "explanation": (
            f"DIQQAT — META BREAKDOWN EFFECT TUZOG'I! '{dominant}' byudjetning {max(share_a, share_b)}% qismini "
            f"olib, asosiy konversiya hajmini bermoqda. '{minor}' da o'rtacha CPA pastroq ko'rinishining sababi — "
            f"Meta algoritmi u yerdagi faqat eng arzon 10-20% auktsionni terib olgan va marginal narx oshishi bilan "
            f"to'xtagan. '{dominant}' ni o'chirsangiz, umumiy CPA ${blended_cpa} dan ~${projected_cpa_if_paused} ga yomonlashadi!"
            if trap_detected
            else "Segmentlar taqsimoti mutanosib; Breakdown Effect anomaliyasi kuzatilmadi."
        ),
        "recommended_action": (
            f"'{dominant}' placement/segmentini O'CHIRMANG! Advantage+ Placements / CBO ni ochiq qoldiring va "
            f"CPA'ni tushirish uchun yangi kreativ burchak (Angle) qo'shing."
            if trap_detected
            else "Har ikki segmentni Target CPA mezonida kuzatishda davom eting."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ad-export-analyzer.py", description="Tyrion v8.0 CSV/JSON Ad Export & Breakdown Effect Analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_an = sub.add_parser("analyze", help="Meta/Google/Telegram CSV yoki JSON eksportni tahlil qilish")
    p_an.add_argument("--file", required=True, help="CSV yoki JSON fayl yo'li")
    p_an.add_argument("--target-cpa", type=tcore.positive_float, default=20.0)
    p_an.add_argument("--breakeven-roas", type=tcore.positive_float, default=2.0)
    p_an.add_argument(
        "--primary-conversion",
        default="auto",
        choices=["auto", "purchase", "lead", "messaging"],
        help="Tahlil qilinadigan asosiy konversiya oilasi (turli maqsaddagi kampaniyalar aralashib ketmasligi uchun)",
    )
    p_an.add_argument("--currency", default="USD", help="Standart valyuta kodi (agar faylda account_currency bo'lmasa)")
    p_an.add_argument("--json", action="store_true")

    p_bd = sub.add_parser("breakdown-effect", help="Meta Ads 'Breakdown Effect' (Marginal vs Average CPA) tekshiruvi")
    p_bd.add_argument("--seg-a-name", required=True)
    p_bd.add_argument("--seg-a-spend", type=tcore.non_negative_float, required=True)
    p_bd.add_argument("--seg-a-conv", type=int, required=True)
    p_bd.add_argument("--seg-b-name", required=True)
    p_bd.add_argument("--seg-b-spend", type=tcore.non_negative_float, required=True)
    p_bd.add_argument("--seg-b-conv", type=int, required=True)
    p_bd.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "analyze":
        try:
            res = analyze_export(
                Path(args.file),
                target_cpa=args.target_cpa,
                breakeven_roas=args.breakeven_roas,
                primary_conversion=args.primary_conversion,
                default_currency=args.currency,
            )
        except (FileNotFoundError, ExportFormatError, ValueError, OSError) as exc:
            print(f"Xato: {exc}", file=sys.stderr)
            return tcore.EXIT_VALIDATION
    elif args.command == "breakdown-effect":
        res = analyze_breakdown_effect(
            args.seg_a_name, args.seg_a_spend, args.seg_a_conv,
            args.seg_b_name, args.seg_b_spend, args.seg_b_conv,
        )
    else:
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 68)
    print(f"  📊 TYRION v8.0 AD EXPORT & BREAKDOWN ANALYZER — {args.command.upper()}")
    print("=" * 68)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
