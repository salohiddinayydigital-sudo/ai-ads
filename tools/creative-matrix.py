#!/usr/bin/env python3
"""Tyrion Creative Matrix & Hook Engine — Global 3x3 Creative Testing Matrix, Multilingual Hooks & Fatigue Radar (0 token).

Commands:
  python3 tools/creative-matrix.py matrix --niche ecom --product "Classic Suit" --price 150 --market eu --currency EUR [--json]
  python3 tools/creative-matrix.py hooks --niche edtech --offer "IELTS 7.0 in 90 Days" --languages en,de,ar,uz_latin [--json]
  python3 tools/creative-matrix.py fatigue --hook-rate 22.0 --hold-rate 9.5 --ctr-drop-pct 35.0 --frequency 2.9 --ftir 52.0 [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
import market_locale as mloc  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

ANGLES = [
    ("A1: PAIN & MISTAKE (Problem / Costly Error)", "Expose the #1 costly mistake or friction point within the first 3 seconds"),
    ("A2: SOCIAL PROOF & CASE (Verified Outcome)", "Quantified customer case study, before/after proof, or verified review breakdown"),
    ("A3: MECHANISM & BNPL OFFER (Unique Mechanism / Flexible Pay)", "Demonstrate why the mechanism works faster + market-native BNPL / risk-reversal anchor"),
]

FORMATS = [
    ("F1: Founder / Expert Face-to-Camera (9:16 Vertical)", "High-trust direct-to-camera hook + dynamic B-roll and native captions"),
    ("F2: Extreme Demo / UGC POV Test (9:16 Vertical)", "Stress-test demonstration or authentic customer POV unboxing/workflow"),
    ("F3: Us vs Them / Offer Breakdown (4:5 Static / Carousel)", "Old way vs Your solution + transparent pricing, BNPL anchor, and guarantee"),
]


def build_matrix(
    niche: str,
    product: str,
    price: float = 100.0,
    market: str = "global",
    currency: str = "",
) -> dict:
    pack = mloc.load_market_pack(market)
    m_id = pack["market_id"]
    curr = (currency or pack.get("default_currency") or "USD").strip().upper()
    bnpl_list = pack.get("bnpl_providers") or ["Klarna", "Afterpay"]
    primary_bnpl = bnpl_list[0]
    template = pack.get("price_anchor_template") or "Or 4 interest-free payments of {installment} with {bnpl}"

    if m_id == "uz" and curr in ("UZS", "USD"):
        installment_uzs = int((price * 12800) / 12) if curr == "USD" else int(price / 12)
        inst_str = f"{installment_uzs:,} so'm"
        bnpl_anchor = f"Oyiga ~{inst_str}dan ({primary_bnpl} orqali 12 oy muddatli to'lov)" if price >= 50 else "Tezkor yetkazib berish"
        cta_str = "Telegram Bot / Instagram DM ('+ ' yoki kalit so'z)" if price >= 50 else "Darhol buyurtma (Payme / Click / Uzum)"
    else:
        div = 12 if m_id in ("latam", "in") else (3 if m_id in ("eu", "uk", "sea") else 4)
        inst_val = mloc.round_currency(price / div, curr)
        inst_str = mloc.format_currency(inst_val, curr)
        bnpl_anchor = template.format(installment=inst_str, bnpl=primary_bnpl)
        primary_funnel = (pack.get("primary_funnels") or ["Direct Checkout"])[0]
        cta_str = f"Shop Now / {primary_bnpl} Checkout ({primary_funnel.split('->')[0].strip()})"

    cells: list[dict] = []
    idx = 1
    for a_code, a_desc in ANGLES:
        for f_code, f_desc in FORMATS:
            cells.append({
                "cell_id": f"C{idx:02d}",
                "angle": a_code,
                "format": f_code,
                "concept": f"{product}: {a_desc} ({f_desc})",
                "cta": cta_str,
                "bnpl_anchor": bnpl_anchor,
            })
            idx += 1

    rounded_price = mloc.round_currency(price, curr)
    return {
        "niche": niche,
        "product": product,
        "market": m_id,
        "currency": curr,
        "price": rounded_price,
        "price_usd": rounded_price,
        "formatted_price": mloc.format_currency(price, curr),
        "bnpl_providers": bnpl_list,
        "price_anchor": bnpl_anchor,
        "andromeda_rule": "Deploy at least 3 distinct Angles x 2 Formats per Ad Set (never 3 minor edits of the same video).",
        "matrix_3x3": cells,
    }


NATIVE_HOOK_TEMPLATES: dict[str, list[str]] = {
    "en": [
        "[Curiosity Gap] The 1 counter-intuitive truth about {offer} that 90% of buyers overlook...",
        "[Pain / Costly Mistake] Stop wasting budget on the old way — here is how {offer} fixes it:",
        "[Quantified Proof] How we achieved measurable results in 14 days without extra overhead ({offer})",
        "[Qualifier Hook] Attention: this is only for teams serious about scaling {offer} profitably.",
    ],
    "de": [
        "[Neugier / Fokus] Die 1 Wahrheit über {offer}, die 90% im DACH-Markt übersehen...",
        "[Fehler vermeiden] Warum die klassische Methode unnötig Budget verbrennt — und wie {offer} das löst:",
        "[Zahlen & Beweis] Messbare Ergebnisse in 14 Tagen mit klarer Garantie ({offer}).",
    ],
    "fr": [
        "[Curiosité] La vérité sur {offer} que 90% des acheteurs ignorent encore...",
        "[Erreur coûteuse] Arrêtez de perdre du budget avec l'ancienne méthode : découvrez {offer}.",
        "[Preuve chiffrée] Comment obtenir des résultats vérifiables en 14 jours ({offer}).",
    ],
    "es": [
        "[Curiosidad] La verdad sobre {offer} que el 90% pasa por alto...",
        "[Error Costoso] Deja de perder presupuesto con el método tradicional: así funciona {offer}.",
        "[Prueba Real] Resultados medibles en 14 días con garantía transparente ({offer}).",
    ],
    "pt-BR": [
        "[Curiosidade] O segredo sobre {offer} que 90% do mercado ignora...",
        "[Erro Caro] Pare de queimar verba do jeito antigo: veja como {offer} resolve isso.",
        "[Prova Real] Como alcançar resultado validado em 14 dias ({offer}).",
    ],
    "ar": [
        "[فضول / فجوة معرفية] حقيقة واحدة عن {offer} يتجاهلها 90% من المشترين...",
        "[خطأ مكلف] توقف عن إهدار الميزانية بالطريقة القديمة — إليك الحل مع {offer}:",
        "[دليل رقمي] كيف تحقق نتائج ملموسة خلال 14 يوماً بضمان واضح ({offer}).",
    ],
    "uz_latin": [
        "[Qiziqish/Bo'shliq] {offer} haqida 90% odam bilmaydigan 1 ta haqiqat...",
        "[Xato/Og'riq] Agar hali ham eski usulda harakat qilayotgan bo'lsangiz, pulingizni havoga sovuryapsiz: {offer}",
        "[Aniq Raqam/Isbot] Qanday qilib 14 kun ichida ortiqcha xarajatsiz natijaga chiqish mumkin? ({offer})",
        "[Filtr-Hook] Diqqat: bu video faqat haqiqiy sifat va kafolat izlayotganlar uchun — {offer}",
    ],
    "uz_cyrillic": [
        "[Қизиқиш] {offer} ҳақида 90% одам билмайдиган 1 та сир...",
        "[Хато/Оғриқ] Пулингизни бефойда тажрибаларга сарфлашни тўхтатинг: {offer}",
        "[Исбот] Натижа бўлмаса — пулингизни қайтарамиз: {offer}",
    ],
    "ru": [
        "[Проблема/Ошибка] 3 главные ошибки при выборе, из-за которых вы теряете время и бюджет ({offer})",
        "[Цифры/Кейс] Как получить результат за 14 дней с гарантией по договору: {offer}",
        "[Фильтр-Хук] Только для тех, кто ценит твердый результат и прозрачные условия: {offer}",
    ],
}


def generate_hooks(niche: str, offer: str, languages: list[str] | None = None) -> dict:
    req_langs = languages or ["uz_latin", "uz_cyrillic", "ru", "en"]
    hooks_out: dict[str, list[str]] = {}
    rtl_notes: dict[str, str] = {}

    for raw_lang in req_langs:
        key = raw_lang.strip()
        if not key:
            continue
        norm_info = mloc.normalize_bcp47_language(key)
        bcp = norm_info["bcp47"]
        lookup = key if key in NATIVE_HOOK_TEMPLATES else (bcp if bcp in NATIVE_HOOK_TEMPLATES else bcp.split("-")[0])
        templates = NATIVE_HOOK_TEMPLATES.get(lookup, NATIVE_HOOK_TEMPLATES["en"])
        hooks_out[key] = [t.format(offer=offer) for t in templates]
        if norm_info["is_rtl"] and norm_info["rtl_formatting_note"]:
            rtl_notes[key] = norm_info["rtl_formatting_note"]

    res: dict[str, object] = {
        "niche": niche,
        "offer": offer,
        "native_copywriting_principle": "Hooks are written natively per target cultural/linguistic market, never mechanically translated word-for-word.",
        "hooks_by_language": hooks_out,
    }
    if rtl_notes:
        res["rtl_formatting_notes"] = rtl_notes
    return res


def analyze_fatigue(
    hook_rate: float,
    hold_rate: float,
    ctr_drop_pct: float,
    frequency: float,
    ftir: float,
) -> dict:
    actions: list[str] = []
    status = "HEALTHY_CREATIVE"

    if hook_rate < 25.0:
        status = "WEAK_3S_HOOK"
        actions.append(f"Hook Rate low ({hook_rate:.1f}% < 25%): Keep body intact and test 3 new visual + verbal 3-second hooks.")
    if hold_rate < 12.0:
        if status == "HEALTHY_CREATIVE":
            status = "WEAK_BODY_RETENTION"
        actions.append(f"Hold Rate low ({hold_rate:.1f}% < 12%): Cut intro filler between seconds 4-10 and pace visual cuts every 2.5s.")
    if ctr_drop_pct >= 25.0 or frequency >= 2.8 or ftir < 55.0:
        status = "CREATIVE_FATIGUED"
        actions.append(
            f"Creative fatigued (CTR drop={ctr_drop_pct:.1f}%, Frequency={frequency:.2f}, FTIR={ftir:.1f}%): "
            "Rotate to a fresh psychological angle (Angle A2/A3) and new creator/location."
        )
    if not actions:
        actions.append("Creative metrics healthy (Hook >=25%, Hold >=12%, FTIR >=55%) — scale horizontally via 'More/Better' variations.")

    return {
        "status": status,
        "metrics": {
            "hook_rate_pct": hook_rate,
            "hold_rate_pct": hold_rate,
            "ctr_drop_pct": ctr_drop_pct,
            "frequency": frequency,
            "ftir_pct": ftir,
        },
        "prescribed_actions": actions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="creative-matrix.py", description="Global Creative Matrix & Multilingual Hook Engine")
    sub = parser.add_subparsers(dest="command", required=True)

    p_mat = sub.add_parser("matrix", help="3x3 Angle x Format creative testing matrix with market BNPL anchor")
    p_mat.add_argument("--niche", default="ecom")
    p_mat.add_argument("--product", required=True)
    p_mat.add_argument("--price", type=float, default=100.0)
    p_mat.add_argument("--market", default="global", help="Market pack (global, uz, us, eu, uk, mena, latam, sea, in)")
    p_mat.add_argument("--currency", default="", help="ISO 4217 currency override (USD, EUR, GBP, JPY, UZS, etc.)")
    p_mat.add_argument("--json", action="store_true")

    p_hk = sub.add_parser("hooks", help="Multilingual 3-second Hook generator (any BCP 47 language)")
    p_hk.add_argument("--niche", default="ecom")
    p_hk.add_argument("--offer", required=True)
    p_hk.add_argument("--languages", default="", help="Comma-separated BCP 47 language codes (e.g. en,de,fr,ar)")
    p_hk.add_argument("--json", action="store_true")

    p_fat = sub.add_parser("fatigue", help="Creative fatigue diagnostics via Hook Rate, Hold Rate & FTIR")
    p_fat.add_argument("--hook-rate", type=float, required=True)
    p_fat.add_argument("--hold-rate", type=float, required=True)
    p_fat.add_argument("--ctr-drop-pct", type=float, default=0.0)
    p_fat.add_argument("--frequency", type=float, default=1.5)
    p_fat.add_argument("--ftir", type=float, default=70.0)
    p_fat.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "matrix":
        res = build_matrix(args.niche, args.product, args.price, market=args.market, currency=args.currency)
    elif args.command == "hooks":
        langs = [x.strip() for x in args.languages.split(",") if x.strip()] if args.languages else None
        res = generate_hooks(args.niche, args.offer, languages=langs)
    elif args.command == "fatigue":
        res = analyze_fatigue(args.hook_rate, args.hold_rate, args.ctr_drop_pct, args.frequency, args.ftir)
    else:
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 66)
    print(f"  🎨 TYRION CREATIVE STUDIO — {args.command.upper()}")
    print("=" * 66)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("=" * 66)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
