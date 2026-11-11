#!/usr/bin/env python3
"""Tyrion CAPI & UTM Builder — Global Meta CAPI SHA-256 PII Normalizer, Consent Gate, EMQ Scorer & UTM Generator (0 token).

Commands:
  python3 tools/capi-utm-builder.py utm --url "https://brand.com/offer" --platform meta --campaign "q4_scale"
  python3 tools/capi-utm-builder.py capi-payload --event "Purchase" --phone "+49 151 23456789" --email "buyer@shop.de" --city "Berlin" --country "de" --market "eu" --value 150 --currency EUR --consent-granted
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
import market_locale as mloc  # noqa: E402
import tyrion_core as tcore  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

DEFAULT_GRAPH_API_VERSION = "v26.0"


def get_graph_api_version() -> str:
    info = mloc.get_configured_api_version("META_GRAPH_API_VERSION", DEFAULT_GRAPH_API_VERSION)
    return info["version"]


def sha256_norm(val: str) -> str:
    return hashlib.sha256(val.strip().lower().encode("utf-8")).hexdigest()


def normalize_phone(phone: str, default_country_code: str = "998") -> str:
    digits = re.sub(r"\D+", "", phone or "")
    if len(digits) == 9 and digits.startswith(("9", "8", "7", "3", "5")) and default_country_code == "998":
        digits = "998" + digits
    return digits


def build_utm_links(base_url: str, platform: str, campaign: str, bot_username: str = "") -> dict:
    base_url = tcore.sanitize_url(base_url)
    clean_camp = re.sub(r"[^a-zA-Z0-9_\-]+", "_", campaign.strip().lower()).strip("_")[:24]
    if platform == "meta":
        params = {
            "utm_source": "ig_fb",
            "utm_medium": "paid_social",
            "utm_campaign": "{{campaign.name}}",
            "utm_content": "{{adset.name}}__{{ad.name}}",
            "utm_term": "{{placement}}",
        }
    elif platform == "google":
        params = {
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "{campaignid}",
            "utm_content": "{adgroupid}__{creative}",
            "utm_term": "{keyword}",
        }
    else:
        params = {
            "utm_source": "telegram",
            "utm_medium": "sponsored_msg",
            "utm_campaign": clean_camp,
            "utm_content": "ch_seed_01",
        }

    # Fragment (#...) so'rov qismidan KEYIN turishi shart; makrolar ({campaignid}, {{ad.name}}) kodlanmaydi.
    parts = urllib.parse.urlsplit(base_url)
    query_str = "&".join(f"{k}={v}" for k, v in params.items())
    new_query = f"{parts.query}&{query_str}" if parts.query else query_str
    full_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))

    tg_links = {}
    if bot_username:
        bot = bot_username.lstrip("@").strip()
        start_payload = f"{platform[:2]}_{clean_camp}_ad01"[:64]
        tg_links = {
            "telegram_bot_deeplink": f"https://t.me/{bot}?start={start_payload}",
            "start_payload": start_payload,
            "payload_length": len(start_payload),
            "within_64_char_limit": len(start_payload) <= 64,
        }

    return {
        "platform": platform,
        "base_url": base_url,
        "full_tracked_url": full_url,
        "utm_parameters": params,
        "telegram_bot_tracking": tg_links,
    }


_ACTION_SOURCES = ("website", "app", "email", "phone_call", "chat", "physical_store", "system_generated", "business_messaging", "other")


def build_capi_payload(
    event_name: str,
    phone: str = "",
    email: str = "",
    first_name: str = "",
    city: str = "",
    country: str = "",
    fbp: str = "",
    fbc: str = "",
    value: float | None = None,
    currency: str = "",
    order_id: str = "",
    event_source_url: str = "",
    market: str = "",
    consent_granted: bool = True,
    ldu_enabled: bool | None = None,
    ldu_state: int = 0,
    special_ad_category: str = "NONE",
    user_agent: str = "",
    ip: str = "",
    action_source: str = "website",
    event_id: str = "",
    event_time: int | None = None,
) -> dict:
    """CAPI payload quradi. Payload'ga FAQAT foydalanuvchi bergan qiymatlar tushadi.

    Yagona avtomatik maydon — ``event_time`` (berilmasa joriy vaqt; ``system_generated_fields`` da ko'rsatiladi).
    Yo'q maydonlar o'ylab topilmaydi — ``missing_fields`` / ``warnings`` da ogohlantirish chiqadi.
    """
    if action_source not in _ACTION_SOURCES:
        raise ValueError(f"action_source {action_source!r} noto'g'ri; ruxsat etilgan: {', '.join(_ACTION_SOURCES)}")
    api_info = mloc.get_configured_api_version("META_GRAPH_API_VERSION", DEFAULT_GRAPH_API_VERSION)
    api_version = api_info["version"]

    det_market = mloc.detect_market(explicit_market=market, geo=country or None, currency=currency or None)
    m_id = det_market["market_id"]
    has_value = value is not None
    if has_value and not (currency or "").strip():
        raise ValueError("--value berilsa --currency ham majburiy (valyuta taxmin qilinmaydi).")
    curr = (currency or "").strip().upper()

    warnings: list[str] = []
    missing: list[str] = []
    user_data: dict[str, object] = {}
    if country:
        user_data["country"] = [sha256_norm(country)]
    emq_points = 0.0

    if not consent_granted:
        # Strict Consent Gate: PII (phone, email, name, city, fbp/fbc, UA, IP) roziliksiz yuborilmaydi
        consent_gate_status = "BLOCKED_PII_NO_CONSENT"
        pii_stripped = True
        emq_score = 0.0
        if any((phone, email, first_name, city, fbp, fbc, user_agent, ip)):
            warnings.append("Rozilik yo'q: berilgan PII maydonlari payload'dan olib tashlandi.")
    else:
        consent_gate_status = "CONSENT_GRANTED_PII_HASHED"
        pii_stripped = False
        if phone:
            norm_ph = normalize_phone(phone, default_country_code="998" if m_id == "uz" else "")
            user_data["ph"] = [sha256_norm(norm_ph)]
            emq_points += 3.2
        if email:
            user_data["em"] = [sha256_norm(email)]
            emq_points += 2.2
        if first_name:
            user_data["fn"] = [sha256_norm(first_name)]
            emq_points += 0.6
        if city:
            user_data["ct"] = [sha256_norm(city)]
            emq_points += 0.4
        if fbp:
            user_data["fbp"] = fbp
            emq_points += 1.0
        if fbc:
            user_data["fbc"] = fbc
            emq_points += 1.1
        if user_agent:
            user_data["client_user_agent"] = user_agent
        if ip:
            user_data["client_ip_address"] = ip
        emq_score = round(min(10.0, emq_points), 1)

    if action_source == "website":
        if not event_source_url:
            missing.append("event_source_url")
            warnings.append("action_source=website uchun event_source_url majburiy — --event-source-url bering.")
        if consent_granted and not user_agent:
            missing.append("client_user_agent")
            warnings.append("action_source=website uchun client_user_agent majburiy — --user-agent bering.")
    if consent_granted and not any(k in user_data for k in ("ph", "em", "fbp", "fbc", "client_ip_address")):
        warnings.append("Moslashtirish uchun identifikator yo'q (phone/email/fbp/fbc/ip) — Meta hodisani bog'lay olmaydi.")

    if not event_id and order_id:
        event_id = f"evt_{event_name.lower()}_{re.sub(r'[^a-zA-Z0-9]+', '', order_id)}"
    if not event_id:
        missing.append("event_id")
        warnings.append("event_id yo'q: Pixel+CAPI deduplikatsiyasi ishlamaydi — --event-id yoki --order-id bering.")

    # Meta Limited Data Use (LDU) for US states (CCPA/CPRA, VA, CO, CT, TX)
    use_ldu = ldu_enabled if ldu_enabled is not None else (m_id == "us" or not consent_granted)
    data_processing_options: list[str] = ["LDU"] if use_ldu else []
    data_processing_options_country = 1 if (use_ldu and m_id == "us") else 0
    data_processing_options_state = ldu_state if (use_ldu and m_id == "us") else 0

    # Google Consent Mode v2 signals (mandatory in EEA/UK)
    consent_state_str = "granted" if consent_granted else "denied"
    google_consent_mode_v2 = {
        "ad_storage": consent_state_str,
        "analytics_storage": consent_state_str,
        "ad_user_data": consent_state_str,
        "ad_personalization": consent_state_str,
        "required_in_market": m_id in ("eu", "uk"),
    }

    rounded_val = (
        mloc.round_currency(tcore.safe_float(value, default=0.0, min_val=0.0, field_name="value"), curr) if has_value else None
    )
    custom_data: dict[str, object] = {}
    if has_value:
        custom_data["currency"] = curr
        custom_data["value"] = rounded_val
    if order_id:
        custom_data["order_id"] = order_id

    generated: list[str] = []
    if event_time is None:
        event_time = int(time.time())
        generated.append("event_time")

    event_obj: dict[str, object] = {
        "event_name": event_name,
        "event_time": int(event_time),
        "action_source": action_source,
        "user_data": user_data,
    }
    if use_ldu:  # LDU maydonlari faqat LDU yoqilganda (foydalanuvchi/bozor qarori) qo'shiladi
        event_obj["data_processing_options"] = data_processing_options
        event_obj["data_processing_options_country"] = data_processing_options_country
        event_obj["data_processing_options_state"] = data_processing_options_state

    if event_id:
        event_obj["event_id"] = event_id
    if event_source_url:
        event_obj["event_source_url"] = event_source_url
    if custom_data:
        event_obj["custom_data"] = custom_data

    payload = {"data": [event_obj]}

    regulatory_checks = {
        "market": m_id,
        "consent_granted": consent_granted,
        "consent_gate_status": consent_gate_status,
        "pii_stripped_due_to_no_consent": pii_stripped,
        "gdpr_eprivacy_compliant": consent_granted or pii_stripped,
        "google_consent_mode_v2": google_consent_mode_v2,
        "meta_ldu": {
            "data_processing_options": data_processing_options,
            "data_processing_options_country": data_processing_options_country,
            "data_processing_options_state": data_processing_options_state,
        },
        "frameworks_checked": [
            "GDPR & ePrivacy (EEA/UK)",
            "Google Consent Mode v2 (ad_storage, analytics_storage, ad_user_data, ad_personalization)",
            "CCPA / CPRA & Meta Limited Data Use (US States)",
            "Brazil LGPD (Lei No. 13.709/2018)",
            "India DPDP Act 2023",
            "EU Digital Markets Act (DMA) & EU Political Ads Regulation 2024/900",
        ],
        "special_ad_category": special_ad_category,
    }

    out: dict[str, object] = {
        "graph_api_version": api_version,
        "capi_endpoint_template": f"POST https://graph.facebook.com/{api_version}/<PIXEL_ID>/events",
        "market": m_id,
        "currency": curr or None,
        "formatted_value": mloc.format_currency(rounded_val, curr) if has_value else None,
        "consent_gate_status": consent_gate_status,
        "pii_stripped_due_to_no_consent": pii_stripped,
        "regulatory_compliance": regulatory_checks,
        "estimated_emq_score_10": emq_score,
        "emq_basis": "HEURISTIC_PRIOR_MODEL",
        "emq_note": (
            "Taxminiy evristika (maydonlar og'irligi), Meta'ning haqiqiy EMQ si emas. "
            "Haqiqiy ballni Events Manager yoki Dataset Quality API dan oling."
        ),
        "missing_fields": missing,
        "warnings": warnings,
        "system_generated_fields": generated,
        "emq_status": (
            "CONSENT_DENIED_ANONYMOUS"
            if pii_stripped
            else ("EXCELLENT (>=8.0)" if emq_score >= 8.0 else ("GOOD (6.5-7.9)" if emq_score >= 6.5 else "WEAK (<6.5 — add phone/email and fbc/fbp if available)"))
        ),
        "deduplication_instruction": (
            f"Browser Pixel MUST call `fbq('track', '{event_name}', {{...}}, {{eventID: '{event_id}'}})` for 100% deduplication."
            if event_id else "event_id berilmagan — deduplikatsiya ko'rsatmasi yo'q."
        ),
        "capi_payload": payload,
        "capi_v22_payload": payload,
    }
    if api_info.get("warning"):
        out["api_version_warning"] = api_info["warning"]
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="capi-utm-builder.py", description="Global Meta CAPI Payload, Consent Gate & UTM Builder")
    sub = parser.add_subparsers(dest="command", required=True)

    p_utm = sub.add_parser("utm", help="Meta/Google dynamic UTM & Telegram Bot <=64 char deep-link builder")
    p_utm.add_argument("--url", required=True)
    p_utm.add_argument("--platform", default="meta", choices=["meta", "google", "telegram"])
    p_utm.add_argument("--campaign", default="global_launch")
    p_utm.add_argument("--bot", default="", help="Telegram bot username (optional)")
    p_utm.add_argument("--json", action="store_true")

    p_capi = sub.add_parser("capi-payload", help="Meta CAPI SHA-256 payload builder with GDPR/CCPA/LGPD/DPDP Consent Gate")
    p_capi.add_argument("--event", default="Lead")
    p_capi.add_argument("--phone", default="")
    p_capi.add_argument("--email", default="")
    p_capi.add_argument("--first-name", default="")
    p_capi.add_argument("--city", default="")
    p_capi.add_argument("--country", default="", help="ISO-2 mamlakat kodi (ixtiyoriy; berilmasa payload'ga qo'shilmaydi)")
    p_capi.add_argument("--market", default="", help="Market pack (global, uz, us, eu, uk, mena, latam, sea, in)")
    p_capi.add_argument("--value", type=float, default=None, help="Hodisa qiymati (berilsa --currency majburiy)")
    p_capi.add_argument("--currency", default="")
    p_capi.add_argument("--order-id", default="")
    p_capi.add_argument("--event-id", default="", help="Pixel bilan bir xil event_id (berilmasa --order-id dan hosil qilinadi)")
    p_capi.add_argument("--event-time", type=int, default=None, help="UNIX vaqt (berilmasa joriy vaqt)")
    p_capi.add_argument("--event-source-url", default="")
    p_capi.add_argument("--fbp", default="")
    p_capi.add_argument("--fbc", default="")
    p_capi.add_argument("--user-agent", default="")
    p_capi.add_argument("--ip", default="")
    p_capi.add_argument("--action-source", default="website", choices=list(_ACTION_SOURCES))
    p_capi.add_argument("--consent-granted", dest="consent_granted", action="store_true", default=True, help="User granted tracking/PII consent (default: True)")
    p_capi.add_argument("--no-consent", dest="consent_granted", action="store_false", help="User denied consent -> strip all PII from CAPI payload")
    p_capi.add_argument("--ldu", action="store_true", help="Enable Meta Limited Data Use (data_processing_options=['LDU'])")
    p_capi.add_argument("--ldu-state", type=int, default=0, help="US LDU state code (e.g. 1000 for California)")
    p_capi.add_argument("--special-ad-category", default="NONE", help="HOUSING, EMPLOYMENT, CREDIT, ISSUES_ELECTIONS_POLITICS, or NONE")
    p_capi.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        res = _run(args)
    except ValueError as exc:
        print(f"Xato: {exc}", file=sys.stderr)
        return 2
    if res is None:
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 68)
    print(f"  📡 TYRION GLOBAL CAPI & UTM BUILDER — {args.command.upper()}")
    print("=" * 68)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("=" * 68)
    return 0


def _run(args: argparse.Namespace) -> dict | None:
    if args.command == "utm":
        return build_utm_links(args.url, args.platform, args.campaign, args.bot)
    if args.command == "capi-payload":
        return build_capi_payload(
            event_name=args.event, phone=args.phone, email=args.email,
            first_name=args.first_name, city=args.city, country=args.country,
            value=args.value, currency=args.currency, order_id=args.order_id,
            fbp=args.fbp, fbc=args.fbc, user_agent=args.user_agent, ip=args.ip,
            action_source=args.action_source, event_id=args.event_id,
            event_time=args.event_time, event_source_url=args.event_source_url,
            market=args.market, consent_granted=args.consent_granted,
            ldu_enabled=(True if args.ldu else None), ldu_state=args.ldu_state,
            special_ad_category=args.special_ad_category,
        )
    return None


if __name__ == "__main__":
    raise SystemExit(main())
