#!/usr/bin/env python3
"""Tyrion v7.0 Creative Matrix, Video Ad Scripting, Andromeda PDA Diversity & Ad Copy Engine (`tools/creative-matrix.py`).

Commands:
  python3 tools/creative-matrix.py matrix --niche ecom --product "Klassik kostyum" --price 150 [--market uz] [--currency USD] [--json]
  python3 tools/creative-matrix.py hooks --niche edtech --offer "IELTS 7.0 3 oyda" [--languages uz_latin,ru,en] [--json]
  python3 tools/creative-matrix.py fatigue --hook-rate 22.0 --hold-rate 9.5 --ctr-drop-pct 35.0 --frequency 2.9 --ftir 52.0 [--json]
  python3 tools/creative-matrix.py video-script --niche medical --product "Tish implantatsiyasi" --problem "Tish yo'qotilishi" --format ugc_reaction_demo --language uz_latin [--json]
  python3 tools/creative-matrix.py pda-matrix --niche ecom --product "Espresso Machine" --price 300 --market eu --currency EUR [--json]
  python3 tools/creative-matrix.py ad-copy --platform meta --product "CRM Avtomatlashtirish" --problem "Lidlar yo'qolishi" --proof "300+ kompaniya" --language uz_latin [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

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
    ("F1: Founder / Expert Face-to-Camera (9:16 Vertical — S-Tier)", "High-trust direct-to-camera hook + dynamic B-roll and native captions"),
    ("F2: Reaction + Hard-Cut UGC Demo (9:16 Vertical — S-Tier)", "Visceral 2s problem reaction -> hard cut into real-time product/service proof"),
    ("F3: Us vs Them / Offer Breakdown (4:5 Static / Carousel — A-Tier)", "Old painful alternative vs Your solution + transparent pricing, BNPL anchor, and guarantee"),
]

# 2026 S->F Meta Ad Format Taxonomy (Andromeda + GEM + UTIS calibrated)
META_FORMAT_TAXONOMY: dict[str, dict[str, Any]] = {
    "ugc_reaction_demo": {
        "tier": "S",
        "title": "Reaction + Hard-Cut Product Demo (UGC 9:16)",
        "funnel_role": "Unicorn Cold-Scaler (TOF)",
        "entity_id_class": "VIDEO_UGC_POV_DEMO",
        "recommended_duration_sec": 25,
        "why_it_scales": "Opens with a 2-second visceral reaction/problem and hard-cuts into live proof — maximizes 3s Hook Rate and UTIS genuine-interest score.",
    },
    "founder_authority": {
        "tier": "S",
        "title": "Founder / Doctor / Expert Direct-to-Camera (9:16)",
        "funnel_role": "Unicorn Cold & High-Ticket Scaler (TOF/MOF)",
        "entity_id_class": "VIDEO_FOUNDER_TALKING_HEAD",
        "recommended_duration_sec": 35,
        "why_it_scales": "Delivers 2–3x ROAS lift on high-consideration offers (Medical, Real Estate, EdTech, B2B, Premium Ecom) via direct authority.",
    },
    "no_yapping_split_screen": {
        "tier": "S",
        "title": "'No Yapping' Split-Screen Tutorial / Fast Demo (9:16)",
        "funnel_role": "Cold & Warm Velocity Scaler",
        "entity_id_class": "VIDEO_SPLIT_SCREEN_TUTORIAL",
        "recommended_duration_sec": 20,
        "why_it_scales": "Top half shows continuous product/software action from frame 1; bottom half delivers rapid numeric payoff with zero intro filler.",
    },
    "imessage_reveal": {
        "tier": "A",
        "title": "iOS-Native iMessage / Telegram Chat Reveal (9:16)",
        "funnel_role": "Cold Pattern-Interrupt",
        "entity_id_class": "VIDEO_UI_CHAT_REVEAL",
        "recommended_duration_sec": 20,
        "why_it_scales": "Unfolds bubble-by-bubble (Screenshot hook -> friend asks 'Where did you get that?' -> Brand + Offer reveal -> End card).",
    },
    "chatgpt_reveal": {
        "tier": "A",
        "title": "AI Search / Prompt-to-Answer Reveal (9:16)",
        "funnel_role": "Cold Solution-Aware Scaler",
        "entity_id_class": "VIDEO_UI_SEARCH_REVEAL",
        "recommended_duration_sec": 20,
        "why_it_scales": "Shows buyer typing their exact problem into an AI/search bar -> streaming comparison reveals the offer's unique mechanism.",
    },
    "greenscreen_proof": {
        "tier": "A",
        "title": "Greenscreen Comment / Price / Case Breakdown (9:16)",
        "funnel_role": "MOF / BOF Objection Crusher",
        "entity_id_class": "VIDEO_GREENSCREEN_COMMENT_REPLY",
        "recommended_duration_sec": 30,
        "why_it_scales": "Creator stands in front of a real customer objection comment or price comparison sheet and proves the math on screen.",
    },
    "faceless_motion_explainer": {
        "tier": "A",
        "title": "Faceless Motion-Style / B-Roll Explainer (9:16 / 4:5)",
        "funnel_role": "Cold & B2B/SaaS Scaler (No Actor Needed)",
        "entity_id_class": "VIDEO_FACELESS_MOTION_EXPLAINER",
        "recommended_duration_sec": 25,
        "why_it_scales": "Combines high-contrast kinetic typography, B-roll/product macro shots, and word-timed voiceover without requiring on-camera talent.",
    },
}

# Banned AI copywriting tells (checked by lint_ai_tells)
AI_TELL_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"\bit'?s not (just )?([^,.]+),\s*it'?s\b", re.I), "CONTRAST_REVEAL_EN", "Avoid 'It's not X, it's Y' contrast reveals; state the concrete benefit directly."),
    (re.compile(r"\bbu shunchaki [^,.]+ emas[,—\-\s]+bu\b", re.I), "CONTRAST_REVEAL_UZ", "Avoid 'Bu shunchaki X emas, bu Y' AI reveal; state the concrete benefit directly."),
    (re.compile(r"\bэто не просто [^,.]+,\s*а\b", re.I), "CONTRAST_REVEAL_RU", "Avoid 'Это не просто X, а Y' AI reveal; state the concrete outcome directly."),
    (re.compile(r"\b(stop scrolling|wait before you scroll|o'tkazib yubormang|не пролистывай)\b", re.I), "HOOK_SLOP", "Replace generic 'Stop scrolling / O'tkazib yubormang' hook slop with a specific buyer problem or number."),
    (re.compile(r"\b(unlock the power of|take .* to the next level|say goodbye to|reimagined)\b", re.I), "STOCK_AI_CLICHE", "Remove stock AI clichés ('unlock the power of', 'say goodbye to')."),
    (re.compile(r"—"), "EM_DASH_TELL", "Replace em-dashes (—) in ad copy with a period, colon, or comma."),
]


def lint_ai_tells(text: str) -> dict[str, Any]:
    """Scans ad copy or video script lines for AI tells and returns cleaned copy + detected issues."""
    raw = str(text or "")
    issues: list[dict[str, str]] = []
    for pat, code, advice in AI_TELL_PATTERNS:
        if pat.search(raw):
            issues.append({"code": code, "advice": advice})

    cleaned = raw.replace(" — ", " - ").replace("—", "-")
    cleaned = re.sub(r"\b[Ss]top scrolling[!.,\s]*", "", cleaned)
    cleaned = re.sub(r"\b[Oo]'tkazib yubormang[!.,\s]*", "", cleaned)
    cleaned = re.sub(r"\b[Нн]е пролистывай(те)?[!.,\s]*", "", cleaned)
    cleaned = re.sub(r"\b[Ii]t'?s not (?:just )?[^,.]+,\s*it'?s\s+", "", cleaned)
    cleaned = re.sub(r"\b[Bb]u shunchaki [^,.]+ emas[,—\-\s]+bu\s+", "", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

    return {
        "has_ai_tells": len(issues) > 0,
        "issues_count": len(issues),
        "issues": issues,
        "original_text": raw,
        "cleaned_text": cleaned,
    }


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
            tier = "S" if "S-Tier" in f_code else "A"
            cells.append({
                "cell_id": f"C{idx:02d}",
                "angle": a_code,
                "format": f_code,
                "format_tier": tier,
                "concept": f"{product}: {a_desc} ({f_desc})",
                "cta": cta_str,
                "bnpl_anchor": bnpl_anchor,
                "falsifiable_hypothesis": (
                    f"In cold TOF prospecting, {f_code.split('(')[0].strip()} with {a_code.split('(')[0].strip()} "
                    f"will beat the account baseline on 3s Hook Rate (>=28%) and Outbound CTR (+15% vs control) within 1,500 impressions."
                ),
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
        "andromeda_rule": (
            "Deploy at least 3 distinct Angles x 2 Formats per Ad Set. Under Meta Andromeda's computer-vision Entity ID clustering, "
            "minor text/hook swaps on the same video get only 1 retrieval ticket — use visually distinct formats (Founder, UGC Demo, Static Comparison)."
        ),
        "matrix_3x3": cells,
    }


NATIVE_HOOK_TEMPLATES: dict[str, list[str]] = {
    "en": [
        "[Curiosity Gap] The 1 counter-intuitive truth about {offer} that 90% of buyers overlook...",
        "[Pain / Costly Mistake] Stop wasting budget on the old way - here is how {offer} fixes it in 14 days:",
        "[Quantified Proof] How we achieved measurable results in 14 days without extra overhead ({offer})",
        "[Qualifier Hook] Attention: this is only for teams serious about scaling {offer} profitably.",
    ],
    "de": [
        "[Neugier / Fokus] Die 1 Wahrheit über {offer}, die 90% im DACH-Markt übersehen...",
        "[Fehler vermeiden] Warum die klassische Methode unnötig Budget verbrennt - und wie {offer} das löst:",
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
        "[خطأ مكلف] توقف عن إهدار الميزانية بالطريقة القديمة - إليك الحل مع {offer}:",
        "[دليل رقمي] كيف تحقق نتائج ملموسة خلال 14 يوماً بضمان واضح ({offer}).",
    ],
    "uz_latin": [
        "[Qiziqish/Bo'shliq] {offer} haqida 90% odam bilmaydigan 1 ta amaliy fakt...",
        "[Xato/Og'riq] Agar hali ham eski usulda harakat qilayotgan bo'lsangiz, vaqt va pul yo'qotyapsiz: {offer}",
        "[Aniq Raqam/Isbot] Qanday qilib 14 kun ichida ortiqcha xarajatsiz natijaga chiqish mumkin? ({offer})",
        "[Filtr-Hook] Diqqat: bu video faqat aniq natija va shartnoma kafolati izlayotganlar uchun ({offer})",
    ],
    "uz_cyrillic": [
        "[Қизиқиш] {offer} ҳақида 90% одам билмайдиган 1 та амалий факт...",
        "[Хато/Оғриқ] Пулингизни бефойда тажрибаларга сарфлашни тўхтатинг: {offer}",
        "[Исбот] Натижа бўлмаса, шартнома бўйича кафолат: {offer}",
    ],
    "ru": [
        "[Проблема/Ошибка] 3 главные ошибки при выборе, из-за которых вы теряете время и бюджет ({offer})",
        "[Цифры/Кейс] Как получить измеримый результат за 14 дней с гарантией по договору: {offer}",
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
        "native_copywriting_principle": "Hooks are written natively per target cultural/linguistic market, never mechanically translated word-for-word, and pass the No-AI-Tells filter.",
        "safe_zone_spec": "Place on-screen hook text inside the central 720x1200 px safe zone (within 1080x1920 9:16 canvas); white fill + 3px black stroke.",
        "hooks_by_language": hooks_out,
    }
    if rtl_notes:
        res["rtl_formatting_notes"] = rtl_notes
    return res


def generate_video_script(
    niche: str = "ecom",
    product: str = "",
    problem: str = "",
    format_name: str = "ugc_reaction_demo",
    duration_sec: int = 30,
    price: float = 100.0,
    market: str = "global",
    currency: str = "",
    language: str = "uz_latin",
) -> dict[str, Any]:
    """Generates a complete, ready-to-shoot 9:16 video ad script and scene-by-scene storyboard with 0 external API keys."""
    fmt_key = format_name if format_name in META_FORMAT_TAXONOMY else "ugc_reaction_demo"
    fmt_meta = META_FORMAT_TAXONOMY[fmt_key]
    mat = build_matrix(niche=niche, product=product or "Taklif", price=price, market=market, currency=currency)
    bnpl_anchor = mat["price_anchor"]
    clean_prod = product.strip() or f"{niche} yechimi"
    clean_prob = problem.strip() or f"{clean_prod} tanlashdagi asosiy muammo va ortiqcha xarajat"

    lang_key = language.strip() or "uz_latin"
    is_ru = lang_key.startswith("ru")
    is_en = lang_key.startswith("en")

    if is_ru:
        hook_variants = [
            {
                "hook_id": "H1_PROBLEM_MISTAKE",
                "visual_action_0_3s": f"Крупный план: демонстрация главной ошибки при выборе ({clean_prob}) -> резкий переход (hard cut) на {clean_prod}.",
                "safe_zone_text_720x1200": f"Не переплачивайте за {clean_prod[:24]}!",
                "spoken_line_0_3s": f"9 из 10 клиентов теряют бюджет из-за этой ошибки при выборе {clean_prod}.",
            },
            {
                "hook_id": "H2_QUANTIFIED_PROOF",
                "visual_action_0_3s": f"Разделенный экран (Split-Screen): сверху реальный процесс работы {clean_prod}, снизу таймер и результат.",
                "safe_zone_text_720x1200": f"Результат за 14 дней: {clean_prod[:22]}",
                "spoken_line_0_3s": f"Вот как выглядит реальный результат {clean_prod} без лишних слов и переплат.",
            },
            {
                "hook_id": "H3_UI_OR_COMMENT_REVEAL",
                "visual_action_0_3s": "Скриншот реального вопроса клиента в Telegram/iMessage или комментарий на фоне Greenscreen.",
                "safe_zone_text_720x1200": f"Честный разбор: {clean_prod[:24]}",
                "spoken_line_0_3s": f"Меня часто спрашивают: почему {clean_prod} окупается быстрее обычных аналогов? Показываю на цифрах.",
            },
        ]
        scenes = [
            {
                "timecode": "00:00 - 00:03",
                "scene_role": "1. HOOK (Thumbstop Gate)",
                "visual_and_camera": hook_variants[0]["visual_action_0_3s"],
                "on_screen_text_720x1200": hook_variants[0]["safe_zone_text_720x1200"],
                "spoken_audio_vo": hook_variants[0]["spoken_line_0_3s"],
                "cut_pacing": "Смена кадра через 1.2 сек, движение в первом кадре",
            },
            {
                "timecode": "00:03 - 00:09",
                "scene_role": "2. PROBLEM & AGITATION (Боль клиента)",
                "visual_and_camera": f"B-Roll: наглядное сравнение старого долгого способа ({clean_prob}) и нового решения.",
                "on_screen_text_720x1200": f"Проблема: {clean_prob[:32]}",
                "spoken_audio_vo": f"Когда вы сталкиваетесь с проблемой «{clean_prob}», стандартные решения только отнимают время.",
                "cut_pacing": "Jump-cut каждые 1.5 сек, без пауз >0.2 сек",
            },
            {
                "timecode": "00:09 - 00:18",
                "scene_role": "3. MECHANISM & LIVE DEMO (Механизм в действии)",
                "visual_and_camera": f"Крупный план (Macro B-Roll): показ работы {clean_prod} с трех ракурсов (3-Capture System).",
                "on_screen_text_720x1200": f"Как работает {clean_prod[:26]}",
                "spoken_audio_vo": f"Именно поэтому в {clean_prod} мы внедрили проверенный механизм, который дает предсказуемый результат с первого шага.",
                "cut_pacing": "Динамичный B-Roll каждые 1.5–2.0 сек",
            },
            {
                "timecode": "00:18 - 00:25",
                "scene_role": "4. PROOF & PRICE ANCHOR (Кейс + Рассрочка / Выгода)",
                "visual_and_camera": "Экран с реальными отзывами клиентов + карточка с условиями оплаты / гарантии.",
                "on_screen_text_720x1200": bnpl_anchor[:48],
                "spoken_audio_vo": f"Более сотни клиентов уже проверили это на практике. Доступно на выгодных условиях: {bnpl_anchor}.",
                "cut_pacing": "Крупная плашка цены в безопасной зоне 720x1200",
            },
            {
                "timecode": "00:25 - 00:30",
                "scene_role": "5. DIRECT CTA (Конкретный шаг)",
                "visual_and_camera": "Спикер указывает на кнопку внизу экрана / показ интерфейса бота или сайта.",
                "on_screen_text_720x1200": "Нажмите кнопку ниже -> расчет за 2 мин",
                "spoken_audio_vo": f"Нажмите кнопку ниже или напишите «+» в директ, чтобы получить точный расчет и бонус по {clean_prod} прямо сейчас.",
                "cut_pacing": "Финальный стоп-кадр с четким призывом",
            },
        ]
    elif is_en:
        hook_variants = [
            {
                "hook_id": "H1_PROBLEM_MISTAKE",
                "visual_action_0_3s": f"Close-up visual of the #1 costly mistake ({clean_prob}) -> instant hard cut to {clean_prod} in action.",
                "safe_zone_text_720x1200": f"Stop overpaying for {clean_prod[:22]}",
                "spoken_line_0_3s": f"9 out of 10 buyers waste budget on {clean_prod} because of this one mistake.",
            },
            {
                "hook_id": "H2_QUANTIFIED_PROOF",
                "visual_action_0_3s": f"Split-Screen: top half shows live {clean_prod} demo from frame 1; bottom half shows before/after metric.",
                "safe_zone_text_720x1200": f"Verified 14-Day Result: {clean_prod[:18]}",
                "spoken_line_0_3s": f"Here is how {clean_prod} solves {clean_prob} in under 14 days with zero guesswork.",
            },
            {
                "hook_id": "H3_UI_OR_COMMENT_REVEAL",
                "visual_action_0_3s": "iMessage bubble notification or real customer objection comment pinned in Greenscreen top-center.",
                "safe_zone_text_720x1200": f"Does {clean_prod[:22]} actually work?",
                "spoken_line_0_3s": f"You asked if {clean_prod} actually delivers on its promise. Look at the side-by-side numbers.",
            },
        ]
        scenes = [
            {
                "timecode": "00:00 - 00:03",
                "scene_role": "1. HOOK (3-Second Thumbstop Gate)",
                "visual_and_camera": hook_variants[0]["visual_action_0_3s"],
                "on_screen_text_720x1200": hook_variants[0]["safe_zone_text_720x1200"],
                "spoken_audio_vo": hook_variants[0]["spoken_line_0_3s"],
                "cut_pacing": "Hard visual cut at 1.0s; motion in frame 1",
            },
            {
                "timecode": "00:03 - 00:09",
                "scene_role": "2. PROBLEM & COST OF INACTION",
                "visual_and_camera": f"B-Roll contrasting the slow legacy alternative ({clean_prob}) vs clean workflow.",
                "on_screen_text_720x1200": f"The Problem: {clean_prob[:30]}",
                "spoken_audio_vo": f"Dealing with {clean_prob} the old way drains your time and margin every single week.",
                "cut_pacing": "1.5s cut cadence, zero dead air",
            },
            {
                "timecode": "00:09 - 00:18",
                "scene_role": "3. UNIQUE MECHANISM & LIVE DEMO",
                "visual_and_camera": f"3-angle close-up demonstration of {clean_prod} (Capture 2 hands-on B-Roll).",
                "on_screen_text_720x1200": f"How {clean_prod[:26]} Works",
                "spoken_audio_vo": f"{clean_prod} fixes this at the root by automating the exact step where most alternatives fail.",
                "cut_pacing": "Visual angle change every 1.5–2.0s",
            },
            {
                "timecode": "00:18 - 00:25",
                "scene_role": "4. SOCIAL PROOF & BNPL / OFFER ANCHOR",
                "visual_and_camera": "Verified customer review overlay + transparent pricing/payment breakdown.",
                "on_screen_text_720x1200": bnpl_anchor[:48],
                "spoken_audio_vo": f"Backed by verified customer outcomes and flexible payment options: {bnpl_anchor}.",
                "cut_pacing": "Highlight offer badge in 720x1200 center",
            },
            {
                "timecode": "00:25 - 00:30",
                "scene_role": "5. SPECIFIC CTA",
                "visual_and_camera": "Creator points toward CTA button + end-card summary of guarantee.",
                "on_screen_text_720x1200": "Tap below to claim your plan ->",
                "spoken_audio_vo": f"Tap the link below right now to get your {clean_prod} plan and risk-free guarantee.",
                "cut_pacing": "Clean 2s hold on end card",
            },
        ]
    else:
        hook_variants = [
            {
                "hook_id": "H1_PROBLEM_MISTAKE",
                "visual_action_0_3s": f"Kрупniy plan (Macro): '{clean_prob}' muammosini jonli ko'rsatish -> 1 soniyada {clean_prod} yechimiga keskin o'tish (hard cut).",
                "safe_zone_text_720x1200": f"{clean_prod[:24]}: 90% odam qiladigan xato!",
                "spoken_line_0_3s": f"{clean_prod} tanlashda 10 tadan 9 kishi aynan shu xato sababli pul va vaqt yo'qotadi.",
            },
            {
                "hook_id": "H2_QUANTIFIED_PROOF",
                "visual_action_0_3s": f"Ikki ekran (Split-Screen): tepada {clean_prod} real jarayoni, pastda aniq raqamli natija va muddat.",
                "safe_zone_text_720x1200": f"14 kunda aniq natija: {clean_prod[:20]}",
                "spoken_line_0_3s": f"Ortiqcha gaplarsiz: {clean_prod} yordamida '{clean_prob}' muammosini qanday hal qilganimizni ko'ring.",
            },
            {
                "hook_id": "H3_UI_OR_COMMENT_REVEAL",
                "visual_action_0_3s": "Telegram/iMessage yozishmasi yoki mijozning 'Qimmat-ku / Ishonchlimi?' degan izohi Greenscreen fonida.",
                "safe_zone_text_720x1200": f"Haqiqatan ishlaydimi? ({clean_prod[:18]})",
                "spoken_line_0_3s": f"Ko'pchilik so'raydi: '{clean_prod} haqiqatan puliga arziydimi?' Keling, aniq hisob-kitobni ko'ramiz.",
            },
        ]
        scenes = [
            {
                "timecode": "00:00 - 00:03",
                "scene_role": "1. HOOK (Birinchi 3 soniya — Thumbstop darvozasi)",
                "visual_and_camera": hook_variants[0]["visual_action_0_3s"],
                "on_screen_text_720x1200": hook_variants[0]["safe_zone_text_720x1200"],
                "spoken_audio_vo": hook_variants[0]["spoken_line_0_3s"],
                "cut_pacing": "1.0 soniyada kadr almashishi; 1-freymda harakat",
            },
            {
                "timecode": "00:03 - 00:09",
                "scene_role": "2. MUAMMO VA OG'RIQ (Problem & Agitation)",
                "visual_and_camera": f"B-Roll: eski usuldagi qiyinchilik ({clean_prob}) va mijoz yo'qotayotgan vaqt/pul tasviri.",
                "on_screen_text_720x1200": f"Asosiy muammo: {clean_prob[:28]}",
                "spoken_audio_vo": f"Agar sizni ham '{clean_prob}' qiynayotgan bo'lsa, oddiy va'dalar emas, tizimli yechim kerak.",
                "cut_pacing": "Har 1.5 soniyada jump-cut; salomlashish ('Assalomu alaykum do'stlar') kesib tashlanadi",
            },
            {
                "timecode": "00:09 - 00:18",
                "scene_role": "3. NOYOB MEXANIZM VA JONLI DEMO (Mechanism & Proof)",
                "visual_and_camera": f"3-Capture B-Roll: {clean_prod} ishlash jarayoni 3 xil rakursdan yaqin planda ko'rsatiladi.",
                "on_screen_text_720x1200": f"{clean_prod[:26]} qanday ishlaydi?",
                "spoken_audio_vo": f"{clean_prod} aynan sababni bartaraf etadi: jarayon oddiy, shaffof va birinchi kundan seziladi.",
                "cut_pacing": "Har 1.5–2.0 soniyada vizual dalil almashadi",
            },
            {
                "timecode": "00:18 - 00:25",
                "scene_role": "4. ISBOT VA NARX ANKORI (Social Proof & BNPL Anchor)",
                "visual_and_camera": "Real mijozlar natijasi / sharhi + bo'lib to'lash va kafolat jadvali.",
                "on_screen_text_720x1200": bnpl_anchor[:48],
                "spoken_audio_vo": f"Yuzlab mijozlarimiz natijasini shartnoma va kafolat bilan tasdiqlaymiz. To'lov sharti: {bnpl_anchor}.",
                "cut_pacing": "720x1200 markaziy zonada narx/nasiya plankasi",
            },
            {
                "timecode": "00:25 - 00:30",
                "scene_role": "5. ANIQ HARAKATGA CHAQIRUV (Direct CTA)",
                "visual_and_camera": "Spiker pastdagi tugmaga ishora qiladi + Telegram bot / forma ekrani ko'rinadi.",
                "on_screen_text_720x1200": "Pastdagi tugmani bosing yoki '+' qoldiring",
                "spoken_audio_vo": f"Hoziroq pastdagi tugmani bosing yoki izohda '+' qoldiring, sizga {clean_prod} bo'yicha bepul hisob-kitobni yuboramiz.",
                "cut_pacing": "2 soniya aniq yakuniy karta (End-Card)",
            },
        ]

    return {
        "schema": "tyrion.video_ad_script/v7",
        "niche": niche,
        "product": clean_prod,
        "problem_solved": clean_prob,
        "format": fmt_key,
        "format_metadata": fmt_meta,
        "duration_sec": duration_sec,
        "language": lang_key,
        "market": mat["market"],
        "currency": mat["currency"],
        "price_anchor": bnpl_anchor,
        "production_specs": {
            "canvas_resolution": "1080x1920 (9:16 Vertical)",
            "text_safe_zone": "720x1200 px central box (keep top 250px, bottom 470px, right 200px clear of UI icons)",
            "caption_style": "White fill (#FFFFFF) + 3px black stroke, 3-5 words per line, lower-middle third",
            "audio_loudness": "-14 LUFS integrated, -1 dBTP true peak, zero dead air >0.25s",
            "three_capture_shooting_checklist": [
                "Capture 1 (A-Roll): Shoot all 3 Hook variations (0-3s) + 1 full Body + 2 CTA variations in one setup.",
                "Capture 2 (Mechanism B-Roll): 5-8 close-up clips showing the product/service in real use.",
                "Capture 3 (Proof B-Roll): Real customer result, review screen, packaging/delivery, or clinic/office proof.",
            ],
        },
        "hook_variations_0_3s": hook_variants,
        "storyboard_scenes": scenes,
        "falsifiable_hypothesis": (
            f"In cold TOF prospecting, this {fmt_meta['title']} script (Hook H1 vs H2) will achieve >=28% 3s Hook Rate, "
            f">=14% Hold Rate, and beat static control ads by -18% CPA within the first 2,000 impressions."
        ),
        "ai_tells_check": lint_ai_tells(" ".join(s["spoken_audio_vo"] for s in scenes)),
    }


def build_pda_diversity_plan(
    niche: str = "ecom",
    product: str = "",
    price: float = 100.0,
    market: str = "global",
    currency: str = "",
) -> dict[str, Any]:
    """Builds the 2026 Andromeda Entity-ID & Persona-Desire-Awareness (PDA) Creative Diversity Plan."""
    mat = build_matrix(niche=niche, product=product or "Offer", price=price, market=market, currency=currency)
    clean_prod = product.strip() or f"{niche} offer"

    pda_concepts = [
        {
            "concept_id": "PDA_01",
            "persona": "Value-Conscious Pragmatist (Fast ROI / Budget-Aware Buyer)",
            "desire": "Eliminate wasted money and get predictable cost-per-use",
            "awareness_stage": "Problem-Aware (Schwartz Stage 2)",
            "assigned_format": "ugc_reaction_demo",
            "format_tier": "S",
            "visual_signature_for_unique_entity_id": "Handheld smartphone POV in home/office setting, split-screen cost calculator",
            "core_hook": f"Why 90% of people overpay for {clean_prod} (and the 14-day math that fixes it)",
            "falsifiable_hypothesis": "Beats control static ad on 3s Hook Rate (>=30%) and lowers TOF CPC by >=15% in Broad audience.",
        },
        {
            "concept_id": "PDA_02",
            "persona": "Skeptical Research Buyer (Burned by Past Alternatives)",
            "desire": "Verified proof, transparent mechanism, and contractual guarantee",
            "awareness_stage": "Solution-Aware (Schwartz Stage 3)",
            "assigned_format": "founder_authority",
            "format_tier": "S",
            "visual_signature_for_unique_entity_id": "Founder/Specialist direct-to-camera in workshop/clinic/studio with live whiteboard/prop breakdown",
            "core_hook": f"Do not buy {clean_prod} until you check these 3 quality criteria",
            "falsifiable_hypothesis": "Increases Hold Rate to >=16% and improves Lead-to-Sale CVR by +20% vs UGC baseline.",
        },
        {
            "concept_id": "PDA_03",
            "persona": "Time-Poor Busy Professional / Parent",
            "desire": "Speed, zero-friction setup/delivery, and instant convenience",
            "awareness_stage": "Product-Aware (Schwartz Stage 4)",
            "assigned_format": "no_yapping_split_screen",
            "format_tier": "S",
            "visual_signature_for_unique_entity_id": "Top/Bottom 50-50 split screen with live timer overlay and rapid 1.0s cuts",
            "core_hook": f"Watch {clean_prod} go from order to full result in 20 seconds (zero filler)",
            "falsifiable_hypothesis": "Achieves highest Outbound CTR (>=1.8%) among busy urban 25-44 cohort.",
        },
        {
            "concept_id": "PDA_04",
            "persona": "Social-Proof & Peer-Driven Buyer",
            "desire": "Status, peer validation, and discovering what insiders use",
            "awareness_stage": "Unaware / Curiosity-Driven (Schwartz Stage 1)",
            "assigned_format": "imessage_reveal",
            "format_tier": "A",
            "visual_signature_for_unique_entity_id": "iOS/Telegram native dark-mode chat thread unfolding with notification sound",
            "core_hook": f"'Wait, how did you fix that so fast?' — The {clean_prod} thread everyone is screenshotting",
            "falsifiable_hypothesis": "Generates +25% lower CPM and higher thumbstop on Instagram Reels placement vs talking-head.",
        },
        {
            "concept_id": "PDA_05",
            "persona": "Analytical Comparison Shopper",
            "desire": "Side-by-side feature, durability, and price-to-value superiority",
            "awareness_stage": "Solution-Aware (Schwartz Stage 3)",
            "assigned_format": "chatgpt_reveal",
            "format_tier": "A",
            "visual_signature_for_unique_entity_id": "Screen capture of AI comparison prompt + hard cut to physical side-by-side Us vs Them card",
            "core_hook": f"We compared {clean_prod} against the 3 leading alternatives on 5 hard metrics",
            "falsifiable_hypothesis": "Drives +18% higher landing page CVR among high-AOV comparison shoppers.",
        },
        {
            "concept_id": "PDA_06",
            "persona": "Price-Sensitive / Payment-Plan Buyer (BOF Fence-Sitter)",
            "desire": "Low monthly commitment via BNPL and zero-risk trial/warranty",
            "awareness_stage": "Most Aware (Schwartz Stage 5 — Objection Crusher)",
            "assigned_format": "greenscreen_proof",
            "format_tier": "A",
            "visual_signature_for_unique_entity_id": "Creator in front of real customer price comment + highlighted installment breakdown sheet",
            "core_hook": f"Replying to @client: 'Is {clean_prod} worth the price?' Here is the exact installment breakdown ({mat['price_anchor']})",
            "falsifiable_hypothesis": "Reduces BOF Retargeting CPA by >=22% among 14-day website/IG engagers.",
        },
    ]

    return {
        "schema": "tyrion.pda_creative_diversity/v7",
        "niche": niche,
        "product": clean_prod,
        "market": mat["market"],
        "currency": mat["currency"],
        "formatted_price": mat["formatted_price"],
        "price_anchor": mat["price_anchor"],
        "andromeda_entity_id_explanation": (
            "Meta's Andromeda retrieval engine clusters visually similar creatives under a single Entity ID (1 retrieval ticket). "
            "Uploading 20 text variations on the same video gives you 1 ticket. This 6-concept PDA portfolio varies Persona + Desire + "
            "Awareness Stage + Visual Format so Andromeda assigns 6 independent retrieval tickets across the auction."
        ),
        "pda_concepts": pda_concepts,
        "matrix_3x3": mat["matrix_3x3"],
    }


PLATFORM_LIMITS: dict[str, dict[str, int]] = {
    "meta": {"primary_text_visible": 125, "primary_text_max": 2200, "headline": 40, "description": 30},
    "google_rsa": {"headline": 30, "description": 90, "path": 15},
    "tiktok": {"ad_text": 80, "ad_text_max": 100, "display_name": 40},
    "linkedin": {"intro_text": 150, "headline": 70, "description": 100},
    "telegram": {"sponsored_text": 160, "button_text": 20},
}


def generate_ad_copy_pack(
    platform: str = "meta",
    product: str = "",
    problem: str = "",
    proof: str = "",
    language: str = "uz_latin",
    market: str = "global",
    price: float = 100.0,
    currency: str = "",
) -> dict[str, Any]:
    """Generates character-validated ad copy variations across angles with automatic No-AI-Tells linting."""
    plat = platform.strip().lower()
    if plat not in PLATFORM_LIMITS:
        plat = "meta"
    limits = PLATFORM_LIMITS[plat]
    mat = build_matrix(niche="ecom", product=product or "Offer", price=price, market=market, currency=currency)
    clean_prod = product.strip() or "Mahsulot"
    clean_prob = problem.strip() or "ortiqcha vaqt va byudjet sarfi"
    clean_proof = proof.strip() or "tasdiqlangan mijozlar natijasi"

    is_ru = language.startswith("ru")
    is_en = language.startswith("en")

    if is_ru:
        variations = [
            {
                "angle": "Pain Point / Costly Mistake",
                "headline": f"{clean_prod[:22]}: результат за 14 дней"[: limits.get("headline", 40)],
                "primary_text": f"Устали терять время из-за проблемы «{clean_prob}»? {clean_prod} решает задачу по договору. {clean_proof}. {mat['price_anchor']}.",
                "description": f"Гарантия по договору"[: limits.get("description", 30)],
            },
            {
                "angle": "Quantified Social Proof",
                "headline": f"{clean_prod[:20]} ({clean_proof[:14]})"[: limits.get("headline", 40)],
                "primary_text": f"{clean_proof} уже выбрали {clean_prod} вместо долгих экспериментов. Прозрачный расчет за 2 минуты.",
                "description": f"Рассрочка 0% без переплат"[: limits.get("description", 30)],
            },
            {
                "angle": "Mechanism & Direct Offer",
                "headline": f"Расчет {clean_prod[:20]} за 2 мин"[: limits.get("headline", 40)],
                "primary_text": f"Получите готовое решение {clean_prod} с фиксированной сметой и гарантией. {mat['price_anchor']}.",
                "description": f"Оставьте заявку сейчас"[: limits.get("description", 30)],
            },
        ]
    elif is_en:
        variations = [
            {
                "angle": "Pain Point / Costly Mistake",
                "headline": f"Fix {clean_prob[:20]} in 14 Days"[: limits.get("headline", 40)],
                "primary_text": f"Spending hours on {clean_prob}? {clean_prod} automates the workflow with verified accuracy ({clean_proof}). {mat['price_anchor']}.",
                "description": f"Verified {clean_proof[:18]}"[: limits.get("description", 30)],
            },
            {
                "angle": "Quantified Social Proof",
                "headline": f"{clean_prod[:22]} ({clean_proof[:12]})"[: limits.get("headline", 40)],
                "primary_text": f"See why {clean_proof} switched to {clean_prod} to eliminate {clean_prob}. Clear pricing, fast onboarding.",
                "description": f"Risk-free guarantee"[: limits.get("description", 30)],
            },
            {
                "angle": "Mechanism & Direct Offer",
                "headline": f"Get {clean_prod[:22]} Today"[: limits.get("headline", 40)],
                "primary_text": f"Built for teams that want measurable ROI on {clean_prod}. {mat['price_anchor']}.",
                "description": f"Start in 2 minutes"[: limits.get("description", 30)],
            },
        ]
    else:
        variations = [
            {
                "angle": "Og'riq va Xato (Pain Point)",
                "headline": f"{clean_prod[:22]}: 14 kunda natija"[: limits.get("headline", 40)],
                "primary_text": f"'{clean_prob}' muammosi vaqtingizni olyaptimi? {clean_prod} orqali aniq yechimga chiqing ({clean_proof}). {mat['price_anchor']}.",
                "description": f"Shartnoma asosida kafolat"[: limits.get("description", 30)],
            },
            {
                "angle": "Aniq Isbot va Keys (Social Proof)",
                "headline": f"{clean_prod[:20]} ({clean_proof[:14]})"[: limits.get("headline", 40)],
                "primary_text": f"{clean_proof} tajribasida sinovdan o'tgan {clean_prod}. Yashirin to'lovlarsiz, aniq smeta va muddat.",
                "description": f"Bepul hisob-kitob oling"[: limits.get("description", 30)],
            },
            {
                "angle": "Noyob Mexanizm va Nasiya (Offer Anchor)",
                "headline": f"{clean_prod[:22]}: qulay to'lov"[: limits.get("headline", 40)],
                "primary_text": f"{clean_prod} bilan '{clean_prob}' muammosini ortiqcha xarajatsiz hal qiling. {mat['price_anchor']}.",
                "description": f"Hoziroq '+' qoldiring"[: limits.get("description", 30)],
            },
        ]

    validated_variations: list[dict[str, Any]] = []
    for idx, var in enumerate(variations, 1):
        lint_h = lint_ai_tells(var["headline"])
        lint_p = lint_ai_tells(var["primary_text"])
        lint_d = lint_ai_tells(var["description"])
        h_clean = lint_h["cleaned_text"]
        p_clean = lint_p["cleaned_text"]
        d_clean = lint_d["cleaned_text"]
        if plat == "telegram":
            p_clean = p_clean[:160]
        validated_variations.append({
            "variation_id": f"V{idx:02d}",
            "angle": var["angle"],
            "headline": h_clean,
            "headline_chars": len(h_clean),
            "headline_limit": limits.get("headline", 40),
            "primary_text": p_clean,
            "primary_text_chars": len(p_clean),
            "primary_text_visible_hook_125": p_clean[:125],
            "description": d_clean,
            "description_chars": len(d_clean),
            "description_limit": limits.get("description", 30),
            "within_platform_limits": len(h_clean) <= limits.get("headline", 200) and len(d_clean) <= limits.get("description", 300),
            "ai_tells_detected": lint_h["issues_count"] + lint_p["issues_count"] + lint_d["issues_count"],
            "falsifiable_hypothesis": f"Variation V{idx:02d} ({var['angle']}) will beat control copy on Outbound CTR by +12% within 1,500 impressions.",
        })

    return {
        "schema": "tyrion.ad_copy_pack/v7",
        "platform": plat,
        "platform_character_limits": limits,
        "product": clean_prod,
        "problem": clean_prob,
        "proof": clean_proof,
        "language": language,
        "market": mat["market"],
        "currency": mat["currency"],
        "price_anchor": mat["price_anchor"],
        "variations": validated_variations,
    }


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
        actions.append(
            f"Hook Rate low ({hook_rate:.1f}% < 25%): Keep body intact and test 3 new visual + verbal 3-second hooks "
            "(Note: under Andromeda Entity ID rules, change the opening visual setting/creator, not just the text caption!)."
        )
    if hold_rate < 12.0:
        if status == "HEALTHY_CREATIVE":
            status = "WEAK_BODY_RETENTION"
        actions.append(
            f"Hold Rate low ({hold_rate:.1f}% < 12%): Cut intro filler between seconds 4-10, pace visual cuts every 1.0-2.0s, "
            "and ensure the video delivers on the hook's promise so Meta's UTIS (User True Interest Survey) score stays high."
        )
    if ctr_drop_pct >= 25.0 or frequency >= 2.8 or ftir < 55.0:
        status = "CREATIVE_FATIGUED"
        actions.append(
            f"Creative fatigued (CTR drop={ctr_drop_pct:.1f}%, Frequency={frequency:.2f}, FTIR={ftir:.1f}%): "
            "Rotate to a fresh Persona-Desire-Awareness (PDA) angle and a new visual format (e.g. Founder -> iMessage Reveal or Partnership Ad) to earn a new Andromeda Entity ID."
        )
    if not actions:
        actions.append("Creative metrics healthy (Hook >=25%, Hold >=12%, FTIR >=55%) — scale horizontally via 'More/Better/New' PDA variations.")

    return {
        "status": status,
        "metrics": {
            "hook_rate_pct": hook_rate,
            "hold_rate_pct": hold_rate,
            "ctr_drop_pct": ctr_drop_pct,
            "frequency": frequency,
            "ftir_pct": ftir,
        },
        "andromeda_utis_note": (
            "Meta's 2026 UTIS (User True Interest Survey) model penalizes clickbait hooks that get high 3s views but low genuine satisfaction; "
            "always match the 0-3s hook directly to the 3-15s mechanism demo."
        ),
        "prescribed_actions": actions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="creative-matrix.py", description="Tyrion v7.0 Global Creative Matrix, Video Script & Ad Copy Engine")
    sub = parser.add_subparsers(dest="command", required=True)

    p_mat = sub.add_parser("matrix", help="3x3 Angle x Format creative testing matrix with market BNPL anchor & falsifiable hypotheses")
    p_mat.add_argument("--niche", default="ecom")
    p_mat.add_argument("--product", required=True)
    p_mat.add_argument("--price", type=float, default=100.0)
    p_mat.add_argument("--market", default="global", help="Market pack (global, uz, us, eu, uk, mena, latam, sea, in)")
    p_mat.add_argument("--currency", default="", help="ISO 4217 currency override (USD, EUR, GBP, JPY, UZS, etc.)")
    p_mat.add_argument("--json", action="store_true")

    p_hk = sub.add_parser("hooks", help="Multilingual 3-second Hook generator (any BCP 47 language)")
    p_hk.add_argument("--niche", default="ecom")
    p_hk.add_argument("--offer", required=True)
    p_hk.add_argument("--languages", default="", help="Comma-separated BCP 47 language codes (e.g. en,de,fr,ar,uz_latin,ru)")
    p_hk.add_argument("--json", action="store_true")

    p_fat = sub.add_parser("fatigue", help="Creative fatigue diagnostics via Hook Rate, Hold Rate, FTIR & UTIS")
    p_fat.add_argument("--hook-rate", type=float, required=True)
    p_fat.add_argument("--hold-rate", type=float, required=True)
    p_fat.add_argument("--ctr-drop-pct", type=float, default=0.0)
    p_fat.add_argument("--frequency", type=float, default=1.5)
    p_fat.add_argument("--ftir", type=float, default=70.0)
    p_fat.add_argument("--json", action="store_true")

    p_vid = sub.add_parser("video-script", help="Ready-to-shoot 9:16 video ad script & scene-by-scene storyboard (720x1200 safe zone)")
    p_vid.add_argument("--niche", default="ecom")
    p_vid.add_argument("--product", required=True, help="Product, service, or offer")
    p_vid.add_argument("--problem", default="", help="Main customer problem or pain point")
    p_vid.add_argument("--format", dest="format_name", default="ugc_reaction_demo", choices=list(META_FORMAT_TAXONOMY.keys()))
    p_vid.add_argument("--duration", type=int, default=30, help="Target video duration in seconds (default: 30)")
    p_vid.add_argument("--price", type=float, default=100.0)
    p_vid.add_argument("--market", default="global")
    p_vid.add_argument("--currency", default="")
    p_vid.add_argument("--language", default="uz_latin")
    p_vid.add_argument("--json", action="store_true")

    p_pda = sub.add_parser("pda-matrix", help="Andromeda Entity-ID & Persona-Desire-Awareness (PDA) Creative Diversity Plan")
    p_pda.add_argument("--niche", default="ecom")
    p_pda.add_argument("--product", required=True)
    p_pda.add_argument("--price", type=float, default=100.0)
    p_pda.add_argument("--market", default="global")
    p_pda.add_argument("--currency", default="")
    p_pda.add_argument("--json", action="store_true")

    p_copy = sub.add_parser("ad-copy", help="Platform-validated ad copy generator with automatic No-AI-Tells linter")
    p_copy.add_argument("--platform", default="meta", choices=list(PLATFORM_LIMITS.keys()))
    p_copy.add_argument("--product", required=True)
    p_copy.add_argument("--problem", default="")
    p_copy.add_argument("--proof", default="")
    p_copy.add_argument("--language", default="uz_latin")
    p_copy.add_argument("--market", default="global")
    p_copy.add_argument("--price", type=float, default=100.0)
    p_copy.add_argument("--currency", default="")
    p_copy.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "matrix":
        res = build_matrix(args.niche, args.product, args.price, market=args.market, currency=args.currency)
    elif args.command == "hooks":
        langs = [x.strip() for x in args.languages.split(",") if x.strip()] if args.languages else None
        res = generate_hooks(args.niche, args.offer, languages=langs)
    elif args.command == "fatigue":
        res = analyze_fatigue(args.hook_rate, args.hold_rate, args.ctr_drop_pct, args.frequency, args.ftir)
    elif args.command == "video-script":
        res = generate_video_script(
            niche=args.niche, product=args.product, problem=args.problem,
            format_name=args.format_name, duration_sec=args.duration,
            price=args.price, market=args.market, currency=args.currency, language=args.language,
        )
    elif args.command == "pda-matrix":
        res = build_pda_diversity_plan(
            niche=args.niche, product=args.product, price=args.price, market=args.market, currency=args.currency,
        )
    elif args.command == "ad-copy":
        res = generate_ad_copy_pack(
            platform=args.platform, product=args.product, problem=args.problem,
            proof=args.proof, language=args.language, market=args.market, price=args.price, currency=args.currency,
        )
    else:
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 72)
    print(f"  🎨 TYRION v7.0 CREATIVE & VIDEO STUDIO — {args.command.upper()}")
    print("=" * 72)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
