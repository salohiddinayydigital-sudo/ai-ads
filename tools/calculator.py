#!/usr/bin/env python3
"""Tyrion Media Math Calculator — Pullik media va byudjet matematikasi.

Meta Ads, Google Ads va Telegram Ads uchun aniq, deterministik hisob-kitoblar:
  1. breakeven       : Sof marja, Break-even CPA va Break-even ROAS
  2. meta-155        : 1-5-5 Andromeda testing taqsimoti va Learning phase hisobi
  3. google-sculpt   : Qidiruv va PMax taqsimoti, Max CPC va Negatives tejamkori
  4. telegram-funnel : CPM -> Ko'rishlar -> Bot start -> Lids -> ROAS voronkasi
  5. ladder          : 3 bosqichli sinov pillapoyasi (Sandbox -> Validation -> Scale)
  6. funnel-economics: strategiya iqtisodi (break-even/target CPA-CPL-ROAS, test byudjeti, stsenariylar, scale cheklovi)

Chiqish kodlari: 0 = muvaffaqiyat · 2 = validatsiya xatosi (nan/inf, manfiy/nol) yoki natijada `error` maydoni.

Buyruqlar:
  python3 tools\\calculator.py breakeven --price 350000 --cogs 120000 --shipping 25000
  python3 tools\\calculator.py meta-155 --daily-budget 150 --target-cpa 15
  python3 tools\\calculator.py google-sculpt --monthly-budget 3000 --target-cpa 25 --avg-cpc 1.8
  python3 tools\\calculator.py telegram-funnel --budget 500 --cpm 3.5 --ctr 1.2 --aov 45
  python3 tools\\calculator.py ladder --total-budget 2000 --breakeven-cpa 20
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
import market_locale as mloc
import tyrion_core as tcore

# Windows UTF-8
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def calc_breakeven(
    price: float,
    cogs: float,
    shipping: float = 0.0,
    processing_fee_pct: float = 2.0,
    target_profit_pct: float = 0.0,
    currency: str = "USD",
) -> dict:
    """Break-even CPA, ROAS va sof marjani hisoblaydi."""
    price = tcore.require_number(price, "price", positive=True)
    cogs = tcore.require_number(cogs, "cogs", non_negative=True)
    shipping = tcore.require_number(shipping, "shipping", non_negative=True)
    processing_fee_pct = tcore.require_number(processing_fee_pct, "processing_fee_pct", min_val=0.0, max_val=100.0)
    target_profit_pct = tcore.require_number(target_profit_pct, "target_profit_pct", min_val=0.0, max_val=100.0)

    processing_fee = price * (processing_fee_pct / 100.0)
    total_direct_costs = cogs + shipping + processing_fee
    gross_profit = price - total_direct_costs
    margin_ratio = gross_profit / price

    if gross_profit <= 0:
        return {
            "error": "Zarardasiz! Mahsulot tannarxi va xarajatlari sotuv narxidan yuqori.",
            "gross_profit": gross_profit,
            "margin_ratio": margin_ratio,
        }

    breakeven_cpa = gross_profit
    breakeven_roas = 1.0 / margin_ratio if margin_ratio > 0 else 0.0

    target_profit_amount = price * (target_profit_pct / 100.0)
    target_cpa = max(0.0, gross_profit - target_profit_amount)
    target_roas = (price / target_cpa) if target_cpa > 0 else 0.0

    return {
        "currency": currency.upper(),
        "formatted_price": mloc.format_currency(price, currency),
        "formatted_breakeven_cpa": mloc.format_currency(breakeven_cpa, currency),
        "price": mloc.round_currency(price, currency),
        "cogs": mloc.round_currency(cogs, currency),
        "shipping": round(shipping, 2),
        "processing_fee": round(processing_fee, 2),
        "gross_profit_per_unit": round(gross_profit, 2),
        "margin_percent": round(margin_ratio * 100.0, 1),
        "breakeven_cpa": round(breakeven_cpa, 2),
        "breakeven_roas": round(breakeven_roas, 2),
        "target_profit_percent": target_profit_pct,
        "target_cpa": round(target_cpa, 2),
        "target_roas": round(target_roas, 2),
    }


def calc_funnel_economics(
    price: float,
    cogs: float,
    shipping: float = 0.0,
    processing_fee_pct: float = 2.0,
    target_profit_pct: float = 0.0,
    lead_to_sale_cvr_pct: float | None = None,
    repeat_orders: float = 1.0,
    daily_budget: float | None = None,
    assumed_cpl: float | None = None,
    cpl_low: float | None = None,
    cpl_high: float | None = None,
    decision_conversions: int = 30,
    currency: str = "USD",
) -> dict:
    """Strategiya uchun yagona iqtisod: break-even/target CPA, CPL, ROAS, test byudjeti, stsenariylar, scale cheklovlari.

    Hech qanday universal CPA/CPL maqsadi yo'q: hammasi mijozning narx/marja/konversiyasidan chiqadi. Hajm prognozi FAQAT
    foydalanuvchi `assumed_cpl` (yoki low/high) bersa hisoblanadi va `ASSUMPTION` deb belgilanadi.
    """
    price = tcore.require_number(price, "price", positive=True)
    base = calc_breakeven(price, cogs, shipping, processing_fee_pct, target_profit_pct, currency)
    if "error" in base:
        return base
    repeat_orders = tcore.require_number(repeat_orders, "repeat_orders", min_val=1.0, max_val=1000.0)
    decision_conversions = int(tcore.require_number(decision_conversions, "decision_conversions", min_val=1.0, max_val=100000.0))
    gp = base["gross_profit_per_unit"]
    cvr = None
    if lead_to_sale_cvr_pct is not None:
        cvr = tcore.require_number(lead_to_sale_cvr_pct, "lead_to_sale_cvr_pct", min_val=0.01, max_val=100.0) / 100.0

    res: dict = {
        "currency": base["currency"],
        "evidence_labels": {
            "unit_economics": "USER_PROVIDED inputs -> deterministic math",
            "volume_scenarios": "ASSUMPTION (faqat assumed_cpl berilganda)",
            "decision_conversions": "HEURISTIC_PRIOR_MODEL (sinov qarori uchun minimal konversiya soni; akkaunt tarixi bilan almashtiring)",
        },
        "gross_profit_per_sale": gp,
        "margin_percent": base["margin_percent"],
        "breakeven_cpa": base["breakeven_cpa"],
        "target_cpa": base["target_cpa"],
        "breakeven_roas": base["breakeven_roas"],
        "target_roas": base["target_roas"],
        "target_profit_percent": base["target_profit_percent"],
    }
    if repeat_orders > 1.0:
        res["ltv_adjusted_breakeven_cpa"] = round(gp * repeat_orders, 2)
        res["ltv_note"] = f"ASSUMPTION: mijoz davr ichida o'rtacha {repeat_orders} buyurtma beradi. Birinchi buyurtma bo'yicha break-even yuqoridagi `breakeven_cpa`."
    if cvr is not None:
        res["lead_to_sale_cvr_pct"] = round(cvr * 100.0, 2)
        res["breakeven_cpl"] = round(base["breakeven_cpa"] * cvr, 2)
        res["target_cpl"] = round(base["target_cpa"] * cvr, 2)
    test_cost_unit = base["target_cpa"] if cvr is None else base["target_cpa"] * cvr
    unit_name = "sotuv" if cvr is None else "lid"
    res["test_budget"] = {
        "decision_unit": unit_name,
        "decision_conversions": decision_conversions,
        "min_test_budget_at_target": round(test_cost_unit * decision_conversions, 2),
        "min_test_budget_at_breakeven": round((base["breakeven_cpa"] if cvr is None else base["breakeven_cpa"] * cvr) * decision_conversions, 2),
        "note": "Bu qaror uchun yetarli ma'lumot yig'ish xarajati. Byudjet shundan kam bo'lsa, kamroq test (1-2 ad set) yoki yuqoriroq funnel hodisasi (lid o'rniga bot/start) bilan boshlang.",
    }
    if daily_budget is not None:
        db = tcore.require_number(daily_budget, "daily_budget", positive=True)
        res["daily_budget"] = db
        res["days_to_reach_decision_at_target"] = round(res["test_budget"]["min_test_budget_at_target"] / db, 1)

    def _scenario(name: str, cpl: float) -> dict:
        cpl = tcore.require_number(cpl, f"{name}_cpl", positive=True)
        out: dict = {"scenario": name, "assumed_cpl": round(cpl, 2), "label": "ASSUMPTION"}
        if cvr is None:
            out["implied_cpa"] = round(cpl, 2)  # CPL emas, to'g'ridan-to'g'ri sotuv narxi deb qabul qilindi
            implied_cpa = cpl
        else:
            implied_cpa = cpl / cvr
            out["implied_cpa"] = round(implied_cpa, 2)
        out["cpa_headroom_vs_breakeven"] = round(base["breakeven_cpa"] - implied_cpa, 2)
        out["profitable_at_breakeven"] = implied_cpa <= base["breakeven_cpa"]
        out["meets_target_profit"] = implied_cpa <= base["target_cpa"]
        if daily_budget is not None:
            leads = db / cpl
            sales = leads * cvr if cvr is not None else leads
            out["daily_leads"] = round(leads, 2) if cvr is not None else None
            out["daily_sales"] = round(sales, 2)
            out["daily_gross_profit_after_ads"] = round(sales * gp - db, 2)
            out["roas"] = round((sales * price) / db, 2)
        return out

    scenarios = []
    if assumed_cpl is not None:
        scenarios.append(_scenario("base", assumed_cpl))
    if cpl_low is not None:
        scenarios.append(_scenario("optimistic", cpl_low))
    if cpl_high is not None:
        scenarios.append(_scenario("pessimistic", cpl_high))
    if scenarios:
        res["scenarios"] = scenarios
    else:
        res["scenarios_note"] = "Hajm/foyda prognozi hisoblanmadi: `--assumed-cpl` (va ixtiyoriy `--cpl-low/--cpl-high`) berilmadi. CPL taxmini mijoz tarixidan yoki sinovdan olinishi kerak; universal benchmark ishlatilmaydi."

    steps_to_double = 0
    b = 1.0
    while b < 2.0:
        b *= 1.2
        steps_to_double += 1
    res["scaling_constraints"] = {
        "max_step_per_change_pct": 20,
        "steps_to_double_budget": steps_to_double,
        "min_days_to_double": steps_to_double * 2,
        "rule": "Spend-Guard: +20% dan oshiq byudjet o'zgarishi bloklanadi; qadamlar orasida kamida 48 soat (Learning phase himoyasi). Gorizontal masshtab: yangi angle/auditoriya klonlari.",
        "stop_scale_when": "marginal CPA break-even'dan oshganda (Breakdown Effect tekshiruvi bilan: ad-export-analyzer.py breakdown-effect)",
    }
    return res


def calc_meta_155(
    daily_budget: float,
    target_cpa: float,
    currency: str = "USD",
) -> dict:
    """Meta Andromeda 2 (1-5-5) testing taqsimoti va o'rganish fazasi barqarorligini hisoblaydi."""
    daily_budget = tcore.require_number(daily_budget, "daily_budget", positive=True)
    target_cpa = tcore.require_number(target_cpa, "target_cpa", positive=True)

    # Tavsiya etilgan taqsimot
    broad_budget = daily_budget * 0.70       # 70% Broad Prospecting (1-5-5)
    asc_budget = daily_budget * 0.25         # 25% Advantage+ Shopping / Retargeting
    reserve_budget = daily_budget * 0.05     # 5% Tezkor qayta sinash

    # O'rganish fazasi: 1 ta ad set haftasiga kamida 50 ta konversiya olishi kerak
    # Demak, 1 ta ad set uchun haftalik byudjet: target_cpa * 50
    # Kunlik byudjet 1 ad set uchun: (target_cpa * 50) / 7
    min_daily_per_adset = (target_cpa * 50.0) / 7.0
    supported_adsets = max(1, int(broad_budget // min_daily_per_adset))

    weekly_estimated_conversions = (daily_budget * 7.0) / target_cpa
    exit_learning_viable = (broad_budget / max(1, supported_adsets)) >= min_daily_per_adset

    return {
        "daily_budget": round(daily_budget, 2),
        "currency": currency,
        "target_cpa": round(target_cpa, 2),
        "allocations": {
            "broad_prospecting_70pct": round(broad_budget, 2),
            "advantage_plus_25pct": round(asc_budget, 2),
            "reserve_5pct": round(reserve_budget, 2),
        },
        "learning_phase_math": {
            "min_daily_per_adset_for_50_convs": round(min_daily_per_adset, 2),
            "recommended_max_active_adsets": supported_adsets,
            "weekly_total_conversions_projected": int(weekly_estimated_conversions),
            "is_learning_exit_viable": exit_learning_viable,
        },
        "structure_guidelines": [
            f"1 CBO yoki ABO kampaniya: {supported_adsets} ta guruh (har birida 5 xil kreativ burchak).",
            "Advantage+ Shopping kampaniyasi umumiy byudjetning ko'pi bilan 25-30% ini olsin.",
            "Kreativ charchash (Fatigue) radari: Agar FTIR < 60% va Frequency > 2.8 bo'lsa yangi burchak yuklang.",
        ],
    }


def calc_google_sculpt(
    monthly_budget: float,
    target_cpa: float,
    avg_cpc: float,
    irrelevant_query_waste_pct: float = 22.0,
    currency: str = "USD",
) -> dict:
    """Google Ads qidiruv auksioni, max profitable CPC va salbiy kalit so'zlar tejamkori."""
    monthly_budget = tcore.require_number(monthly_budget, "monthly_budget", positive=True)
    target_cpa = tcore.require_number(target_cpa, "target_cpa", positive=True)
    avg_cpc = tcore.require_number(avg_cpc, "avg_cpc", positive=True)
    irrelevant_query_waste_pct = tcore.require_number(irrelevant_query_waste_pct, "waste_pct", min_val=0.0, max_val=100.0)

    daily_budget = monthly_budget / 30.4

    # Qidiruv vs PMax taqsimoti (Search Coliseum 60%, PMax/Demand Gen 40%)
    search_budget = monthly_budget * 0.60
    pmax_budget = monthly_budget * 0.40

    # Kutilayotgan konversiya darajasi (CVR) = Avg CPC / Target CPA
    implied_cvr = (avg_cpc / target_cpa) if target_cpa > 0 else 0.02
    max_profitable_cpc = target_cpa * implied_cvr

    # Salbiy kalit so'zlar (STR mining) orqali saqlab qolinadigan tejamkorlik
    projected_waste = search_budget * (irrelevant_query_waste_pct / 100.0)
    extra_clicks_unlocked = projected_waste / avg_cpc
    extra_conversions_unlocked = extra_clicks_unlocked * implied_cvr

    return {
        "currency": currency.upper(),
        "formatted_monthly_budget": mloc.format_currency(monthly_budget, currency),
        "monthly_budget": mloc.round_currency(monthly_budget, currency),
        "daily_budget": round(daily_budget, 2),
        "target_cpa": round(target_cpa, 2),
        "avg_cpc": round(avg_cpc, 2),
        "implied_conversion_rate_pct": round(implied_cvr * 100.0, 2),
        "max_profitable_cpc": round(max_profitable_cpc, 2),
        "channel_split": {
            "search_coliseum_60pct": round(search_budget, 2),
            "pmax_demandgen_40pct": round(pmax_budget, 2),
        },
        "negative_keyword_optimization": {
            "waste_rate_pct": irrelevant_query_waste_pct,
            "projected_monthly_waste_saved": round(projected_waste, 2),
            "extra_high_intent_clicks_reallocated": int(extra_clicks_unlocked),
            "extra_high_intent_conversions": int(extra_conversions_unlocked),
        },
    }


def calc_telegram_funnel(
    budget: float,
    cpm: float = 3.0,
    ctr_pct: float = 1.2,
    bot_start_pct: float = 65.0,
    lead_activation_pct: float = 30.0,
    order_conversion_pct: float = 12.0,
    aov: float = 40.0,
    currency: str = "USD",
) -> dict:
    """Telegram Ads auksionidan to to'lovgacha bo'lgan to'liq voronka hisob-kitobi."""
    budget = tcore.require_number(budget, "budget", positive=True)
    cpm = tcore.require_number(cpm, "cpm", positive=True)
    ctr_pct = tcore.require_number(ctr_pct, "ctr", min_val=0.0, max_val=100.0)
    bot_start_pct = tcore.require_number(bot_start_pct, "bot_start_pct", min_val=0.0, max_val=100.0)
    lead_activation_pct = tcore.require_number(lead_activation_pct, "lead_pct", min_val=0.0, max_val=100.0)
    order_conversion_pct = tcore.require_number(order_conversion_pct, "order_pct", min_val=0.0, max_val=100.0)
    aov = tcore.require_number(aov, "aov", non_negative=True)

    impressions = (budget / cpm) * 1000.0
    clicks = impressions * (ctr_pct / 100.0)
    bot_starts = clicks * (bot_start_pct / 100.0)
    leads = bot_starts * (lead_activation_pct / 100.0)
    orders = leads * (order_conversion_pct / 100.0)
    revenue = orders * aov

    cpc = (budget / clicks) if clicks > 0 else 0.0
    cps = (budget / bot_starts) if bot_starts > 0 else 0.0  # Cost per subscriber / bot start
    cpl = (budget / leads) if leads > 0 else 0.0            # Cost per lead
    cac = (budget / orders) if orders > 0 else 0.0          # Customer acquisition cost
    roas = (revenue / budget) if budget > 0 else 0.0

    return {
        "budget": round(budget, 2),
        "currency": currency,
        "cpm": round(cpm, 2),
        "impressions": int(impressions),
        "clicks": int(clicks),
        "cpc": round(cpc, 2),
        "bot_starts": int(bot_starts),
        "cost_per_bot_start": round(cps, 2),
        "qualified_leads": int(leads),
        "cost_per_lead": round(cpl, 2),
        "orders_closed": int(orders),
        "customer_acquisition_cost": round(cac, 2),
        "projected_revenue": round(revenue, 2),
        "projected_roas": round(roas, 2),
    }


def calc_testing_ladder(
    total_budget: float,
    breakeven_cpa: float,
    currency: str = "USD",
) -> dict:
    """3 bosqichli sinov pillapoyasi (Sandbox -> Validation -> Scale) taqsimoti."""
    total_budget = tcore.require_number(total_budget, "total_budget", positive=True)
    breakeven_cpa = tcore.require_number(breakeven_cpa, "breakeven_cpa", positive=True)

    p1_budget = total_budget * 0.15
    p2_budget = total_budget * 0.35
    p3_budget = total_budget * 0.50

    return {
        "total_budget": round(total_budget, 2),
        "currency": currency,
        "breakeven_cpa": round(breakeven_cpa, 2),
        "phases": {
            "phase_1_sandbox": {
                "budget_share_pct": 15,
                "allocated_budget": round(p1_budget, 2),
                "duration_days": "3-5 kun",
                "purpose": "Kreativ hook va auditoriya qiziqishini tekshirish",
                "stop_condition": "CTR < 1.0% yoki 2x target CPA sarflanib 0 harakat bo'lsa darhol to'xtatish",
                "promote_criteria": "CTR > 1.5%, CPC bozor medianasidan past",
            },
            "phase_2_validation": {
                "budget_share_pct": 35,
                "allocated_budget": round(p2_budget, 2),
                "duration_days": "5-7 kun",
                "purpose": "Haqiqiy xarid va konversiyalar ishonchliligini tasdiqlash",
                "stop_condition": f"CPA > {breakeven_cpa * 1.2:.2f} (> 1.2x breakeven)",
                "promote_criteria": f"CPA ≤ {breakeven_cpa:.2f} (kamida 15-20 ta toza xarid)",
            },
            "phase_3_scale": {
                "budget_share_pct": 50,
                "allocated_budget": round(p3_budget, 2),
                "duration_days": "Doimiy",
                "purpose": "G'olib burchaklarni gorizontal va vertikal masshtablash",
                "stop_condition": "FTIR < 60% yoki kunlik ROAS breakeven darajasidan pastga tushsa",
                "promote_criteria": "Kreativ charchaguncha haftalik +20% byudjet oshirish",
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Tyrion Media Math Calculator — Pullik media va byudjet matematikasi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Breakeven
    p_be = subparsers.add_parser("breakeven", help="Break-even CPA va ROAS hisobi")
    p_be.add_argument("--price", type=str, required=True, help="Mahsulot sotuv narxi")
    p_be.add_argument("--cogs", type=str, required=True, help="Tannarx (COGS)")
    p_be.add_argument("--shipping", type=str, default=0.0, help="Yetkazib berish xarajati")
    p_be.add_argument("--processing-fee-pct", type=str, default=2.0, help="To'lov tizimi komissiyasi foizi (default: 2.0)")
    p_be.add_argument("--target-profit-pct", type=str, default=0.0, help="Kutilayotgan sof foyda foizi")
    p_be.add_argument("--currency", type=str, default="USD", help="ISO 4217 Currency (USD, EUR, GBP, JPY, BRL, INR, UZS)")
    p_be.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Funnel economics
    p_fe = subparsers.add_parser("funnel-economics", help="Strategiya iqtisodi: break-even/target CPA-CPL-ROAS, test byudjeti, stsenariylar, scale cheklovi")
    p_fe.add_argument("--price", type=str, required=True)
    p_fe.add_argument("--cogs", type=str, required=True)
    p_fe.add_argument("--shipping", type=str, default=0.0)
    p_fe.add_argument("--processing-fee-pct", type=str, default=2.0)
    p_fe.add_argument("--target-profit-pct", type=str, default=0.0)
    p_fe.add_argument("--lead-to-sale-cvr", type=str, default=None, help="Lid -> sotuv konversiyasi foizi (mijoz CRM'idan)")
    p_fe.add_argument("--repeat-orders", type=str, default=1.0, help="Davr ichida o'rtacha buyurtmalar soni (taxmin bo'lsa ASSUMPTION)")
    p_fe.add_argument("--daily-budget", type=str, default=None)
    p_fe.add_argument("--assumed-cpl", type=str, default=None, help="Taxminiy CPL/CPA (ASSUMPTION; prognoz faqat shu berilsa)")
    p_fe.add_argument("--cpl-low", type=str, default=None)
    p_fe.add_argument("--cpl-high", type=str, default=None)
    p_fe.add_argument("--decision-conversions", type=str, default=30, help="Test qarori uchun konversiya soni (HEURISTIC_PRIOR_MODEL; default 30)")
    p_fe.add_argument("--currency", type=str, default="USD")
    p_fe.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Meta-155
    p_m155 = subparsers.add_parser("meta-155", help="Meta Andromeda 1-5-5 testing byudjeti va Learning phase")
    p_m155.add_argument("--daily-budget", type=str, required=True, help="Kunlik byudjet")
    p_m155.add_argument("--target-cpa", type=str, required=True, help="Maqsadli CPA")
    p_m155.add_argument("--currency", type=str, default="USD", help="Valyuta (USD, UZS, EUR)")
    p_m155.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Google-sculpt
    p_gs = subparsers.add_parser("google-sculpt", help="Google Ads Search/PMax taqsimoti va tejamkorlik")
    p_gs.add_argument("--monthly-budget", type=str, required=True, help="Oylik byudjet")
    p_gs.add_argument("--target-cpa", type=str, required=True, help="Maqsadli CPA")
    p_gs.add_argument("--avg-cpc", type=str, required=True, help="O'rtacha CPC")
    p_gs.add_argument("--waste-pct", type=str, default=22.0, help="Keraksiz so'rovlar sarfi foizi (default: 22.0)")
    p_gs.add_argument("--currency", type=str, default="USD", help="ISO 4217 Currency (USD, EUR, GBP, JPY, BRL, INR, UZS)")
    p_gs.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Telegram-funnel
    p_tg = subparsers.add_parser("telegram-funnel", help="Telegram Ads to'liq voronka iqtisodiyoti")
    p_tg.add_argument("--budget", type=str, required=True, help="Umumiy byudjet")
    p_tg.add_argument("--cpm", type=str, default=3.0, help="CPM stavkasi")
    p_tg.add_argument("--ctr", type=str, default=1.2, help="CTR foizi (default: 1.2)")
    p_tg.add_argument("--bot-start-pct", type=str, default=65.0, help="Bot /start bosish foizi (default: 65.0)")
    p_tg.add_argument("--lead-pct", type=str, default=30.0, help="Lidga aylanish foizi (default: 30.0)")
    p_tg.add_argument("--order-pct", type=str, default=12.0, help="Buyurtmaga aylanish foizi (default: 12.0)")
    p_tg.add_argument("--aov", type=str, default=40.0, help="O'rtacha chek (AOV)")
    p_tg.add_argument("--currency", type=str, default="USD", help="Valyuta")
    p_tg.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Ladder
    p_lad = subparsers.add_parser("ladder", help="3 bosqichli sinov pillapoyasi (Sandbox -> Validation -> Scale)")
    p_lad.add_argument("--total-budget", type=str, required=True, help="Umumiy sinov byudjeti")
    p_lad.add_argument("--breakeven-cpa", type=str, required=True, help="Break-even CPA")
    p_lad.add_argument("--currency", type=str, default="USD", help="Valyuta")
    p_lad.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    args = parser.parse_args()

    try:
        if args.command == "breakeven":
            res = calc_breakeven(args.price, args.cogs, args.shipping, args.processing_fee_pct, args.target_profit_pct, args.currency)
        elif args.command == "funnel-economics":
            opt = lambda v: None if v is None else v
            res = calc_funnel_economics(
                args.price, args.cogs, args.shipping, args.processing_fee_pct, args.target_profit_pct,
                opt(args.lead_to_sale_cvr), args.repeat_orders, opt(args.daily_budget), opt(args.assumed_cpl),
                opt(args.cpl_low), opt(args.cpl_high), args.decision_conversions, args.currency,
            )
        elif args.command == "meta-155":
            res = calc_meta_155(args.daily_budget, args.target_cpa, args.currency)
        elif args.command == "google-sculpt":
            res = calc_google_sculpt(args.monthly_budget, args.target_cpa, args.avg_cpc, args.waste_pct, args.currency)
        elif args.command == "telegram-funnel":
            res = calc_telegram_funnel(args.budget, args.cpm, args.ctr, args.bot_start_pct, args.lead_pct, args.order_pct, args.aov, args.currency)
        elif args.command == "ladder":
            res = calc_testing_ladder(args.total_budget, args.breakeven_cpa, args.currency)
    except Exception as exc:
        print(f"Xato: {exc}", file=sys.stderr)
        return tcore.EXIT_VALIDATION

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return tcore.exit_code_for_result(res)

    # Inson o'qiydigan chiroyli xulosa
    print(f"\n========================================================")
    print(f"  TYRION MEDIA MATH — {args.command.upper()}")
    print(f"========================================================")
    for k, v in res.items():
        if isinstance(v, dict):
            print(f"\n  [{k}]:")
            for sub_k, sub_v in v.items():
                print(f"    - {sub_k}: {sub_v}")
        elif isinstance(v, list):
            print(f"\n  [{k}]:")
            for item in v:
                print(f"    * {item}")
        else:
            print(f"  {k}: {v}")
    print()
    return tcore.exit_code_for_result(res)


if __name__ == "__main__":
    sys.exit(main())
