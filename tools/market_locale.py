#!/usr/bin/env python3
"""Tyrion Global Market Pack, ISO 4217 Currency, BCP 47 Language & Locale Engine.

Provides market detection, currency formatting (including zero-decimal currencies like
JPY, KRW, UZS, VND, CLP, IDR), BCP 47 + RTL language metadata, and market pack loading
from `markets/<market_id>/pack.json`.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
MARKETS_DIR = VAULT / "markets"
LOCALES_DIR = VAULT / "locales"

SUPPORTED_MARKETS = ("global", "uz", "us", "eu", "uk", "mena", "latam", "sea", "in")

ZERO_DECIMAL_CURRENCIES = {
    "BIF", "CLP", "DJF", "GNF", "ISK", "JPY", "KMF", "KRW", "MGA",
    "PYG", "RWF", "UGX", "UZS", "VND", "VUV", "XAF", "XOF", "XPF", "IDR",
}

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CNY": "¥",
    "KRW": "₩",
    "INR": "₹",
    "BRL": "R$",
    "RUB": "₽",
    "TRY": "₺",
    "AED": "AED ",
    "SAR": "SAR ",
    "SGD": "S$",
    "CAD": "CA$",
    "AUD": "A$",
    "MXN": "MX$",
    "PLN": "zł ",
    "SEK": "kr ",
    "CHF": "CHF ",
    "UZS": "UZS ",
}

RTL_LANG_PREFIXES = ("ar", "he", "iw", "fa", "ur", "ps", "sd", "ug", "yi")

GEO_TO_MARKET = {
    # Uzbekistan & Central Asia
    "uz": "uz", "uzbekistan": "uz", "tashkent": "uz", "toshkent": "uz",
    "samarkand": "uz", "samarqand": "uz", "bukhara": "uz", "buxoro": "uz",
    "namangan": "uz", "andijan": "uz", "andijon": "uz", "fergana": "uz", "farg'ona": "uz",
    # EU / EEA
    "eu": "eu", "eea": "eu", "de": "eu", "germany": "eu", "deutschland": "eu", "berlin": "eu", "munich": "eu",
    "fr": "eu", "france": "eu", "paris": "eu", "es": "eu", "spain": "eu", "madrid": "eu",
    "it": "eu", "italy": "eu", "milan": "eu", "nl": "eu", "netherlands": "eu", "amsterdam": "eu",
    "pl": "eu", "poland": "eu", "warsaw": "eu", "se": "eu", "sweden": "eu", "at": "eu", "austria": "eu",
    "be": "eu", "belgium": "eu", "ie": "eu", "ireland": "eu", "pt": "eu", "portugal": "eu",
    # UK
    "uk": "uk", "gb": "uk", "united kingdom": "uk", "britain": "uk", "england": "uk", "london": "uk", "manchester": "uk",
    # US
    "us": "us", "usa": "us", "united states": "us", "california": "us", "new york": "us", "texas": "us", "florida": "us", "chicago": "us",
    # MENA
    "mena": "mena", "gcc": "mena", "ae": "mena", "uae": "mena", "dubai": "mena", "abu dhabi": "mena",
    "sa": "mena", "ksa": "mena", "saudi": "mena", "saudi arabia": "mena", "riyadh": "mena", "jeddah": "mena",
    "qa": "mena", "qatar": "mena", "kw": "mena", "kuwait": "mena", "eg": "mena", "egypt": "mena", "cairo": "mena",
    # LATAM
    "latam": "latam", "br": "latam", "brazil": "latam", "brasil": "latam", "sao paulo": "latam",
    "mx": "latam", "mexico": "latam", "cdmx": "latam", "co": "latam", "colombia": "latam", "bogota": "latam",
    "cl": "latam", "chile": "latam", "ar": "latam", "argentina": "latam", "pe": "latam", "peru": "latam",
    # SEA
    "sea": "sea", "sg": "sea", "singapore": "sea", "id": "sea", "indonesia": "sea", "jakarta": "sea",
    "th": "sea", "thailand": "sea", "bangkok": "sea", "vn": "sea", "vietnam": "sea",
    "my": "sea", "malaysia": "sea", "kuala lumpur": "sea", "ph": "sea", "philippines": "sea", "manila": "sea",
    # India
    "in": "in", "india": "in", "mumbai": "in", "delhi": "in", "bengaluru": "in", "bangalore": "in", "hyderabad": "in",
}


def load_market_pack(market_id: str | None = None) -> dict[str, Any]:
    m_id = (market_id or os.environ.get("TYRION_MARKET") or "global").strip().lower()
    if m_id not in SUPPORTED_MARKETS:
        m_id = "global"
    pack_path = MARKETS_DIR / m_id / "pack.json"
    if not pack_path.is_file():
        pack_path = MARKETS_DIR / "global" / "pack.json"
    try:
        data = json.loads(pack_path.read_text(encoding="utf-8"))
        data["pack_path"] = f"markets/{data.get('market_id', m_id)}/pack.json"
        data["readme_path"] = f"markets/{data.get('market_id', m_id)}/README.md"
        data["benchmarks_path"] = f"markets/{data.get('market_id', m_id)}/benchmarks.md"
        return data
    except Exception:
        return {
            "market_id": "global",
            "display_name": "Global",
            "default_currency": "USD",
            "supported_currencies": ["USD"],
            "payment_methods": ["Card", "Apple Pay", "PayPal"],
            "bnpl_providers": ["Klarna", "Afterpay", "Affirm"],
            "price_anchor_template": "Or 4 interest-free payments of {installment} with {bnpl}",
            "primary_funnels": ["Ad -> Landing Page -> Checkout"],
            "messaging_channels": ["WhatsApp", "Email"],
            "regulations": {"frameworks": ["GDPR", "CCPA"], "consent_required_for_pii": True, "special_ad_categories": []},
            "languages": ["en"],
            "rtl_languages": ["ar", "he"],
            "niche_taxonomy": {},
            "pack_path": "markets/global/pack.json",
            "readme_path": "markets/global/README.md",
            "benchmarks_path": "markets/global/benchmarks.md",
        }


def format_currency(amount: float | int, currency: str = "USD") -> str:
    code = (currency or "USD").strip().upper()
    sym = CURRENCY_SYMBOLS.get(code, f"{code} ")
    val = float(amount)
    if code in ZERO_DECIMAL_CURRENCIES:
        int_val = int(round(val))
        if code == "UZS":
            return f"{int_val:,} UZS"
        if sym.endswith(" "):
            return f"{sym}{int_val:,}"
        return f"{sym}{int_val:,}"
    if sym.endswith(" "):
        return f"{sym}{val:,.2f}"
    return f"{sym}{val:,.2f}"


def is_rtl_language(lang: str) -> bool:
    clean = (lang or "").strip().lower().replace("_", "-")
    return any(clean == p or clean.startswith(p + "-") for p in RTL_LANG_PREFIXES)


def normalize_bcp47_language(lang: str) -> dict[str, Any]:
    raw = (lang or "en").strip()
    mapping = {
        "uz_latin": "uz-Latn",
        "uz_cyrillic": "uz-Cyrl",
        "uz": "uz-Latn",
        "ru": "ru",
        "en": "en",
        "de": "de",
        "fr": "fr",
        "es": "es",
        "pt": "pt-BR",
        "ar": "ar",
        "he": "he",
        "hi": "hi",
        "id": "id",
        "th": "th",
        "ja": "ja",
        "ko": "ko",
        "tr": "tr",
    }
    bcp47 = mapping.get(raw.lower(), raw.replace("_", "-"))
    rtl = is_rtl_language(bcp47)
    return {
        "input": raw,
        "bcp47": bcp47,
        "is_rtl": rtl,
        "rtl_formatting_note": (
            "RTL language active: enforce logical bidi punctuation, keep currency/number tokens isolated, "
            "and right-align headline/caption overlays in 9:16 & 4:5 creatives."
            if rtl else None
        ),
    }


def detect_market(
    text: str = "",
    explicit_market: str | None = None,
    geo: str | None = None,
    currency: str | None = None,
    detected_lang: str | None = None,
) -> dict[str, Any]:
    # 1. Explicit argument or env override
    for candidate in (explicit_market, os.environ.get("TYRION_MARKET")):
        if candidate and candidate.strip().lower() in SUPPORTED_MARKETS:
            m_id = candidate.strip().lower()
            pack = load_market_pack(m_id)
            curr = (currency or pack["default_currency"]).strip().upper()
            return _enrich_detection(pack, curr, detected_lang or "en", "explicit")

    # 2. Geo parameter lookup
    if geo:
        g_clean = geo.strip().lower()
        if g_clean in GEO_TO_MARKET:
            pack = load_market_pack(GEO_TO_MARKET[g_clean])
            curr = (currency or pack["default_currency"]).strip().upper()
            return _enrich_detection(pack, curr, detected_lang or "en", f"geo:{geo}")

    # 3. Query text inspection for countries, cities, payment methods, currencies, or regulations
    q_low = (text or "").lower()
    keyword_rules = [
        ("uz", (r"\btoshkent\b", r"\btashkent\b", r"\bo'zbekiston\b", r"\bozbekiston\b", r"\buzbekistan\b",
                r"\bsamarqand\b", r"\bbuxoro\b", r"\bpayme\b", r"\buzum\b", r"\balif nasiya\b", r"\bso'm\b", r"\buzs\b",
                r"ташкент", r"узбекист", r"самарканд", r"бухар")),
        ("eu", (r"\bgermany\b", r"\bdeutschland\b", r"\bberlin\b", r"\bfrance\b", r"\bparis\b", r"\bspain\b",
                r"\bitaly\b", r"\bnetherlands\b", r"\bpoland\b", r"\bsweden\b", r"\beuropean union\b",
                r"\beu\b", r"\beea\b", r"\bgdpr\b", r"\beur\b", r"€")),
        ("uk", (r"\bunited kingdom\b", r"\buk\b", r"\blondon\b", r"\bbritain\b", r"\bgbp\b", r"£")),
        ("us", (r"\bunited states\b", r"\busa\b", r"\bcalifornia\b", r"\bnew york\b", r"\btexas\b", r"\bccpa\b", r"\baffirm\b")),
        ("mena", (r"\bdubai\b", r"\buae\b", r"\bsaudi\b", r"\briyadh\b", r"\bksa\b", r"\bmena\b", r"\btabby\b", r"\btamara\b", r"\baed\b", r"\bsar\b")),
        ("latam", (r"\bbrazil\b", r"\bbrasil\b", r"\bmexico\b", r"\bcolombia\b", r"\blatam\b", r"\bpix\b", r"\blgpd\b", r"\bbrl\b", r"\bmxn\b")),
        ("sea", (r"\bsingapore\b", r"\bindonesia\b", r"\bthailand\b", r"\bvietnam\b", r"\bmalaysia\b", r"\bphilippines\b", r"\bgrabpay\b", r"\batome\b", r"\bsgd\b")),
        ("in", (r"\bindia\b", r"\bmumbai\b", r"\bbengaluru\b", r"\bdelhi\b", r"\bupi\b", r"\brazorpay\b", r"\bdpdp\b", r"\binr\b", r"₹")),
    ]
    for m_id, patterns in keyword_rules:
        if any(re.search(pat, q_low) for pat in patterns):
            pack = load_market_pack(m_id)
            curr = (currency or pack["default_currency"]).strip().upper()
            return _enrich_detection(pack, curr, detected_lang or "en", f"query_keyword:{m_id}")

    # 4. Currency hint fallback
    if currency:
        c_up = currency.strip().upper()
        curr_map = {"UZS": "uz", "EUR": "eu", "GBP": "uk", "AED": "mena", "SAR": "mena", "BRL": "latam", "MXN": "latam", "SGD": "sea", "IDR": "sea", "INR": "in"}
        if c_up in curr_map:
            pack = load_market_pack(curr_map[c_up])
            return _enrich_detection(pack, c_up, detected_lang or "en", f"currency:{c_up}")

    # 5. Uzbek language script fallback -> uz market
    if detected_lang in ("uz_latin", "uz_cyrillic", "uz", "uz-Latn", "uz-Cyrl"):
        pack = load_market_pack("uz")
        curr = (currency or "UZS").strip().upper()
        return _enrich_detection(pack, curr, detected_lang, "language_uz")

    # 6. Default: global
    pack = load_market_pack("global")
    curr = (currency or pack["default_currency"]).strip().upper()
    return _enrich_detection(pack, curr, detected_lang or "en", "default_global")


def _enrich_detection(pack: dict[str, Any], currency: str, lang: str, source: str) -> dict[str, Any]:
    lang_info = normalize_bcp47_language(lang)
    return {
        "market_id": pack["market_id"],
        "display_name": pack["display_name"],
        "detection_source": source,
        "currency": currency,
        "is_zero_decimal_currency": currency in ZERO_DECIMAL_CURRENCIES,
        "payment_methods": pack.get("payment_methods", []),
        "bnpl_providers": pack.get("bnpl_providers", []),
        "price_anchor_template": pack.get("price_anchor_template", ""),
        "primary_funnels": pack.get("primary_funnels", []),
        "messaging_channels": pack.get("messaging_channels", []),
        "regulations": pack.get("regulations", {}),
        "language": lang_info["bcp47"],
        "is_rtl": lang_info["is_rtl"],
        "rtl_formatting_note": lang_info["rtl_formatting_note"],
        "pack_path": pack.get("pack_path", f"markets/{pack['market_id']}/pack.json"),
        "readme_path": pack.get("readme_path", f"markets/{pack['market_id']}/README.md"),
        "benchmarks_path": pack.get("benchmarks_path", f"markets/{pack['market_id']}/benchmarks.md"),
    }


def load_locale_messages(locale: str = "en") -> dict[str, str]:
    loc = (locale or "en").strip().lower()
    if loc.startswith("uz"):
        loc = "uz"
    elif loc.startswith("ru"):
        loc = "ru"
    else:
        loc = "en"
    p = LOCALES_DIR / loc / "messages.json"
    if not p.is_file():
        p = LOCALES_DIR / "en" / "messages.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"locale": "en", "language_name": "English"}


def round_currency(amount: float | int, currency: str = "USD") -> float | int:
    code = (currency or "USD").strip().upper()
    if code in ZERO_DECIMAL_CURRENCIES:
        return int(round(float(amount)))
    return round(float(amount), 2)


def get_configured_api_version(env_key: str = "META_GRAPH_API_VERSION", default: str = "v26.0") -> dict[str, Any]:
    raw = os.environ.get(env_key, "").strip()
    if not raw:
        env_file = VAULT / ".env"
        if env_file.is_file():
            for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.strip().startswith(f"{env_key}="):
                    raw = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    ver = raw if raw else default
    m = re.match(r"^v?(\d+)(?:\.(\d+))?$", ver.strip(), re.I)
    major = int(m.group(1)) if m else 26
    is_deprecated = major < 25
    warning = (
        f"Configured {env_key}={ver} is older than v25.0 and may be deprecated or sunset by Meta Graph API; upgrade to {default}."
        if is_deprecated else None
    )
    return {
        "env_key": env_key,
        "version": ver if ver.startswith("v") else f"v{ver}",
        "major": major,
        "is_deprecated": is_deprecated,
        "warning": warning,
    }
