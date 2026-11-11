#!/usr/bin/env python3
"""Tyrion Spend-Guard — Xavfsizlik va Hisob O'zgarishi Nazoratchisi.

Qoida: rules/40-xavfsizlik-va-hisob.md (read-only default, 6 darvoza).
Hech qanday jonli hisob o'zgarmaydi. Tavsiyalar qat'iy tekshiriladi:
  1. Byudjet o'zgarishi: 24 soatda <= 20% (machine learning / smart bidding barqarorligi)
  2. Kunlik limit: max daily spend ceiling dan oshmaslik
  3. Change Packet butunligi: Rollback / Teskari qadam, Xavf, Boshlang'ich ko'rsatkich, Stop-loss
  4. Nusxa / Copy siyosati: Telegram Ads 160 belgi, max 1 emoji, ALL CAPS taqiqi; Google Ads RSA
  5. Tracking: CAPI event_id deduplikatsiyasi, fbp/fbc, xeshlangan ma'lumotlar

Buyruqlar:
  python3 tools\\spend-guard.py budget --current 100 --proposed 115 --max-cap 200
  python3 tools\\spend-guard.py packet path/to/change-packet.md
  python3 tools\\spend-guard.py copy --platform telegram --text "Matn..."
  python3 tools\\spend-guard.py tracking --pixel --capi [--no-event-id] [--unhashed] [--emq 7.5]
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from pathlib import Path

# Windows UTF-8
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def check_budget_change(
    current_daily: float,
    proposed_daily: float,
    max_daily_cap: float = 500.0,
    target_cpa: float | None = None,
    pause_approved: bool = False,
    history: list[dict] | None = None,
    now: float | None = None,
) -> dict:
    """Byudjet o'zgarishini 40-qoida va platforma qonunlari bo'yicha tekshiradi.

    Bloklanadi: nan/inf, manfiy qiymat. ``proposed_daily == 0`` — pauza: alohida tasdiq
    (``pause_approved=True`` / ``--approve-pause``) bo'lmasa bloklanadi.
    """
    errors: list[str] = []
    warnings: list[str] = []

    for label, val in (("Joriy", current_daily), ("Taklif qilingan", proposed_daily), ("Maksimal limit", max_daily_cap)):
        if not isinstance(val, (int, float)) or isinstance(val, bool) or not math.isfinite(val):
            errors.append(f"{label} byudjet chekli son bo'lishi shart (berildi: {val!r}); nan/inf qabul qilinmaydi.")
        elif val < 0:
            errors.append(f"{label} byudjet manfiy bo'lishi mumkin emas (berildi: {val}).")
    if errors:
        return {"passed": False, "action": "invalid", "errors": errors, "warnings": warnings}

    if proposed_daily == 0 and current_daily > 0:
        if not pause_approved:
            errors.append(
                "Taklif 0 = kampaniyani PAUZAGA qo'yish. Pauza ham hisob o'zgarishi: alohida tasdiq talab qilinadi "
                "(operator tasdig'idan so'ng --approve-pause bilan qayta ishga tushiring)."
            )
        else:
            warnings.append("Pauza operator tasdig'i bilan o'tkazildi; qayta yoqishda learning phase qayta boshlanishi mumkin.")
        return {
            "passed": not errors,
            "action": "pause",
            "requires_explicit_approval": True,
            "pause_approved": pause_approved,
            "current_daily": current_daily,
            "proposed_daily": 0.0,
            "percent_change": -100.0,
            "max_daily_cap": max_daily_cap,
            "errors": errors,
            "warnings": warnings,
        }

    if current_daily <= 0:
        errors.append("Joriy kunlik byudjet 0 dan katta bo'lishi shart.")
        return {"passed": False, "errors": errors, "warnings": warnings}

    ratio = proposed_daily / current_daily
    percent_change = (ratio - 1.0) * 100.0

    # 24 soatlik oyna: shu obyekt uchun oxirgi 24 soatdagi o'zgarishlar jami (jurnal bo'lsa)
    window_baseline: float | None = None
    window_entries = 0
    if history:
        t_now = time.time() if now is None else now
        recent = sorted(
            (h for h in history if isinstance(h, dict) and t_now - float(h.get("ts", 0)) < 86400 and float(h.get("from", 0)) > 0),
            key=lambda h: float(h["ts"]),
        )
        if recent:
            window_baseline = float(recent[0]["from"])
            window_entries = len(recent)
            cum = (proposed_daily / window_baseline - 1.0) * 100.0
            if cum > 20.0 and percent_change <= 20.0:
                errors.append(
                    f"Oxirgi 24 soatda {window_entries} ta o'zgarish bor; boshlang'ich {window_baseline:.2f} dan jami "
                    f"+{cum:.1f}% (> 20%). Har bir qadam alohida ≤20% bo'lsa ham jami chegaradan oshmasligi shart."
                )
            percent_change_window = cum
            if cum > percent_change:
                percent_change = cum

    if percent_change > 20.0:
        max_allowed = current_daily * 1.20
        errors.append(
            f"Byudjet oshishi +{percent_change:.1f}% (> 20%). "
            f"Bu Meta o'rganish fazasini (learning phase) yoki Google Smart Bidding algoritmini "
            f"qaytadan boshlaydi (reset). Maksimal ruxsat: +20% (≤ {max_allowed:.2f})."
        )
    elif percent_change < -50.0:
        warnings.append(
            f"Byudjet keskin kamaytirildi ({percent_change:.1f}%). "
            "Auksiondagi yutuq ulushi (impression share) va yetkazib berish barqarorligi yo'qolishi mumkin."
        )

    # 2. Hard Ceiling (Kunlik ship)
    if proposed_daily > max_daily_cap:
        errors.append(
            f"Taklif qilingan kunlik byudjet ({proposed_daily:.2f}) ruxsat etilgan "
            f"maksimal limitdan ({max_daily_cap:.2f}) oshib ketdi."
        )

    # 3. Minimum Learning Volume (Meta uchun tavsiya)
    if target_cpa and target_cpa > 0:
        # 1 ad set uchun kunlik kamida 1.5-2x target CPA kerak (haftasiga kamida 50 ta konversiya)
        min_healthy_daily = (target_cpa * 50) / 7.0
        if proposed_daily < min_healthy_daily:
            warnings.append(
                f"Taklif qilingan byudjet ({proposed_daily:.2f}/kun) 50 ta konversiya/hafta talabini "
                f"qondirish uchun ozlik qilishi mumkin (tavsiya etilgan minimum: {min_healthy_daily:.2f}/kun, "
                f"target CPA {target_cpa:.2f} asosida)."
            )

    passed = len(errors) == 0
    return {
        "passed": passed,
        "current_daily": current_daily,
        "proposed_daily": proposed_daily,
        "percent_change": round(percent_change, 2),
        "window_24h": {"changes": window_entries, "baseline": window_baseline} if window_entries else None,
        "max_daily_cap": max_daily_cap,
        "errors": errors,
        "warnings": warnings,
    }


# ── Holatli jurnal: 24 soatlik oyna va o'zgarishlar tarixi ─────────────────────────────
DEFAULT_LEDGER = Path(__file__).resolve().parent.parent / "outputs" / "spend-guard-ledger.jsonl"


def load_ledger(path: Path, entity: str) -> list[dict]:
    if not path.is_file():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("entity") == entity:
            out.append(obj)
    return out


def record_change(path: Path, entity: str, current: float, proposed: float, approved_by: str, note: str = "") -> dict:
    """Operator o'zgarishni qo'llagandan keyin jurnalga yozadi (Spend-Guard o'zi hisobni o'zgartirmaydi)."""
    entry = {"ts": time.time(), "entity": entity, "from": current, "to": proposed, "approved_by": approved_by, "note": note}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


_PACKET_SECTIONS: dict[str, tuple[str, str]] = {
    "rollback_instructions": (
        r"rollback|teskari qadam|qaytarish|ortga qaytish|favqulodda qaytish",
        "Teskari qadam (Rollback) bo'limi",
    ),
    "stop_loss": (
        r"stop[- ]?loss|stop[- ]?condition|to'xtatish mezoni|kill qoidasi",
        "To'xtatish mezoni (Stop-loss / Stop-condition) bo'limi",
    ),
    "baseline_metrics": (
        r"boshlang'ich|baseline|hozirgi (?:holat|ko'rsatkich)|joriy ko'rsatkich",
        "Boshlang'ich ko'rsatkichlar (Baseline) bo'limi",
    ),
    "risk_assessment": (r"xavf|risk", "Xavf darajasi (Risk) bo'limi"),
    "human_approval": (r"tasdiq|tasdig|approval|ruxsat", "Odam tasdig'i (Human approval) bo'limi"),
}
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")
_FIELD_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)?\**([^:\n*`]{2,80}?)\**\s*:\s*\**\s*(.*)$")


def _clean_value(text: str) -> str:
    return re.sub(r"[*_`]+", "", text).strip()


def _is_placeholder(value: str) -> bool:
    v = _clean_value(value).strip(" .-–—")
    if not v:
        return True
    if re.fullmatch(r"\[[^\]]*\]", v) and not re.fullmatch(r"\[[xX]\]", v):
        return True
    if re.fullmatch(r"(?:tbd|todo|n/?a|yo'q|\.\.\.|…|\?+)", v.lower()):
        return True
    if re.fullmatch(r"[$€£]?\s*0+(?:[.,]0+)?\s*(?:/\s*kun)?", v):
        return True
    return False


def _parse_packet_sections(content: str) -> list[tuple[str, str]]:
    """Change Packet'dan (sarlavha/maydon nomi, qiymat) juftliklarini ajratadi."""
    text = content.replace("\u2019", "'").replace("\u02bb", "'").replace("\u2018", "'")
    pairs: list[tuple[str, str]] = []
    heading: str | None = None
    body: list[str] = []

    def flush() -> None:
        if heading is not None:
            pairs.append((heading, " ".join(b for b in body if b.strip())))

    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        h = _HEADING_RE.match(line)
        if h and not in_fence:
            flush()
            heading, body = re.sub(r"^\d+[.)]\s*", "", _clean_value(h.group(1))), []
            continue
        f = _FIELD_RE.match(line)
        if f and not in_fence:
            pairs.append((_clean_value(f.group(1)), f.group(2)))
            if heading is not None:  # sarlavha ostidagi maydon sarlavha qiymatiga ham kiradi
                body.append(f.group(2).strip())
            continue
        if heading is not None and line.strip() and not re.fullmatch(r"\s*[-*_]{3,}\s*", line):
            body.append(line.strip())
    flush()
    return pairs


def check_change_packet(content: str) -> dict:
    """Change Packet tuzilmasini tekshiradi: har bir majburiy bo'lim sarlavha/maydon + bo'sh bo'lmagan qiymat.

    Majburiy: Rollback, Stop-loss, Baseline, Xavf, Odam tasdig'i. Faqat kalit so'z eslatilishi yetarli emas.
    """
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}
    pairs = _parse_packet_sections(content)

    for key, (pattern, label) in _PACKET_SECTIONS.items():
        label_re = re.compile(pattern, re.IGNORECASE)
        matched = [(n, v) for n, v in pairs if label_re.search(n)]
        filled = any(not _is_placeholder(v) for _, v in matched)
        checks[key] = filled
        if filled:
            continue
        if matched:
            errors.append(f"{label} bor, lekin qiymati bo'sh yoki andoza (placeholder) holatida.")
        else:
            errors.append(f"{label} topilmadi (sarlavha yoki 'Nomi: qiymat' ko'rinishidagi maydon kerak).")

    # Odam tasdig'i: belgilanmagan katak ("[ ]") tasdiq emas
    approval_vals = [v for n, v in pairs if re.search(_PACKET_SECTIONS["human_approval"][0], n, re.IGNORECASE)]
    if approval_vals and all(re.match(r"^\[\s\]", _clean_value(v).lstrip("-+ ")) for v in approval_vals if v.strip()):
        checks["human_approval"] = False
        errors.append("Odam tasdig'i belgilanmagan ('[ ]'). Operator tasdig'isiz o'zgarish kiritilmaydi.")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def check_ad_copy(platform: str, text: str, headline: str = "", destination_url: str = "") -> dict:
    """Platforma qoidalariga ko'ra reklama matnini tekshiradi."""
    errors: list[str] = []
    warnings: list[str] = []
    platform = platform.lower()

    if platform in ("telegram", "tg"):
        # Telegram Ads qoidalari
        char_count = len(text)
        if char_count > 160:
            errors.append(f"Telegram Ads matni 160 belgidan oshmasligi shart (hozirda: {char_count} belgi).")
        elif char_count == 0:
            errors.append("Reklama matni bo'sh bo'lishi mumkin emas.")

        # Emoji siyosati (maksimal 1 ta kontekstga mos emoji)
        # Unicode emoji diapazoni
        emoji_pattern = re.compile(
            r"[\U0001F1E6-\U0001F1FF]{2}|[\u2B50\u2B1B\u2B1C\u2B55\u231A-\u23FF\u2190-\u21FF\u2934\u2935\u00A9\u00AE\u203C\u2049\u2122\u2139\u24C2\u25AA-\u25FE\u3030\u303D\u3297\u3299]"
            r"|[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]"
        )
        emojis = emoji_pattern.findall(text)
        if len(emojis) > 1:
            errors.append(f"Telegram Ads siyosati bo'yicha ko'pi bilan 1 ta emoji ruxsat etiladi (hozirda: {len(emojis)} ta: {' '.join(emojis)}).")

        # ALL CAPS tekshiruvi (faqat qisqartmalar ruxsat etiladi)
        allowed_acronyms = {"CRM", "AI", "B2B", "B2C", "ROI", "ROAS", "CPA", "CPL", "CTR", "CPC", "CPM", "TON", "USD", "UZS", "EUR", "SEO", "PMAX", "CBO", "ABO", "ASC", "SMS", "API"}
        words = re.findall(r"\b[A-ZА-ЯЁЎҚҒҲ]{2,}\b", text)
        forbidden_caps = [w for w in words if w not in allowed_acronyms]
        if forbidden_caps:
            errors.append(f"Telegram Ads ALL CAPS so'zlarni taqiqlaydi: {', '.join(forbidden_caps)}. Kichik harflar bilan yozing.")

        # Havola tekshiruvi
        if destination_url:
            valid_dest = destination_url.startswith(("https://t.me/", "t.me/", "@", "https://"))
            if not valid_dest:
                warnings.append("Telegram Ads manzili 't.me/...', '@kanal', yoki tasdiqlangan HTTPS domen bo'lishi kerak.")

    elif platform in ("meta", "facebook", "instagram"):
        # Meta Ads matn qoidalari
        if headline and len(headline) > 40:
            warnings.append(f"Meta sarlavhasi (Headline) 40 belgidan oshsa mobil ekranda kesilib qolishi mumkin (hozirda: {len(headline)}).")
        if len(text) > 250:
            warnings.append("Birlamchi matn (Primary Text) 125 belgidan keyin 'See more' orqasiga yashirinadi. Eng kuchli hook birinchi 120 belgida bo'lsin.")

        # Taqiqlangan / Shubhali iboralar
        banned_phrases = [
            "tezda boyib ketish", "100% kafolat", "oson daromad", "hech qanday xavfsiz",  # UZ
            "быстро разбогатеть", "100% гарантия", "гарантированный доход", "легкие деньги", "лёгкие деньги",  # RU
            "get rich quick", "100% guaranteed", "guaranteed income", "guaranteed results", "no risk",  # EN
        ]
        for phrase in banned_phrases:
            if phrase in text.lower():
                errors.append(f"Meta siyosatiga zid shubhali va'da: '{phrase}'. Meta hisobni cheklashi mumkin.")

    elif platform in ("google", "google_ads", "gads"):
        # Google Ads Responsive Search Ads (RSA)
        if headline and len(headline) > 30:
            errors.append(f"Google Ads sarlavhasi 30 belgidan oshmasligi shart (hozirda: {len(headline)}).")
        if text and len(text) > 90:
            errors.append(f"Google Ads tavsifi (Description) 90 belgidan oshmasligi shart (hozirda: {len(text)}).")

    # O'zbekiston: kredit/nasiya reklamasi (2026-11-10 qonun, IKKILAMCHI manba — rasmiy tasdiq kerak)
    credit_re = re.compile(r"\b(nasiya|kredit|bo'lib to'lash|muddatli to'lov|rassrochka|installment)\b|рассрочк|кредит", re.IGNORECASE)
    evidence: dict[str, str] = {}
    if credit_re.search(text) or credit_re.search(headline or ""):
        warnings.append(
            "Kredit/nasiya eslatilgan: O'zbekistonda moliyaviy xatar haqidagi ogohlantirish (maydon/davomiylikning kamida 10%) "
            "talab qilinishi mumkin. Manba ikkilamchi (yuz.uz) — yurist yoki lex.uz bilan tasdiqlang."
        )
        evidence["uz_credit_warning_rule"] = "UNVERIFIED_SECONDARY_SOURCE"

    passed = len(errors) == 0
    return {
        "passed": passed,
        "platform": platform,
        "errors": errors,
        "warnings": warnings,
        "evidence": evidence,
    }


def check_tracking_setup(
    has_browser_pixel: bool,
    has_server_capi: bool,
    event_id_present: bool = True,
    user_data_hashed: bool = True,
    emq_score: float | None = None,
) -> dict:
    """Kuzatuv va Konversiya API sozlamalarini tekshiradi."""
    errors: list[str] = []
    warnings: list[str] = []

    if not has_browser_pixel and not has_server_capi:
        errors.append("Hech qanday kuzatuv vositasi (na Pixel, na Server CAPI) mavjud emas.")

    if has_browser_pixel and has_server_capi:
        if not event_id_present:
            errors.append(
                "Pixel va CAPI ikkalasi ham faol, lekin 'event_id' deduplikatsiya parametri yo'q! "
                "Bu har bir xaridni ikki marta (double counting) hisoblash xavfini tug'diradi."
            )
    elif has_browser_pixel and not has_server_capi:
        warnings.append("Faqat brauzer Pixel o'rnatilgan. AdBlock va iOS 14+ tufayli ~20-30% xaridlar yo'qolishi mumkin. CAPI server integratsiyasini qo'shish tavsiya etiladi.")

    if has_server_capi and not user_data_hashed:
        errors.append("CAPI orqali yuborilayotgan foydalanuvchi ma'lumotlari (email/telefon) SHA-256 bilan xeshlanmagan! Maxfiylik qoidasi buzilmoqda.")

    if emq_score is not None:
        if emq_score < 6.0:
            warnings.append(f"Event Match Quality (EMQ) ko'rsatkichi juda past ({emq_score:.1f}/10). Kamida 7.0+ bo'lishi lozim.")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Tyrion Spend-Guard — Xavfsizlik va Hisob O'zgarishi Nazoratchisi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Byudjet buyrug'i
    p_budget = subparsers.add_parser("budget", help="Byudjet o'zgarishini tekshirish")
    p_budget.add_argument("--current", type=float, required=True, help="Joriy kunlik byudjet")
    p_budget.add_argument("--proposed", type=float, required=True, help="Taklif qilingan kunlik byudjet")
    p_budget.add_argument("--max-cap", type=float, default=500.0, help="Maksimal ruxsat etilgan kunlik byudjet (default: 500)")
    p_budget.add_argument("--target-cpa", type=float, default=None, help="Maqsadli CPA (ixtiyoriy)")
    p_budget.add_argument("--entity", default="", help="Kampaniya/ad set identifikatori (24 soatlik jurnal oynasi uchun)")
    p_budget.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER, help="Jurnal fayli (JSONL)")
    p_budget.add_argument("--record", action="store_true", help="O'tgan o'zgarishni jurnalga yozish (faqat --entity va --approved-by bilan)")
    p_budget.add_argument("--approved-by", default="", help="Tasdiqlagan operator (jurnal yozuvi uchun majburiy)")
    p_budget.add_argument("--approve-pause", action="store_true", help="--proposed 0 (pauza) uchun operator tasdig'i")
    p_budget.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Packet buyrug'i
    p_packet = subparsers.add_parser("packet", help="Change Packet faylini tekshirish")
    p_packet.add_argument("file", type=Path, help="Markdown yoki matn fayl yo'li")
    p_packet.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Copy buyrug'i
    p_copy = subparsers.add_parser("copy", help="Reklama matnini platforma qoidalari bo'yicha tekshirish")
    p_copy.add_argument("--platform", choices=["telegram", "meta", "google"], required=True, help="Platforma")
    p_copy.add_argument("--text", type=str, required=True, help="Reklama matni")
    p_copy.add_argument("--headline", type=str, default="", help="Sarlavha")
    p_copy.add_argument("--url", type=str, default="", help="Havola (URL)")
    p_copy.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Tracking buyrug'i
    p_track = subparsers.add_parser("tracking", help="Tracking va CAPI sozlamalarini tekshirish")
    p_track.add_argument("--pixel", action="store_true", help="Pixel mavjudligi")
    p_track.add_argument("--capi", action="store_true", help="Server CAPI mavjudligi")
    p_track.add_argument("--no-event-id", action="store_true", help="event_id yo'qligini bildiradi")
    p_track.add_argument("--unhashed", action="store_true", help="Foydalanuvchi ma'lumotlari xeshlanmagan")
    p_track.add_argument("--emq", type=float, default=None, help="EMQ ball (0-10)")
    p_track.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    args = parser.parse_args()

    res: dict = {}
    if args.command == "budget":
        hist = load_ledger(args.ledger, args.entity) if args.entity else None
        res = check_budget_change(args.current, args.proposed, args.max_cap, args.target_cpa,
                                  pause_approved=args.approve_pause, history=hist)
        if args.record:
            if not (args.entity and args.approved_by.strip()):
                print("Xato: --record uchun --entity va --approved-by majburiy.", file=sys.stderr)
                return 2
            if not res.get("passed"):
                print("Xato: bloklangan o'zgarish jurnalga yozilmaydi.", file=sys.stderr)
            else:
                res["ledger_entry"] = record_change(args.ledger, args.entity, args.current, args.proposed, args.approved_by.strip())
    elif args.command == "packet":
        if not args.file.is_file():
            print(f"Xato: fayl topilmadi: {args.file}", file=sys.stderr)
            return 2
        content = args.file.read_text(encoding="utf-8", errors="replace")
        res = check_change_packet(content)
    elif args.command == "copy":
        res = check_ad_copy(args.platform, args.text, args.headline, args.url)
    elif args.command == "tracking":
        res = check_tracking_setup(
            has_browser_pixel=args.pixel,
            has_server_capi=args.capi,
            event_id_present=not args.no_event_id,
            user_data_hashed=not args.unhashed,
            emq_score=args.emq,
        )

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res.get("passed", False) else 1

    # Inson o'qiydigan chiroyli xulosa
    passed = res.get("passed", False)
    status_icon = "✓ PASSED" if passed else "✗ BLOCKED"
    print(f"\n[Spend-Guard] {status_icon} — {args.command.upper()}")

    if "percent_change" in res and "current_daily" in res:
        print(f"  O'zgarish: {res['percent_change']:+g}% ({res['current_daily']} -> {res['proposed_daily']})")

    if res.get("errors"):
        print("  Xatolar (Taqiqlangan):")
        for err in res["errors"]:
            print(f"    - 🛑 {err}")

    if res.get("warnings"):
        print("  Ogohlantirishlar:")
        for warn in res["warnings"]:
            print(f"    - ⚠ {warn}")

    if passed and not res.get("warnings"):
        print(f"  {args.command}: tekshirilgan qoidalar bo'yicha to'siq topilmadi.")

    print()
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
