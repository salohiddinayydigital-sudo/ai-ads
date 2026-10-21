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

    sep = "&" if "?" in base_url else "?"
    query_str = "&".join(f"{k}={v}" for k, v in params.items())
    full_url = f"{base_url}{sep}{query_str}"

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


def build_capi_payload(
    event_name: str,
    phone: str = "",
    email: str = "",
    first_name: str = "",
    city: str = "tashkent",
    country: str = "uz",
    fbp: str = "fb.1.1729200000.123456789",
    fbc: str = "fb.1.1729200000.IwAR0xyz",
    value: float = 0.0,
    currency: str = "USD",
    order_id: str = "LEAD_001",
    event_source_url: str = "https://brand.uz/",
    market: str = "",
    consent_granted: bool = True,
    ldu_enabled: bool | None = None,
    ldu_state: int = 0,
    special_ad_category: str = "NONE",
) -> dict:
    api_info = mloc.get_configured_api_version("META_GRAPH_API_VERSION", DEFAULT_GRAPH_API_VERSION)
    api_version = api_info["version"]

    det_market = mloc.detect_market(explicit_market=market, geo=country, currency=currency)
    m_id = det_market["market_id"]
    curr = (currency or det_market["currency"] or "USD").strip().upper()

    user_data: dict[str, object] = {
        "country": [sha256_norm(country)],
    }
    emq_points = 1.5

    if not consent_granted:
        # Strict Consent Gate: never hash or transmit PII (phone, email, name, city, fbp/fbc) without user consent
        consent_gate_status = "BLOCKED_PII_NO_CONSENT"
        pii_stripped = True
        emq_score = 1.5
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
        emq_score = round(min(10.0, emq_points), 1)

    event_id = f"evt_{event_name.lower()}_{re.sub(r'[^a-zA-Z0-9]+', '', order_id)}"

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

    rounded_val = mloc.round_currency(tcore.safe_float(value, default=0.0, min_val=0.0, field_name="value"), curr)

    event_obj: dict[str, object] = {
        "event_name": event_name,
        "event_time": int(time.time()),
        "action_source": "website",
        "event_id": event_id,
        "event_source_url": event_source_url,
        "user_data": user_data,
        "custom_data": {
            "currency": curr,
            "value": rounded_val,
            "order_id": order_id,
        },
        "data_processing_options": data_processing_options,
        "data_processing_options_country": data_processing_options_country,
        "data_processing_options_state": data_processing_options_state,
    }

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
        "currency": curr,
        "formatted_value": mloc.format_currency(rounded_val, curr),
        "consent_gate_status": consent_gate_status,
        "pii_stripped_due_to_no_consent": pii_stripped,
        "regulatory_compliance": regulatory_checks,
        "estimated_emq_score_10": emq_score,
        "emq_status": (
            "CONSENT_DENIED_ANONYMOUS"
            if pii_stripped
            else ("EXCELLENT (>=8.0)" if emq_score >= 8.0 else ("GOOD (6.5-7.9)" if emq_score >= 6.5 else "WEAK (<6.5 — add phone and fbc/fbp!)"))
        ),
        "deduplication_instruction": f"Browser Pixel MUST call `fbq('track', '{event_name}', {{...}}, {{eventID: '{event_id}'}})` for 100% deduplication.",
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
    p_capi.add_argument("--city", default="tashkent")
    p_capi.add_argument("--country", default="uz")
    p_capi.add_argument("--market", default="", help="Market pack (global, uz, us, eu, uk, mena, latam, sea, in)")
    p_capi.add_argument("--value", type=float, default=0.0)
    p_capi.add_argument("--currency", default="USD")
    p_capi.add_argument("--order-id", default="CRM_1001")
    p_capi.add_argument("--consent-granted", dest="consent_granted", action="store_true", default=True, help="User granted tracking/PII consent (default: True)")
    p_capi.add_argument("--no-consent", dest="consent_granted", action="store_false", help="User denied consent -> strip all PII from CAPI payload")
    p_capi.add_argument("--ldu", action="store_true", help="Enable Meta Limited Data Use (data_processing_options=['LDU'])")
    p_capi.add_argument("--ldu-state", type=int, default=0, help="US LDU state code (e.g. 1000 for California)")
    p_capi.add_argument("--special-ad-category", default="NONE", help="HOUSING, EMPLOYMENT, CREDIT, ISSUES_ELECTIONS_POLITICS, or NONE")
    p_capi.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "utm":
        res = build_utm_links(args.url, args.platform, args.campaign, args.bot)
    elif args.command == "capi-payload":
        res = build_capi_payload(
            event_name=args.event, phone=args.phone, email=args.email,
            first_name=args.first_name, city=args.city, country=args.country,
            value=args.value, currency=args.currency, order_id=args.order_id,
            market=args.market, consent_granted=args.consent_granted,
            ldu_enabled=(True if args.ldu else None), ldu_state=args.ldu_state,
            special_ad_category=args.special_ad_category,
        )
    else:
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


if __name__ == "__main__":
    raise SystemExit(main())
