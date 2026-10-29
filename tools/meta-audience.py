#!/usr/bin/env python3
"""Tyrion Meta Ads Audience Engine v5.0 — Andromeda 2, O'zbekiston bozori va Detailed Targeting Accuracy integratsiyasi (0 token).

Asosiy modullar:
  1. architect          : Unit-ekonomikaga tayangan 4-qatlamli auditoriya rejasi + Exclusion matritsasi
  2. interests          : Nisha bo'yicha boshlang'ich qidiruv lug'ati (`RELATED_UNVERIFIED`) + Graph API v26.0 tekshiruvi
  3. detailed-targeting : To'liq 6-statusli (`VERIFIED_AVAILABLE`, `FOUND_NOT_VALIDATED`, `UNAVAILABLE_OR_CONSOLIDATED`,
                          `RELATED_UNVERIFIED`, `NOT_FOUND`, `API_UNAVAILABLE`) Detailed Targeting Accuracy hisoboti
  4. overlap            : Static Pool Overlap (<20% qoidasi) va Live Auction Overlap farqi
  5. saturation         : Ssenariy sezgirlik oralig'i (`scenario_sensitivity_window_days`) va charchash prognozi
  6. retargeting        : Haqiqiy trafikka tayangan dinamik Retargeting oynalari (--no-telegram-bot qo'llab-quvvatlanadi)
  7. lookalike          : Heuristic Seed Readiness Score (0-100) va 1%–5% hajm pog'onasi
  8. diagnose           : Meta Ads metrikalar zanjiridan (CPM->CTR->CVR->Sale) tor joyni topish
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import sys
import urllib.parse
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
import market_locale as mloc  # noqa: E402

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

DEFAULT_GRAPH_API_VERSION = "v26.0"
OVERLAP_WARNING_THRESHOLD_PCT = 20.0
OVERLAP_CRITICAL_THRESHOLD_PCT = 30.0


def get_graph_api_version() -> str:
    """Muhit o'zgaruvchisidan META_GRAPH_API_VERSION ni o'qiydi (standart: v26.0)."""
    ver = os.environ.get("META_GRAPH_API_VERSION", DEFAULT_GRAPH_API_VERSION).strip()
    return ver if ver else DEFAULT_GRAPH_API_VERSION


def _parse_bool_arg(val: str | bool) -> bool:
    if isinstance(val, bool):
        return val
    v = str(val).strip().lower()
    if v in ("1", "true", "yes", "y", "ha", "on"):
        return True
    if v in ("0", "false", "no", "n", "yoq", "off"):
        return False
    raise argparse.ArgumentTypeError(f"Noto'g'ri mantiqiy qiymat: {val!r} (true/false kiriting)")


def _validate_finite_positive(val: float, name: str, max_val: float = 100_000_000.0) -> float:
    fval = float(val)
    if not math.isfinite(fval) or fval <= 0.0 or fval > max_val:
        raise ValueError(f"{name} 0 dan katta va <= {max_val:g} bo'lishi shart (kiritildi: {val!r}).")
    return fval


def _validate_percentage(val: float, name: str) -> float:
    fval = float(val)
    if not math.isfinite(fval) or fval <= 0.0 or fval > 100.0:
        raise ValueError(
            f"{name} foiz ko'rsatkichi (0, 100] oralig'ida bo'lishi shart (kiritildi: {val!r}% — >100% iqtisodiy jihatdan imkonsiz)."
        )
    return fval


# 8 ta asosiy nisha bo'yicha boshlang'ich qidiruv urug'lari (CANDIDATE SEARCH SEEDS — RELATED_UNVERIFIED)
# MUHIM: Ushbu ro'yxat faqat qidiruv uchun boshlang'ich lug'atdir; live API tasdig'isiz `VERIFIED_AVAILABLE` deb ko'rsatilmaydi!
NICHE_TAXONOMY: dict[str, dict] = {
    "ecom": {
        "title": "E-Commerce, Onlayn Do'kon va Chakana Savdo",
        "core_interests": [
            "Online shopping", "Shopping and fashion", "Boutique", "Discount store",
            "Consumer electronics", "Home appliances", "Department store"
        ],
        "behaviors": [
            "Engaged Shoppers (Xarid tugmasini bosgan faol xaridorlar — gipoteza)",
            "Mobile Device User: Flagship Smartphone Users (qurilma gipotezasi)",
        ],
        "creative_angles": [
            "TOF Problem/Solution: Mahsulot muammoni 3 soniyada qanday hal qiladi (UGC unboxing)",
            "TOF Social Proof: Real mijoz sharhlari va yetkazib berish jarayoni",
            "BOF Objection Crusher: Nasiya (Uzum/Payme bo'lib to'lash), kafolat va bepul yetkazish"
        ],
        "recommended_cpa_ratio": 0.08,
    },
    "edu": {
        "title": "Ta'lim, Kurslar, Xususiy Maktab va O'quv Markazlari",
        "core_interests": [
            "Higher education", "Online learning", "Language school", "IELTS",
            "Professional certification", "Career development", "Parenting (K-12 uchun)"
        ],
        "behaviors": [
            "Parents (All) / Parents with teenagers (13-17) / Parents with early school-age children",
            "Frequent Travelers / International education seekers"
        ],
        "creative_angles": [
            "TOF Transformation: O'quvchining oldingi va keyingi natijasi (IELTS 7.5+ / ishga kirish keysi)",
            "TOF Authority/Teacher: Ustoz metodikasi va 1-bepul sinov darsi / diagnostika",
            "BOF Urgency/Guarantee: Guruh to'lishiga 4 ta joy qoldi + shartnoma/natija kafolati"
        ],
        "recommended_cpa_ratio": 0.06,
    },
    "real-estate": {
        "title": "Ko'chmas Mulk (Novostroyka, Tijorat Binolari, Xonadonlar)",
        "core_interests": [
            "Real estate", "Property investment", "Apartment", "Mortgage loan",
            "Luxury real estate", "Interior design", "Architecture"
        ],
        "behaviors": [
            "Frequent International Travelers (to'lov qobiliyati bo'yicha marketing gipotezasi)",
            "Business Decision Makers / Small Business Owners",
            "Flagship device owners (marketing gipotezasi)"
        ],
        "creative_angles": [
            "TOF Financial Plan: Boshlang'ich to'lov va 0% muddatli to'lov (rassrochka) hisob-kitobi",
            "TOF Infrastructure/Location: Joylashuv, metro/maktab yaqinligi va qurilish jarayoni (jonli video)",
            "BOF Investor ROI: Kvadrat metr narxi o'sishi va ijara daromadliligi jadvali"
        ],
        "recommended_cpa_ratio": 0.12,
    },
    "medical": {
        "title": "Tibbiyot, Stomatologiya, Estetika va Sog'lomlashtirish Klinikalari",
        "core_interests": [
            "Healthcare", "Dentistry", "Cosmetic dentistry", "Physical therapy",
            "Wellness", "Medical specialty", "Skin care"
        ],
        "behaviors": [
            "Geo-radius targeting (klinika atrofida +5..15 km yoki shahar bo'yicha)",
            "Age-segmented cohorts (30-55 yosh qatlam)"
        ],
        "creative_angles": [
            "TOF Doctor Authority: Shifokor tushuntirishi — og'riqsiz va xavfsiz davolash mexanizmi (Policy-safe!)",
            "TOF Patient Story: Mijozning intervyu-fikri (Meta taqiqlagan 'before/after' yaqin plan rasmlarsiz!)",
            "BOF Free Consultation/Diagnostics: Bepul birlamchi ko'rik yoki 3D diagnostika paketi"
        ],
        "recommended_cpa_ratio": 0.07,
    },
    "b2b": {
        "title": "B2B Xizmatlar, SaaS, Ulgurji Savdo va Agentliklar",
        "core_interests": [
            "Small and medium-sized enterprises", "Entrepreneurship", "Business management",
            "Digital marketing", "Customer relationship management (CRM)", "Enterprise software"
        ],
        "behaviors": [
            "Facebook Page Admins (Business Page Admins)",
            "Small Business Owners",
            "Instagram Business Profile Admins"
        ],
        "creative_angles": [
            "TOF Cost of Inaction: Biznesda yo'qotilayotgan pul/vaqt auditi (aniq raqamlar bilan)",
            "TOF Case Study: 'Qanday qilib X kompaniyasi 30 kunda sotuvni +42% oshirdi' tahlili",
            "BOF Risk-Free Audit/Demo: 15 daqiqalik bepul tizim auditi yoki tayyor shablon lead-magnet"
        ],
        "recommended_cpa_ratio": 0.10,
    },
    "beauty": {
        "title": "Go'zallik, Parfyumeriya, Kosmetika va Moda Brendlari",
        "core_interests": [
            "Cosmetics", "Fragrances", "Beauty salon", "Skin care",
            "Luxury goods", "Women's clothing", "Men's fashion"
        ],
        "behaviors": [
            "Engaged Shoppers",
            "Instagram active engagers"
        ],
        "creative_angles": [
            "TOF Sensory/Emotion: Mahsulot teksturasi, qadoqlanishi va komplement olish hissiyoti",
            "TOF Bundle/Tester Offer: Sinov to'plami (Discovery set) yoki '2+1' maxsus taklifi",
            "BOF Fast Delivery: Toshkent bo'ylab 2 soatda yetkazish + original mahsulot kafolati"
        ],
        "recommended_cpa_ratio": 0.06,
    },
    "auto": {
        "title": "Avto-servis, Deteyling, Ehtiyot Qismlar va Avtosalonlar",
        "core_interests": [
            "Automobile", "Car dealership", "Auto detailing", "Vehicle insurance",
            "SUV", "Electric vehicle", "Automotive repair shop"
        ],
        "behaviors": [
            "Men/Women 24-55 in urban centers",
            "Engaged Shoppers"
        ],
        "creative_angles": [
            "TOF Process ASMR/Visual: Avtomobilga xizmat ko'rsatish jarayoni va sifat kafolati",
            "TOF Price Transparency: Aniq paket narxlari va yashirin to'lovlarsiz smeta",
            "BOF Lead Magnet: Bepul diagnostika yoki mavsumiy chek-list"
        ],
        "recommended_cpa_ratio": 0.07,
    },
    "local": {
        "title": "Lokal Xizmatlar, Fitness, Restoran, Mehmonxona va Dam Olish Zonalari",
        "core_interests": [
            "Physical fitness", "Gym", "Restaurants", "Tourism",
            "Resort", "Hotel", "Family entertainment"
        ],
        "behaviors": [
            "People living in or recently in this location (Geo Pin +3..10 km)",
            "Frequent Travelers / Weekend commuters"
        ],
        "creative_angles": [
            "TOF Atmosphere Tour: 15 soniyalik POV video-sayohat va muhit namoyishi",
            "TOF First-Visit Offer: Birinchi tashrif yoki oilaviy paket uchun maxsus bonus",
            "BOF Instant Booking: Telegram bot yoki Direct orqali 1 daqiqada joy band qilish"
        ],
        "recommended_cpa_ratio": 0.05,
    },
}

SOLVENTNOST_FILTERS = [
    "Engaged Shoppers (So'nggi 7 kunda 'Shop Now' bosganlar — xarid faolligi gipotezasi, `RELATED_UNVERIFIED`)",
    "Frequent International Travelers (Chet elga chiquvchilar — to'lov qobiliyati bo'yicha marketing gipotezasi, `RELATED_UNVERIFIED`)",
    "Mobile Device: Flagship / iPhone Pro Series (Yuqori chekli mahsulotlar uchun qurilma gipotezasi — tasdiqlangan daromad filtri emas, `RELATED_UNVERIFIED`)",
    "Facebook Page Admins & Small Business Owners (B2B qaror qabul qiluvchilar gipotezasi, `RELATED_UNVERIFIED`)",
    "Geo-Tiering: Toshkent shahri alohida kampaniya/ad setda, Viloyatlar alohida ad setda (CPM farqi sababli arxitektura qoidasi)",
]



def _build_layer_2_targeting(
    niche: str,
    tax: dict,
    cold_budget: float,
    currency: str,
    product: str = "",
    customer_profile: str = "",
    problem_solved: str = "",
    queries: list[str] | None = None,
    ad_account_id: str = "",
    live_targeting: bool | None = None,
) -> dict:
    tok = os.environ.get("META_ACCESS_TOKEN", "").strip()
    has_token = bool(tok and tok != "your_meta_access_token_here")
    run_live = bool(live_targeting) if live_targeting is not None else (has_token and bool(product or problem_solved or queries or ad_account_id))

    if run_live:
        mte = importlib.import_module("meta-targeting-engine")
        rep = mte.search_and_validate_targeting(
            product=product,
            niche=niche,
            customer_profile=customer_profile,
            problem_solved=problem_solved,
            queries=queries,
            ad_account_id=ad_account_id,
        )
        prim = rep.get("primary_recommended_interests") or []
        if prim:
            top_status = prim[0]["validation_status"]
            top_names = [f"{it['name']} (id={it['id']}, score={it['relevance_score']}/100)" for it in prim[:5]]
            return {
                "layer": "2-Qatlam: Verified Detailed Targeting Test Groups & Solventnost Hypotheses (TOF)",
                "budget_share": mloc.round_currency(cold_budget * 0.45, currency),
                "budget_share_usd": round(cold_budget * 0.45, 2),
                "targeting_verification_status": top_status,
                "verified_interests": prim[:5],
                "suggested_test_groups": rep["recommended_audience_combinations"].get("suggested_test_groups", []),
                "candidate_seed_terms": tax["core_interests"][:5],
                "targeting": f"Rasmiy Meta API tasdiqlagan ({top_status}) va moslik bo'yicha saralangan variantlar: {', '.join(top_names)}",
                "verification_instruction": rep["recommended_audience_combinations"]["note"],
                "advantage_plus_mode": "Yuqori chekli/B2B nishada Hard Interest (Advantage+ Audience OFF), ommaviy B2C da Advantage+ Audience ON (Suggestion sifatida).",
                "exclusions": ["Purchase_180d", "CRM_Active_Clients", "LeadForm_Submitted_90d"],
            }

    return {
        "layer": "2-Qatlam: Advantage+ Interest Stack & Solventnost Hypotheses (TOF)",
        "budget_share": mloc.round_currency(cold_budget * 0.45, currency),
        "budget_share_usd": round(cold_budget * 0.45, 2),
        "targeting_verification_status": "RELATED_UNVERIFIED",
        "candidate_seed_terms": tax["core_interests"][:5],
        "targeting": (
            f"Nomzod qidiruv urug'lari (RELATED_UNVERIFIED — avval live API da tekshiring!): "
            f"{', '.join(tax['core_interests'][:5])} | Behavior gipotezasi: {tax['behaviors'][0]}"
        ),
        "verification_instruction": (
            "MUHIM: Ushbu nomlar statik qidiruv lug'atidan olingan (`RELATED_UNVERIFIED`). "
            "Reklamani yoqishdan oldin `python3 tools/meta-targeting-engine.py search --niche "
            f"{niche} --account-id act_...` orqali ularning Meta API da `VERIFIED_AVAILABLE` ekanini tasdiqlang."
        ),
        "advantage_plus_mode": "Yuqori chekli/B2B nishada Hard Interest (Advantage+ Audience OFF), ommaviy B2C da Advantage+ Audience ON (Suggestion sifatida).",
        "exclusions": ["Purchase_180d", "CRM_Active_Clients", "LeadForm_Submitted_90d"],
    }


def build_architecture(
    niche: str,
    daily_budget: float,
    geo: str = "uzbekistan",
    has_pixel: bool = True,
    has_crm: bool = True,
    ig_followers: int = 5000,
    target_cpa: float | None = None,
    measured_cpa: float | None = None,
    aov: float | None = None,
    margin_pct: float | None = None,
    lead_to_sale_cvr: float | None = None,
    currency: str = "USD",
    market: str = "",
    product: str = "",
    customer_profile: str = "",
    problem_solved: str = "",
    queries: list[str] | None = None,
    ad_account_id: str = "",
    live_targeting: bool | None = None,
) -> dict:
    """Andromeda 2 + O'zbekiston bozori uchun 4-qatlamli Meta Ads auditoriya arxitekturasi."""
    daily_budget = _validate_finite_positive(daily_budget, "daily_budget", max_val=10_000_000.0)
    if target_cpa is not None:
        target_cpa = _validate_finite_positive(target_cpa, "target_cpa", max_val=1_000_000.0)
    if measured_cpa is not None:
        measured_cpa = _validate_finite_positive(measured_cpa, "measured_cpa", max_val=1_000_000.0)
    if aov is not None:
        aov = _validate_finite_positive(aov, "aov", max_val=100_000_000.0)
    if margin_pct is not None:
        margin_pct = _validate_percentage(margin_pct, "margin_pct")
    if lead_to_sale_cvr is not None:
        lead_to_sale_cvr = _validate_percentage(lead_to_sale_cvr, "lead_to_sale_cvr")

    if (aov is not None) ^ (margin_pct is not None):
        raise ValueError("Unit-ekonomikadan CPA hisoblash uchun `--aov` va `--margin-pct` birgalikda berilishi shart.")

    tax = NICHE_TAXONOMY.get(niche, NICHE_TAXONOMY["ecom"])
    economic_warnings: list[str] = []

    if measured_cpa is not None:
        est_cpa = round(measured_cpa, 2)
        cpa_source = "MEASURED_HISTORICAL_CPA"
        cpa_confidence = "MODERATE_HISTORICAL_BASELINE"
        cpa_explanation = f"Akkauntning haqiqiy o'lchangan tarixiy CPA ko'rsatkichidan (${est_cpa}) olindi."
    elif aov is not None and margin_pct is not None:
        gross_margin_usd = aov * (margin_pct / 100.0)
        sale_target_cpa = gross_margin_usd * 0.65
        if lead_to_sale_cvr is not None:
            est_cpa = max(0.5, round(sale_target_cpa * (lead_to_sale_cvr / 100.0), 2))
            cpa_explanation = (
                f"Unit-ekonomikadan hisoblandi: AOV=${aov}, Marja={margin_pct}%, "
                f"Lid->Sotuv CVR={lead_to_sale_cvr}% (Break-even CPAning 65% xavfsiz chegarasi)."
            )
        else:
            est_cpa = max(1.0, round(sale_target_cpa, 2))
            cpa_explanation = (
                f"Unit-ekonomikadan hisoblandi: AOV=${aov}, Marja={margin_pct}% "
                f"(Break-even sotuv CPA=${gross_margin_usd:.2f} ning 65% xavfsiz chegarasi)."
            )
        cpa_source = "UNIT_ECONOMICS_DERIVED"
        cpa_confidence = "MODERATE_UNIT_ECONOMICS_MODEL"
        if target_cpa is not None and target_cpa > gross_margin_usd:
            economic_warnings.append(
                f"DIQQAT: Kiritilgan target_cpa (${target_cpa}) mahsulotning yalpi foydasidan (${gross_margin_usd:.2f}) katta — har bir sotuv zarar keltiradi!"
            )
    elif target_cpa is not None:
        est_cpa = round(target_cpa, 2)
        cpa_source = "USER_SPECIFIED_TARGET_GOAL"
        cpa_confidence = "UNVERIFIED_USER_TARGET"
        cpa_explanation = (
            f"Foydalanuvchi tomonidan maqsad (goal) sifatida kiritilgan CPA (${est_cpa}). "
            "DIQQAT: Bu o'lchangan tarixiy natija EMAS va unit-ekonomika (--aov, --margin-pct) bilan tasdiqlanmagan."
        )
    else:
        est_cpa = max(3.0, round(daily_budget * tax["recommended_cpa_ratio"], 2))
        cpa_source = "PROVISIONAL_HEURISTIC_FALLBACK"
        cpa_confidence = "LOW_PROVISIONAL_ESTIMATE"
        cpa_explanation = (
            f"DIQQAT: AOV, marja yoki real CPA kiritilmagani sababli nisha koeffitsiyenti "
            f"({tax['recommended_cpa_ratio']*100:.0f}% * kunlik byudjet) asosida taxminiy olindi. "
            "Aniq reja uchun `--measured-cpa` yoki `--aov` va `--margin-pct` parametrlarini bering."
        )

    min_daily_per_adset = round((est_cpa * 50.0) / 7.0, 2)
    max_adsets = max(1, min(6, int(daily_budget // max(min_daily_per_adset, 10.0))))

    if daily_budget < 30:
        cold_pct, warm_pct, hot_pct = 85, 15, 0
        structure_mode = "Konsolidatsiyalangan ABO (1-2 Ad Set: Broad + 1 Interest Stack)"
    elif daily_budget < 150:
        cold_pct, warm_pct, hot_pct = 75, 15, 10
        structure_mode = "Hybrid ABO Sandbox + Warm IG/Web Retargeting (3-4 Ad Set)"
    else:
        cold_pct, warm_pct, hot_pct = 70, 20, 10
        structure_mode = "Andromeda 1-5-5 CBO/ASC + Full-Funnel 1P Retargeting & Value LAL"

    cold_budget = round(daily_budget * (cold_pct / 100.0), 2)
    warm_budget = round(daily_budget * (warm_pct / 100.0), 2)
    hot_budget = round(daily_budget * (hot_pct / 100.0), 2)

    layers = [
        {
            "layer": "1-Qatlam: Broad + Creative Signal Steering (TOF)",
            "budget_share": mloc.round_currency(cold_budget * 0.55, currency),
            "budget_share_usd": round(cold_budget * 0.55, 2),
            "targeting": f"Geo: {geo.upper()} | Yosh: 22-54 | Ochiq (Broad) — kreativ burchakning o'zi algoritm uchun filtr vazifasini bajaradi.",
            "language_rule": "O'zbek (Lotin/Kirill) va Rus tilidagi kreativlarni bitta ad setga aralashtirmang — til bo'yicha alohida ad set oching.",
            "exclusions": ["Purchase_180d", "CRM_Active_Clients", "LeadForm_Submitted_90d"],
        },
        (lambda: _build_layer_2_targeting(
            niche=niche,
            tax=tax,
            cold_budget=cold_budget,
            currency=currency,
            product=product,
            customer_profile=customer_profile,
            problem_solved=problem_solved,
            queries=queries,
            ad_account_id=ad_account_id,
            live_targeting=live_targeting,
        ))(),
        {
            "layer": "3-Qatlam: First-Party (1P) Warm Retargeting (MOF — IG/Video/Telegram/Web)",
            "budget_share": mloc.round_currency(warm_budget, currency),
            "budget_share_usd": warm_budget,
            "custom_audiences": [
                f"IG_Engaged_30d (Instagram profil faollari — joriy obunachilar: {ig_followers:,})",
                "Video_Viewers_50pct_14d (Reels/Video reklamani kamida 50% ko'rgan qiziquvchilar)",
                "LeadForm_Opened_Not_Submitted_30d (Lead formani ochib to'ldirmaganlar)",
            ] + (["Web_Visitors_30d & ViewContent_14d (Pixel + CAPI)"] if has_pixel else ["⚠ Pixel yo'q: IG Direct va Lead Form engagement bazasiga tayaning"]),
            "exclusions": ["Purchase_180d", "LeadForm_Submitted_30d", "CRM_Converted_Buyers"],
        },
        {
            "layer": "4-Qatlam: Value Lookalike (LAL) & Hot BOF Closing",
            "budget_share": mloc.round_currency(hot_budget, currency),
            "budget_share_usd": hot_budget,
            "lal_strategy": (
                "Value-Based LAL 1% va 1-2% — FAQAT CRM/CAPI dagi to'lov qilgan mijozlar (kamida 100-500 ta sifatli lid/xaridor) asosida. Xom, sifatsiz lidlardan LAL qurmang!"
                if has_crm else
                "⚠ CRM bazasi ulanmagan: IG_DM_Messagers_90d yoki Purchase_180d (≥100 hodisa) yig'ilgach 1% LAL yoqing."
            ),
            "bof_closing": "AddToCart_14d + InitiateCheckout_7d + CRM_Unclosed_Leads_14d (E'tirozlarni yopuvchi BOF kreativlar bilan)",
            "exclusions": ["Purchase_30d (So'nggi 30 kunda xarid qilganlar)"],
        },
    ]

    exclusion_matrix = [
        {"stage": "Cold Prospecting (Broad / Interest / LAL)", "include": "Yangi auditoriya", "must_exclude": "Purchase_180d, CRM_Active_Clients, LeadForm_Submitted_90d"},
        {"stage": "Warm Engagement (MOF Retargeting)", "include": "IG_Engaged_30d, Video_50pct_14d, Web_30d", "must_exclude": "Purchase_180d, InitiateCheckout_7d, LeadForm_Submitted_30d"},
        {"stage": "Hot Conversion (BOF Retargeting)", "include": "AddToCart_14d, Checkout_7d, IG_DM_14d, CRM_Warm_Leads", "must_exclude": "Purchase_30d"},
        {"stage": "Advantage+ Shopping (ASC)", "include": "Avtomatik (20-50 xil kreativ)", "must_exclude": "Existing Customer Budget Cap <= 25-30% qilib qulflansin"},
    ]

    return {
        "niche": niche,
        "niche_title": tax["title"],
        "geo": geo,
        "currency": currency.upper(),
        "formatted_daily_budget": mloc.format_currency(daily_budget, currency),
        "daily_budget": mloc.round_currency(daily_budget, currency),
        "daily_budget_usd": round(daily_budget, 2),
        "estimated_target_cpa": mloc.round_currency(est_cpa, currency),
        "estimated_target_cpa_usd": est_cpa,
        "evidence_and_assumptions": {
            "cpa_source": cpa_source,
            "confidence_level": cpa_confidence,
            "cpa_derivation": cpa_explanation,
            "economic_warnings": economic_warnings,
            "detailed_targeting_status": "RELATED_UNVERIFIED_CANDIDATE_SEEDS",
            "solventnost_hypothesis_disclosure": (
                "Solventnost signallari (iPhone, xalqaro sayohat, Page Admin) Meta tomonidan tasdiqlangan rasmiy daromad "
                "filtri EMAS, balki kampaniyada A/B sinov orqali tekshiriladigan marketing gipotezasidir."
            ),
            "learning_phase_assumption": "Meta Andromeda 2 ad set Learning Phase'dan chiqishi uchun 7 kunda >=50 optimizatsiya hodisasi talab qilinadi.",
        },
        "learning_phase_guardrail": {
            "min_daily_budget_per_adset_usd": min_daily_per_adset,
            "recommended_active_adsets": max_adsets,
            "rule": "Har bir ad set haftasiga >=50 konversiya olishi shart; aks holda ad setlarni birlashtiring.",
        },
        "meta_2026_ai_stack_and_value_rules": {
            "five_system_hierarchy": ["GEM (Teacher Foundation Model)", "Andromeda (Retrieval + Entity ID Clustering)", "Lattice (Unified Cross-Surface Ranking + Sequence Learning)", "UTIS (User True Interest Survey Calibrator)", "Adaptive Ranking Model (<100ms Inference)"],
            "asc_api_mode": "smart_promotion_type=GUIDED_CREATION (Marketing API v25.0+ standard)",
            "value_rules_guidance": "When >=50 weekly conversions are reached, use Meta Value Rules (+200% to -90% bid multipliers, up to 10 rules per campaign) to prioritize high-LTV geo/age segments instead of splitting ad sets.",
            "entity_id_creative_rule": "Andromeda groups visually similar ads under 1 Entity ID (1 retrieval ticket). Pair each audience layer with 4-6 visually distinct PDA concepts (UGC Demo, Founder Authority, iMessage Reveal, Greenscreen, Static Comparison).",
            "verified_sources": [
                "https://greghal.no/en/blog/meta-ads-algorithm-2026-complete-guide/",
                "https://lineardesign.com/blog/metas-advantage-audience/",
            ],
        },
        "recommended_structure": structure_mode,
        "budget_split_usd": {
            f"cold_prospecting_{cold_pct}pct": cold_budget,
            f"warm_retargeting_{warm_pct}pct": warm_budget,
            f"hot_bof_and_lal_{hot_pct}pct": hot_budget,
        },
        "audience_layers": layers,
        "exclusion_matrix": exclusion_matrix,
        "uzbekistan_solventnost_filters": SOLVENTNOST_FILTERS,
        "recommended_creative_angles": tax["creative_angles"],
    }


def calc_overlap(size_a: int, size_b: int, shared: int) -> dict:
    """Ikki ad set auditoriyasi o'rtasidagi geometrik kesishmani (Static Pool Overlap) hisoblaydi."""
    if size_a <= 0 or size_b <= 0 or shared < 0:
        raise ValueError("Auditoriya hajmlari musbat bo'lishi shart.")
    if shared > min(size_a, size_b):
        raise ValueError("Umumiy (shared) auditoriya kichik to'plamdan katta bo'lishi mumkin emas.")

    smaller = min(size_a, size_b)
    larger = max(size_a, size_b)
    union = size_a + size_b - shared

    overlap_of_smaller_pct = round((shared / smaller) * 100.0, 2)
    overlap_of_larger_pct = round((shared / larger) * 100.0, 2)
    jaccard_pct = round((shared / union) * 100.0, 2) if union > 0 else 0.0

    if overlap_of_smaller_pct >= OVERLAP_CRITICAL_THRESHOLD_PCT:
        status = "CRITICAL_COLLISION"
        action = (
            f"Kichik ad setning {overlap_of_smaller_pct}% qismi ikkinchi ad set bilan ustma-ust tushmoqda (>={OVERLAP_CRITICAL_THRESHOLD_PCT:.0f}%). "
            "Ikki ad setni BITTA ad setga birlashtiring (konsolidatsiya) yoki kichik auditoriyani kattasidan Exclude qiling!"
        )
    elif overlap_of_smaller_pct >= OVERLAP_WARNING_THRESHOLD_PCT:
        status = "MODERATE_OVERLAP"
        action = (
            f"Auditoriya kesishishi {overlap_of_smaller_pct}% (>={OVERLAP_WARNING_THRESHOLD_PCT:.0f}% chegara qoidasi buzildi). "
            "O'zaro Exclude qoidasini kiriting va Ads Manager 'Delivery Insights -> Auction Overlap' ko'rsatkichini tekshiring."
        )
    else:
        status = "HEALTHY_ISOLATION"
        action = f"Auditoriya kesishishi xavfsiz darajada ({overlap_of_smaller_pct}% < {OVERLAP_WARNING_THRESHOLD_PCT:.0f}%). Ad setlar alohida ishlashi mumkin."

    return {
        "audience_a": size_a,
        "audience_b": size_b,
        "shared_audience": shared,
        "overlap_of_smaller_pct": overlap_of_smaller_pct,
        "overlap_of_larger_pct": overlap_of_larger_pct,
        "jaccard_index_pct": jaccard_pct,
        "threshold_policy_pct": OVERLAP_WARNING_THRESHOLD_PCT,
        "metric_type": "STATIC_AUDIENCE_POOL_INTERSECTION",
        "status": status,
        "recommendation": action,
        "auction_competition_disclaimer": (
            "MUHIM FARQ: Ushbu foiz ikki auditoriya to'plamining statik kesishmasidir (Static Pool Overlap). "
            "Real Meta auktsionidagi raqobat (Live Auction Overlap) bid, byudjet, placement va kreativ sifatiga "
            "qarab o'zgaradi. Haqiqiy auktsion to'qnashuvini Ads Manager Inspect oynasidan yoki `meta-insights-sync.py` orqali tekshiring."
        ),
    }


def calc_saturation(
    audience_size: int,
    daily_budget: float,
    cpm: float = 3.2,
    days: int = 14,
    active_reach_ratio: float = 0.60,
    measured_freq_7d: float | None = None,
) -> dict:
    """Auditoriya sig'imi, Frequency o'sishi va deterministik ssenariy sezgirlik oralig'ini (`scenario_sensitivity_window_days`) hisoblaydi."""
    if audience_size <= 0 or daily_budget <= 0 or cpm <= 0 or days <= 0:
        raise ValueError("Barcha parametrlar 0 dan katta bo'lishi shart.")
    if not (0.05 <= active_reach_ratio <= 1.0):
        raise ValueError("active_reach_ratio 0.05 va 1.0 oralig'ida bo'lishi shart.")

    reachable_pool = max(1, int(audience_size * active_reach_ratio))
    daily_impressions = (daily_budget / cpm) * 1000.0
    total_impressions = daily_impressions * days

    if measured_freq_7d is not None:
        measured_freq_7d = _validate_finite_positive(measured_freq_7d, "measured_freq_7d", max_val=100.0)
        daily_frequency_rate = measured_freq_7d / 7.0
        projected_frequency = round(daily_frequency_rate * days, 2)
        data_source_type = "MEASURED_ACCOUNT_DATA"
        confidence_level = (
            "MODERATE_CALIBRATED_LINEAR_PROJECTION (7-kunlik real Frequency bilan kalibrlangan, "
            "ammo kelajakdagi charchash chiziqli o'sish taxminiga tayanadi)"
        )
    else:
        daily_frequency_rate = daily_impressions / reachable_pool
        projected_frequency = round(total_impressions / reachable_pool, 2)
        data_source_type = "HEURISTIC_PRIOR_MODEL"
        confidence_level = (
            "LOW_TO_MODERATE_HEURISTIC_PRIOR (Prior ssenariy modeli — real CPM, reach va kreativ CTR ga qarab farq qiladi)"
        )

    fatigue_day = round(2.8 / daily_frequency_rate, 1) if daily_frequency_rate > 0 else 999.0
    conservative_day = round(max(1.0, fatigue_day * 0.72), 1)
    optimistic_day = round(min(999.0, fatigue_day * 1.30), 1)

    max_safe_daily_budget = round(((reachable_pool * 2.5) / 14.0 / 1000.0) * cpm, 2)

    if projected_frequency > 3.5:
        verdict = "OVERSATURATED_HIGH_RISK"
        advice = (
            f"{days} kunda o'rtacha Frequency ~{projected_frequency}x ga chiqadi "
            f"(ssenariy sezgirlik oralig'i: {conservative_day}–{optimistic_day} kun, tayanch nuqta ~{fatigue_day}-kun). "
            f"Bu auditoriya uchun kunlik byudjetni <= ${max_safe_daily_budget} ga tushiring yoki Broad/LAL orqali auditoriyani kengaytiring."
        )
    elif projected_frequency > 2.4:
        verdict = "WATCH_FATIGUE"
        advice = (
            f"{days} kunda Frequency ~{projected_frequency}x ga yetadi "
            f"(ssenariy sezgirlik oralig'i: {conservative_day}–{optimistic_day} kun). "
            "Har 7-10 kunda kamida 3 ta yangi hook kiriting."
        )
    else:
        verdict = "HEALTHY_CAPACITY"
        advice = f"Auditoriya sig'imi yetarli ({days} kunda Frequency ~{projected_frequency}x, ssenariy oralig'i >{conservative_day} kun). Masshtablash xavfsiz."

    sensitivity_window = {
        "conservative_early_fatigue_day": conservative_day,
        "baseline_fatigue_day": fatigue_day,
        "optimistic_late_fatigue_day": optimistic_day,
        "is_statistical_confidence_interval": False,
        "band_multipliers": "0.72x (downside fast fatigue) .. 1.30x (upside slow fatigue)",
    }

    return {
        "total_audience_size": audience_size,
        "active_reach_ratio": round(active_reach_ratio, 2),
        "estimated_reachable_pool": reachable_pool,
        "daily_budget_usd": round(daily_budget, 2),
        "cpm_usd": round(cpm, 2),
        "daily_impressions": int(daily_impressions),
        "period_days": days,
        "projected_frequency": projected_frequency,
        "estimated_fatigue_day": fatigue_day,
        "scenario_sensitivity_window_days": sensitivity_window,
        "estimated_fatigue_window_days": sensitivity_window,
        "max_safe_daily_budget_14d_usd": max_safe_daily_budget,
        "status": verdict,
        "recommendation": advice,
        "model_disclosure": {
            "data_source_type": data_source_type,
            "confidence_level": confidence_level,
            "interval_methodology": "DETERMINISTIC_SCENARIO_SENSITIVITY_BAND (0.72x..1.30x) — NOT_A_STATISTICAL_CONFIDENCE_INTERVAL",
            "assumptions": [
                f"Faol yetib boriladigan qatlam (active_reach_ratio) umumiy auditoriyaning {active_reach_ratio*100:.0f}% qismi ({reachable_pool:,} kishi) deb olindi.",
                f"O'rtacha CPM ${cpm:.2f} deb olindi (real kampaniyada auktsion raqobati va kreativ sifatiga qarab o'zgaradi).",
                "Charchash chegarasi Frequency=2.8x va chiziqli (linear) frequency o'sishi taxmini bo'yicha hisoblandi; bu statistik confidence interval emas, balki ssenariy sezgirlik oralig'idir.",
            ],
        },
    }


def query_live_graph_api(query: str, limit: int = 15, ad_account_id: str = "") -> list[dict]:
    """`meta-targeting-engine.py` orqali rasmiy Meta Graph API qidiruvini bajaradi."""
    mte = importlib.import_module("meta-targeting-engine")
    report = mte.search_and_validate_targeting(
        queries=[query] if query else None,
        ad_account_id=ad_account_id,
        limit_per_query=limit,
    )
    if not report["live_check_status"]["executed"]:
        return []
    return report["verified_targeting_options"]


def get_interests(
    niche: str,
    query: str = "",
    live: bool | None = None,
    product: str = "",
    customer_profile: str = "",
    problem_solved: str = "",
    customer_needs: str = "",
    purchase_intent: str = "",
    complementary_products: str = "",
    ad_account_id: str = "",
    special_ad_category: str = "NONE",
    max_queries: int = 12,
    locale: str = "en_US",
) -> dict:
    """Nisha bo'yicha qidiruv urug'lari (`RELATED_UNVERIFIED`) va live Graph API (`meta-targeting-engine.py`) hisobotini qaytaradi.
    Agar `META_ACCESS_TOKEN` sozlangan bo'lsa (yoki `live=True` berilsa), avtomatik live qidiruv va moslik saralashni bajaradi.
    """
    tax = NICHE_TAXONOMY.get(niche, NICHE_TAXONOMY["ecom"])
    q_term = query or tax["core_interests"][0]
    api_version = get_graph_api_version()

    mte = importlib.import_module("meta-targeting-engine")
    token_present = bool(os.environ.get("META_ACCESS_TOKEN", "").strip() and os.environ.get("META_ACCESS_TOKEN", "").strip() != "your_meta_access_token_here")
    should_run_live = bool(live) if live is not None else token_present

    if should_run_live:
        accuracy_report = mte.search_and_validate_targeting(
            product=product,
            niche=niche,
            customer_profile=customer_profile,
            problem_solved=problem_solved,
            customer_needs=customer_needs,
            purchase_intent=purchase_intent,
            complementary_products=complementary_products,
            queries=[query] if query else None,
            ad_account_id=ad_account_id,
            special_ad_category=special_ad_category,
            max_queries=max_queries,
            locale=locale,
        )
        live_results = accuracy_report["verified_targeting_options"]
        live_status = accuracy_report["live_check_status"]["status"]
    else:
        accuracy_report = None
        live_results = []
        live_status = "NOT_REQUESTED_OFFLINE_SEED_MODE"

    return {
        "niche": niche,
        "title": tax["title"],
        "graph_api_version": api_version,
        "api_version_warning": mloc.get_configured_api_version("META_GRAPH_API_VERSION", DEFAULT_GRAPH_API_VERSION).get("warning"),
        "static_taxonomy_status": mte.STATUS_RELATED_UNVERIFIED,
        "static_taxonomy_warning": (
            "DIQQAT: `core_interest_clusters` va `high_intent_behaviors` statik qidiruv lug'ati (`RELATED_UNVERIFIED`) hisoblanadi. "
            "Ularni Meta Ads Manager'da tasdiqlangan (`VERIFIED_AVAILABLE`) deb qabul qilmang — `--live` yoki `meta-targeting-engine.py` orqali tekshiring!"
        ),
        "live_verification_status": live_status,
        "core_interest_clusters": tax["core_interests"],
        "high_intent_behaviors": tax["behaviors"],
        "uzbekistan_solventnost_filters": SOLVENTNOST_FILTERS,
        "solventnost_hypothesis_disclaimer": (
            "Solventnost signallari (iPhone, xalqaro sayohat, Page Admin) Meta tomonidan tasdiqlangan daromad filtri EMAS, "
            "balki faqat tekshiriladigan marketing gipotezasidir (`MARKETING_HYPOTHESIS`)."
        ),
        "creative_angles": tax["creative_angles"],
        "graph_api_readonly_endpoint": f"GET https://graph.facebook.com/{api_version}/search?type=adinterest&q={urllib.parse.quote(q_term)}&limit=20",
        "live_api_results": live_results,
        "detailed_targeting_accuracy_report": accuracy_report,
    }


def calc_retargeting(
    aov: float = 100.0,
    daily_visitors: int = 300,
    ig_engagers_30d: int = 5000,
    video_viewers_14d: int = 8000,
    has_telegram_bot: bool = True,
) -> dict:
    """Dinamik Retargeting Oynalari (3d/7d/14d/30d/180d) va byudjet sig'imi hisoblagichi."""
    if daily_visitors < 0 or ig_engagers_30d < 0 or video_viewers_14d < 0:
        raise ValueError("Trafik va auditoriya ko'rsatkichlari manfiy bo'lishi mumkin emas.")

    sales_cycle = "LONG_HIGH_TICKET" if aov >= 300 else ("MEDIUM_CONSIDERATION" if aov >= 50 else "FAST_IMPULSE")
    hot_pool = int(daily_visitors * 7 * 0.25)
    warm_pool = int(video_viewers_14d * 0.6 + ig_engagers_30d * 0.4)
    social_pool = int(ig_engagers_30d)
    winback_pool = int(daily_visitors * 1.5)
    total_retargetable = hot_pool + warm_pool + social_pool

    if total_retargetable < 100:
        rec_daily_budget = 0.0
        readiness_status = "INSUFFICIENT_RETARGETING_POOL"
        readiness_note = (
            f"Jami retargeting bazasi ({total_retargetable} kishi) Meta Custom Audience minimal chegarasidan (<100 faol profil) kichik. "
            "Retargeting ad set ochmang — byudjetni 100% TOF (Broad/Interest) kampaniyaga yo'naltirib avval trafik yig'ing."
        )
    else:
        rec_daily_budget = round(max(2.0, min(150.0, (total_retargetable / 1000.0) * 0.95)), 2)
        readiness_status = "READY_FOR_RETARGETING"
        readiness_note = f"Retargeting bazasi yetarli ({total_retargetable:,} profil). Tavsiya etilgan kunlik byudjet: ${rec_daily_budget}."

    windows = [
        {
            "window": "W1: HOT INTENT (0–3 kun / 0–7 kun)",
            "sources": ["AddToCart_7d", "InitiateCheckout_7d", "LeadForm_Opened_Not_Submitted_7d"]
                       + (["Telegram_Bot_Started_No_Contact_7d"] if has_telegram_bot else []),
            "exclusions": ["Purchase_180d", "Qualified_Lead_30d"],
            "estimated_pool": hot_pool,
            "window_viable": hot_pool >= 100,
            "creative_angle": "E'tirozni yopish + Tezkor bonus / Bepul yetkazib berish / Nasiya eslatmasi",
            "target_frequency_7d": "4.0 – 6.0",
        },
        {
            "window": "W2: WARM VIDEO & DM (7–14 kun)",
            "sources": ["Video_Watched_50pct_14d", "IG_DM_Messaged_14d", "Website_Visitors_Top25_Time_14d"],
            "exclusions": ["Purchase_180d", "Qualified_Lead_30d", "W1_Hot_Intent_7d"],
            "estimated_pool": warm_pool,
            "window_viable": warm_pool >= 100,
            "creative_angle": "Mijoz sharhlari (UGC / Case Study) + Jarayon ichidan ko'rsatuv (Behind the scenes)",
            "target_frequency_7d": "2.8 – 4.2",
        },
        {
            "window": "W3: SOCIAL ENGAGERS (15–30 kun)",
            "sources": ["IG_Engagers_30d", "FB_Page_Engagers_30d", "Ad_Savers_Shares_30d"],
            "exclusions": ["Purchase_180d", "Qualified_Lead_30d", "W1_Hot_Intent_7d", "W2_Warm_14d"],
            "estimated_pool": social_pool,
            "window_viable": social_pool >= 100,
            "creative_angle": "Yangi Offer / Lead Magnet (PDF/Quiz/Diagnostika) orqali voronkaga tortish",
            "target_frequency_7d": "2.0 – 3.0",
        },
        {
            "window": "W4: WINBACK & LTV UPSELL (31–180 kun)",
            "sources": ["Purchase_180d", "CRM_Past_Clients_List"],
            "exclusions": ["Purchase_14d"],
            "estimated_pool": winback_pool,
            "window_viable": winback_pool >= 100,
            "creative_angle": "VIP mijozlar uchun yangi kolleksiya / Qayta xarid bonusi / Referal taklif",
            "target_frequency_7d": "1.5 – 2.5",
        },
    ]
    return {
        "aov_usd": aov,
        "has_telegram_bot": bool(has_telegram_bot),
        "sales_cycle_type": sales_cycle,
        "retargeting_readiness": readiness_status,
        "retargeting_note": readiness_note,
        "total_retargetable_pool": total_retargetable,
        "recommended_retargeting_daily_budget_usd": rec_daily_budget,
        "retargeting_windows": windows,
    }


def calc_lookalike(
    seed_size: int,
    seed_type: str = "purchase_ltv",
    country: str = "UZ",
) -> dict:
    """Lookalike (LAL) manba tayyorligi indeksi (Heuristic Seed Readiness Score) va 1%–5% pog'onali hajm hisoblagichi."""
    country_reach = {"UZ": 9_200_000, "KZ": 13_500_000, "US": 240_000_000, "IN": 380_000_000, "BR": 170_000_000, "DE": 45_000_000, "GB": 42_000_000, "UK": 42_000_000, "FR": 40_000_000, "AE": 9_800_000, "SA": 24_000_000, "SG": 4_500_000, "ID": 140_000_000, "JP": 65_000_000, "KR": 32_000_000, "GLOBAL": 100_000_000}
    base_pop = country_reach.get(country.upper(), 9_200_000)

    type_weights = {
        "purchase_ltv": (95, "CRM LTV / Yuqori chekli xaridorlar (Value-Based) — ENG KUCHLI SIGNAL"),
        "purchase_all": (85, "Barcha xaridorlar (Pixel + CAPI Purchase)"),
        "qualified_leads": (78, "CRM da tasdiqlangan sifatli lidlar (Qualified Leads)"),
        "raw_leads": (58, "Barcha forma/bot lidlari (ichida sifatsiz lidlar bo'lishi mumkin)"),
        "ig_engagers": (40, "Instagram/Video faollari (xarid niyati past — Broad ko'pincha yaxshiroq)"),
    }
    base_score, type_desc = type_weights.get(seed_type, (65, "Maxsus ro'yxat"))

    if seed_size >= 1000:
        size_bonus = 5
        size_verdict = "IDEAL_SEED_SIZE (>=1,000)"
    elif seed_size >= 300:
        size_bonus = -5
        size_verdict = "ACCEPTABLE_SEED_SIZE (300–999)"
    elif seed_size >= 100:
        size_bonus = -25
        size_verdict = "WEAK_SEED_SIZE (100–299 — algoritm signali zaif)"
    else:
        size_bonus = -50
        size_verdict = "INSUFFICIENT_SEED (<100 — Meta LAL yaratish tavsiya etilmaydi!)"

    quality_score = max(5, min(100, base_score + size_bonus))
    one_pct = int(base_pop * 0.01)

    tiers = [
        {"tier": "LAL 0%–1% (Core Twin)", "estimated_reach": one_pct, "min_daily_budget_usd": 20.0, "priority": "1-o'rinda sinov (Eng yaqin o'xshashlik)"},
        {"tier": "LAL 1%–2% (Expansion)", "estimated_reach": one_pct, "min_daily_budget_usd": 25.0, "priority": "1% isbotlangach scaling uchun"},
        {"tier": "LAL 2%–3% (Mid Scale)", "estimated_reach": one_pct, "min_daily_budget_usd": 30.0, "priority": "Katta byudjetda ($100+/kun) qo'shiladi"},
        {"tier": "LAL 3%–5% (Broad-Like)", "estimated_reach": one_pct * 2, "min_daily_budget_usd": 45.0, "priority": "Faqat yuqori hajmli B2C uchun"},
    ]
    return {
        "country": country.upper(),
        "seed_size": seed_size,
        "seed_type": seed_type,
        "seed_description": type_desc,
        "seed_size_verdict": size_verdict,
        "heuristic_seed_readiness_score_100": quality_score,
        "seed_quality_score_100": quality_score,
        "recommendation": (
            "1% Value-Based LAL ni alohida Ad Setda L1 Broad bilan A/B sinovga qo'ying."
            if quality_score >= 70
            else "Seed hajmi yoki sifati past — LAL o'rniga L1 Broad + L2 Solventnost Stack ishlating va avval 300+ sifatli konversiya yig'ing."
        ),
        "lal_tiers": tiers,
        "model_disclosure": {
            "score_type": "HEURISTIC_SEED_READINESS_INDEX",
            "is_meta_internal_score": False,
            "explanation": (
                "Ushbu 0–100 ball Meta algoritmining ichki bahosi EMAS, balki manba auditoriyaning (seed) "
                "hajmi (>=1,000 ideal, <100 yetarli emas) va hodisa turi (LTV xaridor vs xom lid) asosidagi "
                "ekspert tayyorlik indeksidir."
            ),
        },
    }


def diagnose_metrics(
    cpm: float,
    ctr: float,
    cpc: float,
    lp_cvr: float,
    lead_to_sale: float = 10.0,
    frequency: float = 1.6,
    ftir: float = 72.0,
) -> dict:
    """Meta Ads metrikalar zanjiri bo'yicha darhol tor joyni (bottleneck) va yechimni topadi."""
    bottlenecks: list[dict] = []
    healthy: list[str] = []

    if frequency > 2.8 or ftir < 55.0:
        bottlenecks.append({
            "stage": "AUDIENCE_SATURATION_AND_FATIGUE",
            "severity": "HIGH",
            "evidence": f"Frequency={frequency:.2f} (>2.8) yoki FTIR={ftir:.1f}% (<55%)",
            "fix": "Auditoriya to'yingan: yangi 3 xil Creative Angle qo'shing va auditoriyani Broad / yangi LAL qatlamiga kengaytiring.",
        })
    else:
        healthy.append(f"Auditoriya yangiligi sog'lom (Frequency={frequency:.2f}, FTIR={ftir:.1f}%)")

    if cpm > 6.5:
        bottlenecks.append({
            "stage": "AUCTION_CPM_INFLATION",
            "severity": "MEDIUM",
            "evidence": f"CPM=${cpm:.2f} (O'zbekiston me'yori $1.50–$5.00 dan yuqori)",
            "fix": "Juda tor qiziqish ustma-ustligi (narrowing) yoki Ad Set'lar o'rtasidagi Overlap >=20% ni tekshiring; Placement'da Reels+Feed'ni oching.",
        })
    else:
        healthy.append(f"Auktsion CPM me'yorda (${cpm:.2f})")

    if ctr < 1.0:
        bottlenecks.append({
            "stage": "HOOK_AND_CREATIVE_STOP_RATE",
            "severity": "CRITICAL",
            "evidence": f"Link CTR={ctr:.2f}% (<1.0%) va CPC=${cpc:.2f}",
            "fix": "Muammo auditoriyada emas — KREATIV HOOKDA! Birinchi 3 soniyada aniq og'riq, raqam yoki noodatiy vizual (Demo/50-50) bilan yangi 3 ta Hook yozing (`tools/creative-matrix.py`).",
        })
    else:
        healthy.append(f"Kreativ CTR yaxshi ({ctr:.2f}%)")

    if ctr >= 1.0 and lp_cvr < 8.0:
        bottlenecks.append({
            "stage": "LANDING_OR_TELEGRAM_BOT_FRICTION",
            "severity": "CRITICAL",
            "evidence": f"CTR={ctr:.2f}% yaxshi, lekin Sahifa/Bot konversiyasi (LP CVR)={lp_cvr:.1f}% (<8%)",
            "fix": "Reklama va'dasi (Offer) bilan Landing/Telegram Bot birinchi ekrani mos emas yoki sahifa >3 soniya yuklanyapti. Telegram Botda ortiqcha savollarni 2 taga tushiring.",
        })
    elif lp_cvr >= 8.0:
        healthy.append(f"Voronka (Landing/Bot) konversiyasi sog'lom ({lp_cvr:.1f}%)")

    if lp_cvr >= 8.0 and lead_to_sale < 5.0:
        bottlenecks.append({
            "stage": "LEAD_QUALITY_OR_SALES_SPEED",
            "severity": "HIGH",
            "evidence": f"Lid bor (LP CVR={lp_cvr:.1f}%), lekin Lid->Sotuv={lead_to_sale:.1f}% (<5%)",
            "fix": "1) Sotuv bo'limi lidga >15 daqiqada qo'ng'iroq qilyapti; 2) Kreativda narx/byudjet filtri (Solventnost) yo'qligi sababli pulsiz lidlar tushyapti — Instant Form/Botga 2 ta saralovchi savol qo'shing.",
        })
    elif lead_to_sale >= 5.0:
        healthy.append(f"Sotuv konversiyasi me'yorda ({lead_to_sale:.1f}%)")

    return {
        "overall_health": "CRITICAL_BOTTLENECK_FOUND" if any(b["severity"] == "CRITICAL" for b in bottlenecks)
                          else ("NEEDS_OPTIMIZATION" if bottlenecks else "HEALTHY_SCALABLE"),
        "bottlenecks": bottlenecks,
        "healthy_signals": healthy,
    }






def analyze_audience_competitors_and_offers(
    product: str,
    niche: str = "ecom",
    competitors: list[str] | None = None,
    price: float = 100.0,
    country: str = "UZ",
    language: str = "uz_latin",
    currency: str = "USD",
    problem_solved: str = "Vaqt va pul yo'qotish, natija kafolati yo'qligi",
    unique_mechanism: str = "Bosqichma-bosqich shaffof tizim va shartnomaviy kafolat",
    proof_point: str = "30 kunda 240+ tasdiqlangan mijoz natijasi",
) -> dict:
    """Deep Audience Psychographics (JTBD), Competitor Ad Teardown, and Segment-Matched Offer Engine (0 LLM tokens)."""
    clean_prod = (product or "Asosiy Mahsulot").strip()
    comp_list = [c.strip() for c in (competitors or []) if c.strip()] or [
        f"{niche.upper()} bozoridagi odatiy arzon/shablon o'yinchilar",
        f"{niche.upper()} sohasidagi qimmat, lekin kafolatsiz brendlar",
    ]
    c_code = (country or "UZ").strip().upper()
    q_encoded = urllib.parse.quote(clean_prod)
    mkt_info = mloc.detect_market(text=f"{clean_prod} {c_code}", explicit_market=c_code.lower() if c_code.lower() in ("uz", "us", "eu", "uk", "mena", "latam", "sea", "in") else None, currency=currency)
    bnpl_methods = ", ".join(mkt_info.get("payment_methods", [])[:3]) or "Bo'lib to'lash (0% muddatli to'lov)"
    fmt_price = mloc.format_currency(price, currency)
    monthly_bnpl = mloc.format_currency(round(price / 6.0, 2), currency)

    # 1. Deep Audience JTBD & 4 Buyer Personas
    audience_segments = [
        {
            "segment_id": "S1_SKEPTICAL_BURNED",
            "segment_name": "1-Segment: 'Oldin kuygan va shubhali' (Skeptical / Risk-Averse — ~35% bozor)",
            "jtbd_functional": f"{clean_prod} orqali {problem_solved} muammosini aldanmasdan hal qilish.",
            "jtbd_emotional": "Yana pul va vaqt yo'qotib, oila/jamoa oldida uyalib qolmaslik.",
            "hidden_objection": "Hamma chiroyli va'da beradi, lekin pulni olgach xizmat sifati tushib ketadi.",
            "schwartz_awareness": "Solution Aware / Jaded (Vadalardan charchagan — faqat ISBOT va KAFOLAT ishlaydi)",
            "andromeda_creative_signal": "Video 0-3s da mijozning real shartnomasi, jonli natija skrinshoti yoki jarayon ichidan isbot (Greenscreen / Case Study).",
            "matched_offer_type": "RISK_REVERSAL_GUARANTEE_OFFER",
            "tailored_offer": {
                "offer_headline": f"{clean_prod}: Natija shartnomada yoziladi yoki bosqichma-bosqich kafolatlanadi",
                "core_hook": f"Oldin {clean_prod} dan ko'nglingiz qolganmi? Shu sababli biz quruq va'da emas, {unique_mechanism} va {proof_point} asosida ishlaymiz.",
                "risk_reversal": "Birinchi bosqichda kelishilgan KPI/standart bajarilmasa, keyingi bosqich to'lovi olinmaydi yoki bepul qayta ishlanadi.",
                "cta": "Shartnoma shartlari va real mijozlar natijasini ko'rish",
            },
        },
        {
            "segment_id": "S2_URGENT_FAST_RESULT",
            "segment_name": "2-Segment: 'Vaqt tig'iz — tez va tayyor yechim kerak' (Speed & Convenience — ~25% bozor)",
            "jtbd_functional": f"Ortiqcha bosh og'riqsiz va uzoq kutmasdan {clean_prod} natijasini olish.",
            "jtbd_emotional": "Vaqtni tejash va jarayonni mutaxassislarga to'liq topshirish (Done-For-You).",
            "hidden_objection": "Bunga mening vaqtim yo'q, jarayon juda uzoq va murakkab bo'lsa kerak.",
            "schwartz_awareness": "Product Aware (Tezlik va qulaylik qidiryapti)",
            "andromeda_creative_signal": "Video 0-3s da 'Qanday qilib X vaqtda ortiqcha ovoragarchiliksiz...' + tayyor 'kalitgacha' (turnkey) jarayon.",
            "matched_offer_type": "FAST_TRACK_DFY_OFFER",
            "tailored_offer": {
                "offer_headline": f"Tayyor '{clean_prod}' paketi — 24 soat ichida ishga tushiramiz",
                "core_hook": f"{problem_solved} bilan o'zingiz kurashib vaqt yo'qotmang: {unique_mechanism} orqali barcha texnik ishni o'zimiz bajaramiz.",
                "speed_bonus": "Bugun murojaat qilganlarga 15 daqiqalik tezkor audit / ekspress-diagnostika bepul.",
                "cta": "Tayyor paket va muddatni 2 daqiqada hisoblatish",
            },
        },
        {
            "segment_id": "S3_CASHFLOW_BNPL_SMART",
            "segment_name": "3-Segment: 'Ehtiyoji kuchli, lekin birvarakayiga katta to'lovga ikkilanadi' (Smart Cash-Flow / BNPL — ~25% bozor)",
            "jtbd_functional": f"Byudjetni qiynamasdan hoziroq {clean_prod} dan foydalanishni boshlash.",
            "jtbd_emotional": "Sifatdan voz kechmasdan oylik kichik to'lov bilan maqsadga erishish.",
            "hidden_objection": f"{fmt_price} ni bitta to'lovda chiqarish hozirgi byudjetimga og'irlik qiladi.",
            "schwartz_awareness": "Most Aware (Mahsulotni xohlaydi, faqat to'lov sharti to'xtatib turibdi)",
            "andromeda_creative_signal": f"Video va bannerda yirik {fmt_price} o'rniga 'Oyiga atigi {monthly_bnpl} dan ({bnpl_methods})' langari.",
            "matched_offer_type": "PAYMENT_STRUCTURED_OR_DIAGNOSTIC_ENTRY_OFFER",
            "tailored_offer": {
                "offer_headline": f"{clean_prod} — boshlang'ich to'lovsiz oyiga {monthly_bnpl} dan ({bnpl_methods})",
                "core_hook": f"To'liq summani hozir to'lash shart emas: {clean_prod} ni bugun boshlang va {bnpl_methods} orqali qulay bo'lib to'lang.",
                "entry_step": "Bepul dastlabki hisob-kitob va individual to'lov grafigi.",
                "cta": "Oylik to'lov jadvalini Telegramda olish",
            },
        },
        {
            "segment_id": "S4_VIP_PRESTIGE_QUALITY",
            "segment_name": "4-Segment: 'Premium sifat, status va maksimal e'tibor' (VIP / High-LTV — ~15% bozor, lekin 50%+ foyda)",
            "jtbd_functional": f"Bozordagi eng ishonchli, individual yondashuvli {clean_prod} yechimini olish.",
            "jtbd_emotional": "Status, xotirjamlik va eng kuchli mutaxassis bilan bevosita ishlash.",
            "hidden_objection": "Arzon ommaviy xizmatlarda sifat va shaxsiy nazorat bo'lmaydi.",
            "schwartz_awareness": "Problem/Solution Aware (Eng yuqori sifat va ekspertlikni tanlaydi)",
            "andromeda_creative_signal": "Founder / Bosh ekspert yuzi bilan chuqur tahliliy video, yuqori estetika, CHEGIRMA SO'ZI YO'Q (chegirma VIP mijozni cho'chitadi).",
            "matched_offer_type": "VIP_CONCIERGE_VALUE_STACK_OFFER",
            "tailored_offer": {
                "offer_headline": f"{clean_prod} VIP Individual Dasturi (Oyiga faqat cheklangan mijozlar uchun)",
                "core_hook": f"Standart shablonlar sizning darajangizga to'g'ri kelmaydi: bosh ekspert nazorati ostidagi {clean_prod} tizimi.",
                "vip_bonus_stack": "Shaxsiy menejer + ustuvor xizmat + yopiq audit va 90 kunlik kuzatuv.",
                "cta": "VIP konsultatsiya uchun bo'sh vaqtni band qilish",
            },
        },
    ]

    # 2. Competitor Teardown & Counter-Positioning Matrix
    competitor_teardown = {
        "official_ad_spy_links": {
            "meta_ad_library_url": f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={c_code}&q={q_encoded}",
            "google_ads_transparency_url": f"https://adstransparency.google.com/?region={c_code}&query={q_encoded}",
            "tiktok_creative_center_url": "https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en",
        },
        "analyzed_competitors": comp_list,
        "competitor_weaknesses_to_exploit": [
            {
                "weakness": "1. Bir xil quruq va'da ('Yuqori sifat va hamyonbop narx')",
                "why_they_lose": "Bozorda hamma shu gapni aytgani uchun mijozda 'banner blindness' paydo bo'lgan — hech kim ularga ishonmaydi.",
                "our_counter_wedge": f"Va'da emas, MEZANIZM va ISBOT ko'rsating: '{unique_mechanism}' + '{proof_point}' (`Proof > Promise` qoidasi).",
            },
            {
                "weakness": "2. Faqat 'Chegirma -30%' bilan sotishga urinish",
                "why_they_lose": "Chegirma faqat arzonchi/bepulchi auditoriyani tortadi va brend qadrini tushiradi.",
                "our_counter_wedge": "Chegirma o'rniga BONUS STACK (asosiy mahsulot qadrini oshiruvchi 3 ta qo'shimcha qiymat) va shartli KAFOLAT bering.",
            },
            {
                "weakness": "3. Lid tushgach sekin va skriptsiz sotuv (>30 daqiqa kutish)",
                "why_they_lose": "Mijoz raqam qoldirgach 15 daqiqa ichida sovib ketadi yoki boshqa raqobatchidan oladi.",
                "our_counter_wedge": "Lid tushgan soniyada Telegram/WhatsApp orqali 45s video-keyslar yuborish va <5 daqiqada diagnostik qo'ng'iroq qilish.",
            },
            {
                "weakness": "4. Barcha auditoriyaga bitta umumiy reklama aylantirish",
                "why_they_lose": "Meta Andromeda algoritmi bitta umumiy reklamani faqat eng arzon segmentga ko'rsatadi.",
                "our_counter_wedge": "Yuqoridagi 4 ta segment (Skeptik, Shoshilinch, BNPL/Bo'lib to'lov, VIP) uchun 4 xil alohida Hook va Offer ishlatish.",
            },
        ],
        "competitor_ad_longevity_rule": (
            "Meta Ad Library'da raqobatchining qaysi reklamasi 30+ kundan beri o'chirilmasdan aylanayotgan bo'lsa — "
            "o'sha kreativ ularga pul keltiryapti. Uning so'zlarini ko'chirmang: uning Hook strukturasi va Offer kuchini tahlil qilib, undan kuchliroq Proof bering."
        ),
    }

    # 3. Hormozi Value Equation Master Offer Construction
    master_grand_slam_offer = {
        "framework": "Alex Hormozi Value Equation: (Dream Outcome x Perceived Likelihood) / (Time Delay x Effort & Sacrifice)",
        "1_core_promise": f"{clean_prod} orqali {problem_solved} muammosini {unique_mechanism} yordamida hal qilish.",
        "2_proof_and_likelihood_booster": f"Quruq gap emas: {proof_point} (jonli keyslar, shartnoma va shaffof jarayon).",
        "3_speed_first_win_lever": "Murojaat qilgan kuniyoq (24 soat ichida) dastlabki diagnostika / 1-bosqich natijasini ko'rsatish (Time Delay -> minimal).",
        "4_effort_reduction_lever": "Mijozdan minimal harakat talab qilinadigan 'Tayyor Tizim' (Done-For-You / shaxsiy kuzatuv).",
        "5_bonus_stack": [
            f"Bonus #1 (Boshlang'ich to'siqni yechish): Bepul dastlabki audit / shaxsiy reja ({mloc.format_currency(round(price * 0.25, 2), currency)} qiymatida — bugun murojaat qilganlarga 0).",
            f"Bonus #2 (Tezlikni oshirish): Tayyor shablonlar / tekshiruv ro'yxati / ekspress yo'riqnoma.",
            f"Bonus #3 (Xavfsizlik): 30 kunlik qo'llab-quvvatlash va sifat nazorati.",
        ],
        "6_risk_reversal_guarantee": "Shartli Natija Kafolati: Kelishilgan standart va muddat bajarilmasa, kamchilik o'z hisobimizdan bepul bartaraf etiladi.",
        "7_honest_scarcity": "Sifatni saqlash uchun har haftada jamoa sig'imiga qarab cheklangan miqdordagi mijozlar qabul qilinadi (soxta taymerlarsiz).",
        "8_price_and_payment_anchor": f"To'liq qiymat: {fmt_price} | Qulay kirish varianti: oyiga {monthly_bnpl} dan ({bnpl_methods}).",
    }

    return {
        "schema": "tyrion.market_intel_and_offers/v7.2",
        "zero_llm_tokens_execution": True,
        "product": clean_prod,
        "niche": niche,
        "country": c_code,
        "currency": currency.upper(),
        "1_audience_jtbd_and_4_segments": audience_segments,
        "2_competitor_teardown_and_gaps": competitor_teardown,
        "3_master_grand_slam_offer": master_grand_slam_offer,
    }


def build_launch_blueprint(
    product: str,
    niche: str = "ecom",
    daily_budget: float = 50.0,
    aov: float = 100.0,
    margin_pct: float = 40.0,
    lead_to_sale_cvr: float = 15.0,
    country: str = "UZ",
    language: str = "uz",
    currency: str = "USD",
    problem_solved: str = "Reklama byudjeti kuyishi va sifatsiz lidlar",
    proof_point: str = "30 kunda 3.2x ROAS va 240+ tasdiqlangan sotuv",
    video_format: str = "pas",
    ad_account_id: str = "",
) -> dict:
    """Turnkey 10-Point Result-Maximizer Launch Blueprint (0 LLM tokens).

    Combines Unit Economics, 2026 Meta 5-System Targeting, Andromeda P x D x A Creative Plan,
    30s 9:16 Video Script, AI-Tell-Free Ad Copy, Anti-Junk-Lead Conversion Gate, and 7-Day Kill/Scale Protocol.
    """
    clean_prod = (product or "Premium Offer").strip()
    arch = build_architecture(
        niche=niche,
        daily_budget=daily_budget,
        geo=country,
        currency=currency,
        aov=aov,
        margin_pct=margin_pct,
        lead_to_sale_cvr=lead_to_sale_cvr,
        has_pixel=True,
        has_crm=True,
    )
    mte = importlib.import_module("meta-targeting-engine")
    targeting_rep = mte.search_and_validate_targeting(
        product=clean_prod,
        niche=niche,
        problem_solved=problem_solved,
        purchase_intent=f"{clean_prod} buyurtma va narx",
        objective="SALES" if niche == "ecom" else "LEADS",
        country=country,
        language=language,
        ad_account_id=ad_account_id,
        max_queries=8,
    )
    cm = importlib.import_module("creative-matrix")
    pda_plan = cm.build_pda_diversity_plan(niche=niche, product=clean_prod, price=aov, currency=currency)
    lang_code = "uz_latin" if language in ("uz", "uz_latin", "uz-Latn") else language
    video_script = cm.generate_video_script(
        niche=niche,
        product=clean_prod,
        problem=problem_solved,
        format_name=video_format,
        duration_sec=30,
        price=aov,
        market=country.lower(),
        currency=currency,
        language=lang_code,
    )
    ad_copy = cm.generate_ad_copy_pack(
        product=clean_prod,
        problem=problem_solved,
        proof=proof_point,
        platform="meta",
        language=lang_code,
        price=aov,
        currency=currency,
    )
    target_cpa = arch.get("unit_economics", {}).get("derived_target_cpa") or round(aov * (margin_pct / 100.0) * 0.5, 2)
    kill_cpa = round(float(target_cpa) * 1.5, 2)

    lead_quality_gate = {
        "why_junk_leads_happen": (
            "Meta Instant Form default 'More Volume' rejimida avto-to'ldirilgan raqamlarni yuboradi va "
            "algoritm (GEM + Andromeda) xaridorni emas, shunchaki arzon forma to'ldiruvchilarni qidiradi."
        ),
        "mandatory_fixes_for_real_sales": [
            "1. FORM FRICTION GATE: Instant Form turini 'Higher Intent' (Review screen bilan) ga o'tkazing va 2 ta saralovchi savol (byudjet / muddat) qo'shing.",
            "2. CAPI DOWN-FUNNEL SIGNAL: Xom 'Lead' emas, CRM yoki Telegram botda tasdiqlangan 'QualifiedLead' va 'Purchase' hodisasini Meta CAPI v26.0 orqali (EMQ >= 8.0) qaytarib yuboring.",
            "3. CREATIVE PRICE/SOLVENTNOST ANCHOR: Video va matnning birinchi 5 soniyasida narx diapazoni yoki minimal paket shartini ochiq ayting — bepulchilar o'zi bosmaydi (UTIS filtr).",
            "4. 5-MINUTE SPEED-TO-LEAD SLA: Lid tushgach < 5 daqiqada qo'ng'iroq qiling va qo'ng'iroqqacha Telegram/WhatsApp orqali 45 soniyalik isbot videosini avto-yuboring (ko'tarish foizi 35% dan 75%+ ga oshadi).",
        ],
    }

    seven_day_protocol = [
        {
            "days": "1–2 kun (Learning Phase — Tegilmasin)",
            "rule": "48 soat ichida byudjet, auditoriya yoki kreativni o'zgartirmang. Lattice va Andromeda dastlabki 1,500–3,000 ko'rishda xaridorga mos klasterlarni qidiradi.",
        },
        {
            "days": "3-kun (Hook va CTR Darvozasi)",
            "rule": "3-soniyalik Hook Rate >= 25%, 15-soniyalik Hold Rate >= 12% va Link CTR >= 1.0% ekanini tekshiring. Agar Hook < 25% bo'lsa, videoning faqat 0–3s boshini almashtiring.",
        },
        {
            "days": "5-kun (Stop-Loss / Kill Darvozasi)",
            "rule": f"Agar biror Ad Set yoki reklama ${kill_cpa} (1.5x Target CPA) sarflab 0 ta sifatli konversiya bersa, darhol o'chiring va byudjetni g'olib Entity ID kontseptsiyasiga o'tkazing.",
        },
        {
            "days": "7-kun (Spend-Guard Scaling + More/Better/New)",
            "rule": f"CPA <= ${target_cpa} bo'lgan g'olib Ad Set byudjetini har 48–72 soatda maksimal +20% ga oshiring (Spend-Guard qoidasi) va g'olib hook atrofida 3 ta yangi 'More/Better/New' variatsiya chiqaring.",
        },
    ]

    return {
        "schema": "tyrion.launch_blueprint/v7.1",
        "zero_llm_tokens_execution": True,
        "product": clean_prod,
        "niche": niche,
        "country": country.upper(),
        "currency": currency.upper(),
        "daily_budget": daily_budget,
        "1_unit_economics_and_guardrails": {
            "aov": aov,
            "margin_pct": margin_pct,
            "lead_to_sale_cvr_pct": lead_to_sale_cvr,
            "target_cpa": target_cpa,
            "stop_loss_kill_cpa": kill_cpa,
            "max_safe_budget_step_pct": 20.0,
        },
        "2_audience_architecture_and_meta_2026_stack": {
            "recommended_structure": arch.get("recommended_structure"),
            "audience_layers": arch.get("audience_layers"),
            "mandatory_exclusions": arch.get("mandatory_exclusions"),
            "meta_2026_ai_stack": arch.get("meta_2026_ai_stack_and_value_rules"),
        },
        "3_detailed_targeting_and_ads_manager_setup": {
            "verification_mode": targeting_rep.get("targetologist_report", {}).get("1_overview", {}).get("verification_mode"),
            "recommended_packs": targeting_rep.get("targetologist_report", {}).get("7_recommended_targeting_packs"),
            "practitioner_ads_manager_playbook": targeting_rep.get("targetologist_report", {}).get("9_practitioner_ads_manager_playbook"),
        },
        "4_andromeda_pda_creative_diversity": pda_plan,
        "5_ready_to_shoot_video_script_9x16": video_script,
        "6_platform_native_ad_copy": ad_copy,
        "7_lead_quality_and_sales_conversion_gate": lead_quality_gate,
        "8_seven_day_kill_scale_protocol": seven_day_protocol,
        "9_audience_competitor_and_offer_matrix": analyze_audience_competitors_and_offers(
            product=clean_prod,
            niche=niche,
            price=aov,
            country=country,
            language=lang_code,
            currency=currency,
            problem_solved=problem_solved,
            proof_point=proof_point,
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="meta-audience.py",
        description="Tyrion v5.0 Meta Ads Audience & Detailed Targeting Accuracy Engine",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_arch = sub.add_parser("architect", help="4-qatlamli Meta Ads auditoriya arxitekturasi va Exclusion matritsasi")
    p_arch.add_argument("--niche", choices=list(NICHE_TAXONOMY.keys()), default="ecom")
    p_arch.add_argument("--daily-budget", type=float, required=True)
    p_arch.add_argument("--geo", default="global", help="Any ISO 3166 country/region/city (e.g. DE, US, GB, UZ, Berlin, Tashkent)")
    p_arch.add_argument("--currency", default="USD", help="ISO 4217 currency code (USD, EUR, GBP, JPY, UZS, etc.)")
    p_arch.add_argument("--market", default="", help="Market pack override")
    p_arch.add_argument("--target-cpa", type=float, default=None, help="Foydalanuvchi maqsad qilgan CPA (goal)")
    p_arch.add_argument("--measured-cpa", type=float, default=None, help="Akkauntda haqiqatda o'lchangan tarixiy CPA")
    p_arch.add_argument("--aov", type=float, default=None, help="O'rtacha chek (>0) — unit-ekonomikadan CPA chiqarish uchun")
    p_arch.add_argument("--margin-pct", type=float, default=None, help="Yalpi marja foizi (0 < margin <= 100)")
    p_arch.add_argument("--lead-to-sale-cvr", type=float, default=None, help="Liddan sotuvga o'tish konversiyasi (0 < cvr <= 100)")
    p_arch.add_argument("--has-pixel", action="store_true")
    p_arch.add_argument("--has-crm", action="store_true")
    p_arch.add_argument("--ig-followers", type=int, default=5000)
    p_arch.add_argument("--json", action="store_true")

    p_int = sub.add_parser("interests", help="Nisha bo'yicha qidiruv urug'lari (`RELATED_UNVERIFIED`) va live Graph API tekshiruvi")
    p_int.add_argument("--niche", choices=list(NICHE_TAXONOMY.keys()), default="ecom")
    p_int.add_argument("--query", default="")
    p_int.add_argument("--product", default="", help="Mahsulot yoki xizmat tavsifi")
    p_int.add_argument("--customer-profile", default="", help="Maqsadli mijoz profili")
    p_int.add_argument("--account-id", default="", help="Meta Ad Account ID (`act_...`) — targetingsearch va targetingvalidation uchun")
    p_int.add_argument("--special-ad-category", default="NONE")
    p_int.add_argument("--live", action="store_true", help="META_ACCESS_TOKEN orqali jonli Graph API v26.0 qidiruvi va tekshiruvi")
    p_int.add_argument("--json", action="store_true")

    p_dt = sub.add_parser("detailed-targeting", help="6-statusli Detailed Targeting Accuracy Engine hisoboti")
    p_dt.add_argument("--product", default="")
    p_dt.add_argument("--niche", choices=list(NICHE_TAXONOMY.keys()), default="ecom")
    p_dt.add_argument("--customer-profile", default="")
    p_dt.add_argument("--problem", "--problem-solved", dest="problem_solved", default="")
    p_dt.add_argument("--needs", "--customer-needs", dest="customer_needs", default="")
    p_dt.add_argument("--intent", "--purchase-intent", dest="purchase_intent", default="")
    p_dt.add_argument("--complementary", "--complementary-products", dest="complementary_products", default="")
    p_dt.add_argument("--objective", default="SALES", choices=["SALES", "LEADS", "ENGAGEMENT", "TRAFFIC", "AWARENESS"])
    p_dt.add_argument("--country", default="UZ")
    p_dt.add_argument("--language", default="auto", help="Any BCP 47 language code (en, de, fr, es, ar, uz-Latn, ru, auto)")
    p_dt.add_argument("--query", action="append", default=[])
    p_dt.add_argument("--max-queries", type=int, default=12)
    p_dt.add_argument("--min-relevance", type=float, default=35.0)
    p_dt.add_argument("--locale", default="en_US")
    p_dt.add_argument("--account-id", "--ad-account-id", dest="account_id", default="")
    p_dt.add_argument("--special-ad-category", default="NONE")
    p_dt.add_argument("--suggestions", action="store_true")
    p_dt.add_argument("--no-validate", action="store_true")
    p_dt.add_argument("--json", action="store_true")

    p_ovl = sub.add_parser("overlap", help="Ikki ad set o'rtasidagi Static Pool Overlap (<20% qoidasi) ni hisoblash")
    p_ovl.add_argument("--size-a", type=int, required=True)
    p_ovl.add_argument("--size-b", type=int, required=True)
    p_ovl.add_argument("--shared", type=int, required=True)
    p_ovl.add_argument("--json", action="store_true")

    p_sat = sub.add_parser("saturation", help="Auditoriya sig'imi, Frequency va ssenariy sezgirlik oralig'ini hisoblash")
    p_sat.add_argument("--audience-size", type=int, required=True)
    p_sat.add_argument("--daily-budget", type=float, required=True)
    p_sat.add_argument("--cpm", type=float, default=3.2)
    p_sat.add_argument("--days", type=int, default=14)
    p_sat.add_argument("--active-reach-ratio", type=float, default=0.60, help="Auditoriyaning faol yetib boriladigan ulushi (0.05..1.0)")
    p_sat.add_argument("--measured-freq-7d", type=float, default=None, help="Haqiqiy akkauntdan olingan 7 kunlik Frequency")
    p_sat.add_argument("--json", action="store_true")

    p_ret = sub.add_parser("retargeting", help="Dinamik Retargeting oynalari (3d/7d/14d/30d/180d) va byudjet hisobi")
    p_ret.add_argument("--aov", type=float, default=100.0)
    p_ret.add_argument("--daily-visitors", type=int, default=300)
    p_ret.add_argument("--ig-engagers", type=int, default=5000)
    p_ret.add_argument("--video-viewers", type=int, default=8000)
    p_ret.add_argument(
        "--has-telegram-bot",
        dest="has_telegram_bot",
        nargs="?",
        const=True,
        default=True,
        type=_parse_bool_arg,
        help="Telegram bot voronkasi mavjudligi (true/false, yoki --no-telegram-bot)",
    )
    p_ret.add_argument(
        "--no-telegram-bot",
        "--no-has-telegram-bot",
        dest="has_telegram_bot",
        action="store_false",
        help="Telegram bot voronkasini o'chirish (has_telegram_bot=False)",
    )
    p_ret.add_argument("--json", action="store_true")

    p_lal = sub.add_parser("lookalike", help="Lookalike (LAL) seed tayyorlik indeksi va 1%-5% pog'onali hajm hisoblagichi")
    p_lal.add_argument("--seed-size", type=int, required=True)
    p_lal.add_argument("--seed-type", default="purchase_ltv",
                       choices=["purchase_ltv", "purchase_all", "qualified_leads", "raw_leads", "ig_engagers"])
    p_lal.add_argument("--country", default="UZ")
    p_lal.add_argument("--json", action="store_true")

    p_diag = sub.add_parser("diagnose", help="Meta Ads metrikalar zanjiridan (CPM->CTR->CVR->Sale) tor joyni topish")
    p_diag.add_argument("--cpm", type=float, required=True)
    p_diag.add_argument("--ctr", type=float, required=True)
    p_diag.add_argument("--cpc", type=float, default=0.35)
    p_diag.add_argument("--lp-cvr", type=float, required=True)
    p_diag.add_argument("--lead-to-sale", type=float, default=10.0)
    p_diag.add_argument("--frequency", type=float, default=1.6)
    p_diag.add_argument("--ftir", type=float, default=72.0)
    p_diag.add_argument("--json", action="store_true")

    p_bp = sub.add_parser("launch-blueprint", help="10-bandlik tayyor Result-Maximizer Launch Blueprint (Targeting + Video Script + Ad Copy + Lead Quality Gate + 7-Day Protocol)")
    p_bp.add_argument("--product", required=True, help="Mahsulot yoki xizmat nomi")
    p_bp.add_argument("--niche", choices=list(NICHE_TAXONOMY.keys()), default="ecom")
    p_bp.add_argument("--daily-budget", type=float, default=50.0)
    p_bp.add_argument("--aov", type=float, default=100.0)
    p_bp.add_argument("--margin-pct", type=float, default=40.0)
    p_bp.add_argument("--lead-to-sale-cvr", type=float, default=15.0)
    p_bp.add_argument("--country", default="UZ")
    p_bp.add_argument("--language", default="uz")
    p_bp.add_argument("--currency", default="USD")
    p_bp.add_argument("--problem", default="Reklama byudjeti kuyishi va sifatsiz lidlar")
    p_bp.add_argument("--proof", default="30 kunda 3.2x ROAS va 240+ tasdiqlangan sotuv")
    p_bp.add_argument("--format", default="pas", choices=["ugc_testimonial", "founder_story", "pas", "greenscreen", "split_screen", "street_interview", "faceless_broll"])
    p_bp.add_argument("--account-id", default="")
    p_bp.add_argument("--json", action="store_true")

    p_mi = sub.add_parser("market-intel", help="Chuqur Auditoriya (4 JTBD segment), Raqobatchilar tahlili (Ad Library + Counter-Wedge) va Segmentga mos Offer generatori")
    p_mi.add_argument("--product", required=True, help="Mahsulot yoki xizmat nomi")
    p_mi.add_argument("--niche", choices=list(NICHE_TAXONOMY.keys()), default="ecom")
    p_mi.add_argument("--competitor", action="append", default=[], help="Raqobatchi nomi (bir nechta berish mumkin)")
    p_mi.add_argument("--price", type=float, default=100.0, help="Mahsulot narxi / o'rtacha chek")
    p_mi.add_argument("--country", default="UZ")
    p_mi.add_argument("--language", default="uz_latin")
    p_mi.add_argument("--currency", default="USD")
    p_mi.add_argument("--problem", default="Vaqt va pul yo'qotish, natija kafolati yo'qligi")
    p_mi.add_argument("--mechanism", default="Bosqichma-bosqich shaffof tizim va shartnomaviy kafolat")
    p_mi.add_argument("--proof", default="30 kunda 240+ tasdiqlangan mijoz natijasi")
    p_mi.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    try:
        if args.command == "architect":
            res = build_architecture(
                niche=args.niche,
                daily_budget=args.daily_budget,
                geo=args.geo,
                has_pixel=args.has_pixel,
                has_crm=args.has_crm,
                ig_followers=args.ig_followers,
                target_cpa=args.target_cpa,
                measured_cpa=args.measured_cpa,
                aov=args.aov,
                margin_pct=args.margin_pct,
                lead_to_sale_cvr=args.lead_to_sale_cvr,
            )
        elif args.command == "interests":
            res = get_interests(
                niche=args.niche,
                query=args.query,
                live=args.live,
                product=args.product,
                customer_profile=args.customer_profile,
                ad_account_id=args.account_id,
                special_ad_category=args.special_ad_category,
            )
        elif args.command == "detailed-targeting":
            mte = importlib.import_module("meta-targeting-engine")
            res = mte.search_and_validate_targeting(
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
                max_queries=args.max_queries,
                min_relevance_score=args.min_relevance,
                locale=args.locale,
            )
        elif args.command == "overlap":
            res = calc_overlap(args.size_a, args.size_b, args.shared)
        elif args.command == "saturation":
            res = calc_saturation(
                args.audience_size,
                args.daily_budget,
                args.cpm,
                args.days,
                active_reach_ratio=args.active_reach_ratio,
                measured_freq_7d=args.measured_freq_7d,
            )
        elif args.command == "retargeting":
            res = calc_retargeting(args.aov, args.daily_visitors, args.ig_engagers, args.video_viewers, args.has_telegram_bot)
        elif args.command == "lookalike":
            res = calc_lookalike(args.seed_size, args.seed_type, args.country)
        elif args.command == "diagnose":
            res = diagnose_metrics(args.cpm, args.ctr, args.cpc, args.lp_cvr, args.lead_to_sale, args.frequency, args.ftir)
        elif args.command == "launch-blueprint":
            res = build_launch_blueprint(
                product=args.product,
                niche=args.niche,
                daily_budget=args.daily_budget,
                aov=args.aov,
                margin_pct=args.margin_pct,
                lead_to_sale_cvr=args.lead_to_sale_cvr,
                country=args.country,
                language=args.language,
                currency=args.currency,
                problem_solved=args.problem,
                proof_point=args.proof,
                video_format=args.format,
                ad_account_id=args.account_id,
            )
        elif args.command == "market-intel":
            res = analyze_audience_competitors_and_offers(
                product=args.product,
                niche=args.niche,
                competitors=args.competitor,
                price=args.price,
                country=args.country,
                language=args.language,
                currency=args.currency,
                problem_solved=args.problem,
                unique_mechanism=args.mechanism,
                proof_point=args.proof,
            )
        else:
            return 2
    except Exception as exc:
        print(f"Xato: {exc}", file=sys.stderr)
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 66)
    print(f"  🎯 TYRION v5.0 META AUDIENCE ENGINE — {args.command.upper()}")
    print("=" * 66)
    for k, v in res.items():
        if isinstance(v, list):
            print(f"\n  [{k}]:")
            for item in v:
                if isinstance(item, dict):
                    title = item.get("layer") or item.get("stage") or item.get("name") or item.get("window") or item.get("tier") or ""
                    print(f"    • {title}")
                    for sk, sv in item.items():
                        if sk not in ("layer", "stage", "name", "window", "tier"):
                            print(f"        {sk}: {sv}")
                else:
                    print(f"    • {item}")
        elif isinstance(v, dict):
            print(f"\n  [{k}]:")
            for sk, sv in v.items():
                print(f"    • {sk}: {sv}")
        else:
            print(f"  {k:36}: {v}")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
