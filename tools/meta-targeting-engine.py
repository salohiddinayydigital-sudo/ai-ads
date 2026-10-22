#!/usr/bin/env python3
"""Tyrion v6.0 Detailed Targeting Discovery, Verification & Relevance Ranking Engine (`tools/meta-targeting-engine.py`).

Purpose:
  Discover, verify, rank, and explain Meta Ads Detailed Targeting options (Interests, Behaviors, Demographics)
  for a specific product/service, customer problem, market, and campaign objective using official read-only
  Meta Marketing API v26.0 endpoints — without hallucinating interests, fabricating IDs, or blindly trusting API order.

Official Read-Only Meta Marketing API Endpoints:
  1. Global Targeting Search      : `GET /{api_version}/search?type=adinterest&q={q}&limit={limit}&locale={locale}`
  2. Account Targeting Search     : `GET /{api_version}/act_{ad_account_id}/targetingsearch?q={q}&limit={limit}&locale={locale}`
  3. Account Targeting Suggestions: `GET /{api_version}/act_{ad_account_id}/targetingsuggestions?targeting_list={json}`
  4. Account Targeting Validation : `GET /{api_version}/act_{ad_account_id}/targetingvalidation?targeting_list={json}`

6 Strict Verification Statuses (`validation_status`):
  - `VERIFIED_AVAILABLE`          : Returned by official Meta API search AND confirmed `valid: true` by `targetingvalidation`.
  - `FOUND_NOT_VALIDATED`         : Returned by official Meta API search (`/search` or `targetingsearch`), but `targetingvalidation` was not run.
  - `UNAVAILABLE_OR_CONSOLIDATED` : Flagged by Meta API as invalid (`valid: false`), deprecated, or consolidated into a replacement option.
  - `RELATED_UNVERIFIED`          : Candidate search idea, business-context expansion, or static taxonomy seed — NOT verified in Meta API!
  - `NOT_FOUND`                   : Live API search succeeded (`HTTP 200`, `data: []`) and returned zero matching options for this query.
  - `API_UNAVAILABLE`             : Live API search could not be completed (missing token, HTTP 401/403, HTTP 429, HTTP 5xx, network failure, or malformed payload).
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import tyrion_core as tcore  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

DEFAULT_GRAPH_API_VERSION = "v26.0"

# 6 Canonical Statuses
STATUS_VERIFIED_AVAILABLE = "VERIFIED_AVAILABLE"
STATUS_FOUND_NOT_VALIDATED = "FOUND_NOT_VALIDATED"
STATUS_UNAVAILABLE_OR_CONSOLIDATED = "UNAVAILABLE_OR_CONSOLIDATED"
STATUS_RELATED_UNVERIFIED = "RELATED_UNVERIFIED"
STATUS_NOT_FOUND = "NOT_FOUND"
STATUS_API_UNAVAILABLE = "API_UNAVAILABLE"

ALL_VALID_STATUSES = (
    STATUS_VERIFIED_AVAILABLE,
    STATUS_FOUND_NOT_VALIDATED,
    STATUS_UNAVAILABLE_OR_CONSOLIDATED,
    STATUS_RELATED_UNVERIFIED,
    STATUS_NOT_FOUND,
    STATUS_API_UNAVAILABLE,
)

SPECIAL_AD_CATEGORIES = ("NONE", "HOUSING", "EMPLOYMENT", "CREDIT", "ISSUES_ELECTIONS_POLITICS")

# Rich multilingual business-concept to Meta search-candidate map (UZ Latin, UZ Cyrillic, RU, EN).
# IMPORTANT: These are SEARCH QUERIES ONLY, never treated as verified Meta interests without live API proof!
MULTILINGUAL_QUERY_SYNONYMS: dict[str, list[str]] = {
    # Real estate / Ko'chmas mulk / Недвижимость
    "ko'chmas mulk": ["Real estate", "Property", "Apartment", "Mortgage loan", "Real estate investing"],
    "kochmas mulk": ["Real estate", "Property", "Apartment", "Mortgage loan"],
    "xonadon": ["Apartment", "Condominium", "Housing", "Interior design"],
    "kvartira": ["Apartment", "Condominium", "Real estate", "Housing"],
    "novostroyka": ["Apartment", "Real estate", "New construction", "Property investment"],
    "yangi uylar": ["Apartment", "Real estate", "Housing", "Mortgage loan"],
    "ipoteka": ["Mortgage loan", "Home equity", "Real estate", "Personal finance"],
    "interyer": ["Interior design", "Home improvement", "Furniture", "Architecture"],
    "ta'mirlash": ["Home improvement", "Interior design", "Renovation", "Furniture"],
    "remont": ["Home improvement", "Interior design", "Renovation", "Construction"],
    "ofis": ["Commercial property", "Office space", "Real estate", "Entrepreneurship"],
    "новостройки": ["Apartment", "Real estate", "New construction", "Property investment"],
    "кўчмас мулк": ["Real estate", "Property", "Apartment", "Mortgage loan"],
    "хонадон": ["Apartment", "Housing", "Interior design"],
    "ипотека": ["Mortgage loan", "Real estate", "Personal finance"],
    "недвижимость": ["Real estate", "Property", "Apartment", "Real estate investing"],
    "квартира": ["Apartment", "Condominium", "Interior design", "Housing"],
    "ремонт": ["Home improvement", "Interior design", "Furniture"],
    "интерьер": ["Interior design", "Home improvement", "Furniture", "Architecture"],
    "застройщик": ["Real estate", "Property investment", "Apartment"],
    "жилой комплекс": ["Apartment", "Condominium", "Real estate"],
    # Education / Ta'lim / Образование / EdTech
    "ta'lim": ["Higher education", "Online learning", "Education", "Career development"],
    "talim": ["Higher education", "Online learning", "Education"],
    "kurs": ["Online learning", "Professional certification", "Vocational education", "Career development"],
    "o'quv markazi": ["Education", "Language school", "Online learning", "Tutoring"],
    "oquv markazi": ["Education", "Language school", "Online learning"],
    "ingliz tili": ["English language", "IELTS", "Language school", "TOEFL"],
    "ielts": ["IELTS", "English language", "TOEFL", "Study abroad"],
    "dasturlash": ["Computer programming", "Software development", "Web development", "Information technology"],
    "it kurs": ["Computer programming", "Software development", "Online learning", "Information technology"],
    "matematika": ["Mathematics", "STEM fields", "Higher education", "Tutoring"],
    "abituriyent": ["Higher education", "University", "College", "Entrance examination"],
    "xususiy maktab": ["Private school", "Primary education", "Parenting", "Montessori education"],
    "таълим": ["Higher education", "Online learning", "Education"],
    "инглиз тили": ["English language", "IELTS", "Language school"],
    "ўқув маркази": ["Education", "Language school", "Online learning"],
    "дастурлаш": ["Computer programming", "Software development", "Information technology"],
    "образование": ["Higher education", "Online learning", "Education"],
    "курсы": ["Online learning", "Professional certification", "Career development"],
    "английский язык": ["English language", "IELTS", "Language school"],
    "программирование": ["Computer programming", "Software development", "Web development"],
    "частная школа": ["Private school", "Parenting", "Education"],
    # Medical / Tibbiyot / Медицина / Стоматология / Клиника
    "stomatologiya": ["Dentistry", "Cosmetic dentistry", "Oral hygiene", "Dental implant"],
    "tish": ["Dentistry", "Cosmetic dentistry", "Oral hygiene", "Orthodontics"],
    "implant": ["Dental implant", "Dentistry", "Cosmetic dentistry"],
    "breket": ["Orthodontics", "Dentistry", "Cosmetic dentistry"],
    "vinir": ["Cosmetic dentistry", "Dentistry", "Smile"],
    "klinika": ["Healthcare", "Medicine", "Physical therapy", "Wellness"],
    "tibbiyot": ["Healthcare", "Medicine", "Wellness", "Medical specialty"],
    "diagnostika": ["Medical diagnosis", "Healthcare", "Preventive healthcare", "Medicine"],
    "kardiologiya": ["Cardiology", "Healthcare", "Medicine", "Preventive healthcare"],
    "dermatologiya": ["Dermatology", "Skin care", "Cosmetology", "Healthcare"],
    "стоматология": ["Dentistry", "Cosmetic dentistry", "Oral hygiene", "Dental implant"],
    "имплантация": ["Dental implant", "Dentistry", "Cosmetic dentistry"],
    "виниры": ["Cosmetic dentistry", "Dentistry"],
    "брекеты": ["Orthodontics", "Dentistry", "Cosmetic dentistry"],
    "клиника": ["Healthcare", "Medicine", "Wellness", "Medical diagnosis"],
    "медицина": ["Healthcare", "Medicine", "Wellness"],
    "здоровье": ["Health & wellness", "Healthcare", "Preventive healthcare", "Fitness and wellness"],
    # E-commerce, Fashion, Electronics & Home
    "kiyim": ["Clothing", "Shopping and fashion", "Boutique", "Online shopping"],
    "erkaklar kostyumi": ["Men's clothing", "Suit (clothing)", "Formal wear", "Shopping and fashion"],
    "kostyum": ["Suit (clothing)", "Formal wear", "Men's clothing", "Fashion"],
    "ayollar kiyimi": ["Women's clothing", "Dresses", "Boutique", "Shopping and fashion"],
    "oyoq kiyim": ["Shoes", "Footwear", "Sneakers", "Shopping and fashion"],
    "krossovka": ["Sneakers", "Shoes", "Sportswear", "Athletic shoe"],
    "onlayn do'kon": ["Online shopping", "E-commerce", "Discount store", "Shopping"],
    "maishiy texnika": ["Home appliances", "Consumer electronics", "Kitchen appliance", "Smart home"],
    "telefon": ["Smartphone", "Mobile phones", "Consumer electronics", "Online shopping"],
    "mebel": ["Furniture", "Interior design", "Home improvement", "Living room"],
    "кийим": ["Clothing", "Shopping and fashion", "Online shopping"],
    "мебел": ["Furniture", "Interior design", "Home improvement"],
    "одежда": ["Clothing", "Shopping and fashion", "Boutique", "Online shopping"],
    "мужской костюм": ["Men's clothing", "Suit (clothing)", "Formal wear"],
    "женская одежда": ["Women's clothing", "Dresses", "Boutique", "Shopping and fashion"],
    "обувь": ["Shoes", "Footwear", "Shopping and fashion"],
    "мебель": ["Furniture", "Interior design", "Home improvement"],
    "бытовая техника": ["Home appliances", "Consumer electronics", "Kitchen appliance"],
    # Beauty, Cosmetics & Aesthetics
    "kosmetika": ["Cosmetics", "Skin care", "Beauty salon", "Fragrances"],
    "teri parvarishi": ["Skin care", "Cosmetics", "Natural skin care", "Anti-aging cream"],
    "atir": ["Fragrances", "Perfume", "Luxury goods", "Cosmetics"],
    "parfyumeriya": ["Fragrances", "Perfume", "Cosmetics", "Luxury goods"],
    "go'zallik saloni": ["Beauty salon", "Cosmetology", "Hair care", "Skin care"],
    "soch": ["Hair care", "Hairstyle", "Beauty salon", "Shampoo"],
    "косметика": ["Cosmetics", "Skin care", "Beauty salon"],
    "уход за кожей": ["Skin care", "Cosmetics", "Natural skin care", "Beauty salon"],
    "парфюмерия": ["Fragrances", "Perfume", "Luxury goods"],
    "духи": ["Perfume", "Fragrances", "Luxury goods"],
    "салон красоты": ["Beauty salon", "Cosmetology", "Skin care", "Hair care"],
    # Auto & Detailing
    "avtomobil": ["Automobile", "Car dealership", "Auto detailing", "Automotive repair shop"],
    "mashina": ["Automobile", "Vehicles", "Car dealership", "SUV"],
    "avtoservis": ["Automotive repair shop", "Auto detailing", "Vehicle maintenance", "Car parts"],
    "deteyling": ["Auto detailing", "Car wash", "Automobile", "Luxury vehicle"],
    "keramika": ["Auto detailing", "Car wash", "Automobile"],
    "tonirovka": ["Auto detailing", "Automobile", "Car accessories"],
    "ehtiyot qismlar": ["Car parts", "Automotive repair shop", "Vehicle maintenance"],
    "электромобиль": ["Electric vehicle", "Hybrid vehicle", "Automobile"],
    "автомобиль": ["Automobile", "Car dealership", "Auto detailing"],
    "автосервис": ["Automotive repair shop", "Auto detailing", "Vehicle maintenance"],
    "детейлинг": ["Auto detailing", "Car wash", "Automobile", "Luxury vehicle"],
    "запчасти": ["Car parts", "Automotive repair shop", "Vehicle maintenance"],
    # B2B, SaaS, Finance & Consulting
    "biznes": ["Small and medium-sized enterprises", "Entrepreneurship", "Business management"],
    "tadbirkor": ["Entrepreneurship", "Small business owners", "Business management", "Commerce"],
    "crm": ["Customer relationship management", "Enterprise software", "Sales", "Marketing automation"],
    "erp": ["Enterprise resource planning", "Supply chain management", "Business software"],
    "avtomatlashtirish": ["Marketing automation", "Business software", "Customer relationship management", "Cloud computing"],
    "buxgalteriya": ["Accounting", "Accounting software", "Corporate finance", "Tax"],
    "ulgurji": ["Wholesale", "Business-to-business", "Retail", "Supply chain"],
    "бизнес": ["Small and medium-sized enterprises", "Entrepreneurship", "Business management"],
    "предприниматель": ["Entrepreneurship", "Small business owners", "Business management"],
    "автоматизация": ["Business software", "Customer relationship management", "Enterprise resource planning"],
    "бухгалтерия": ["Accounting", "Corporate finance", "Business management"],
    "оптом": ["Wholesale", "Business-to-business", "Commerce"],
    # Local, Fitness, HoReCa & Travel
    "fitnes": ["Physical fitness", "Gym", "Weight training", "Yoga", "Personal trainer"],
    "sport zal": ["Gym", "Physical fitness", "Weight training", "Bodybuilding"],
    "ozish": ["Weight loss", "Physical fitness", "Healthy diet", "Nutrition"],
    "restoran": ["Restaurants", "Fine dining", "Dining out", "Coffeehouses"],
    "kafe": ["Coffeehouses", "Restaurants", "Dining out", "Dessert"],
    "yetkazib berish": ["Food delivery", "Online food ordering", "Fast food", "Restaurants"],
    "mehmonxona": ["Hotel", "Tourism", "Resort", "Travel"],
    "sayohat": ["Travel", "Tourism", "Vacation", "Frequent Travelers"],
    "turizm": ["Tourism", "Travel", "Travel agency", "Vacation"],
    "фитнес": ["Physical fitness", "Gym", "Weight training", "Yoga"],
    "похудение": ["Weight loss", "Physical fitness", "Healthy diet"],
    "ресторан": ["Restaurants", "Dining out", "Fine dining"],
    "доставка еды": ["Food delivery", "Online food ordering", "Restaurants"],
    "туризм": ["Tourism", "Travel", "Vacation", "Hotel"],
    "путешествия": ["Travel", "Tourism", "Frequent Travelers", "Vacation"],
}

NICHE_SEED_CANDIDATES: dict[str, list[str]] = {
    "ecom": ["Online shopping", "Shopping and fashion", "Boutique", "Consumer electronics", "Engaged Shoppers"],
    "edu": ["Higher education", "Online learning", "Language school", "IELTS", "Career development"],
    "real-estate": ["Real estate", "Property investment", "Apartment", "Mortgage loan", "Interior design"],
    "medical": ["Healthcare", "Dentistry", "Cosmetic dentistry", "Physical therapy", "Wellness"],
    "b2b": ["Small and medium-sized enterprises", "Entrepreneurship", "Business management", "Digital marketing"],
    "beauty": ["Cosmetics", "Fragrances", "Beauty salon", "Skin care", "Luxury goods"],
    "auto": ["Automobile", "Car dealership", "Auto detailing", "SUV", "Automotive repair shop"],
    "local": ["Physical fitness", "Gym", "Restaurants", "Tourism", "Hotel"],
}

# Complementary & adjacent category signals by niche for richer discovery and semantic scoring
NICHE_COMPLEMENTARY_SIGNALS: dict[str, dict[str, list[str]]] = {
    "ecom": {
        "problems": ["time saving shopping", "wardrobe upgrade", "gift buying", "home organization"],
        "complementary": ["Fashion accessories", "Footwear", "Home decor", "Loyalty program", "Coupon"],
        "intent_signals": ["Engaged Shoppers", "Online shopping", "Boutique", "Shopping and fashion", "Department store"],
        "expected_categories": ["shopping", "fashion", "retail", "consumer electronics", "apparel", "commerce", "behaviors"],
    },
    "edu": {
        "problems": ["career advancement", "university admission", "language fluency", "skill certification"],
        "complementary": ["Study abroad", "Scholarship", "Educational technology", "Book", "Professional certification"],
        "intent_signals": ["Online learning", "Higher education", "Language school", "IELTS", "TOEFL", "Career development"],
        "expected_categories": ["education", "learning", "language", "university", "career", "school", "science"],
    },
    "real-estate": {
        "problems": ["buying first home", "property investment return", "family housing upgrade", "commercial relocation"],
        "complementary": ["Interior design", "Architecture", "Furniture", "Home improvement", "Property management"],
        "intent_signals": ["Real estate", "Property", "Apartment", "Condominium", "Mortgage loan", "Real estate investing", "Luxury real estate"],
        "expected_categories": ["real estate", "property", "housing", "home", "architecture", "finance", "mortgage", "investment"],
    },
    "medical": {
        "problems": ["pain relief", "dental restoration", "aesthetic smile", "preventive checkup", "skin health"],
        "complementary": ["Oral hygiene", "Wellness", "Health insurance", "Healthy diet", "Dermatology"],
        "intent_signals": ["Dentistry", "Cosmetic dentistry", "Dental implant", "Orthodontics", "Healthcare", "Medicine", "Physical therapy"],
        "expected_categories": ["health", "medical", "dentistry", "wellness", "fitness", "medicine", "care"],
    },
    "b2b": {
        "problems": ["sales pipeline leakage", "manual workflow inefficiency", "accounting automation", "lead generation"],
        "complementary": ["Cloud computing", "Project management", "Business intelligence", "E-commerce", "B2B marketing"],
        "intent_signals": ["Small and medium-sized enterprises", "Entrepreneurship", "Business management", "Customer relationship management", "Enterprise software", "Facebook Page Admins"],
        "expected_categories": ["business", "industry", "entrepreneurship", "management", "software", "finance", "marketing", "small business"],
    },
    "beauty": {
        "problems": ["anti-aging", "skin hydration", "signature scent", "bridal/event makeover"],
        "complementary": ["Luxury goods", "Fashion accessories", "Spa", "Wellness", "Organic product"],
        "intent_signals": ["Cosmetics", "Skin care", "Fragrances", "Perfume", "Beauty salon", "Hair care"],
        "expected_categories": ["beauty", "cosmetics", "skin care", "fragrance", "fashion", "personal care", "spa"],
    },
    "auto": {
        "problems": ["paint protection", "vehicle maintenance", "car resale value", "reliable repair"],
        "complementary": ["Vehicle insurance", "Car accessories", "Motor oil", "Tires", "Electric vehicle"],
        "intent_signals": ["Automobile", "Auto detailing", "Automotive repair shop", "Car dealership", "SUV", "Car wash"],
        "expected_categories": ["vehicles", "automobile", "automotive", "cars", "transportation"],
    },
    "local": {
        "problems": ["fitness transformation", "family dining", "weekend getaway", "stress relief"],
        "complementary": ["Healthy diet", "Sportswear", "Coffee", "Event planning", "Recreation"],
        "intent_signals": ["Physical fitness", "Gym", "Weight training", "Restaurants", "Coffeehouses", "Hotel", "Tourism"],
        "expected_categories": ["fitness", "food", "drink", "restaurants", "travel", "tourism", "hotel", "recreation", "sports"],
    },
}

# Known off-target / entertainment / noise patterns that often pollute Meta keyword search results
NOISE_AND_IRRELEVANT_PATTERNS = (
    r"\bfreebies\b", r"\bfunny\b", r"\bmemes?\b", r"\bhoroscope\b", r"\bastrology\b",
    r"\bvideo games?\b", r"\bonline poker\b", r"\bgambling\b", r"\blottery\b",
    r"\b(band|musical group|rock band|tv series|television show|film|movie|anime|cartoon)\b",
    r"\bgossip\b", r"\btabloid\b", r"\bprank\b",
)

OVERLY_BROAD_GENERIC_NAMES = {
    "music", "entertainment", "movies", "sports", "news", "technology", "food",
    "friendship", "love", "life", "happiness", "nature", "photography", "art",
    "internet", "social media", "mobile phone", "television", "comedy", "games",
}

SOLVENTNOST_HYPOTHESES: list[dict[str, str]] = [
    {
        "candidate_name": "Engaged Shoppers",
        "category_hint": "behaviors",
        "hypothesis_type": "MARKETING_HYPOTHESIS",
        "note": "So'nggi 7 kunda reklamadagi 'Shop Now' CTA tugmasini bosgan foydalanuvchilar. Yuqori daromad kafolati emas, balki onlayn xarid faolligi gipotezasi.",
    },
    {
        "candidate_name": "Frequent International Travelers",
        "category_hint": "behaviors",
        "hypothesis_type": "MARKETING_HYPOTHESIS",
        "note": "Chet elga safar qiluvchilar. Yuqori to'lov qobiliyati uchun bilvosita marketing gipotezasi — xizmat sohasiga qarab A/B sinov talab etiladi.",
    },
    {
        "candidate_name": "Facebook Page Admins",
        "category_hint": "behaviors",
        "hypothesis_type": "MARKETING_HYPOTHESIS",
        "note": "Biznes sahifa administratorlari. B2B qaror qabul qiluvchilar uchun gipoteza (SMM mutaxassislari ham kirib qolishi mumkin).",
    },
    {
        "candidate_name": "Mobile Device User: Flagship / iPhone Pro Series",
        "category_hint": "user_device",
        "hypothesis_type": "MARKETING_HYPOTHESIS",
        "note": "Qurilma modeli daromadning mutlaq isboti emas (nasiyaga olingan bo'lishi mumkin) — faqat tekshiriladigan gipoteza sifatida qo'llang.",
    },
]

FAILURE_DIAGNOSTIC_GUIDE: dict[str, dict[str, str]] = {
    "MISSING_TOKEN": {
        "category_explanation": "META_ACCESS_TOKEN muhit o'zgaruvchisi o'rnatilmagan yoki bo'sh. Shu sababli Meta Graph API ga real HTTP so'rov yuborilmadi.",
        "next_diagnostic_step": "1) `.env` fayliga yoki terminalga `export META_ACCESS_TOKEN='EAA...'` (kamida `ads_read` ruxsatiga ega System User yoki User token) kiriting; 2) `python3 tools/meta-targeting-engine.py search --product '...' --account-id act_...` buyrug'ini qayta ishga tushiring.",
    },
    "AUTH_401": {
        "category_explanation": "Autentifikatsiya xatosi (HTTP 401): `META_ACCESS_TOKEN` muddati tugagan (expired), bekor qilingan yoki noto'g'ri formatda.",
        "next_diagnostic_step": "Meta Business Suite -> System Users oynasidan yangi `ads_read` tokeni generatsiya qiling va `META_ACCESS_TOKEN` ni yangilang.",
    },
    "PERMISSION_403": {
        "category_explanation": "Ruxsat xatosi (HTTP 403): Token yaroqli, ammo ko'rsatilgan `act_<ad_account_id>` reklama akkauntiga `ads_read` / `ads_management` ruxsati yo'q yoki App Development rejimida bloklangan.",
        "next_diagnostic_step": "Meta Business Settings -> Ad Accounts bo'limida ushbu System User/foydalanuvchiga `act_<id>` akkaunti biriktirilganini tekshiring yoki `--account-id` siz global `/search?type=adinterest` rejimida sinab ko'ring.",
    },
    "RATE_LIMIT_429": {
        "category_explanation": "So'rovlar limiti oshib ketdi (HTTP 429 Rate Limit): Meta Graph API vaqtinchalik cheklov o'rnatdi.",
        "next_diagnostic_step": "60–120 soniya kuting, `--max-queries` va `--max-pages` sonini kamaytiring hamda `--cache-file output/.cache/targeting_cache.json` orqali keshni yoqing.",
    },
    "SERVER_5XX": {
        "category_explanation": "Meta Graph API serverlarida vaqtinchalik ichki xatolik (HTTP 500/502/503/504).",
        "next_diagnostic_step": "Avtomatik qayta urinish (backoff) dan so'ng ham server javob bermadi; bir necha daqiqadan keyin qayta urinib ko'ring.",
    },
    "INVALID_JSON": {
        "category_explanation": "Meta API yoki proksi-server yaroqsiz (buzilgan) JSON oqimini qaytardi.",
        "next_diagnostic_step": "`META_GRAPH_API_BASE_URL` manzili (`https://graph.facebook.com`) va tarmoq/proksi sozlamalarini tekshiring.",
    },
    "UNEXPECTED_PAYLOAD_SHAPE": {
        "category_explanation": "Meta API HTTP 200 qaytardi, lekin javob tarkibida kutilgan `data: [...]` ro'yxati yo'q.",
        "next_diagnostic_step": "Endpoint URL va `META_GRAPH_API_VERSION` (`v26.0`) mosligini tekshiring.",
    },
    "MALFORMED_ITEM_PAYLOAD": {
        "category_explanation": "Meta API `data` ro'yxatida elementlar qaytardi, biroq ularning barchasida majburiy `id` yoki `name` maydoni yo'q (buzilgan javob). Bu bo'sh qidiruv (`NOT_FOUND`) emas!",
        "next_diagnostic_step": "API javobini `--json` rejimida log qiling va Graph API versiyasini tekshiring.",
    },
    "NETWORK_ERROR": {
        "category_explanation": "Tarmoq uzilishi, DNS xatosi yoki ulanish vaqti (timeout) tugashi sababli `graph.facebook.com` ga ulanib bo'lmadi.",
        "next_diagnostic_step": "Internet ulanishi, firewall va `https://graph.facebook.com` ga chiqish ruxsatini tekshiring.",
    },
}


def get_graph_api_version() -> str:
    ver = os.environ.get("META_GRAPH_API_VERSION", DEFAULT_GRAPH_API_VERSION).strip()
    return ver if ver else DEFAULT_GRAPH_API_VERSION


def normalize_account_id_optional(account_id: str) -> str:
    clean = str(account_id or "").strip()
    if not clean:
        clean = os.environ.get("META_AD_ACCOUNT_ID", "").strip()
    if not clean or clean == "act_1234567890":
        return ""
    if not clean.startswith("act_"):
        clean = f"act_{clean}"
    if not clean[4:].isdigit():
        raise ValueError(f"Noto'g'ri Meta Ad Account ID formati: {clean!r} (namuna: act_1234567890)")
    return clean


def detect_query_language(text: str, explicit_lang: str = "auto") -> str:
    if explicit_lang and explicit_lang != "auto":
        return explicit_lang
    s = str(text or "")
    if re.search(r"[ўқғҳЎҚҒҲ]", s):
        return "uz_cyrillic"
    if re.search(r"[а-яА-ЯёЁ]", s):
        return "ru"
    if re.search(
        r"\b(ko'chmas|kochmas|ta'lim|talim|bo'yicha|uchun|do'kon|dokon|kiyim|xonadon|shifokor|stomatologiya|tish|kurs|avtoservis|mebel|atir)\b",
        s.lower(),
    ):
        return "uz_latin"
    return "en"


def resolve_meta_locale(locale: str = "en_US", detected_lang: str = "en", country: str = "UZ") -> str:
    """Resolves a sensible Meta Graph API locale while preserving explicit overrides (default en_US)."""
    raw = str(locale or "").strip()
    if raw and raw.lower() != "auto":
        return raw
    if detected_lang == "ru":
        return "ru_RU"
    return "en_US"


_STOPWORDS = {
    "va", "uchun", "bilan", "yoki", "ham", "eng", "bu", "shu", "o'z", "bir", "bor", "yo'q",
    "toshkent", "toshkentda", "samarqand", "o'zbekiston", "uzbekistan", "tashkent", "shahar", "shahri",
    "и", "в", "на", "для", "с", "по", "из", "от", "до", "ташкент", "ташкенте", "узбекистан",
    "and", "the", "for", "with", "from", "into", "your", "our", "best", "top", "new", "in", "of", "to",
}


def _extract_meaningful_phrases(text: str) -> list[str]:
    """Extracts clean 1-to-3 word phrases and tokens from product/problem/intent descriptions without mechanical garbage."""
    if not text or not str(text).strip():
        return []
    cleaned = re.sub(r"[^\w\s'’-]+", " ", str(text).strip(), flags=re.UNICODE)
    words = [w.strip("'-") for w in cleaned.split() if len(w.strip("'-")) >= 3 and w.strip("'-").lower() not in _STOPWORDS]
    phrases: list[str] = []
    if 1 <= len(words) <= 4:
        phrases.append(" ".join(words))
    for w in words:
        if w.lower() not in {p.lower() for p in phrases}:
            phrases.append(w)
    return phrases[:6]


def expand_search_queries(
    product: str = "",
    niche: str = "ecom",
    customer_profile: str = "",
    problem_solved: str = "",
    customer_needs: str = "",
    purchase_intent: str = "",
    complementary_products: str = "",
    objective: str = "SALES",
    country: str = "UZ",
    extra_queries: list[str] | None = None,
    max_queries: int = 12,
) -> list[dict[str, str]]:
    """Generates prioritized search candidates from business context (explicit queries FIRST, then product/problem/intent/multilingual expansions, then niche seeds).

    CRITICAL INVARIANT:
      1. Explicit user queries (`extra_queries`) are ALWAYS added in a dedicated first pass and are NEVER crowded out by synonyms or niche seeds!
      2. If `len(explicit_queries) > max_queries`, `effective_max` expands to preserve every explicit user query.
      3. All returned items carry `role = "SEARCH_QUERY_ONLY_NOT_VERIFIED_INTEREST"`.
    """
    explicit_clean: list[str] = []
    seen_explicit: set[str] = set()
    if extra_queries:
        for q in extra_queries:
            if q and str(q).strip():
                c_q = re.sub(r"\s+", " ", str(q).strip())[:100]
                if len(c_q) >= 2 and c_q.lower() not in seen_explicit:
                    seen_explicit.add(c_q.lower())
                    explicit_clean.append(c_q)

    effective_max = max(int(max_queries or 12), len(explicit_clean), 1)
    candidates: list[dict[str, str]] = []
    seen: set[str] = set()

    def _add(term: str, origin: str, priority_tier: str = "standard") -> None:
        clean = re.sub(r"\s+", " ", str(term or "").strip())
        if not clean or len(clean) < 2:
            return
        key = clean.lower()
        if key not in seen and len(candidates) < effective_max:
            seen.add(key)
            candidates.append({
                "query": clean[:100],
                "origin": origin,
                "priority_tier": priority_tier,
                "role": "SEARCH_QUERY_ONLY_NOT_VERIFIED_INTEREST",
            })

    # Pass 1 (Highest Priority): ALL explicit user queries first — never dropped by synonym expansion or niche seeds!
    for eq in explicit_clean:
        _add(eq, "explicit_user_query", priority_tier="P1_EXPLICIT_USER_QUERY")

    # Pass 2: Multilingual & domain synonyms of explicit user queries
    for eq in explicit_clean:
        low_q = eq.lower()
        for syn in MULTILINGUAL_QUERY_SYNONYMS.get(low_q, []):
            _add(syn, f"multilingual_synonym:{low_q}", priority_tier="P2_EXPLICIT_QUERY_EXPANSION")
        for phrase, syns in MULTILINGUAL_QUERY_SYNONYMS.items():
            if phrase != low_q and len(phrase) >= 4 and phrase in low_q:
                for syn in syns:
                    _add(syn, f"multilingual_synonym:{phrase}", priority_tier="P2_EXPLICIT_QUERY_EXPANSION")

    # Pass 3: Business context — Product/Service, Problem Solved, Customer Needs/Intent, Complementary Products
    context_blocks = [
        ("product_service", product),
        ("problem_solved", problem_solved),
        ("purchase_intent", purchase_intent),
        ("customer_needs", customer_needs),
        ("customer_profile", customer_profile),
        ("complementary_products", complementary_products),
    ]
    combined_context_lower = " ".join(str(val or "") for _, val in context_blocks).strip().lower()

    if combined_context_lower:
        # Match longest known multilingual concepts first so specific phrases ("erkaklar kostyumi", "stomatologiya") rank before generic words
        for phrase, syns in sorted(MULTILINGUAL_QUERY_SYNONYMS.items(), key=lambda x: -len(x[0])):
            if phrase in combined_context_lower:
                for syn in syns:
                    _add(syn, f"multilingual_synonym:{phrase}", priority_tier="P3_BUSINESS_CONTEXT_SYNONYM")

    # Direct concise English/Latin/Cyrillic phrases from product, problem_solved, purchase_intent, complementary_products
    if product and str(product).strip():
        clean_prod = re.sub(r"\s+", " ", str(product).strip())
        if len(clean_prod.split()) <= 4:
            _add(clean_prod, "product_description", priority_tier="P3_DIRECT_PRODUCT")
        for ph in _extract_meaningful_phrases(clean_prod):
            if re.search(r"^[A-Za-z0-9\s'&-]+$", ph):
                _add(ph, "product_phrase", priority_tier="P3_DIRECT_PRODUCT")

    for label, raw_text in (
        ("problem_solved", problem_solved),
        ("purchase_intent", purchase_intent),
        ("customer_needs", customer_needs),
        ("complementary_products", complementary_products),
    ):
        if raw_text and str(raw_text).strip():
            for ph in _extract_meaningful_phrases(str(raw_text)):
                if re.search(r"^[A-Za-z0-9\s'&-]+$", ph):
                    _add(ph, f"business_context:{label}", priority_tier="P4_PROBLEM_AND_INTENT")

    # Pass 4: Campaign Objective & Niche Intent Signals
    niche_meta = NICHE_COMPLEMENTARY_SIGNALS.get(niche, NICHE_COMPLEMENTARY_SIGNALS["ecom"])
    for sig in niche_meta.get("intent_signals", []):
        _add(sig, f"niche_intent_signal:{niche}", priority_tier="P5_NICHE_INTENT")

    if objective.upper() == "SALES" and niche in ("ecom", "beauty"):
        _add("Engaged Shoppers", "objective_signal:SALES", priority_tier="P5_OBJECTIVE_INTENT")
    elif objective.upper() == "LEADS" and niche == "b2b":
        _add("Small and medium-sized enterprises", "objective_signal:LEADS", priority_tier="P5_OBJECTIVE_INTENT")

    # Pass 5 (Lowest Priority Fallback): Niche seed candidates (only if slots remain under effective_max)
    for seed in NICHE_SEED_CANDIDATES.get(niche, NICHE_SEED_CANDIDATES["ecom"]):
        _add(seed, f"niche_seed:{niche}", priority_tier="P6_NICHE_SEED_FALLBACK")

    for comp in niche_meta.get("complementary", []):
        _add(comp, f"complementary_category:{niche}", priority_tier="P6_COMPLEMENTARY_FALLBACK")

    return candidates[:effective_max]


def _tokenize_for_relevance(text: str) -> set[str]:
    if not text:
        return set()
    words = re.findall(r"[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ0-9]{3,}", text.lower())
    return {w for w in words if w not in _STOPWORDS}


def score_and_rank_candidate(
    item: dict[str, Any],
    product: str = "",
    niche: str = "ecom",
    customer_profile: str = "",
    problem_solved: str = "",
    customer_needs: str = "",
    purchase_intent: str = "",
    complementary_products: str = "",
    objective: str = "SALES",
    explicit_queries: list[str] | None = None,
    expanded_queries: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Transparent 5-factor relevance ranking model for a candidate Meta targeting option.

    IMPORTANT DISCLOSURE:
      This score (0.0..100.0) is Tyrion's heuristic relevance estimate based on lexical, semantic,
      category-path, and breadth signals — it is NOT a Meta-provided score and NEVER proves that
      an unverified idea exists in Meta Ads Manager.
    """
    name = str(item.get("name") or item.get("candidate_term") or "").strip()
    name_low = name.lower()
    item_type = str(item.get("type") or item.get("category_hint") or "interests").strip().lower()
    raw_path = item.get("path")
    path_list = [str(p) for p in raw_path] if isinstance(raw_path, list) else []
    path_str = " > ".join(path_list).lower()
    topic_str = str(item.get("topic") or "").lower()
    desc_str = str(item.get("description") or "").lower()
    matched_qs = [str(q).lower() for q in (item.get("matched_queries") or ([item.get("search_query")] if item.get("search_query") else []))]

    # Build target concept vocabulary from explicit queries, product, problem, intent, and multilingual synonyms
    explicit_set = {str(q).strip().lower() for q in (explicit_queries or []) if q and str(q).strip()}
    product_syns: set[str] = set()
    context_text = f"{product} {problem_solved} {customer_needs} {purchase_intent} {customer_profile} {' '.join(explicit_set)}".lower()
    for phrase, syns in MULTILINGUAL_QUERY_SYNONYMS.items():
        if phrase in context_text:
            for s in syns:
                product_syns.add(s.lower())

    direct_vocab = _tokenize_for_relevance(f"{product} {' '.join(explicit_set)} {' '.join(product_syns)}")
    intent_vocab = _tokenize_for_relevance(f"{problem_solved} {customer_needs} {purchase_intent} {customer_profile}")
    comp_meta = NICHE_COMPLEMENTARY_SIGNALS.get(niche, NICHE_COMPLEMENTARY_SIGNALS["ecom"])
    semantic_vocab = _tokenize_for_relevance(
        " ".join(comp_meta.get("intent_signals", []))
        + " " + " ".join(comp_meta.get("complementary", []))
        + " " + " ".join(NICHE_SEED_CANDIDATES.get(niche, []))
    )
    expected_cats = [c.lower() for c in comp_meta.get("expected_categories", [])]

    name_tokens = _tokenize_for_relevance(name_low)
    meta_text_tokens = _tokenize_for_relevance(f"{name_low} {path_str} {topic_str} {desc_str}")

    # Factor 1: Direct relevance to actual product/service & explicit user queries (0..35 pts)
    f1_direct = 0.0
    if name_low in explicit_set or name_low in product_syns or (product and name_low == product.strip().lower()):
        f1_direct = 35.0
    elif any(eq in name_low or name_low in eq for eq in (explicit_set | product_syns) if len(eq) >= 4):
        f1_direct = 29.0
    elif direct_vocab and (name_tokens & direct_vocab):
        overlap_ratio = len(name_tokens & direct_vocab) / max(1, min(len(name_tokens), len(direct_vocab)))
        f1_direct = round(18.0 + 14.0 * min(1.0, overlap_ratio), 1)
    elif direct_vocab and (meta_text_tokens & direct_vocab):
        f1_direct = 14.0
    elif not direct_vocab and (name_low in {s.lower() for s in NICHE_SEED_CANDIDATES.get(niche, [])}):
        f1_direct = 24.0

    # Boost if matched via an explicit user query rather than only a fallback seed
    if any(mq in explicit_set for mq in matched_qs) and f1_direct >= 14.0:
        f1_direct = min(35.0, f1_direct + 4.0)

    # Factor 2: Customer problem, needs & purchase intent alignment (0..25 pts)
    f2_intent = 0.0
    high_intent_signals = {s.lower() for s in comp_meta.get("intent_signals", [])}
    if name_low in high_intent_signals:
        f2_intent = 23.0
    elif intent_vocab and (meta_text_tokens & intent_vocab):
        f2_intent = 21.0
    elif any(hs in name_low or name_low in hs for hs in high_intent_signals if len(hs) >= 4):
        f2_intent = 18.0
    elif "behavior" in item_type or name_low == "engaged shoppers":
        f2_intent = 19.0 if objective.upper() in ("SALES", "LEADS") else 14.0
    elif f1_direct >= 24.0:
        f2_intent = 16.0
    elif meta_text_tokens & semantic_vocab:
        f2_intent = 11.0

    # Factor 3: Semantic & complementary relationship to the offer (0..20 pts)
    f3_semantic = 0.0
    comp_signals = {c.lower() for c in comp_meta.get("complementary", [])}
    if name_low in comp_signals or name_low in product_syns:
        f3_semantic = 19.0
    elif name_tokens & semantic_vocab:
        f3_semantic = 16.0
    elif meta_text_tokens & semantic_vocab:
        f3_semantic = 12.0
    elif f1_direct >= 20.0:
        f3_semantic = 14.0

    # Factor 4: Meta category path, topic, and description alignment (0..10 pts)
    f4_category = 5.0  # neutral baseline when Meta omits path
    if path_str or topic_str or desc_str:
        cat_blob = f"{path_str} {topic_str} {desc_str}"
        if any(ec in cat_blob for ec in expected_cats):
            f4_category = 10.0
        elif meta_text_tokens & (direct_vocab | semantic_vocab):
            f4_category = 8.0
        elif any(bad in cat_blob for bad in ("music", "band", "tv show", "humor", "gaming", "astrology", "horoscope")):
            f4_category = 0.0
        else:
            f4_category = 3.0

    # Factor 5: Breadth, ambiguity & noise evaluation (-45..+10 pts)
    f5_specificity = 8.0
    quality_flags: list[str] = []
    full_blob = f"{name_low} {path_str} {topic_str} {desc_str}"

    # Check noise / off-domain entertainment / ambiguity patterns
    if any(re.search(pat, full_blob, re.I) for pat in NOISE_AND_IRRELEVANT_PATTERNS):
        f5_specificity = -45.0
        quality_flags.append("IRRELEVANT_OR_ENTERTAINMENT_HOMONYM")
    elif name_low in OVERLY_BROAD_GENERIC_NAMES:
        f5_specificity = -22.0
        quality_flags.append("OVERLY_BROAD_GENERIC_INTEREST")

    upper_bound = _parse_optional_bound(item.get("audience_size_upper_bound"))
    lower_bound = _parse_optional_bound(item.get("audience_size_lower_bound"))
    if upper_bound is not None and upper_bound > 250_000_000 and f1_direct < 25.0:
        f5_specificity -= 12.0
        quality_flags.append("EXTREMELY_BROAD_GLOBAL_POOL")
    elif lower_bound is not None and upper_bound is not None and 5_000 <= upper_bound <= 50_000_000:
        f5_specificity = min(10.0, f5_specificity + 2.0)

    # If the candidate has zero overlap with direct, intent, or semantic vocab and low category fit, penalize as unrelated
    if f1_direct == 0.0 and f2_intent == 0.0 and f3_semantic == 0.0:
        f5_specificity = min(f5_specificity, -20.0)
        if "UNRELATED_TO_OFFER" not in quality_flags:
            quality_flags.append("UNRELATED_TO_OFFER")

    raw_total = f1_direct + f2_intent + f3_semantic + f4_category + f5_specificity
    score_100 = round(max(0.0, min(99.0, raw_total)), 1)
    score_0_1 = round(score_100 / 100.0, 2)

    if "IRRELEVANT_OR_ENTERTAINMENT_HOMONYM" in quality_flags or "UNRELATED_TO_OFFER" in quality_flags or score_100 < 35.0:
        tier = "WEAK_OR_IRRELEVANT"
        is_recommended = False
    elif "OVERLY_BROAD_GENERIC_INTEREST" in quality_flags or score_100 < 52.0:
        tier = "BROAD_CONTEXTUAL"
        is_recommended = score_100 >= 42.0 and "OVERLY_BROAD_GENERIC_INTEREST" not in quality_flags
    elif score_100 >= 72.0:
        tier = "STRONG_FIT"
        is_recommended = True
    else:
        tier = "MODERATE_FIT"
        is_recommended = True

    # Assign thematic test group for targetologist testing structure
    if "behavior" in item_type or name_low in ("engaged shoppers", "frequent international travelers", "facebook page admins"):
        test_group = "GROUP_C_BUYER_BEHAVIOR_AND_SOLVENTNOST_HYPOTHESIS"
        test_group_title = "Guruh C: Xarid Xulq-Atvori va To'lov Qobiliyati (Behavior / Solventnost Gipotezasi)"
    elif f1_direct >= 24.0:
        test_group = "GROUP_A_CORE_PRODUCT_AND_DIRECT_INTENT"
        test_group_title = "Guruh A: Bevosita Mahsulot / Xizmat Qiziqishi (Core Product & Direct Intent)"
    else:
        test_group = "GROUP_B_PROBLEM_AND_COMPLEMENTARY_CONTEXT"
        test_group_title = "Guruh B: Mijoz Muammosi va Yondosh Ehtiyojlar (Problem & Complementary Context)"

    # Build human-readable targetologist explanation
    reason_bits: list[str] = []
    if f1_direct >= 24.0:
        reason_bits.append(f"taklif ('{product or niche}') va asosiy qidiruv so'rovi bilan bevosita mos ({f1_direct:.0f}/35)")
    elif f1_direct > 0:
        reason_bits.append(f"mahsulot/nisha tushunchasi bilan qisman kesishadi ({f1_direct:.0f}/35)")
    if f2_intent >= 16.0:
        reason_bits.append(f"xarid niyati va mijoz muammosiga ('{problem_solved or customer_profile or objective}') yuqori moslik ({f2_intent:.0f}/25)")
    if path_list:
        reason_bits.append(f"Meta kategoriya yo'li: {' > '.join(path_list)}")
    if quality_flags:
        reason_bits.append(f"cheklov/ogohlantirish: {', '.join(quality_flags)}")

    explanation = (
        f"[Tyrion Relevance Estimate: {score_100}/100 ({tier}) — Meta ichki bahosi yoki natija kafolati EMAS] "
        + ("; ".join(reason_bits) if reason_bits else f"'{niche}' nishasi bo'yicha qo'shimcha kontekstual signal")
        + "."
    )

    return {
        "relevance_score": score_100,
        "relevance_score_0_1": score_0_1,
        "relevance_tier": tier,
        "is_primary_recommendation": is_recommended,
        "suggested_test_group": test_group,
        "suggested_test_group_title": test_group_title,
        "quality_flags": quality_flags,
        "relevance_breakdown": {
            "direct_product_match_35": round(f1_direct, 1),
            "problem_and_intent_alignment_25": round(f2_intent, 1),
            "semantic_offer_relationship_20": round(f3_semantic, 1),
            "category_path_and_description_fit_10": round(f4_category, 1),
            "specificity_and_noise_adjustment_10": round(f5_specificity, 1),
        },
        "score_disclaimer": "SYSTEM_RELEVANCE_ESTIMATE_NOT_META_SCORE_OR_PERFORMANCE_GUARANTEE",
        "relevance_reason": explanation,
    }


def _validate_same_origin(next_url: str, base_url: str) -> str:
    clean_next = tcore.sanitize_url(next_url)
    p_next = urllib.parse.urlparse(clean_next)
    p_base = urllib.parse.urlparse(base_url)
    if p_next.scheme.lower() != p_base.scheme.lower() or p_next.netloc.lower() != p_base.netloc.lower():
        raise PermissionError(
            f"Xavfsizlik xatosi: paging.next URL manzili ({p_next.netloc}) asosiy Graph API domeniga ({p_base.netloc}) mos emas!"
        )
    return clean_next


def _compute_relevance_reason(
    item_name: str,
    item_type: str,
    item_path: list[str] | None,
    search_query: str,
    product: str,
    niche: str,
    customer_profile: str,
) -> str:
    """Backward-compatible wrapper around score_and_rank_candidate."""
    ranked = score_and_rank_candidate(
        item={"name": item_name, "type": item_type, "path": item_path, "search_query": search_query},
        product=product,
        niche=niche,
        customer_profile=customer_profile,
    )
    return ranked["relevance_reason"]


def _parse_optional_bound(val: Any) -> int | None:
    """Faqat API javobida aniq son qaytganda int qaytaradi; aks holda None (hech qachon uydirmaydi)."""
    if val is None or isinstance(val, bool) or val == "":
        return None
    try:
        num = int(float(val))
        return num if num >= 0 else None
    except (ValueError, TypeError):
        return None


def _build_cache_context(
    product: str,
    niche: str,
    customer_profile: str,
    queries: list[str],
    ad_account_id: str,
    special_ad_category: str,
    country: str,
    objective: str,
    language: str,
    detected_language: str,
    locale: str,
    api_version: str,
    api_base_url: str,
    validate_results: bool,
    include_suggestions: bool,
    limit_per_query: int,
    max_pages_per_query: int,
    problem_solved: str = "",
    customer_needs: str = "",
    purchase_intent: str = "",
    complementary_products: str = "",
) -> tuple[str, dict[str, Any]]:
    ctx: dict[str, Any] = {
        "product": str(product or "").strip(),
        "niche": str(niche or "").strip(),
        "customer_profile": str(customer_profile or "").strip(),
        "problem_solved": str(problem_solved or "").strip(),
        "customer_needs": str(customer_needs or "").strip(),
        "purchase_intent": str(purchase_intent or "").strip(),
        "complementary_products": str(complementary_products or "").strip(),
        "queries": [str(q) for q in queries],
        "ad_account_id": str(ad_account_id or "").strip(),
        "special_ad_category": str(special_ad_category or "NONE").strip().upper(),
        "country": str(country or "UZ").strip().upper(),
        "objective": str(objective or "SALES").strip().upper(),
        "language": str(language or "auto").strip(),
        "detected_language": str(detected_language or "en").strip(),
        "locale": str(locale or "en_US").strip(),
        "api_version": str(api_version or DEFAULT_GRAPH_API_VERSION).strip(),
        "api_base_url": str(api_base_url or "https://graph.facebook.com").strip().rstrip("/"),
        "validate_results": bool(validate_results),
        "include_suggestions": bool(include_suggestions),
        "limit_per_query": int(limit_per_query),
        "max_pages_per_query": int(max_pages_per_query),
    }
    sig_raw = json.dumps(ctx, sort_keys=True, ensure_ascii=False)
    cache_key = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()[:32]
    return cache_key, ctx


def _load_valid_cache(
    cache_path: Path | None,
    cache_key: str,
    cache_context: dict[str, Any],
    ttl_seconds: int,
) -> tuple[dict[str, Any] | None, str, str | None]:
    if cache_path is None:
        return None, "DISABLED", None
    if not cache_path.is_file():
        return None, "MISS_NO_FILE", None
    try:
        raw_text = cache_path.read_text(encoding="utf-8")
        raw = json.loads(raw_text)
    except Exception:
        return None, "CORRUPTED", "Kesh fayli buzilgan (noto'g'ri JSON) — rad etildi va live API ga murojaat qilinadi."

    if not isinstance(raw, dict) or not isinstance(raw.get("entries"), dict):
        return None, "CORRUPTED", "Kesh fayli sxemasi yaroqsiz (`entries` ob'ekti yo'q) — rad etildi."

    entries: dict[str, Any] = raw["entries"]
    entry = entries.get(cache_key)

    if not isinstance(entry, dict):
        for _k, other_entry in entries.items():
            if not isinstance(other_entry, dict):
                continue
            qp = other_entry.get("query_params")
            if isinstance(qp, dict) and qp.get("queries") == cache_context.get("queries"):
                other_ver = str(other_entry.get("api_version") or qp.get("api_version") or "")
                if other_ver and other_ver != cache_context["api_version"]:
                    return (
                        None,
                        "VERSION_MISMATCH",
                        f"Kesh versiyasi mos emas ({other_ver} != {cache_context['api_version']}) — yangi live so'rov talab etiladi.",
                    )
                diff_keys = [
                    ck for ck in (
                        "special_ad_category", "country", "objective", "language",
                        "locale", "ad_account_id", "api_base_url", "validate_results", "include_suggestions"
                    )
                    if qp.get(ck) != cache_context.get(ck)
                ]
                if diff_keys:
                    return (
                        None,
                        "CONTEXT_MISMATCH",
                        f"Kesh konteksti mos emas (farqli parametrlar: {', '.join(diff_keys)}) — boshqa kontekst keshi ishlatilmaydi.",
                    )
        return None, "MISS_KEY_NOT_FOUND", None

    cached_ver = str(entry.get("api_version", ""))
    if cached_ver != cache_context["api_version"]:
        return (
            None,
            "VERSION_MISMATCH",
            f"Kesh versiyasi eskirgan ({cached_ver} != {cache_context['api_version']}) — yangi live so'rov talab etiladi.",
        )

    stored_params = entry.get("query_params")
    if isinstance(stored_params, dict):
        mismatched = [
            ck for ck in (
                "special_ad_category", "country", "objective", "language",
                "locale", "ad_account_id", "api_version", "api_base_url",
                "validate_results", "include_suggestions"
            )
            if ck in stored_params and stored_params.get(ck) != cache_context.get(ck)
        ]
        if mismatched:
            return (
                None,
                "CONTEXT_MISMATCH",
                f"Kesh yozuvi konteksti joriy so'rovga mos emas ({', '.join(mismatched)}) — rad etildi.",
            )

    try:
        fetched_epoch = float(entry.get("fetched_epoch", 0.0))
        entry_ttl = int(entry.get("ttl_seconds", ttl_seconds))
    except (ValueError, TypeError):
        return None, "CORRUPTED", "Kesh yozuvidagi vaqt tamg'asi buzilgan — rad etildi."

    effective_ttl = min(entry_ttl, int(ttl_seconds)) if ttl_seconds > 0 else 0
    age = time.time() - fetched_epoch
    if age > effective_ttl or effective_ttl <= 0:
        return (
            None,
            "EXPIRED",
            f"Kesh muddati tugagan (yoshi {int(age)}s > TTL {effective_ttl}s) — eskirgan kesh tasdiqlangan natija sifatida ishlatilmaydi.",
        )

    payload = entry.get("payload")
    if not isinstance(payload, dict) or payload.get("schema") != "tyrion.detailed_targeting_accuracy/v5":
        return None, "CORRUPTED", "Kesh payload tuzilmasi yaroqsiz — rad etildi."

    return payload, "HIT_VALID", None


def _save_cache(
    cache_path: Path | None,
    cache_key: str,
    api_version: str,
    ttl_seconds: int,
    query_params: dict[str, Any],
    payload: dict[str, Any],
) -> None:
    if cache_path is None or ttl_seconds <= 0:
        return
    existing: dict[str, Any] = {"schema": "tyrion.targeting_cache/v5", "entries": {}}
    if cache_path.is_file():
        try:
            loaded = json.loads(cache_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and isinstance(loaded.get("entries"), dict):
                existing = loaded
        except Exception:
            pass
    existing["entries"][cache_key] = {
        "api_version": api_version,
        "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fetched_epoch": time.time(),
        "ttl_seconds": ttl_seconds,
        "query_params": query_params,
        "payload": payload,
    }
    tcore.atomic_write_json(cache_path, existing)


def _fetch_paginated_endpoint(
    initial_url: str,
    base_url: str,
    headers: dict[str, str],
    max_pages: int = 3,
    timeout: float = 8.0,
    max_retries: int = 2,
) -> dict[str, Any]:
    all_items: list[dict[str, Any]] = []
    current_url: str | None = initial_url
    pages_fetched = 0
    raw_rows_total = 0
    malformed_rows_total = 0

    while current_url and pages_fetched < max_pages:
        resp = tcore.http_get_json_with_backoff(
            current_url, headers=headers, timeout=timeout, max_retries=max_retries
        )
        if not isinstance(resp, dict):
            return {
                "ok": False,
                "error": "Meta Graph API javobi JSON ob'ekt emas.",
                "http_status": None,
                "error_category": "UNEXPECTED_PAYLOAD_SHAPE",
                "retries_attempted": 0,
                "items": all_items,
                "pages_fetched": pages_fetched,
                "is_truncated": False,
                "raw_rows_total": raw_rows_total,
                "malformed_rows_total": malformed_rows_total,
            }
        if "error" in resp:
            return {
                "ok": False,
                "error": tcore.redact_secrets(str(resp.get("error", "API xatosi"))),
                "http_status": resp.get("http_status"),
                "error_category": resp.get("error_category", "API_ERROR"),
                "retries_attempted": resp.get("retries_attempted", 0),
                "items": all_items,
                "pages_fetched": pages_fetched,
                "is_truncated": False,
                "raw_rows_total": raw_rows_total,
                "malformed_rows_total": malformed_rows_total,
            }
        if "data" not in resp or not isinstance(resp.get("data"), list):
            return {
                "ok": False,
                "error": "Meta Graph API javobida `data` ro'yxati topilmadi (noto'g'ri payload shakli).",
                "http_status": 200,
                "error_category": "UNEXPECTED_PAYLOAD_SHAPE",
                "retries_attempted": 0,
                "items": all_items,
                "pages_fetched": pages_fetched,
                "is_truncated": False,
                "raw_rows_total": raw_rows_total,
                "malformed_rows_total": malformed_rows_total,
            }

        data = resp["data"]
        raw_rows_total += len(data)
        for row in data:
            if not isinstance(row, dict):
                malformed_rows_total += 1
                continue
            raw_id = row.get("id")
            raw_name = row.get("name")
            if raw_id is None or raw_name is None or str(raw_id).strip() == "" or str(raw_name).strip() == "":
                malformed_rows_total += 1
                continue
            all_items.append(row)

        pages_fetched += 1

        paging = resp.get("paging")
        next_raw = paging.get("next") if isinstance(paging, dict) else None
        if next_raw and isinstance(next_raw, str) and next_raw.strip():
            try:
                current_url = _validate_same_origin(next_raw.strip(), base_url)
            except PermissionError as exc:
                return {
                    "ok": False,
                    "error": str(exc),
                    "http_status": 200,
                    "error_category": "SSRF_PAGINATION_BLOCKED",
                    "retries_attempted": 0,
                    "items": all_items,
                    "pages_fetched": pages_fetched,
                    "is_truncated": True,
                    "raw_rows_total": raw_rows_total,
                    "malformed_rows_total": malformed_rows_total,
                }
        else:
            current_url = None

    if raw_rows_total > 0 and len(all_items) == 0:
        return {
            "ok": False,
            "error": (
                f"Meta Graph API `data` ichida {raw_rows_total} ta element qaytardi, "
                "biroq ularning barchasida majburiy `id` yoki `name` maydoni yo'q (buzilgan javob shakli)."
            ),
            "http_status": 200,
            "error_category": "MALFORMED_ITEM_PAYLOAD",
            "retries_attempted": 0,
            "items": [],
            "pages_fetched": pages_fetched,
            "is_truncated": current_url is not None,
            "raw_rows_total": raw_rows_total,
            "malformed_rows_total": malformed_rows_total,
        }

    return {
        "ok": True,
        "items": all_items,
        "pages_fetched": pages_fetched,
        "is_truncated": current_url is not None,
        "raw_rows_total": raw_rows_total,
        "malformed_rows_total": malformed_rows_total,
    }


def _run_targeting_validation(
    base_url: str,
    api_version: str,
    account_id: str,
    headers: dict[str, str],
    items_by_key: dict[tuple[str, str], dict[str, Any]],
    checked_at: str,
) -> tuple[bool, str | None]:
    if not account_id or not items_by_key:
        return False, None

    targeting_list = [
        {"id": item["id"], "type": item["type"], "name": item["name"]}
        for item in items_by_key.values()
    ]
    params = urllib.parse.urlencode({
        "targeting_list": json.dumps(targeting_list, ensure_ascii=False),
    })
    val_endpoint = f"GET /{api_version}/{account_id}/targetingvalidation"
    url = f"{base_url}/{api_version}/{account_id}/targetingvalidation?{params}"
    resp = tcore.http_get_json_with_backoff(url, headers=headers, timeout=8.0, max_retries=2)
    if "error" in resp:
        return False, f"targetingvalidation bajarilmadi ({resp.get('error_category', 'ERROR')}): {tcore.redact_secrets(str(resp['error']))}"

    data = resp.get("data")
    if not isinstance(data, list):
        return False, "targetingvalidation kutilmagan javob qaytardi (`data` ro'yxat emas)."

    val_by_id: dict[str, dict[str, Any]] = {}
    for row in data:
        if isinstance(row, dict) and row.get("id") is not None:
            val_by_id[str(row["id"]).strip()] = row

    for (_id, _type), item in items_by_key.items():
        vrow = val_by_id.get(_id)
        if vrow is None:
            continue
        is_valid = vrow.get("valid")
        status_text = str(vrow.get("status") or vrow.get("deprecation_status") or "").upper()
        replacements_raw = vrow.get("replacements") or vrow.get("suggested_replacements") or vrow.get("consolidated_into")
        replacement_info = None
        if isinstance(replacements_raw, list) and replacements_raw:
            first_rep = replacements_raw[0]
            if isinstance(first_rep, dict) and first_rep.get("id") and first_rep.get("name"):
                replacement_info = {
                    "id": str(first_rep["id"]),
                    "name": str(first_rep["name"]),
                    "type": str(first_rep.get("type") or item["type"]),
                }
        elif isinstance(replacements_raw, dict) and replacements_raw.get("id") and replacements_raw.get("name"):
            replacement_info = {
                "id": str(replacements_raw["id"]),
                "name": str(replacements_raw["name"]),
                "type": str(replacements_raw.get("type") or item["type"]),
            }

        if is_valid is False or "DEPRECATED" in status_text or "CONSOLIDATED" in status_text or "INVALID" in status_text:
            item["validation_status"] = STATUS_UNAVAILABLE_OR_CONSOLIDATED
            item["validation_details"] = {
                "validated_via": val_endpoint,
                "valid": False,
                "reason": str(vrow.get("message") or vrow.get("reason") or status_text or "Meta targetingvalidation ushbu variantni yaroqsiz yoki birlashtirilgan deb topdi."),
                "consolidated_into": replacement_info,
                "checked_at": checked_at,
            }
        elif is_valid is True:
            item["validation_status"] = STATUS_VERIFIED_AVAILABLE
            item["validation_details"] = {
                "validated_via": val_endpoint,
                "valid": True,
                "reason": "Meta targetingvalidation orqali joriy akkauntda ishlashi tasdiqlandi.",
                "consolidated_into": None,
                "checked_at": checked_at,
            }

    return True, None


def _build_broad_vs_detailed_guidance(
    niche: str,
    objective: str,
    special_ad_category: str,
    verified_count: int,
) -> dict[str, Any]:
    """Explains when Broad targeting vs Detailed Targeting is appropriate for a working targetologist."""
    if special_ad_category != "NONE":
        recommended_approach = "BROAD_REQUIRED_BY_SPECIAL_AD_CATEGORY"
        summary = (
            f"Special Ad Category ({special_ad_category}) faol bo'lgani sababli ko'plab Detailed Targeting va demografik "
            "filtrlar Meta tomonidan cheklangan. Asosiy byudjetni Broad (Geo + ruxsat etilgan keng yosh + kuchli kreativ filtr) ga yo'naltiring."
        )
    elif niche in ("b2b", "real-estate", "medical") or objective.upper() == "LEADS":
        recommended_approach = "PARALLEL_AB_TEST_BROAD_VS_THEMATIC_DETAILED_CLUSTERS"
        summary = (
            "Yuqori chekli / B2B / Lead-Gen takliflarda 15-20 ta interestni bitta ad setga aralashtirmang (stacking algoritm signalini bulg'aydi). "
            "Eng to'g'ri tuzilma: Ad Set #1 = Broad (Geo + Yosh + 3 soniyalik saralovchi kreativ hook), "
            "Ad Set #2 = Guruh A (2-4 ta eng yuqori moslikdagi bevosita mahsulot interesti), "
            "Ad Set #3 = Guruh B/C (muammo yoki xarid xulq-atvori klasteri)."
        )
    else:
        recommended_approach = "BROAD_PRIMARY_WITH_THEMATIC_INTEREST_TEST"
        summary = (
            "Ommaviy B2C / E-Commerce takliflarida Meta Andromeda algoritmi Pixelda haftasiga >=50 konversiya bo'lganda "
            "Broad (Ochiq) auditoriyada eng past CPM beradi. Yangi/sovuq pikselda esa 1 ta Broad ad setga parallel ravishda "
            "2-4 ta yuqori moslikdagi (`STRONG_FIT`) tasdiqlangan interestdan iborat alohida sinov guruhini (Test Group) yoqing."
        )

    return {
        "recommended_approach": recommended_approach,
        "anti_stacking_rule": "Hech qachon 10+ ta turli mavzudagi interestni bitta ad set ichiga qorishtirmang; har bir sinov guruhida 2 tadan 5 tagacha bir xil niyatli (thematic) interest bo'lsin.",
        "when_to_use_broad": [
            "Pixel / CAPI haftasiga >=50 ta sifatli konversiya olayotgan bo'lsa",
            "Mahsulot ommaviy iste'mol (B2C E-Commerce, HoReCa, keng xizmatlar) bo'lsa",
            "Kreativning birinchi 3 soniyasi maqsadli auditoriyani aniq chaqirsa (Creative-as-Targeting)",
        ],
        "when_to_use_detailed_targeting": [
            "Yangi reklama akkaunti yoki sovuq Pixel (<50 konversiya/hafta) uchun dastlabki algoritm yo'nalishi berishda",
            "Tor B2B, qimmat ko'chmas mulk, maxsus tibbiyot yoki aniq kasb/ehtiyoj segmentlarida",
            "Broad ad setda sifatsiz lidlar ulushi oshib ketganda A/B nazorat guruhi sifatida",
        ],
        "verified_candidates_available_for_testing": verified_count,
        "summary_uz_ru": summary,
    }


def _build_test_groups(primary_recommended: list[dict[str, Any]], pool_status: str) -> list[dict[str, Any]]:
    """Groups relevant verified options into clean thematic test groups (2-5 options per group) with explicit rationale."""
    groups_map: dict[str, dict[str, Any]] = {
        "GROUP_A_CORE_PRODUCT_AND_DIRECT_INTENT": {
            "group_id": "GROUP_A_CORE_PRODUCT_AND_DIRECT_INTENT",
            "group_name": "Guruh A — Bevosita Mahsulot va Asosiy Ehtiyoj (Core Product & Direct Intent)",
            "grouping_reason": "Mahsulot yoki xizmat kategoriyasini bevosita qidirayotgan eng issiq qiziqish signallari; sovuq pikselni o'qitish uchun 1-raqamli sinov ad seti.",
            "options_status": pool_status,
            "requires_validation_before_launch": (pool_status != STATUS_VERIFIED_AVAILABLE),
            "interests": [],
        },
        "GROUP_B_PROBLEM_AND_COMPLEMENTARY_CONTEXT": {
            "group_id": "GROUP_B_PROBLEM_AND_COMPLEMENTARY_CONTEXT",
            "group_name": "Guruh B — Mijoz Muammosi va Yondosh Kategoriyalar (Problem & Complementary Context)",
            "grouping_reason": "Bevosita mahsulot auditoriyasi to'yinganda (Frequency > 2.5) qamrovni kengaytirish uchun mijozning yondosh muammosi va turmush tarzi signallari.",
            "options_status": pool_status,
            "requires_validation_before_launch": (pool_status != STATUS_VERIFIED_AVAILABLE),
            "interests": [],
        },
        "GROUP_C_BUYER_BEHAVIOR_AND_SOLVENTNOST_HYPOTHESIS": {
            "group_id": "GROUP_C_BUYER_BEHAVIOR_AND_SOLVENTNOST_HYPOTHESIS",
            "group_name": "Guruh C — Xarid Faolligi va To'lov Qobiliyati Gipotezasi (Buyer Behavior / Solventnost)",
            "grouping_reason": "Onlayn xarid xulq-atvori yoki B2B qaror qabul qiluvchilar gipotezasi (`MARKETING_HYPOTHESIS`); alohida A/B ad setda sinovdan o'tkaziladi.",
            "options_status": pool_status,
            "requires_validation_before_launch": (pool_status != STATUS_VERIFIED_AVAILABLE),
            "interests": [],
        },
    }

    for it in primary_recommended:
        gid = it.get("suggested_test_group", "GROUP_A_CORE_PRODUCT_AND_DIRECT_INTENT")
        if gid not in groups_map:
            gid = "GROUP_A_CORE_PRODUCT_AND_DIRECT_INTENT"
        if len(groups_map[gid]["interests"]) < 5:
            groups_map[gid]["interests"].append({
                "id": it["id"],
                "name": it["name"],
                "type": it["type"],
                "validation_status": it["validation_status"],
                "relevance_score": it["relevance_score"],
                "relevance_tier": it["relevance_tier"],
                "source_endpoint": it["source_endpoint"],
                "matched_query": it["search_query"],
                "why_it_fits": it["relevance_reason"],
            })

    return [g for g in groups_map.values() if g["interests"]]


def _build_targetologist_report(
    product: str,
    niche: str,
    customer_profile: str,
    problem_solved: str,
    customer_needs: str,
    purchase_intent: str,
    complementary_products: str,
    objective: str,
    country: str,
    locale_used: str,
    ad_account_id: str,
    special_ad_category: str,
    live_check_status: dict[str, Any],
    primary_recommended: list[dict[str, Any]],
    excluded_low_relevance: list[dict[str, Any]],
    unavailable_options: list[dict[str, Any]],
    related_unverified: list[dict[str, Any]],
    not_found_queries: list[dict[str, Any]],
    test_groups: list[dict[str, Any]],
    broad_guidance: dict[str, Any],
    limitations: list[str],
) -> dict[str, Any]:
    """Builds the 8-section structured report tailored for a working performance targetologist."""
    missing_inputs: list[str] = []
    if not product.strip():
        missing_inputs.append("Aniq mahsulot/xizmat tavsifi (`--product`) berilmagan — nisha bo'yicha umumiy kontekst ishlatildi.")
    if not ad_account_id:
        missing_inputs.append("Meta Ad Account ID (`--account-id act_...`) berilmagan — akkaunt darajasidagi `targetingsearch` va `targetingvalidation` o'rniga global `/search` ishlatildi.")
    if not (problem_solved.strip() or customer_profile.strip() or purchase_intent.strip()):
        missing_inputs.append("Mijoz muammosi (`--problem`) yoki maqsadli mijoz profili (`--customer-profile`) kiritilsa, moslik reytingi (relevance ranking) yanada aniqroq ishlaydi.")

    err_cat = str(live_check_status.get("error_category") or "NONE")
    diag_guide = FAILURE_DIAGNOSTIC_GUIDE.get(err_cat, {
        "category_explanation": live_check_status.get("error_message") or "Live API qidiruvi yakunlandi.",
        "next_diagnostic_step": "Tasdiqlangan guruhlarni Ads Manager'da A/B sinovga qo'ying.",
    })

    return {
        "1_business_and_audience_understanding": {
            "product_or_service": product or f"({niche} nishasi taklifi)",
            "niche": niche,
            "problem_solved": problem_solved or "Kiritilmagan (nisha standart muammolari olindi)",
            "customer_profile_and_needs": customer_profile or customer_needs or "Kiritilmagan",
            "purchase_intent": purchase_intent or f"{objective.upper()} konversiya niyati",
            "complementary_products": complementary_products or ", ".join(NICHE_COMPLEMENTARY_SIGNALS.get(niche, {}).get("complementary", [])[:4]),
            "target_market_country": country.upper(),
            "campaign_objective": objective.upper(),
            "locale_used": locale_used,
            "special_ad_category": special_ad_category,
        },
        "2_ranked_verified_interests": [
            {
                "rank": idx + 1,
                "id": it["id"],
                "name": it["name"],
                "type": it["type"],
                "validation_status": it["validation_status"],
                "relevance_score": it["relevance_score"],
                "relevance_tier": it["relevance_tier"],
                "score_disclaimer": it["score_disclaimer"],
                "category_path": it.get("path"),
                "audience_size_lower_bound": it.get("audience_size_lower_bound"),
                "audience_size_upper_bound": it.get("audience_size_upper_bound"),
                "matched_queries": it.get("matched_queries", []),
                "locale_used": it.get("locale_used", locale_used),
                "source_endpoint": it["source_endpoint"],
            }
            for idx, it in enumerate(primary_recommended)
        ],
        "3_validation_status_and_official_ids": {
            "live_api_executed": bool(live_check_status.get("executed")),
            "overall_status": live_check_status.get("status"),
            "verified_available_count": sum(1 for x in primary_recommended if x["validation_status"] == STATUS_VERIFIED_AVAILABLE),
            "found_not_validated_count": sum(1 for x in primary_recommended if x["validation_status"] == STATUS_FOUND_NOT_VALIDATED),
            "excluded_low_relevance_count": len(excluded_low_relevance),
            "unavailable_or_consolidated_count": len(unavailable_options),
            "official_ids_summary": [
                {"id": it["id"], "name": it["name"], "status": it["validation_status"]}
                for it in primary_recommended
            ],
        },
        "4_offer_fit_explanations": [
            {
                "id": it["id"],
                "name": it["name"],
                "relevance_score": it["relevance_score"],
                "relevance_tier": it["relevance_tier"],
                "why_it_fits_offer": it["relevance_reason"],
                "relevance_breakdown": it["relevance_breakdown"],
            }
            for it in primary_recommended
        ],
        "5_related_alternatives_by_status": {
            "found_not_validated_official": [
                {"id": it["id"], "name": it["name"], "relevance_score": it["relevance_score"], "status": it["validation_status"]}
                for it in primary_recommended if it["validation_status"] == STATUS_FOUND_NOT_VALIDATED
            ],
            "excluded_low_relevance_official_results": [
                {
                    "id": it["id"],
                    "name": it["name"],
                    "status": it["validation_status"],
                    "relevance_score": it["relevance_score"],
                    "quality_flags": it.get("quality_flags", []),
                    "exclusion_reason": it["relevance_reason"],
                }
                for it in excluded_low_relevance
            ],
            "unavailable_or_consolidated_official": [
                {
                    "id": it["id"],
                    "name": it["name"],
                    "status": it["validation_status"],
                    "consolidated_into": (it.get("validation_details") or {}).get("consolidated_into"),
                    "reason": (it.get("validation_details") or {}).get("reason"),
                }
                for it in unavailable_options
            ],
            "related_unverified_offline_ideas": [
                {
                    "candidate_term": idea["candidate_term"],
                    "status": idea["validation_status"],
                    "origin": idea.get("origin") or idea.get("category_hint"),
                    "relevance_score_estimate": idea.get("relevance_score"),
                    "warning": "Meta API da TASDIQLANMAGAN (`RELATED_UNVERIFIED`) — live tekshiruvsiz kampaniyaga qo'shmang!",
                }
                for idea in related_unverified[:12]
            ],
            "not_found_queries": [
                {"query": nf["query"], "status": nf["validation_status"], "endpoint": nf["source_endpoint"]}
                for nf in not_found_queries
            ],
        },
        "6_suggested_test_groups": test_groups,
        "7_broad_targeting_alternatives": broad_guidance,
        "8_missing_inputs_limitations_and_next_steps": {
            "missing_inputs": missing_inputs,
            "failure_category": err_cat,
            "failure_explanation": diag_guide["category_explanation"],
            "next_diagnostic_step": diag_guide["next_diagnostic_step"],
            "api_limitations_and_disclosures": limitations,
        },
    }


def search_and_validate_targeting(
    product: str = "",
    niche: str = "ecom",
    customer_profile: str = "",
    problem_solved: str = "",
    customer_needs: str = "",
    purchase_intent: str = "",
    complementary_products: str = "",
    objective: str = "SALES",
    country: str = "UZ",
    language: str = "auto",
    queries: list[str] | None = None,
    ad_account_id: str = "",
    special_ad_category: str = "NONE",
    include_suggestions: bool = False,
    validate_results: bool = True,
    limit_per_query: int = 15,
    max_pages_per_query: int = 2,
    max_queries: int = 12,
    min_relevance_score: float = 35.0,
    locale: str = "en_US",
    cache_path: Path | None = None,
    cache_ttl_seconds: int = 3600,
) -> dict[str, Any]:
    """Discovers, validates, ranks, and explains Meta Ads Detailed Targeting options across 6 strict verification statuses."""
    api_version = get_graph_api_version()
    base_url = os.environ.get("META_GRAPH_API_BASE_URL", "https://graph.facebook.com").strip().rstrip("/")
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    acct = normalize_account_id_optional(ad_account_id)
    spec_cat = str(special_ad_category or "NONE").strip().upper()
    if spec_cat not in SPECIAL_AD_CATEGORIES:
        raise ValueError(f"Noto'g'ri special_ad_category: {special_ad_category!r}. Ruxsat etilgan: {SPECIAL_AD_CATEGORIES}")

    safe_limit = tcore.safe_int(limit_per_query, default=15, min_val=1, max_val=100, field_name="limit_per_query")
    safe_max_pages = tcore.safe_int(max_pages_per_query, default=2, min_val=1, max_val=20, field_name="max_pages_per_query")
    safe_max_queries = tcore.safe_int(max_queries, default=12, min_val=1, max_val=50, field_name="max_queries")

    combined_text_for_lang = f"{product} {problem_solved} {customer_needs} {purchase_intent} {customer_profile} {' '.join(queries or [])}"
    detected_lang = detect_query_language(combined_text_for_lang, explicit_lang=language)
    effective_locale = resolve_meta_locale(locale=locale, detected_lang=detected_lang, country=country)

    expanded_queries = expand_search_queries(
        product=product,
        niche=niche,
        customer_profile=customer_profile,
        problem_solved=problem_solved,
        customer_needs=customer_needs,
        purchase_intent=purchase_intent,
        complementary_products=complementary_products,
        objective=objective,
        country=country,
        extra_queries=queries,
        max_queries=safe_max_queries,
    )

    cache_key, cache_context = _build_cache_context(
        product=product,
        niche=niche,
        customer_profile=customer_profile,
        queries=[q["query"] for q in expanded_queries],
        ad_account_id=acct,
        special_ad_category=spec_cat,
        country=country,
        objective=objective,
        language=language,
        detected_language=detected_lang,
        locale=effective_locale,
        api_version=api_version,
        api_base_url=base_url,
        validate_results=validate_results,
        include_suggestions=include_suggestions,
        limit_per_query=safe_limit,
        max_pages_per_query=safe_max_pages,
        problem_solved=problem_solved,
        customer_needs=customer_needs,
        purchase_intent=purchase_intent,
        complementary_products=complementary_products,
    )

    cached_payload, cache_status, cache_warning = _load_valid_cache(
        cache_path=cache_path,
        cache_key=cache_key,
        cache_context=cache_context,
        ttl_seconds=cache_ttl_seconds,
    )
    if cached_payload is not None:
        cached_copy = json.loads(json.dumps(cached_payload))
        cached_copy["live_check_status"]["served_from_valid_cache"] = True
        cached_copy["live_check_status"]["cache_status"] = cache_status
        cached_copy["live_check_status"]["cache_key"] = cache_key
        return cached_copy

    # Build unverified related ideas (search candidates + solventnost hypotheses).
    # STRICT INVARIANT: These ALWAYS have validation_status = RELATED_UNVERIFIED and can NEVER enter verified_targeting_options!
    related_unverified_ideas: list[dict[str, Any]] = []
    for q_obj in expanded_queries:
        rk = score_and_rank_candidate(
            item={"name": q_obj["query"], "type": "search_candidate", "search_query": q_obj["query"]},
            product=product,
            niche=niche,
            customer_profile=customer_profile,
            problem_solved=problem_solved,
            customer_needs=customer_needs,
            purchase_intent=purchase_intent,
            complementary_products=complementary_products,
            objective=objective,
            explicit_queries=queries,
            expanded_queries=expanded_queries,
        )
        related_unverified_ideas.append({
            "candidate_term": q_obj["query"],
            "origin": q_obj["origin"],
            "priority_tier": q_obj.get("priority_tier", "standard"),
            "validation_status": STATUS_RELATED_UNVERIFIED,
            "is_verified_meta_option": False,
            "relevance_score": rk["relevance_score"],
            "relevance_tier": rk["relevance_tier"],
            "score_disclaimer": rk["score_disclaimer"],
            "explanation": "Qidiruv uchun shakllantirilgan nomzod ibora yoki statik klaster. Live API tasdig'isiz Ads Manager'da mavjud deb hisoblanmasin.",
        })
    for sh in SOLVENTNOST_HYPOTHESES:
        rk_sh = score_and_rank_candidate(
            item={"name": sh["candidate_name"], "type": sh["category_hint"], "search_query": sh["candidate_name"]},
            product=product,
            niche=niche,
            customer_profile=customer_profile,
            problem_solved=problem_solved,
            customer_needs=customer_needs,
            purchase_intent=purchase_intent,
            complementary_products=complementary_products,
            objective=objective,
            explicit_queries=queries,
            expanded_queries=expanded_queries,
        )
        related_unverified_ideas.append({
            "candidate_term": sh["candidate_name"],
            "category_hint": sh["category_hint"],
            "validation_status": STATUS_RELATED_UNVERIFIED,
            "is_verified_meta_option": False,
            "hypothesis_type": sh["hypothesis_type"],
            "relevance_score": rk_sh["relevance_score"],
            "relevance_tier": rk_sh["relevance_tier"],
            "score_disclaimer": rk_sh["score_disclaimer"],
            "explanation": sh["note"],
        })

    limitations: list[str] = []
    if cache_warning:
        limitations.append(cache_warning)
    if spec_cat != "NONE":
        limitations.append(
            f"DIQQAT (Special Ad Category = {spec_cat}): Meta reklama siyosatiga ko'ra yosh, jins, pochta indeksi va ko'plab "
            "demografik/behavior targeting opsiyalari cheklangan. Ushbu cheklovlarni chetlab o'tishga urinmang!"
        )
    limitations.append(
        "To'lov qobiliyati (Solventnost — iPhone, xalqaro sayohat, Page Admin) signallari tasdiqlangan daromad filtri EMAS, "
        "balki kampaniyada A/B sinov orqali tekshiriladigan marketing gipotezasidir."
    )
    limitations.append(
        "Moslik balli (`relevance_score` 0..100) — Tyrion tizimining ichki evristik bahosi bo'lib, Meta tomonidan berilgan "
        "ko'rsatkich yoki reklama natijasi kafolati hisoblanmaydi."
    )

    token = os.environ.get("META_ACCESS_TOKEN", "").strip()
    if not token or token == "your_meta_access_token_here":
        diag_missing = FAILURE_DIAGNOSTIC_GUIDE["MISSING_TOKEN"]
        limitations.insert(
            0,
            f"META_ACCESS_TOKEN o'rnatilmagan (`API_UNAVAILABLE` / `MISSING_TOKEN`): {diag_missing['category_explanation']} "
            f"Keyingi qadam: {diag_missing['next_diagnostic_step']}",
        )
        live_status_obj = {
            "executed": False,
            "status": STATUS_API_UNAVAILABLE,
            "is_complete": False,
            "is_truncated": False,
            "total_pages_fetched": 0,
            "error_category": "MISSING_TOKEN",
            "http_status": None,
            "error_message": "META_ACCESS_TOKEN muhit o'zgaruvchisi topilmadi.",
            "failure_explanation": diag_missing["category_explanation"],
            "next_diagnostic_step": diag_missing["next_diagnostic_step"],
            "api_version": api_version,
            "locale_used": effective_locale,
            "checked_at": checked_at,
            "served_from_valid_cache": False,
            "cache_status": cache_status,
            "cache_key": cache_key,
            "query_diagnostics": [],
        }
        broad_guide = _build_broad_vs_detailed_guidance(niche, objective, spec_cat, verified_count=0)
        t_report = _build_targetologist_report(
            product=product, niche=niche, customer_profile=customer_profile,
            problem_solved=problem_solved, customer_needs=customer_needs,
            purchase_intent=purchase_intent, complementary_products=complementary_products,
            objective=objective, country=country, locale_used=effective_locale,
            ad_account_id=acct, special_ad_category=spec_cat,
            live_check_status=live_status_obj, primary_recommended=[],
            excluded_low_relevance=[], unavailable_options=[],
            related_unverified=related_unverified_ideas, not_found_queries=[],
            test_groups=[], broad_guidance=broad_guide, limitations=limitations,
        )
        return {
            "schema": "tyrion.detailed_targeting_accuracy/v5",
            "query_context": {
                "product": product,
                "niche": niche,
                "customer_profile": customer_profile,
                "problem_solved": problem_solved,
                "customer_needs": customer_needs,
                "purchase_intent": purchase_intent,
                "complementary_products": complementary_products,
                "objective": objective.upper(),
                "country": country.upper(),
                "language": language,
                "detected_query_language": detected_lang,
                "locale": effective_locale,
                "ad_account_id": acct or None,
                "special_ad_category": spec_cat,
                "max_queries": safe_max_queries,
                "generated_search_queries": expanded_queries,
                "cache_key": cache_key,
            },
            "live_check_status": live_status_obj,
            "query_diagnostics": [],
            "verified_targeting_options": [],
            "primary_recommended_interests": [],
            "excluded_low_relevance_options": [],
            "unavailable_or_consolidated_options": [],
            "related_unverified_ideas": related_unverified_ideas,
            "not_found_queries": [],
            "recommended_audience_combinations": {
                "status": "NO_VERIFIED_OPTIONS_AVAILABLE",
                "note": "Live API tekshiruvi bajarilmagani (`API_UNAVAILABLE`) sababli tasdiqlangan targeting kombinatsiyasi tuzilmadi. Avval `META_ACCESS_TOKEN` orqali live qidiruvni bajaring.",
                "combinations": [],
                "suggested_test_groups": [],
                "broad_vs_detailed_guidance": broad_guide,
            },
            "targetologist_report": t_report,
            "limitations_and_disclosures": limitations,
        }

    headers = {"Authorization": f"Bearer {token}"}
    items_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    not_found_queries: list[dict[str, Any]] = []
    api_failures: list[dict[str, Any]] = []
    query_diagnostics: list[dict[str, Any]] = []
    total_pages_fetched = 0
    any_truncated = False

    for q_obj in expanded_queries:
        q_str = q_obj["query"]
        q_origin = q_obj.get("origin", "search_query")
        if acct:
            endpoint_label = f"GET /{api_version}/{acct}/targetingsearch"
            params = urllib.parse.urlencode({
                "q": q_str,
                "limit": str(safe_limit),
                "locale": effective_locale,
            })
            url = f"{base_url}/{api_version}/{acct}/targetingsearch?{params}"
        else:
            endpoint_label = f"GET /{api_version}/search?type=adinterest"
            params = urllib.parse.urlencode({
                "type": "adinterest",
                "q": q_str,
                "limit": str(safe_limit),
                "locale": effective_locale,
            })
            url = f"{base_url}/{api_version}/search?{params}"

        fetched = _fetch_paginated_endpoint(
            initial_url=url,
            base_url=base_url,
            headers=headers,
            max_pages=safe_max_pages,
        )
        q_pages = int(fetched.get("pages_fetched", 0))
        q_truncated = bool(fetched.get("is_truncated", False))
        q_raw_count = int(fetched.get("raw_rows_total", 0))
        q_malformed_count = int(fetched.get("malformed_rows_total", 0))
        total_pages_fetched += q_pages
        if q_truncated:
            any_truncated = True

        if not fetched["ok"]:
            err_cat = str(fetched.get("error_category", "API_ERROR"))
            diag_info = FAILURE_DIAGNOSTIC_GUIDE.get(err_cat, {
                "category_explanation": fetched["error"],
                "next_diagnostic_step": "API javobini va token ruxsatlarini tekshiring.",
            })
            fail_entry = {
                "query": q_str,
                "query_origin": q_origin,
                "locale_used": effective_locale,
                "endpoint": endpoint_label,
                "status": STATUS_API_UNAVAILABLE,
                "error": fetched["error"],
                "http_status": fetched.get("http_status"),
                "error_category": err_cat,
                "failure_explanation": diag_info["category_explanation"],
                "next_diagnostic_step": diag_info["next_diagnostic_step"],
                "retries_attempted": fetched.get("retries_attempted", 0),
                "pages_fetched": q_pages,
                "is_truncated": q_truncated,
                "raw_results_count": q_raw_count,
                "valid_results_count": 0,
                "malformed_results_count": q_malformed_count,
            }
            api_failures.append(fail_entry)
            query_diagnostics.append({
                "query": q_str,
                "query_origin": q_origin,
                "locale_used": effective_locale,
                "endpoint": endpoint_label,
                "status": STATUS_API_UNAVAILABLE,
                "error_category": err_cat,
                "pages_fetched": q_pages,
                "is_truncated": q_truncated,
                "results_count": 0,
                "raw_results_count": q_raw_count,
                "malformed_results_count": q_malformed_count,
                "is_complete": False,
                "note": fetched["error"],
            })
            if err_cat in ("AUTH_401", "PERMISSION_403"):
                break
            continue

        raw_rows = fetched["items"]
        valid_rows_for_query = len(raw_rows)
        for arrival_idx, row in enumerate(raw_rows):
            item_id = str(row["id"]).strip()
            item_name = str(row["name"])  # Preserve exact Meta name without translating or modifying!
            item_type = str(row.get("type") or "adinterest").strip()
            raw_path = row.get("path")
            item_path = [str(p) for p in raw_path] if isinstance(raw_path, list) else None

            lower_bound = _parse_optional_bound(row.get("audience_size_lower_bound"))
            upper_bound = _parse_optional_bound(row.get("audience_size_upper_bound"))

            dedup_key = (item_id, item_type.lower())

            row_valid = row.get("valid")
            row_deprecated = bool(row.get("deprecated") or str(row.get("status", "")).upper() in ("DEPRECATED", "CONSOLIDATED", "INVALID"))
            initial_status = STATUS_UNAVAILABLE_OR_CONSOLIDATED if (row_valid is False or row_deprecated) else STATUS_FOUND_NOT_VALIDATED

            replacement_obj = None
            rep_raw = row.get("consolidated_into") or row.get("replacement")
            if isinstance(rep_raw, dict) and rep_raw.get("id") and rep_raw.get("name"):
                replacement_obj = {
                    "id": str(rep_raw["id"]),
                    "name": str(rep_raw["name"]),
                    "type": str(rep_raw.get("type") or item_type),
                }

            if dedup_key not in items_by_key:
                items_by_key[dedup_key] = {
                    "id": item_id,
                    "name": item_name,
                    "type": item_type,
                    "path": item_path,
                    "topic": row.get("topic"),
                    "description": row.get("description"),
                    "audience_size_lower_bound": lower_bound,
                    "audience_size_upper_bound": upper_bound,
                    "search_query": q_str,
                    "query_origin": q_origin,
                    "locale_used": effective_locale,
                    "matched_queries": [q_str],
                    "api_arrival_order": len(items_by_key) + 1,
                    "source_endpoint": endpoint_label,
                    "api_version": api_version,
                    "checked_at": checked_at,
                    "pages_fetched": q_pages,
                    "is_truncated": q_truncated,
                    "validation_status": initial_status,
                    "validation_details": {
                        "validated_via": endpoint_label if initial_status == STATUS_UNAVAILABLE_OR_CONSOLIDATED else None,
                        "valid": False if initial_status == STATUS_UNAVAILABLE_OR_CONSOLIDATED else None,
                        "reason": (
                            str(row.get("deprecation_reason") or "Meta API ushbu opsiyani eskirgan yoki birlashtirilgan deb belgilagan.")
                            if initial_status == STATUS_UNAVAILABLE_OR_CONSOLIDATED
                            else "Rasmiy qidiruvdan topildi, ammo targetingvalidation hali bajarilmagan."
                        ),
                        "consolidated_into": replacement_obj,
                        "checked_at": checked_at,
                    },
                    "relevance_is_ai_opinion_not_meta_proof": True,
                }
            else:
                if q_str not in items_by_key[dedup_key]["matched_queries"]:
                    items_by_key[dedup_key]["matched_queries"].append(q_str)

        if valid_rows_for_query == 0 and q_raw_count == 0:
            not_found_queries.append({
                "query": q_str,
                "query_origin": q_origin,
                "locale_used": effective_locale,
                "source_endpoint": endpoint_label,
                "api_version": api_version,
                "checked_at": checked_at,
                "pages_fetched": q_pages,
                "is_truncated": q_truncated,
                "results_count": 0,
                "validation_status": STATUS_NOT_FOUND,
                "explanation": (
                    f"'{q_str}' so'rovi (locale={effective_locale}) bo'yicha {endpoint_label} javobida 0 ta rasmiy natija qaytdi (`data: []`). "
                    "Eslatma: NOT_FOUND bu tushuncha Meta'da umuman yo'qligining mutlaq isboti emas, balki ayni so'rov bo'yicha topilmaganini bildiradi."
                ),
            })
            query_diagnostics.append({
                "query": q_str,
                "query_origin": q_origin,
                "locale_used": effective_locale,
                "endpoint": endpoint_label,
                "status": STATUS_NOT_FOUND,
                "error_category": "NONE",
                "pages_fetched": q_pages,
                "is_truncated": q_truncated,
                "results_count": 0,
                "raw_results_count": 0,
                "malformed_results_count": 0,
                "is_complete": not q_truncated,
                "note": "Rasmiy API bo'sh ro'yxat (`data: []`) qaytardi.",
            })
        else:
            q_diag_status = "TRUNCATED_PARTIAL_RESULTS" if q_truncated else "COMPLETE_RESULTS"
            query_diagnostics.append({
                "query": q_str,
                "query_origin": q_origin,
                "locale_used": effective_locale,
                "endpoint": endpoint_label,
                "status": q_diag_status,
                "error_category": "NONE",
                "pages_fetched": q_pages,
                "is_truncated": q_truncated,
                "results_count": valid_rows_for_query,
                "raw_results_count": q_raw_count,
                "malformed_results_count": q_malformed_count,
                "is_complete": not q_truncated,
                "note": (
                    f"DIQQAT: Sahifalash limiti ({safe_max_pages} sahifa) tugadi va `paging.next` qoldi — natijalar to'liq emas!"
                    if q_truncated
                    else f"{q_pages} ta sahifa to'liq o'qildi ({valid_rows_for_query} ta yaroqli natija)."
                ),
            })

    if any_truncated:
        truncated_queries = [qd["query"] for qd in query_diagnostics if qd.get("is_truncated")]
        limitations.insert(
            0,
            f"DIQQAT (Pagination Truncated / Natija To'liq Emas): {len(truncated_queries)} ta so'rovda ({', '.join(repr(x) for x in truncated_queries)}) "
            f"`max_pages_per_query={safe_max_pages}` chegarasiga yetildi va keyingi sahifalar (`paging.next`) o'qilmadi. "
            "Kesilgan qidiruv to'liq tekshirilgan qidiruv hisoblanmaydi (`is_truncated=True`, `is_complete=False`)!",
        )

    if api_failures:
        limitations.insert(
            0,
            f"DIQQAT: {len(api_failures)} ta so'rovda API yoki javob shakli xatosi yuz berdi "
            f"({', '.join(f['query'] + ':' + f['error_category'] for f in api_failures)}). "
            "Buzilgan API javoblari `NOT_FOUND` sifatida emas, balki `API_UNAVAILABLE` xatosi sifatida qayd etildi.",
        )

    if api_failures and not items_by_key and not not_found_queries:
        first_fail = api_failures[0]
        err_cat = first_fail["error_category"]
        diag_fail = FAILURE_DIAGNOSTIC_GUIDE.get(err_cat, {
            "category_explanation": first_fail["error"],
            "next_diagnostic_step": "API token, ruxsat va tarmoq ulanishini tekshiring.",
        })
        live_fail_status = {
            "executed": False,
            "status": STATUS_API_UNAVAILABLE,
            "is_complete": False,
            "is_truncated": any_truncated,
            "total_pages_fetched": total_pages_fetched,
            "error_category": err_cat,
            "http_status": first_fail.get("http_status"),
            "error_message": first_fail["error"],
            "failure_explanation": diag_fail["category_explanation"],
            "next_diagnostic_step": diag_fail["next_diagnostic_step"],
            "api_version": api_version,
            "locale_used": effective_locale,
            "checked_at": checked_at,
            "served_from_valid_cache": False,
            "cache_status": cache_status,
            "cache_key": cache_key,
            "api_failures": api_failures,
            "query_diagnostics": query_diagnostics,
        }
        broad_guide = _build_broad_vs_detailed_guidance(niche, objective, spec_cat, verified_count=0)
        t_report = _build_targetologist_report(
            product=product, niche=niche, customer_profile=customer_profile,
            problem_solved=problem_solved, customer_needs=customer_needs,
            purchase_intent=purchase_intent, complementary_products=complementary_products,
            objective=objective, country=country, locale_used=effective_locale,
            ad_account_id=acct, special_ad_category=spec_cat,
            live_check_status=live_fail_status, primary_recommended=[],
            excluded_low_relevance=[], unavailable_options=[],
            related_unverified=related_unverified_ideas, not_found_queries=[],
            test_groups=[], broad_guidance=broad_guide, limitations=limitations,
        )
        return {
            "schema": "tyrion.detailed_targeting_accuracy/v5",
            "query_context": {
                "product": product,
                "niche": niche,
                "customer_profile": customer_profile,
                "problem_solved": problem_solved,
                "customer_needs": customer_needs,
                "purchase_intent": purchase_intent,
                "complementary_products": complementary_products,
                "objective": objective.upper(),
                "country": country.upper(),
                "language": language,
                "detected_query_language": detected_lang,
                "locale": effective_locale,
                "ad_account_id": acct or None,
                "special_ad_category": spec_cat,
                "max_queries": safe_max_queries,
                "generated_search_queries": expanded_queries,
                "cache_key": cache_key,
            },
            "live_check_status": live_fail_status,
            "query_diagnostics": query_diagnostics,
            "verified_targeting_options": [],
            "primary_recommended_interests": [],
            "excluded_low_relevance_options": [],
            "unavailable_or_consolidated_options": [],
            "related_unverified_ideas": related_unverified_ideas,
            "not_found_queries": [],
            "recommended_audience_combinations": {
                "status": "NO_VERIFIED_OPTIONS_AVAILABLE",
                "note": f"API xatosi (`API_UNAVAILABLE` / `{err_cat}`) sababli tasdiqlangan variantlar olinmadi. Keyingi qadam: {diag_fail['next_diagnostic_step']}",
                "combinations": [],
                "suggested_test_groups": [],
                "broad_vs_detailed_guidance": broad_guide,
            },
            "targetologist_report": t_report,
            "limitations_and_disclosures": limitations,
        }

    # Optional Step B: Account-scoped targetingsuggestions (seeded from highest-relevance preliminary items)
    if include_suggestions and acct and items_by_key:
        prelim_sorted = sorted(
            [it for it in items_by_key.values() if it["validation_status"] != STATUS_UNAVAILABLE_OR_CONSOLIDATED],
            key=lambda x: -score_and_rank_candidate(
                x, product=product, niche=niche, customer_profile=customer_profile,
                problem_solved=problem_solved, customer_needs=customer_needs,
                purchase_intent=purchase_intent, complementary_products=complementary_products,
                objective=objective, explicit_queries=queries, expanded_queries=expanded_queries,
            )["relevance_score"],
        )
        seed_list = [{"id": it["id"], "type": it["type"]} for it in prelim_sorted[:5]]
        if seed_list:
            sug_endpoint = f"GET /{api_version}/{acct}/targetingsuggestions"
            sug_params = urllib.parse.urlencode({
                "targeting_list": json.dumps(seed_list, ensure_ascii=False),
                "limit": str(safe_limit),
            })
            sug_url = f"{base_url}/{api_version}/{acct}/targetingsuggestions?{sug_params}"
            sug_fetched = _fetch_paginated_endpoint(sug_url, base_url, headers, max_pages=safe_max_pages)
            sug_pages = int(sug_fetched.get("pages_fetched", 0))
            sug_trunc = bool(sug_fetched.get("is_truncated", False))
            total_pages_fetched += sug_pages
            if sug_trunc:
                any_truncated = True
            if sug_fetched["ok"]:
                for row in sug_fetched["items"]:
                    s_id = str(row["id"]).strip()
                    s_name = str(row["name"])
                    s_type = str(row.get("type") or "interests").strip()
                    s_key = (s_id, s_type.lower())
                    if s_key not in items_by_key:
                        s_path = [str(p) for p in row["path"]] if isinstance(row.get("path"), list) else None
                        items_by_key[s_key] = {
                            "id": s_id,
                            "name": s_name,
                            "type": s_type,
                            "path": s_path,
                            "topic": row.get("topic"),
                            "description": row.get("description"),
                            "audience_size_lower_bound": _parse_optional_bound(row.get("audience_size_lower_bound")),
                            "audience_size_upper_bound": _parse_optional_bound(row.get("audience_size_upper_bound")),
                            "search_query": "targetingsuggestions_seed",
                            "query_origin": "targetingsuggestions",
                            "locale_used": effective_locale,
                            "matched_queries": ["targetingsuggestions_seed"],
                            "api_arrival_order": len(items_by_key) + 1,
                            "source_endpoint": sug_endpoint,
                            "api_version": api_version,
                            "checked_at": checked_at,
                            "pages_fetched": sug_pages,
                            "is_truncated": sug_trunc,
                            "validation_status": STATUS_FOUND_NOT_VALIDATED,
                            "validation_details": {
                                "validated_via": None,
                                "valid": None,
                                "reason": "Meta targetingsuggestions endpointidan olindi; targetingvalidation hali bajarilmagan.",
                                "consolidated_into": None,
                                "checked_at": checked_at,
                            },
                            "relevance_is_ai_opinion_not_meta_proof": True,
                        }
                query_diagnostics.append({
                    "query": "targetingsuggestions_seed",
                    "query_origin": "targetingsuggestions",
                    "locale_used": effective_locale,
                    "endpoint": sug_endpoint,
                    "status": "TRUNCATED_PARTIAL_RESULTS" if sug_trunc else "COMPLETE_RESULTS",
                    "error_category": "NONE",
                    "pages_fetched": sug_pages,
                    "is_truncated": sug_trunc,
                    "results_count": len(sug_fetched["items"]),
                    "raw_results_count": int(sug_fetched.get("raw_rows_total", len(sug_fetched["items"]))),
                    "malformed_results_count": int(sug_fetched.get("malformed_rows_total", 0)),
                    "is_complete": not sug_trunc,
                    "note": "targetingsuggestions natijalari olindi.",
                })
            else:
                limitations.append(f"targetingsuggestions qo'shimcha so'rovi bajarilmadi: {sug_fetched['error']}")

    # Step C: Account-scoped targetingvalidation
    validation_executed = False
    if validate_results and acct and items_by_key:
        validation_executed, val_err = _run_targeting_validation(
            base_url=base_url,
            api_version=api_version,
            account_id=acct,
            headers=headers,
            items_by_key=items_by_key,
            checked_at=checked_at,
        )
        if val_err:
            limitations.append(val_err)
    elif not acct:
        limitations.insert(
            0,
            "Reklama akkaunt ID si (`--account-id act_...`) berilmagani sababli global `/search?type=adinterest` ishlatildi va "
            "`/{ad-account-id}/targetingvalidation` bajarilmadi. Topilgan rasmiy natijalar `FOUND_NOT_VALIDATED` holatida qoldirildi.",
        )

    # Step D: Score & Rank all official items by Transparent Relevance Model (NOT API arrival order!)
    verified_all: list[dict[str, Any]] = []
    unavailable_options: list[dict[str, Any]] = []

    for item in items_by_key.values():
        rk_info = score_and_rank_candidate(
            item=item,
            product=product,
            niche=niche,
            customer_profile=customer_profile,
            problem_solved=problem_solved,
            customer_needs=customer_needs,
            purchase_intent=purchase_intent,
            complementary_products=complementary_products,
            objective=objective,
            explicit_queries=queries,
            expanded_queries=expanded_queries,
        )
        item.update(rk_info)
        if item["validation_status"] == STATUS_UNAVAILABLE_OR_CONSOLIDATED:
            unavailable_options.append(item)
        else:
            verified_all.append(item)

    # Rank: VERIFIED_AVAILABLE first, then FOUND_NOT_VALIDATED; within each status, sort by relevance_score DESC, then api_arrival_order ASC
    status_priority = {
        STATUS_VERIFIED_AVAILABLE: 0,
        STATUS_FOUND_NOT_VALIDATED: 1,
    }
    verified_all.sort(
        key=lambda x: (
            status_priority.get(x["validation_status"], 9),
            -float(x.get("relevance_score", 0.0)),
            int(x.get("api_arrival_order", 9999)),
        )
    )

    # Separate primary relevant verified recommendations from low-relevance / off-target API noise
    primary_recommended = [
        it for it in verified_all
        if it.get("is_primary_recommendation", True) and float(it.get("relevance_score", 0.0)) >= min_relevance_score
    ]
    excluded_low_relevance = [
        it for it in verified_all
        if it not in primary_recommended
    ]

    # verified_targeting_options places all relevant verified options first (ranked by relevance), followed by any low-relevance official items
    # so exact API-returned options are never lost while top-ranked items are always the relevant ones!
    verified_options = primary_recommended + excluded_low_relevance

    found_names_lower = {it["name"].lower() for it in verified_options}
    filtered_unverified = [
        idea for idea in related_unverified_ideas
        if idea["candidate_term"].lower() not in found_names_lower
    ]

    # Build Recommended Audience Combinations & Thematic Test Groups STRICTLY from primary_recommended official options
    # (Never include excluded_low_relevance noise or RELATED_UNVERIFIED ideas in combinations!)
    strictly_verified_primary = [it for it in primary_recommended if it["validation_status"] == STATUS_VERIFIED_AVAILABLE]
    usable_pool = strictly_verified_primary if strictly_verified_primary else primary_recommended
    combinations: list[dict[str, Any]] = []
    test_groups: list[dict[str, Any]] = []

    if usable_pool:
        pool_status = STATUS_VERIFIED_AVAILABLE if strictly_verified_primary else STATUS_FOUND_NOT_VALIDATED
        test_groups = _build_test_groups(usable_pool, pool_status)
        for tg in test_groups:
            combinations.append({
                "layer_name": tg["group_id"],
                "group_title": tg["group_name"],
                "grouping_reason": tg["grouping_reason"],
                "options_status": pool_status,
                "requires_validation_before_launch": (pool_status != STATUS_VERIFIED_AVAILABLE),
                "included_options": [
                    {
                        "id": opt["id"],
                        "name": opt["name"],
                        "type": opt["type"],
                        "validation_status": opt["validation_status"],
                        "relevance_score": opt["relevance_score"],
                        "relevance_tier": opt["relevance_tier"],
                        "source_endpoint": opt["source_endpoint"],
                    }
                    for opt in tg["interests"]
                ],
                "recommended_exclusions": ["Purchase_180d", "CRM_Active_Clients", "LeadForm_Submitted_90d"],
            })
        combo_block = {
            "status": "BUILT_FROM_OFFICIAL_API_RESULTS",
            "source_validation_status": pool_status,
            "ranking_method": "TRANSPARENT_5_FACTOR_RELEVANCE_MODEL (not raw API arrival order)",
            "excluded_irrelevant_official_count": len(excluded_low_relevance),
            "note": (
                f"Tavsiyalar {len(usable_pool)} ta yuqori moslikdagi (`VERIFIED_AVAILABLE`) rasmiy Meta opsiyasidan mavzuli sinov guruhlariga (Test Groups) bo'lib tuzildi."
                if pool_status == STATUS_VERIFIED_AVAILABLE
                else f"DIQQAT: Tavsiyalar {len(usable_pool)} ta yuqori moslikdagi (`FOUND_NOT_VALIDATED`) rasmiy qidiruv natijasidan tuzildi — "
                     "kampaniyani yoqishdan oldin `--account-id act_...` bilan `targetingvalidation` tekshiruvidan o'tkazing."
            ),
            "combinations": combinations,
            "suggested_test_groups": test_groups,
            "broad_vs_detailed_guidance": _build_broad_vs_detailed_guidance(niche, objective, spec_cat, verified_count=len(usable_pool)),
        }
    else:
        broad_guide = _build_broad_vs_detailed_guidance(niche, objective, spec_cat, verified_count=0)
        combo_block = {
            "status": "NO_VERIFIED_OPTIONS_AVAILABLE",
            "source_validation_status": STATUS_NOT_FOUND,
            "ranking_method": "TRANSPARENT_5_FACTOR_RELEVANCE_MODEL",
            "excluded_irrelevant_official_count": len(excluded_low_relevance),
            "note": (
                "Rasmiy API qidiruvida taklifga mos tasdiqlangan variant topilmagani sababli kombinatsiya tuzilmadi "
                "(tasdiqlanmagan AI g'oyalaridan yoki aloqasiz API natijalaridan kombinatsiya qurish taqiqlangan)."
            ),
            "combinations": [],
            "suggested_test_groups": [],
            "broad_vs_detailed_guidance": broad_guide,
        }

    is_complete = (not any_truncated) and (not api_failures)
    if any_truncated:
        overall_status = (
            "LIVE_SEARCH_AND_VALIDATION_PARTIAL_TRUNCATED"
            if validation_executed
            else "LIVE_SEARCH_ONLY_PARTIAL_TRUNCATED"
        )
    elif api_failures:
        overall_status = (
            "LIVE_SEARCH_AND_VALIDATION_PARTIAL_ERRORS"
            if validation_executed
            else "LIVE_SEARCH_ONLY_PARTIAL_ERRORS"
        )
    else:
        overall_status = (
            "LIVE_SEARCH_AND_VALIDATION_COMPLETED"
            if validation_executed
            else "LIVE_SEARCH_ONLY_NO_VALIDATION"
        )

    live_status_obj = {
        "executed": True,
        "status": overall_status,
        "is_complete": is_complete,
        "is_truncated": any_truncated,
        "total_pages_fetched": total_pages_fetched,
        "validation_executed": validation_executed,
        "error_category": "PARTIAL_QUERY_ERRORS" if api_failures else ("TRUNCATED_PAGINATION" if any_truncated else "NONE"),
        "api_version": api_version,
        "locale_used": effective_locale,
        "checked_at": checked_at,
        "served_from_valid_cache": False,
        "cache_status": cache_status,
        "cache_key": cache_key,
        "counts": {
            "verified_available": sum(1 for x in verified_options if x["validation_status"] == STATUS_VERIFIED_AVAILABLE),
            "found_not_validated": sum(1 for x in verified_options if x["validation_status"] == STATUS_FOUND_NOT_VALIDATED),
            "primary_recommended": len(primary_recommended),
            "excluded_low_relevance": len(excluded_low_relevance),
            "unavailable_or_consolidated": len(unavailable_options),
            "related_unverified": len(filtered_unverified),
            "not_found_queries": len(not_found_queries),
            "total_results_count": len(verified_options) + len(unavailable_options),
            "total_pages_fetched": total_pages_fetched,
            "truncated_queries_count": sum(1 for qd in query_diagnostics if qd.get("is_truncated")),
        },
        "partial_api_failures": api_failures,
        "query_diagnostics": query_diagnostics,
    }

    targetologist_rep = _build_targetologist_report(
        product=product, niche=niche, customer_profile=customer_profile,
        problem_solved=problem_solved, customer_needs=customer_needs,
        purchase_intent=purchase_intent, complementary_products=complementary_products,
        objective=objective, country=country, locale_used=effective_locale,
        ad_account_id=acct, special_ad_category=spec_cat,
        live_check_status=live_status_obj, primary_recommended=primary_recommended,
        excluded_low_relevance=excluded_low_relevance, unavailable_options=unavailable_options,
        related_unverified=filtered_unverified, not_found_queries=not_found_queries,
        test_groups=test_groups, broad_guidance=combo_block["broad_vs_detailed_guidance"],
        limitations=limitations,
    )

    result_payload = {
        "schema": "tyrion.detailed_targeting_accuracy/v5",
        "query_context": {
            "product": product,
            "niche": niche,
            "customer_profile": customer_profile,
            "problem_solved": problem_solved,
            "customer_needs": customer_needs,
            "purchase_intent": purchase_intent,
            "complementary_products": complementary_products,
            "objective": objective.upper(),
            "country": country.upper(),
            "language": language,
            "detected_query_language": detected_lang,
            "locale": effective_locale,
            "ad_account_id": acct or None,
            "special_ad_category": spec_cat,
            "max_queries": safe_max_queries,
            "generated_search_queries": expanded_queries,
            "cache_key": cache_key,
        },
        "live_check_status": live_status_obj,
        "query_diagnostics": query_diagnostics,
        "verified_targeting_options": verified_options,
        "primary_recommended_interests": primary_recommended,
        "excluded_low_relevance_options": excluded_low_relevance,
        "unavailable_or_consolidated_options": unavailable_options,
        "related_unverified_ideas": filtered_unverified,
        "not_found_queries": not_found_queries,
        "recommended_audience_combinations": combo_block,
        "targetologist_report": targetologist_rep,
        "limitations_and_disclosures": limitations,
    }

    if not api_failures and not any_truncated:
        _save_cache(
            cache_path=cache_path,
            cache_key=cache_key,
            api_version=api_version,
            ttl_seconds=cache_ttl_seconds,
            query_params=cache_context,
            payload=result_payload,
        )

    return result_payload


def main(argv: list[str] | None = None) -> int:
    effective_argv = list(sys.argv[1:] if argv is None else argv)
    if effective_argv and effective_argv[0].startswith("-") and effective_argv[0] not in ("-h", "--help"):
        effective_argv = ["search", *effective_argv]

    parser = argparse.ArgumentParser(
        prog="meta-targeting-engine.py",
        description="Tyrion v6.0 Meta Ads Detailed Targeting Discovery, Verification & Relevance Ranking Engine",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Mahsulot/nisha bo'yicha Detailed Targeting variantlarini rasmiy Meta API orqali qidirish, tekshirish va saralash")
    p_search.add_argument("--product", default="", help="Mahsulot yoki xizmat tavsifi (masalan: 'Tish implantatsiyasi va vinirlar' yoki 'Стоматология Ташкент')")
    p_search.add_argument("--niche", default="ecom", choices=list(NICHE_SEED_CANDIDATES.keys()))
    p_search.add_argument("--customer-profile", default="", help="Maqsadli mijoz profili")
    p_search.add_argument("--problem", "--problem-solved", dest="problem_solved", default="", help="Mahsulot hal qiladigan asosiy muammo")
    p_search.add_argument("--needs", "--customer-needs", dest="customer_needs", default="", help="Mijoz ehtiyojlari")
    p_search.add_argument("--intent", "--purchase-intent", dest="purchase_intent", default="", help="Xarid niyati (purchase intent)")
    p_search.add_argument("--complementary", "--complementary-products", dest="complementary_products", default="", help="Yondosh (komplementar) mahsulotlar va kategoriyalar")
    p_search.add_argument("--objective", default="SALES", choices=["SALES", "LEADS", "ENGAGEMENT", "TRAFFIC", "AWARENESS"])
    p_search.add_argument("--country", default="UZ")
    p_search.add_argument("--language", default="auto", help="Any BCP 47 language code (en, de, fr, es, ar, uz-Latn, uz_latin, uz_cyrillic, ru, auto)")
    p_search.add_argument("--query", action="append", default=[], help="Aniq qidiruv so'rovi (bir nechta berish mumkin — hech qachon tushirib qoldirilmaydi)")
    p_search.add_argument("--max-queries", type=int, default=12, help="Generatsiya qilinadigan maksimal qidiruv so'rovlari soni (default: 12)")
    p_search.add_argument("--min-relevance", type=float, default=35.0, help="Asosiy tavsiyaga kiritish uchun minimal moslik balli (0..100, default: 35.0)")
    p_search.add_argument("--account-id", "--ad-account-id", dest="account_id", default="", help="Meta Ad Account ID (`act_...`) — targetingsearch va targetingvalidation uchun")
    p_search.add_argument("--special-ad-category", default="NONE", choices=list(SPECIAL_AD_CATEGORIES))
    p_search.add_argument("--suggestions", action="store_true", help="`/{act_id}/targetingsuggestions` endpointini ham chaqirish")
    p_search.add_argument("--no-validate", action="store_true", help="`targetingvalidation` qadamini o'tkazib yuborish")
    p_search.add_argument("--limit", type=int, default=15)
    p_search.add_argument("--max-pages", type=int, default=2)
    p_search.add_argument("--locale", default="en_US", help="Meta API locale (masalan: en_US, ru_RU yoki auto)")
    p_search.add_argument("--cache-file", default="", help="Ixtiyoriy TTL kesh fayli yo'li")
    p_search.add_argument("--cache-ttl", type=int, default=3600, help="Kesh yaroqlilik muddati (soniya)")
    p_search.add_argument("--json", action="store_true")

    args = parser.parse_args(effective_argv)
    try:
        cpath = Path(args.cache_file) if args.cache_file else None
        res = search_and_validate_targeting(
            product=args.product,
            niche=args.niche,
            customer_profile=args.customer_profile,
            problem_solved=args.problem_solved,
            customer_needs=args.customer_needs,
            purchase_intent=args.purchase_intent,
            complementary_products=args.complementary_products,
            objective=args.objective,
            country=args.country,
            language=args.language,
            queries=args.query,
            ad_account_id=args.account_id,
            special_ad_category=args.special_ad_category,
            include_suggestions=args.suggestions,
            validate_results=not args.no_validate,
            limit_per_query=args.limit,
            max_pages_per_query=args.max_pages,
            max_queries=args.max_queries,
            min_relevance_score=args.min_relevance,
            locale=args.locale,
            cache_path=cpath,
            cache_ttl_seconds=args.cache_ttl,
        )
    except Exception as exc:
        print(f"Xato: {tcore.redact_secrets(str(exc))}", file=sys.stderr)
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    lcs = res["live_check_status"]
    tr = res["targetologist_report"]
    bu = tr["1_business_and_audience_understanding"]
    print("=" * 80)
    print("  🎯 TYRION DETAILED TARGETING REPORT (TARGETOLOGIST EDITION)")
    print("=" * 80)
    print("  1. BIZNES VA AUDITORIYA TAHLILI (Business & Audience Understanding):")
    print(f"     • Taklif / Mahsulot : {bu['product_or_service']} (Nisha: {bu['niche']}, Maqsad: {bu['campaign_objective']})")
    print(f"     • Asosiy Muammo     : {bu['problem_solved']}")
    print(f"     • Mijoz va Niyat    : {bu['customer_profile_and_needs']} | {bu['purchase_intent']}")
    print(f"     • Bozor va Locale   : Country={bu['target_market_country']}, Locale={bu['locale_used']}, SpecialAdCategory={bu['special_ad_category']}")

    print(
        f"\n  2. LIVE TEKSHIRUV HOLATI : {lcs['status']} "
        f"(executed={lcs['executed']}, is_complete={lcs.get('is_complete')}, is_truncated={lcs.get('is_truncated')}, "
        f"pages_fetched={lcs.get('total_pages_fetched', 0)}, API={lcs['api_version']}, locale={lcs.get('locale_used')})"
    )
    if lcs.get("is_truncated"):
        print("     ⚠️ OGOHLANTIRISH      : [TRUNCATED / NATIJA TO'LIQ EMAS] Sahifalash limiti tugadi; kesilgan qidiruv to'liq tekshirilgan hisoblanmaydi!")
    if lcs.get("error_message"):
        print(f"     Sabab / Xato          : [{lcs.get('error_category')}] {lcs['error_message']}")
        if lcs.get("next_diagnostic_step"):
            print(f"     Keyingi Qadam         : {lcs['next_diagnostic_step']}")

    q_diags = res.get("query_diagnostics") or []
    if q_diags:
        print(f"\n  2B. SO'ROVLAR DIAGNOSTIKASI ({len(q_diags)} ta so'rov):")
        for qd in q_diags:
            trunc_badge = " [TRUNCATED]" if qd.get("is_truncated") else ""
            print(
                f"     • '{qd['query']}' (origin={qd.get('query_origin', 'query')}, locale={qd.get('locale_used', 'en_US')}) "
                f"-> status={qd['status']}{trunc_badge} | pages={qd['pages_fetched']} | results={qd['results_count']}"
            )

    prim = res.get("primary_recommended_interests") or []
    print(f"\n  3. MOSLIK BO'YICHA SARALANGAN TASDIQLANGAN INTERESTLAR ({len(prim)} ta):")
    if not prim:
        print("     • (Rasmiy API dan tasdiqlangan va taklifga mos variant yo'q)")
    for idx, it in enumerate(prim, 1):
        bounds = (
            f"hajm: {it['audience_size_lower_bound']:,}..{it['audience_size_upper_bound']:,}"
            if it["audience_size_lower_bound"] is not None and it["audience_size_upper_bound"] is not None
            else "hajm: API qaytarmagan"
        )
        path_txt = f" | yo'l: {' > '.join(it['path'])}" if it.get("path") else ""
        print(
            f"     {idx}. [{it['validation_status']}] {it['name']} (id={it['id']}, type={it['type']}, "
            f"relevance={it['relevance_score']}/100 [{it['relevance_tier']}], {bounds}{path_txt})"
        )
        print(f"        Manba: {it['source_endpoint']} | So'rov: '{it['search_query']}' | {it['relevance_reason']}")

    excl = res.get("excluded_low_relevance_options") or []
    if excl:
        print(f"\n  3B. PAST MOSLIK / ALOQASIZ DEB CHETLATILGAN RASMIY NATIJALAR ({len(excl)} ta):")
        for it in excl:
            print(f"     • [{it['validation_status']}] {it['name']} (id={it['id']}, relevance={it['relevance_score']}/100) — {it['relevance_reason']}")

    if res["unavailable_or_consolidated_options"]:
        print(f"\n  4. ESKIRGAN YOKI BIRLASHTIRILGAN VARIANTLAR ({len(res['unavailable_or_consolidated_options'])} ta):")
        for it in res["unavailable_or_consolidated_options"]:
            rep = (it.get("validation_details") or {}).get("consolidated_into")
            rep_str = f" -> Yangi variant: {rep['name']} (id={rep['id']})" if isinstance(rep, dict) else ""
            print(f"     • [{it['validation_status']}] {it['name']} (id={it['id']}){rep_str}")

    print(f"\n  5. TASDIQLANMAGAN, LEKIN MAZMUNAN MOS G'OYALAR (`RELATED_UNVERIFIED`, {len(res['related_unverified_ideas'])} ta):")
    for idea in res["related_unverified_ideas"][:8]:
        print(f"     • [{idea['validation_status']}] {idea['candidate_term']} (est. relevance={idea.get('relevance_score', '—')}/100) — {idea['explanation']}")

    if res["not_found_queries"]:
        print(f"\n  6. RASMIY NATIJA TOPILMAGAN SO'ROVLAR (`NOT_FOUND`, {len(res['not_found_queries'])} ta):")
        for nf in res["not_found_queries"]:
            print(f"     • [{nf['validation_status']}] '{nf['query']}' ({nf['source_endpoint']}, locale={nf.get('locale_used')})")

    t_groups = tr.get("6_suggested_test_groups") or []
    print(f"\n  7. TAVSIYA ETILGAN SINOV GURUHLARI (Suggested Test Groups: {len(t_groups)} ta):")
    if not t_groups:
        print(f"     • {res['recommended_audience_combinations']['note']}")
    for tg in t_groups:
        names_str = ", ".join(f"{o['name']} (id={o['id']}, {o['relevance_score']}/100)" for o in tg["interests"])
        print(f"     • {tg['group_name']}: {names_str}")
        print(f"       Sabab: {tg['grouping_reason']}")

    bg = tr["7_broad_targeting_alternatives"]
    print(f"\n  8. BROAD VS DETAILED TARGETING QAROR QOIDASI ({bg['recommended_approach']}):")
    print(f"     • {bg['summary_uz_ru']}")
    print(f"     • Qoida: {bg['anti_stacking_rule']}")

    print("\n  9. CHEKLOVLAR, YETISHMAYOTGAN MA'LUMOTLAR VA KEYINGI QADAMLAR:")
    for mi in tr["8_missing_inputs_limitations_and_next_steps"]["missing_inputs"]:
        print(f"     • [Kiritilsa yaxshi] {mi}")
    for lim in res["limitations_and_disclosures"]:
        print(f"     • {lim}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
