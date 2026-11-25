#!/usr/bin/env python3
"""Tyrion v8.2 Creative Matrix, Video Ad Scripting, Andromeda PDA Diversity & Ad Copy Engine (`tools/creative-matrix.py`).

Commands:
  python3 tools/creative-matrix.py matrix --niche ecom --product "Klassik kostyum" --price 150 [--market uz] [--currency USD] [--json]
  python3 tools/creative-matrix.py hooks --niche edtech --offer "IELTS 7.0 3 oyda" [--languages uz_latin,ru,en] [--json]
  python3 tools/creative-matrix.py fatigue --hook-rate 22.0 --hold-rate 9.5 --ctr-drop-pct 35.0 --frequency 2.9 --ftir 52.0 [--json]
  python3 tools/creative-matrix.py video-script --niche medical --product "Tish implantatsiyasi" --problem "Tish yo'qotilishi" --format ugc_reaction_demo --language uz_latin [--json]
  python3 tools/creative-matrix.py video-script --mode sales|organic|plan|motion --lang uz|ru|en --duration 15|30|45|60 --hooks 3 --product "..." [--json]   # video pre-production skeletlari
  python3 tools/creative-matrix.py pda-matrix --niche ecom --product "Espresso Machine" --price 300 --market eu --currency EUR [--json]
  python3 tools/creative-matrix.py ad-copy --platform meta --product "CRM Avtomatlashtirish" --problem "Lidlar yo'qolishi" --proof "300+ kompaniya" --language uz_latin [--json]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

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


UNVERIFIED_CLAIM_PATTERNS = [
    (re.compile(r"\b\d{1,3}\s?%"), "NUMERIC_PERCENT", "Foiz/statistika: faqat tasdiqlangan manba bo'lsa qoldiring."),
    (re.compile(r"\b\d+\s?(kun|day|days|дн|дней)\b", re.I), "TIMEFRAME_PROMISE", "Muddat va'dasi: haqiqiy natija/shartnoma bo'lsa qoldiring."),
    (re.compile(r"\b(\d+\s?tadan\s?\d+|\d+ out of \d+|\d+ из \d+)\b", re.I), "RATIO_STAT", "Nisbiy statistika: manbasiz ishlatmang."),
    (re.compile(r"\b(kafolat|guarantee|гаранти)", re.I), "GUARANTEE_CLAIM", "Kafolat: faqat mijoz tasdiqlagan shartlar bilan."),
    (re.compile(r"\b(#1|eng yaxshi|best|лучший|number one)\b", re.I), "SUPERLATIVE", "Superlativ: dalilsiz ishlatmang."),
]


def lint_unverified_claims(payload: Any) -> dict[str, Any]:
    """Skriptdagi tasdiqlanmagan raqam/kafolat/superlativlarni topadi. [ ] ichidagi to'ldirish joylari (placeholder) hisobga olinmaydi."""
    skip = {"self_audit_checklist", "funnel_mix", "falsifiable_hypothesis", "andromeda_rule", "production_specs", "andromeda_utis_note", "claim_safety", "test_thresholds_note"}

    def _prune(o: Any) -> Any:
        if isinstance(o, dict):
            return {k: _prune(v) for k, v in o.items() if k not in skip}
        if isinstance(o, list):
            return [_prune(v) for v in o]
        return o

    text = json.dumps(_prune(payload), ensure_ascii=False)
    text = re.sub(r"\[[^\]]{3,120}\]", " ", text)  # placeholderlar
    findings: list[dict[str, str]] = []
    for pat, code, advice in UNVERIFIED_CLAIM_PATTERNS:
        hits = sorted({m.group(0) for m in pat.finditer(text)})
        if hits:
            findings.append({"code": code, "matches": hits[:6], "advice": advice})
    return {
        "rule": "00-manba: manbasiz fakt yo'q",
        "needs_verification": bool(findings),
        "findings": findings,
        "placeholders_present": bool(re.search(r"\[(HAQIQIY|NARX|ADD VERIFIED|ТАСДИҚ|ВСТАВЬТЕ|INSERT|INSERIR|INSÉRER|INSERTAR|أدخل|VERIFIZIERT)", json.dumps(payload, ensure_ascii=False))),
    }


def build_matrix(
    niche: str,
    product: str,
    price: float | None = None,
    market: str = "global",
    currency: str = "",
) -> dict:
    pack = mloc.load_market_pack(market)
    m_id = pack["market_id"]
    curr = (currency or pack.get("default_currency") or "USD").strip().upper()
    bnpl_list = pack.get("bnpl_providers") or ["Klarna", "Afterpay"]
    primary_bnpl = bnpl_list[0]
    template = pack.get("price_anchor_template") or "Or 4 interest-free payments of {installment} with {bnpl}"

    price_known = price is not None and price > 0
    if not price_known:
        inst_str = ""
        bnpl_anchor = "[NARX KIRITILMAGAN: haqiqiy narxni --price bilan bering; taksit/BNPL anchor hisoblanmadi]"
        cta_str = "Telegram Bot / Instagram DM yoki sayt formasi (kanalni mijoz bilan tasdiqlang)"
        price = 0.0
    elif m_id == "uz" and curr in ("UZS", "USD"):
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
        "price": rounded_price if price_known else None,
        "price_usd": rounded_price if price_known else None,
        "price_known": price_known,
        "formatted_price": mloc.format_currency(price, curr) if price_known else "[narx kiritilmagan]",
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
        "[Curiosity Gap] The one counter-intuitive thing most buyers of {offer} only learn after paying...",
        "[Pain / Costly Mistake] Stop wasting budget on the old way - here is how {offer} fixes it:",
        "[Quantified Proof] [ADD VERIFIED RESULT + TIMEFRAME] How {offer} delivered it without extra overhead",
        "[Qualifier Hook] Attention: this is only for teams serious about scaling {offer} profitably.",
    ],
    "de": [
        "[Neugier / Fokus] Die eine Sache über {offer}, die viele Käufer erst nach dem Kauf erfahren...",
        "[Fehler vermeiden] Warum die klassische Methode unnötig Budget verbrennt - und wie {offer} das löst:",
        "[Zahlen & Beweis] [VERIFIZIERTES ERGEBNIS + ZEITRAUM EINSETZEN] ({offer})",
    ],
    "fr": [
        "[Curiosité] Ce que beaucoup d'acheteurs de {offer} découvrent trop tard...",
        "[Erreur coûteuse] Arrêtez de perdre du budget avec l'ancienne méthode : découvrez {offer}.",
        "[Preuve chiffrée] [INSÉRER RÉSULTAT VÉRIFIÉ + DÉLAI] ({offer})",
    ],
    "es": [
        "[Curiosidad] Lo que muchos compradores de {offer} descubren demasiado tarde...",
        "[Error Costoso] Deja de perder presupuesto con el método tradicional: así funciona {offer}.",
        "[Prueba Real] [INSERTAR RESULTADO VERIFICADO + PLAZO] ({offer})",
    ],
    "pt-BR": [
        "[Curiosidade] O que muitos compradores de {offer} só descobrem tarde demais...",
        "[Erro Caro] Pare de queimar verba do jeito antigo: veja como {offer} resolve isso.",
        "[Prova Real] [INSERIR RESULTADO VERIFICADO + PRAZO] ({offer})",
    ],
    "ar": [
        "[فضول / فجوة معرفية] أمر واحد عن {offer} يكتشفه كثير من المشترين متأخراً...",
        "[خطأ مكلف] توقف عن إهدار الميزانية بالطريقة القديمة - إليك الحل مع {offer}:",
        "[دليل رقمي] [أدخل نتيجة موثقة + المدة] ({offer})",
    ],
    "uz_latin": [
        "[Qiziqish/Bo'shliq] {offer} xaridorlari ko'pincha to'lovdan keyingina bilib oladigan 1 ta amaliy holat...",
        "[Xato/Og'riq] Agar hali ham eski usulda harakat qilayotgan bo'lsangiz, vaqt va pul yo'qotyapsiz: {offer}",
        "[Aniq Raqam/Isbot] [HAQIQIY NATIJA + MUDDATNI KIRITING] {offer} ortiqcha xarajatsiz qanday natija berdi?",
        "[Filtr-Hook] Diqqat: bu video faqat shartlari aniq, shaffof xizmat izlayotganlar uchun ({offer})",
    ],
    "uz_cyrillic": [
        "[Қизиқиш] {offer} харидорлари кўпинча тўловдан кейингина билиб оладиган 1 та амалий ҳолат...",
        "[Хато/Оғриқ] Пулингизни бефойда тажрибаларга сарфлашни тўхтатинг: {offer}",
        "[Исбот] [ТАСДИҚЛАНГАН КАФОЛАТ ШАРТИНИ КИРИТИНГ] {offer}",
    ],
    "ru": [
        "[Проблема/Ошибка] 3 главные ошибки при выборе, из-за которых вы теряете время и бюджет ({offer})",
        "[Цифры/Кейс] [ВСТАВЬТЕ ПРОВЕРЕННЫЙ РЕЗУЛЬТАТ И СРОК] {offer}",
        "[Фильтр-Хук] Только для тех, кому важны прозрачные условия: {offer}",
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
    price: float | None = None,
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
                "spoken_line_0_3s": f"Here is how {clean_prod} solves {clean_prob}. [ADD VERIFIED RESULT AND TIMEFRAME HERE]",
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
                "visual_action_0_3s": f"Yaqin plan (Macro): '{clean_prob}' muammosini jonli ko'rsatish -> 1 soniyada {clean_prod} yechimiga keskin o'tish (hard cut).",
                "safe_zone_text_720x1200": f"{clean_prod[:24]}: eng ko'p uchraydigan xato",
                "spoken_line_0_3s": f"{clean_prod} tanlashda aynan shu xato ko'pchilikning pul va vaqtini oladi. Bu xatoni birinchi bo'lib ko'rsataman.",
            },
            {
                "hook_id": "H2_QUANTIFIED_PROOF",
                "visual_action_0_3s": f"Ikki ekran (Split-Screen): tepada {clean_prod} real jarayoni, pastda mijozning HAQIQIY raqamli natijasi (manba: o'zingizning ma'lumotingiz; yo'q bo'lsa bu hookni ishlatmang).",
                "safe_zone_text_720x1200": f"[HAQIQIY NATIJA]: {clean_prod[:20]}",
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
                "spoken_audio_vo": f"{clean_prod} aynan sababni bartaraf etadi: jarayonni qadam-baqadam ko'rsataman. [HAQIQIY MEXANIZMNI 1 JUMLADA YOZING]",
                "cut_pacing": "Har 1.5–2.0 soniyada vizual dalil almashadi",
            },
            {
                "timecode": "00:18 - 00:25",
                "scene_role": "4. ISBOT VA NARX ANKORI (Social Proof & BNPL Anchor)",
                "visual_and_camera": "Real mijozlar natijasi / sharhi + bo'lib to'lash va kafolat jadvali.",
                "on_screen_text_720x1200": bnpl_anchor[:48],
                "spoken_audio_vo": f"[MIJOZ TASDIQLAGAN ISBOTNI KIRITING: sharh, natija yoki shartnoma sharti]. To'lov sharti: {bnpl_anchor}.",
                "cut_pacing": "720x1200 markaziy zonada narx/nasiya plankasi",
            },
            {
                "timecode": "00:25 - 00:30",
                "scene_role": "5. ANIQ HARAKATGA CHAQIRUV (Direct CTA)",
                "visual_and_camera": "Spiker pastdagi tugmaga ishora qiladi + Telegram bot / forma ekrani ko'rinadi.",
                "on_screen_text_720x1200": "Pastdagi tugmani bosing yoki '+' qoldiring",
                "spoken_audio_vo": f"Hoziroq pastdagi tugmani bosing yoki izohda '+' qoldiring, [TAKLIF: faqat haqiqatan bor bo'lsa, masalan konsultatsiya yoki hisob-kitob] - {clean_prod} bo'yicha yozing.",
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
    price: float | None = None,
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
            "core_hook": f"Why people overpay for {clean_prod} (show your real cost comparison)",
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
    price: float | None = None,
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
                "headline": f"{clean_prod[:22]}: aniq yechim"[: limits.get("headline", 40)],
                "primary_text": f"'{clean_prob}' muammosi vaqtingizni olyaptimi? {clean_prod} orqali aniq yechimga chiqing ({clean_proof}). {mat['price_anchor']}.",
                "description": f"Shartlar oldindan aytiladi"[: limits.get("description", 30)],
            },
            {
                "angle": "Aniq Isbot va Keys (Social Proof)",
                "headline": f"{clean_prod[:20]} ({clean_proof[:14]})"[: limits.get("headline", 40)],
                "primary_text": f"{clean_proof} tajribasida sinovdan o'tgan {clean_prod}. Narx va shartlar oldindan aniq aytiladi (tasdiqlangan shartlarni kiriting).",
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


# Priors faqat baseline berilmaganda ishlatiladi va HEURISTIC_PRIOR_MODEL deb belgilanadi (akkaunt tarixi bilan almashtiring).
_ITER_PRIORS = {"hook_rate": 25.0, "hold_rate": 12.0}
_ITER_STAGES = [
    # (metric, stage, hypothesis, change, keep)
    ("hook_rate", "ATTENTION",
     "Birinchi kadr/hook e'tiborni ushlamayapti (gipoteza).",
     "Faqat ochilish 0-3s: birinchi kadr, ekrandagi matn, birinchi gap, kamera. 3 ta moddiy farqli hook.",
     "Tana (mexanizm, isbot), taklif, CTA, davomiylik."),
    ("hold_rate", "RETENTION",
     "Hook ishlaydi, lekin tana va hikoya tomoshabinni ushlab turmayapti (gipoteza).",
     "Tana: tempo (kesish chastotasi), mexanizm ko'rsatish tartibi, filler 4-10s, isbotni erta joylash.",
     "Ishlayotgan hook, taklif, CTA."),
    ("outbound_ctr", "CLICK",
     "Ko'rishlar yaxshi, lekin klik yo'q: taklif, CTA yoki isbot yetarli emas (gipoteza).",
     "CTA aniqligi, taklif ifodasi, isbot joylashuvi, primary text/headline.",
     "Hook va tana strukturasi."),
    ("lp_cvr", "LANDING",
     "Klik bor, lekin sahifa/forma konvertatsiya qilmayapti: message match, taklif yoki tezlik (gipoteza).",
     "Reklama va sahifa xabari mosligi, birinchi ekran, forma uzunligi, yuklanish tezligi. Kreativni EMAS, sahifani sinang.",
     "Ishlayotgan kreativ."),
    ("qualified_lead_rate", "LEAD_QUALITY",
     "Lidlar arzon, lekin sifatsiz: kvalifikatsiya, auditoriya mosligi yoki savdo ishlovi (gipoteza).",
     "Kreativda aniq filtr (narx/shart/kim uchun), forma savollari, auditoriya signali, CRM feedback (CAPI offline event). Savdo ishlovini tekshiring.",
     "Hajm beruvchi hook."),
]


def diagnose_creative_iteration(
    metrics: dict[str, float | None],
    baselines: dict[str, float | None] | None = None,
    cpa: float | None = None,
    breakeven_cpa: float | None = None,
    impressions: int | None = None,
    min_impressions: int = 1000,
) -> dict[str, Any]:
    """Real ko'rsatkichlardan KETMA-KET (voronka bo'yicha) diagnostik GIPOTEZALAR. Avtomatik xulosa emas; baseline akkauntniki bo'lishi kerak."""
    baselines = baselines or {}
    findings: list[dict[str, Any]] = []
    used_priors: list[str] = []
    for metric, stage, hyp, change, keep in _ITER_STAGES:
        val = metrics.get(metric)
        if val is None:
            continue
        base = baselines.get(metric)
        base_src = "ACCOUNT_BASELINE"
        if base is None and metric in _ITER_PRIORS:
            base, base_src = _ITER_PRIORS[metric], "HEURISTIC_PRIOR_MODEL"
            used_priors.append(metric)
        if base is None or base <= 0:
            findings.append({"stage": stage, "metric": metric, "value": val, "status": "NO_BASELINE",
                             "note": f"{metric} uchun akkaunt baseline yo'q: o'z kreativlaringiz o'rtachasi bilan solishtiring (--baseline-{metric.replace('_', '-')})."})
            continue
        ratio = val / base
        status = "BELOW" if ratio < 0.85 else ("ABOVE" if ratio > 1.15 else "NEAR")
        row: dict[str, Any] = {"stage": stage, "metric": metric, "value": val, "baseline": base, "baseline_source": base_src,
                               "ratio_to_baseline": round(ratio, 2), "status": status}
        if status == "BELOW":
            row.update({"hypothesis": hyp, "change_next": change, "keep_constant": keep})
        findings.append(row)

    below = [f for f in findings if f["status"] == "BELOW"]
    primary = below[0] if below else None  # eng yuqori (voronkada birinchi) yo'qotish: avval shuni tuzating
    econ: dict[str, Any] = {}
    if cpa is not None and breakeven_cpa is not None and breakeven_cpa > 0:
        econ = {"cpa": cpa, "breakeven_cpa": breakeven_cpa, "above_breakeven": cpa > breakeven_cpa,
                "note": "CPA break-even'dan yuqori bo'lsa ham, avval yo'qotish bosqichini toping; kreativ faqat bitta sabab."}
    warnings = []
    if impressions is not None and impressions < min_impressions:
        warnings.append(f"Namuna kichik ({impressions} < {min_impressions} impression): xulosa ishonchsiz, ko'proq ma'lumot yig'ing.")
    if used_priors:
        warnings.append(f"{', '.join(used_priors)} uchun akkaunt baseline berilmadi: HEURISTIC_PRIOR_MODEL ishlatildi; o'z baseline'ingizni bering.")
    if not findings:
        warnings.append("Hech qanday ko'rsatkich berilmadi.")
    return {
        "schema": "tyrion.creative_iteration/v1",
        "nature": "DIAGNOSTIC_HYPOTHESES (avtomatik xulosa emas)",
        "findings": findings,
        "priority_fix": None if not primary else {
            "stage": primary["stage"], "hypothesis": primary["hypothesis"],
            "change_next": primary["change_next"], "keep_constant": primary["keep_constant"],
            "test_design": "Bitta o'zgaruvchi: faqat shu bosqich o'zgaradi; qolgani doimiy. Qaror mezonini oldindan yozing.",
        },
        "economics": econ,
        "rules": [
            "Kosmetik resize/qayta-sarlavha yangi konsept emas (Andromeda Entity ID bir xil).",
            "Yangi konsept: avatar, muammo, angle yoki format materiel farq qilsin.",
            "Qarorni CPA/ROAS va CRM lid sifati bilan tasdiqlang, faqat hook rate bilan emas.",
        ],
        "warnings": warnings,
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



def _load_metrics_rows(path: str | Path) -> list[dict]:
    """`--metrics`: tools/normalize.py (metrics.v1) orqali yuklaydi; xato bo'lsa ValueError."""
    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location("_tyrion_normalize", Path(__file__).resolve().parent / "normalize.py")
    mod = _ilu.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules.setdefault("_tyrion_normalize", mod)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    try:
        return mod.load_metrics_file(path)
    except Exception as exc:  # NormalizeError va fayl xatolari
        raise ValueError(str(exc)) from exc


def metrics_creative_signals(rows: list[dict], entity_id: str | None = None) -> dict:
    """metrics.v1 dan: hook/hold rate, outbound CTR, CPA, frequency va kunlik CTR trendidan ctr_drop_pct."""
    sel = [r for r in rows if entity_id is None or str(r.get("entity_id")) == str(entity_id)]
    if not sel:
        raise ValueError("metrics.v1 da mos qator yo'q" + (f" (entity_id={entity_id})" if entity_id else ""))
    impr = sum(float(r.get("impressions") or 0) for r in sel)
    v3 = sum(float(r.get("video_3s") or 0) for r in sel)
    tru = sum(float(r.get("thruplay") or 0) for r in sel)
    clk = sum(float(r.get("link_clicks") or r.get("clicks") or 0) for r in sel)
    spend = sum(float(r.get("spend") or 0) for r in sel)
    conv = sum(sum((r.get("conversions") or {}).values()) for r in sel)
    fw = sum(float(r.get("impressions") or 0) for r in sel if r.get("frequency") is not None)
    freq = (sum(float(r["frequency"]) * float(r.get("impressions") or 0) for r in sel if r.get("frequency") is not None) / fw) if fw else None
    by_day: dict[str, list[float]] = {}
    for r in sel:
        d = by_day.setdefault(str(r["date"]), [0.0, 0.0])
        d[0] += float(r.get("impressions") or 0)
        d[1] += float(r.get("link_clicks") or r.get("clicks") or 0)
    days = sorted(by_day)
    ctr_drop = None
    if len(days) >= 4:
        half = len(days) // 2
        def _ctr(ds):
            i = sum(by_day[x][0] for x in ds); c = sum(by_day[x][1] for x in ds)
            return c / i if i else None
        a, b = _ctr(days[:half]), _ctr(days[-half:])
        if a and b is not None:
            ctr_drop = max(0.0, round((a - b) / a * 100, 2))
    return {
        "hook_rate": round(v3 / impr * 100, 2) if impr and v3 else None,
        "hold_rate": round(tru / v3 * 100, 2) if v3 and tru else None,
        "outbound_ctr": round(clk / impr * 100, 2) if impr and clk else None,
        "cpa": round(spend / conv, 2) if conv else None,
        "impressions": int(impr) or None,
        "frequency": round(freq, 2) if freq is not None else None,
        "ctr_drop_pct": ctr_drop, "days": len(days),
        "definitions": "hook=video_3s/impressions; hold=thruplay/video_3s; ctr_drop=(birinchi yarim - oxirgi yarim)/birinchi yarim (kunlik, >=4 kun)",
    }


# ---------------------------------------------------------------------------
# Video pre-production modes: sales | organic | plan | motion  (`video-script --mode ...`)
# Skelet generatori: struktura, vaqt yig'indisi, so'z limitlari va placeholderlar. Strategiya,
# isbot, narx va da'volar mijoz ma'lumotidan keladi (`[ADD VERIFIED ...]`), to'qilmaydi.
# ---------------------------------------------------------------------------

VIDEO_MODES = ("sales", "organic", "plan", "motion")
VIDEO_LANGS = {"uz": "uz", "uz_latin": "uz", "ru": "ru", "en": "en"}
VIDEO_DURATIONS = (15, 30, 45, 60)
MOTION_EXTRA_DURATIONS = (5, 8, 10)
VO_WORDS_PER_SEC = 2.6  # HEURISTIC_PRIOR_MODEL: 2.2-2.6 so'z/soniya
AWARENESS_STAGES = ("unaware", "problem_aware", "solution_aware", "product_aware", "most_aware")
ORGANIC_FORMATS = ("expert", "story", "myth", "bts", "versus", "qa", "listicle", "series")
MOTION_TYPES = ("kinetic", "ui", "explainer", "data", "bumper")
MOTION_RATIOS = ("9:16", "16:9", "1:1")
GREETING_RE = re.compile(r"^\s*(assalomu|salom|hello|hi\b|hey|привет|здравствуй|всем привет)", re.I)

_L = {
    "uz": {
        "_k": "uz",
        "stage": {"hook": "Hook", "problem": "Muammo", "mechanism": "Mexanizm", "proof": "Isbot", "objection": "E'tiroz",
                  "offer": "Taklif", "cta": "CTA", "thesis": "Tezis", "point": "Nuqta", "conflict": "Ziddiyat", "context": "Kontekst",
                  "turn": "Burilish", "result": "Natija", "lesson": "Saboq", "myth": "Mif", "why_wrong": "Nega noto'g'ri",
                  "right_way": "To'g'ri yondashuv", "process": "Jarayon", "team": "Jamoa", "quality": "Sifat nazorati",
                  "final": "Yakuniy natija", "criteria": "Mezonlar", "option_a": "A variant", "option_b": "B variant",
                  "verdict": "Xulosa", "question": "Savol", "answer": "Javob", "reason": "Sabab", "example": "Misol",
                  "item": "Band", "top_item": "Eng muhim band", "recap": "Qisqa eslatma", "main": "Asosiy qism",
                  "open_loop": "Ochiq savol", "part_next": "Keyingi qism", "summary": "Xulosa", "save_cta": "Saqlash sababi",
                  "soft_cta": "Yumshoq CTA"},
        "add": "[ADD: {x}]", "add_proof": "[ADD VERIFIED {x}]",
        "hooks": {
            "pain": ("Yaqin plan: {pb} lahzasi, keskin kesim", "{pb}?", "{pb}. Tanishmi?", "Og'riq lahzasi"),
            "fact": ("Ekranda kutilmagan fakt kartasi, qo'l ishorasi", "[ADD VERIFIED FAKT]", "Bilasizmi, [ADD VERIFIED FAKT]?", "Kutilmagan fakt"),
            "contrarian": ("Spiker kameraga qaraydi, bosh chayqaydi, 'mif' kartasi", "Bu noto'g'ri", "{prod} haqida hamma xato o'ylaydi.", "Qarshi fikr"),
            "result": ("Natija ko'rinishi (faqat tasdiqlangan material), taymer", "[ADD VERIFIED NATIJA]", "Mana natija. Qanday qilganimizni ko'rsataman.", "Natija namoyishi"),
            "direct": ("Spiker aniq auditoriyaga ishora qiladi", "[ADD AVATAR] uchun", "[ADD AVATAR] bo'lsangiz, buni ko'ring.", "To'g'ridan-to'g'ri chaqiriq"),
        },
        "vo": {"hook": "[ADD: hook gapi]", "problem": "[ADD: muammo lahzasi, 1 gap]", "mechanism": "{prod}: [ADD MEXANIZM, 1-2 gap]",
               "proof": "[ADD: isbot, 1 gap]", "objection": "[ADD: asosiy e'tirozga javob]", "offer": "[ADD VERIFIED TAKLIF]",
               "cta": "[ADD: aniq keyingi qadam]", "generic": "[ADD: {x}, 1 gap]"},
        "text": {"problem": "[ADD: 3-5 so'z]", "mechanism": "[ADD: 3-5 so'z]", "proof": "[ADD VERIFIED RAQAM]", "objection": "[ADD: 3-5 so'z]",
                 "offer": "[ADD VERIFIED TAKLIF]", "cta": "[ADD: harakat fe'li]", "generic": "[ADD: 3-5 so'z]"},
        "visual": {"a_roll": "A-roll: spiker kameraga, yaqin/o'rta plan", "b_roll": "B-roll: jarayon yoki mahsulot, yaqin plan",
                   "proof": "Isbot B-roll: haqiqiy natija, sharh ekrani yoki hujjat (ruxsat bilan)", "screen": "Ekran yozuvi / UI",
                   "text_card": "Matn kartochkasi, kalit so'z urg'u rangida", "end_card": "End-card: logo, CTA, aloqa"},
        "cam": {"a_roll": "Jump cut, ovoz urg'usi", "b_roll": "Rakurs/crop o'zgarishi, whoosh", "proof": "Zoom-in, pop SFX",
                "screen": "Click SFX, kursor urg'usi", "text_card": "Slide-up reveal, pop", "end_card": "Statik 2 s, musiqa tugaydi"},
        "pn": {"delivery": "Spiker: tez, jonli, qisqa gaplar; har gapda bitta fikr; hook'da kulgi/jilmayish yo'q ({x})",
               "light": "Yorug'lik: yuzga yumshoq yon yorug'lik; fon tartibli; mikrofon yaqin",
               "broll": "B-roll ro'yxati: [ADD: 5-8 klip: yaqin plan, jarayon, ekran, isbot]",
               "capture": ["Capture 1 (A-roll): 3-5 hook + to'liq tana + 2 CTA bir sozlamada", "Capture 2 (mexanizm B-roll): 5-8 yaqin plan klip",
                           "Capture 3 (isbot B-roll): haqiqiy natija, sharh ekrani, yetkazib berish"]},
        "bodies": ("Demo-led: muammo, mexanizm demosi, isbot, e'tiroz", "Case-led: kontekst, case, mexanizm, e'tiroz"),
        "ctas": ("Direct CTA: aniq taklif + aniq qadam", "Soft CTA: saqlash / profilga o'tish / savol yozish"),
        "idea": "[ADD: One Big Idea, 1 jumla]", "ph": "[ADD]",
    },
    "ru": {
        "_k": "ru",
        "stage": {"hook": "Хук", "problem": "Проблема", "mechanism": "Механизм", "proof": "Доказательство", "objection": "Возражение",
                  "offer": "Оффер", "cta": "CTA", "thesis": "Тезис", "point": "Пункт", "conflict": "Конфликт", "context": "Контекст",
                  "turn": "Поворот", "result": "Результат", "lesson": "Вывод", "myth": "Миф", "why_wrong": "Почему неверно",
                  "right_way": "Правильный подход", "process": "Процесс", "team": "Команда", "quality": "Контроль качества",
                  "final": "Итог", "criteria": "Критерии", "option_a": "Вариант A", "option_b": "Вариант B", "verdict": "Вывод",
                  "question": "Вопрос", "answer": "Ответ", "reason": "Причина", "example": "Пример", "item": "Пункт",
                  "top_item": "Главный пункт", "recap": "Краткий пересказ", "main": "Основная часть", "open_loop": "Открытый вопрос",
                  "part_next": "Следующая часть", "summary": "Итог", "save_cta": "Причина сохранить", "soft_cta": "Мягкий CTA"},
        "add": "[ВСТАВЬТЕ: {x}]", "add_proof": "[ВСТАВЬТЕ ПРОВЕРЕННЫЙ {x}]",
        "hooks": {
            "pain": ("Крупный план: момент проблемы «{pb}», резкая склейка", "{pb}?", "{pb}. Знакомо?", "Момент боли"),
            "fact": ("На экране карточка с неожиданным фактом, жест рукой", "[ВСТАВЬТЕ ПРОВЕРЕННЫЙ ФАКТ]", "Знаете, что [ВСТАВЬТЕ ПРОВЕРЕННЫЙ ФАКТ]?", "Неожиданный факт"),
            "contrarian": ("Спикер смотрит в камеру, качает головой, карточка «миф»", "Это неверно", "Про {prod} все думают неправильно.", "Встречное мнение"),
            "result": ("Показ результата (только подтверждённый материал), таймер", "[ВСТАВЬТЕ ПРОВЕРЕННЫЙ РЕЗУЛЬТАТ]", "Вот результат. Покажу, как мы это сделали.", "Показ результата"),
            "direct": ("Спикер обращается к конкретной аудитории", "Для [ВСТАВЬТЕ АВАТАР]", "Если вы [ВСТАВЬТЕ АВАТАР], посмотрите.", "Прямое обращение"),
        },
        "vo": {"hook": "[ВСТАВЬТЕ: фраза хука]", "problem": "[ВСТАВЬТЕ: момент проблемы, 1 фраза]", "mechanism": "{prod}: [ВСТАВЬТЕ МЕХАНИЗМ, 1-2 фразы]",
               "proof": "[ВСТАВЬТЕ: доказательство, 1 фраза]", "objection": "[ВСТАВЬТЕ: ответ на возражение]", "offer": "[ВСТАВЬТЕ ПРОВЕРЕННЫЙ ОФФЕР]",
               "cta": "[ВСТАВЬТЕ: конкретный шаг]", "generic": "[ВСТАВЬТЕ: {x}, 1 фраза]"},
        "text": {"problem": "[ВСТАВЬТЕ: 3-5 слов]", "mechanism": "[ВСТАВЬТЕ: 3-5 слов]", "proof": "[ВСТАВЬТЕ ПРОВЕРЕННОЕ ЧИСЛО]", "objection": "[ВСТАВЬТЕ: 3-5 слов]",
                 "offer": "[ВСТАВЬТЕ ПРОВЕРЕННЫЙ ОФФЕР]", "cta": "[ВСТАВЬТЕ: глагол действия]", "generic": "[ВСТАВЬТЕ: 3-5 слов]"},
        "visual": {"a_roll": "A-roll: спикер в камеру, крупный/средний план", "b_roll": "B-roll: процесс или продукт, крупный план",
                   "proof": "B-roll доказательства: реальный результат, экран отзыва или документ (с разрешения)", "screen": "Запись экрана / UI",
                   "text_card": "Текстовая карточка, ключевое слово акцентным цветом", "end_card": "End-card: логотип, CTA, контакт"},
        "cam": {"a_roll": "Jump cut, акцент голосом", "b_roll": "Смена ракурса/кропа, whoosh", "proof": "Zoom-in, pop SFX",
                "screen": "Click SFX, акцент курсором", "text_card": "Slide-up reveal, pop", "end_card": "Статика 2 с, музыка затухает"},
        "pn": {"delivery": "Спикер: быстро, живо, короткие фразы; одна мысль на фразу; в хуке без улыбки-приветствия ({x})",
               "light": "Свет: мягкий боковой на лицо; аккуратный фон; микрофон близко",
               "broll": "Список B-roll: [ВСТАВЬТЕ: 5-8 клипов: крупные планы, процесс, экран, доказательство]",
               "capture": ["Capture 1 (A-roll): 3-5 хуков + полное тело + 2 CTA за один сетап", "Capture 2 (B-roll механизма): 5-8 крупных планов",
                           "Capture 3 (B-roll доказательства): реальный результат, экран отзыва, доставка"]},
        "bodies": ("Demo-led: проблема, демонстрация механизма, доказательство, возражение", "Case-led: контекст, кейс, механизм, возражение"),
        "ctas": ("Direct CTA: конкретный оффер + конкретный шаг", "Soft CTA: сохранить / перейти в профиль / задать вопрос"),
        "idea": "[ВСТАВЬТЕ: Одна большая идея, 1 фраза]", "ph": "[ВСТАВЬТЕ]",
    },
    "en": {
        "_k": "en",
        "stage": {"hook": "Hook", "problem": "Problem", "mechanism": "Mechanism", "proof": "Proof", "objection": "Objection",
                  "offer": "Offer", "cta": "CTA", "thesis": "Thesis", "point": "Point", "conflict": "Conflict", "context": "Context",
                  "turn": "Turning point", "result": "Result", "lesson": "Lesson", "myth": "Myth", "why_wrong": "Why it is wrong",
                  "right_way": "Right approach", "process": "Process", "team": "Team", "quality": "Quality control",
                  "final": "Final result", "criteria": "Criteria", "option_a": "Option A", "option_b": "Option B", "verdict": "Verdict",
                  "question": "Question", "answer": "Answer", "reason": "Reason", "example": "Example", "item": "Item",
                  "top_item": "Top item", "recap": "Recap", "main": "Main part", "open_loop": "Open loop", "part_next": "Next part",
                  "summary": "Summary", "save_cta": "Reason to save", "soft_cta": "Soft CTA"},
        "add": "[ADD: {x}]", "add_proof": "[ADD VERIFIED {x}]",
        "hooks": {
            "pain": ("Close-up: the moment of '{pb}', hard cut", "{pb}?", "{pb}. Sound familiar?", "Pain moment"),
            "fact": ("Unexpected fact card on screen, hand gesture", "[ADD VERIFIED FACT]", "Did you know [ADD VERIFIED FACT]?", "Unexpected fact"),
            "contrarian": ("Speaker looks into camera, shakes head, 'myth' card", "That is wrong", "Everyone gets {prod} wrong.", "Contrarian take"),
            "result": ("Result shown (verified material only), timer", "[ADD VERIFIED RESULT]", "Here is the result. Watch how.", "Result first"),
            "direct": ("Speaker points at a specific audience", "For [ADD AVATAR]", "If you are [ADD AVATAR], watch this.", "Direct call-out"),
        },
        "vo": {"hook": "[ADD: hook line]", "problem": "[ADD: problem moment, 1 sentence]", "mechanism": "{prod}: [ADD MECHANISM, 1-2 sentences]",
               "proof": "[ADD: proof, 1 sentence]", "objection": "[ADD: answer to the main objection]", "offer": "[ADD VERIFIED OFFER]",
               "cta": "[ADD: concrete next step]", "generic": "[ADD: {x}, 1 sentence]"},
        "text": {"problem": "[ADD: 3-5 words]", "mechanism": "[ADD: 3-5 words]", "proof": "[ADD VERIFIED NUMBER]", "objection": "[ADD: 3-5 words]",
                 "offer": "[ADD VERIFIED OFFER]", "cta": "[ADD: action verb]", "generic": "[ADD: 3-5 words]"},
        "visual": {"a_roll": "A-roll: speaker to camera, close/medium shot", "b_roll": "B-roll: process or product, close-up",
                   "proof": "Proof B-roll: real result, review screen or document (with permission)", "screen": "Screen recording / UI",
                   "text_card": "Text card, keyword in accent colour", "end_card": "End card: logo, CTA, contact"},
        "cam": {"a_roll": "Jump cut, vocal emphasis", "b_roll": "Angle/crop change, whoosh", "proof": "Zoom-in, pop SFX",
                "screen": "Click SFX, cursor emphasis", "text_card": "Slide-up reveal, pop", "end_card": "Static 2 s, music ends"},
        "pn": {"delivery": "Speaker: fast, lively, short sentences; one idea per sentence; no greeting or smile in the hook ({x})",
               "light": "Light: soft side light on the face; tidy background; mic close",
               "broll": "B-roll list: [ADD: 5-8 clips: close-ups, process, screen, proof]",
               "capture": ["Capture 1 (A-roll): 3-5 hooks + full body + 2 CTAs in one setup", "Capture 2 (mechanism B-roll): 5-8 close-up clips",
                           "Capture 3 (proof B-roll): real result, review screen, delivery"]},
        "bodies": ("Demo-led: problem, mechanism demo, proof, objection", "Case-led: context, case, mechanism, objection"),
        "ctas": ("Direct CTA: concrete offer + concrete step", "Soft CTA: save / visit profile / ask a question"),
        "idea": "[ADD: One Big Idea, 1 sentence]", "ph": "[ADD]",
    },
}

_STAGE_KIND = {
    "hook": "a_roll", "problem": "a_roll", "mechanism": "b_roll", "proof": "proof", "objection": "a_roll", "offer": "text_card", "cta": "end_card",
    "thesis": "a_roll", "point": "text_card", "conflict": "a_roll", "context": "b_roll", "turn": "b_roll", "result": "proof", "lesson": "a_roll",
    "myth": "a_roll", "why_wrong": "b_roll", "right_way": "a_roll", "process": "b_roll", "team": "b_roll", "quality": "b_roll", "final": "proof",
    "criteria": "text_card", "option_a": "b_roll", "option_b": "b_roll", "verdict": "a_roll", "question": "screen", "answer": "a_roll",
    "reason": "a_roll", "example": "proof", "item": "text_card", "top_item": "a_roll", "recap": "text_card", "main": "a_roll",
    "open_loop": "a_roll", "part_next": "end_card", "summary": "text_card", "save_cta": "end_card", "soft_cta": "end_card",
}

_ORGANIC_SKELETONS = {
    "expert": ("hook", "thesis", "point", "point", "point", "summary", "save_cta"),
    "story": ("hook", "context", "turn", "result", "lesson", "save_cta"),
    "myth": ("hook", "why_wrong", "right_way", "example", "save_cta"),
    "bts": ("hook", "process", "team", "quality", "final", "soft_cta"),
    "versus": ("hook", "criteria", "option_a", "option_b", "verdict", "save_cta"),
    "qa": ("hook", "answer", "reason", "example", "soft_cta"),
    "listicle": ("hook", "item", "item", "item", "top_item", "save_cta"),
    "series": ("hook", "recap", "main", "open_loop", "part_next"),
}
_ORGANIC_HOOK_BY_FORMAT = {"expert": "fact", "story": "pain", "myth": "contrarian", "bts": "result", "versus": "contrarian",
                           "qa": "direct", "listicle": "fact", "series": "pain"}
_ORGANIC_METRIC = {"expert": "Watch time / Saves", "story": "Hold / Shares", "myth": "Comments / Shares", "bts": "Hold / Profile visits",
                   "versus": "Saves / DM", "qa": "Comments / DM", "listicle": "Saves", "series": "Return views / Follow"}

_MOTION_SCENES = {
    "kinetic": ("hook", "point", "point", "point", "offer", "cta"),
    "ui": ("hook", "problem", "feature", "feature", "feature", "result", "cta"),
    "explainer": ("hook", "problem", "solution", "how", "how", "benefit", "cta"),
    "data": ("hook", "number", "compare", "number", "offer", "cta"),
    "bumper": ("logo_in", "tagline", "logo_out"),
}
_MOTION_CUES = {
    "hook": ("zoom-in punch", "whoosh + hit"), "point": ("slide-up reveal", "pop"), "problem": ("camera pan", "soft whoosh"),
    "feature": ("slide-up reveal", "click / pop"), "result": ("counter roll-up", "riser into hit"), "solution": ("morph transition", "whoosh"),
    "how": ("slide-up reveal", "pop"), "benefit": ("zoom-in punch", "hit"), "number": ("counter roll-up", "tick + hit"),
    "compare": ("split reveal", "whoosh"), "offer": ("zoom-in punch", "riser, silence hit before the number"),
    "cta": ("scale-up end-card", "beat drop, then music out"), "logo_in": ("morph transition", "whoosh"),
    "tagline": ("slide-up reveal", "pop"), "logo_out": ("scale-up end-card", "hit, music out"),
}
_MOTION_LABELS = {
    "uz": {"hook": "Hook", "point": "Asosiy nuqta", "problem": "Muammo", "feature": "Funksiya", "result": "Natija", "solution": "Yechim",
           "how": "Qanday ishlaydi", "benefit": "Foyda", "number": "Raqam", "compare": "Taqqoslash", "offer": "Taklif", "cta": "CTA + logo",
           "logo_in": "Logo kirishi", "tagline": "Tagline", "logo_out": "Logo yakuni"},
    "ru": {"hook": "Хук", "point": "Ключевой пункт", "problem": "Проблема", "feature": "Функция", "result": "Результат", "solution": "Решение",
           "how": "Как работает", "benefit": "Выгода", "number": "Число", "compare": "Сравнение", "offer": "Оффер", "cta": "CTA + логотип",
           "logo_in": "Появление логотипа", "tagline": "Тэглайн", "logo_out": "Финал логотипа"},
    "en": {"hook": "Hook", "point": "Key point", "problem": "Problem", "feature": "Feature", "result": "Result", "solution": "Solution",
           "how": "How it works", "benefit": "Benefit", "number": "Number", "compare": "Comparison", "offer": "Offer", "cta": "CTA + logo",
           "logo_in": "Logo in", "tagline": "Tagline", "logo_out": "Logo out"},
}
_MOTION_BPM = {"kinetic": 125, "ui": 110, "explainer": 90, "data": 110, "bumper": 120}
_MOTION_ASSETS = {
    "kinetic": ["Brend shriftlar (OTF/TTF, litsenziya, lotin+kirill)", "Rang palitrasi (HEX)", "Asosiy matnlar (tasdiqlangan)", "Logo SVG"],
    "ui": ["UI skrinshot/ekran yozuvi (shaxsiy ma'lumotlar yopilgan)", "Logo SVG", "Brend shriftlar", "Raqamli dalillar (tasdiqlangan)"],
    "explainer": ["Ikonalar/illustratsiyalar (vektor)", "Jarayon sxemasi", "Logo SVG", "Brend shriftlar", "Voiceover skripti tasdig'i"],
    "data": ["Tasdiqlangan raqamlar va manba", "Grafik ma'lumotlari (CSV)", "Logo SVG", "Brend shriftlar"],
    "bumper": ["Logo SVG + monoxrom variant", "Tagline matni", "Brend tovush/musiqa (litsenziyali)", "Rang palitrasi (HEX)"],
}
_MOTION_ASSETS_COMMON = ["Musiqa/SFX litsenziyasi (nomi va havola)", "Voiceover yozuvi yoki TTS ovozi (agar bo'lsa)"]


_XT = {
    "ru": {"auditoriya": "аудитория", "muammo": "проблема", "auditoriya savoli": "вопрос аудитории", "kontent ustuni": "рубрика контента",
           "saqlash/ulashish sababi": "причина сохранить/поделиться", "haqiqiy mijoz savoli #{n}": "реальный вопрос клиента #{n}",
           "lokatsiya {n}": "локация {n}", "ustun {n}": "рубрика {n}",
           "umumiy B-roll: qo'llar, jarayon, ekran, mijoz bilan muloqot, detal (20-30 klip)": "общий B-roll: руки, процесс, экран, общение с клиентом, детали (20-30 клипов)",
           "VO, <= {n} so'z": "VO, <= {n} слов", "3-5 so'z, kalit so'z urg'uli": "3-5 слов, ключевое слово выделено", "logo / tagline": "логотип / тэглайн",
           "fon, UI karta, ikona, mahsulot yoki grafik: nima qayerda": "фон, UI-карта, иконка, продукт или график: что где",
           "diktor uslubi, til, tezlik": "стиль диктора, язык, темп", "3 sifat + 1 'bo'lmasin'": "3 качества + 1 «чего не должно быть»"},
    "en": {"auditoriya": "audience", "muammo": "problem", "auditoriya savoli": "audience question", "kontent ustuni": "content pillar",
           "saqlash/ulashish sababi": "reason to save/share", "haqiqiy mijoz savoli #{n}": "real customer question #{n}",
           "lokatsiya {n}": "location {n}", "ustun {n}": "pillar {n}",
           "umumiy B-roll: qo'llar, jarayon, ekran, mijoz bilan muloqot, detal (20-30 klip)": "common B-roll: hands, process, screen, customer interaction, details (20-30 clips)",
           "VO, <= {n} so'z": "VO, <= {n} words", "3-5 so'z, kalit so'z urg'uli": "3-5 words, keyword accented", "logo / tagline": "logo / tagline",
           "fon, UI karta, ikona, mahsulot yoki grafik: nima qayerda": "background, UI card, icon, product or chart: what goes where",
           "diktor uslubi, til, tezlik": "narrator style, language, pace", "3 sifat + 1 'bo'lmasin'": "3 qualities + 1 'must not be'"},
}


def _a(lang: dict, key: str, **kw: Any) -> str:
    """Til bo'yicha `[ADD: ...]` placeholder (kalitlar uz matni; ru/en tarjimasi _XT da)."""
    text = _XT.get(lang["_k"], {}).get(key, key)
    return lang["add"].format(x=text.format(**kw) if kw else text)


def _fmt_t(t: float) -> str:
    m, s = divmod(float(t), 60.0)
    return f"{int(m):02d}:{int(s):02d}" + (".5" if abs(s - int(s) - 0.5) < 1e-9 else "")


def _split(total: float, parts: int) -> list[float]:
    """total soniyani parts ta bo'lakka teng (0.5 s qadam) bo'ladi; qoldiq birinchi bo'laklarga qo'shiladi, yig'indisi aniq total."""
    parts = max(1, min(parts, int(total // 1.5) or 1))
    units = int(round(total * 2))
    q, r = divmod(units, parts)
    return [(q + (1 if i < r else 0)) / 2 for i in range(parts)]


def _words(text: str) -> int:
    return len(re.findall(r"[\w'’]+", text or "", re.U))


def _short(text: str, n: int) -> str:
    w = (text or "").strip().split()
    return " ".join(w[:n])


def _row(start: float, end: float, stage: str, visual: str, vo: str, text: str, cam: str, hint: str = "") -> dict[str, Any]:
    limit = int((end - start) * VO_WORDS_PER_SEC)
    if _words(vo) > limit:  # qisqa qatorga sig'maydigan skelet VO ni minimal placeholderga almashtiramiz
        vo = "[ADD VO]" if limit >= 2 else ""
    return {"time": f"{_fmt_t(start)}-{_fmt_t(end)}", "start_s": round(start, 2), "end_s": round(end, 2), "stage": stage,
            "visual": visual, "vo": vo, "on_screen_text": text, "camera_rhythm_sfx": cam, "hint": hint}


def check_av_table(rows: list[dict[str, Any]], duration_sec: float, hook_count: int | None = None) -> dict[str, Any]:
    """Avtomatik tekshiriladigan sifat bandlari (script-quality-rubric.md): vaqt yig'indisi, VO limit, ekran matni, salomlashish."""
    issues: list[str] = []
    if not rows:
        return {"time_sum_matches_duration": False, "vo_within_word_limit": False, "on_screen_text_within_limit": False,
                "no_greeting_open": False, "hook_count_ok": False, "issues": ["jadval bo'sh"]}
    ordered = sorted(rows, key=lambda r: r["start_s"])
    cursor, contiguous = 0.0, True
    for r in ordered:
        if abs(r["start_s"] - cursor) > 0.01:
            contiguous = False
        cursor = r["end_s"]
    time_ok = contiguous and abs(cursor - duration_sec) < 0.01
    if not time_ok:
        issues.append(f"vaqt yig'indisi {cursor}s != {duration_sec}s yoki bo'shliq bor")
    vo_ok, txt_ok = True, True
    for r in ordered:
        limit = int((r["end_s"] - r["start_s"]) * VO_WORDS_PER_SEC)
        if _words(r.get("vo", "")) > limit:
            vo_ok = False
            issues.append(f"{r['time']}: VO {_words(r['vo'])} so'z > limit {limit}")
        tlimit = 7 if r["start_s"] < 3 else 5
        if _words(r.get("on_screen_text", "")) > tlimit:
            txt_ok = False
            issues.append(f"{r['time']}: ekran matni {_words(r['on_screen_text'])} so'z > {tlimit}")
    greet_ok = not GREETING_RE.search(ordered[0].get("vo", ""))
    if not greet_ok:
        issues.append("birinchi qator salomlashish bilan boshlanadi")
    hook_ok = True if hook_count is None else 3 <= hook_count <= 5
    return {"time_sum_matches_duration": time_ok, "vo_within_word_limit": vo_ok, "on_screen_text_within_limit": txt_ok,
            "no_greeting_open": greet_ok, "hook_count_ok": hook_ok, "issues": issues}


def _self_audit(automated: dict[str, Any], mode: str) -> dict[str, Any]:
    return {
        "rubric": "skills/video/references/script-quality-rubric.md",
        "pass_score": 85,
        "automated_checks": automated,
        "manual_criteria": ["hook_strength (20)", "retention_rhythm (15)", "conversion_or_value_logic (20)", "natural_speech_anti_cliche (15)",
                            "visual_safe_zone_executability (20)", "platform_compliance_honesty (10)"],
        "evidence_label": "HEURISTIC_PRIOR_MODEL",
        "note": f"{mode}: skelet tekshiruvi; nutq tabiiyligi va mantiq qo'lda baholanadi; ball natija prognozi emas",
    }


def _vo_for(lang: dict, key: str, prod: str, x: str = "") -> str:
    tpl = lang["vo"].get(key) or lang["vo"]["generic"]
    return tpl.format(prod=_short(prod, 3), x=x)


def _text_for(lang: dict, key: str) -> str:
    return lang["text"].get(key) or lang["text"]["generic"]


def _stage_row(lang: dict, stage_key: str, start: float, end: float, prod: str, label_suffix: str = "") -> dict[str, Any]:
    kind = _STAGE_KIND.get(stage_key, "a_roll")
    label = lang["stage"][stage_key] + label_suffix
    base = stage_key if stage_key in lang["vo"] else "generic"
    return _row(start, end, label, lang["visual"][kind], _vo_for(lang, base, prod, x=lang["stage"][stage_key].lower()),
                _text_for(lang, base if base in lang["text"] else "generic"), lang["cam"][kind])


def _validate_common(lang_code: str, duration: int, allow_extra: bool = False) -> str:
    key = VIDEO_LANGS.get((lang_code or "uz").strip().lower())
    if not key:
        raise ValueError(f"lang '{lang_code}' qo'llab-quvvatlanmaydi (uz|ru|en)")
    allowed = VIDEO_DURATIONS + (MOTION_EXTRA_DURATIONS if allow_extra else ())
    if duration not in allowed:
        raise ValueError(f"duration {duration} noto'g'ri; ruxsat: {', '.join(map(str, allowed))}")
    return key


def _brief_header(lang: dict, mode: str, niche: str, product: str, problem: str, goal: str, awareness: str, fmt: str, duration: int, extra: dict | None = None) -> dict[str, Any]:
    hdr = {
        "business_product": product, "niche": niche, "problem": problem or lang["ph"], "goal": goal, "audience": _a(lang, "auditoriya"),
        "awareness_stage": awareness, "format": fmt, "duration_sec": duration, "one_big_idea": lang["idea"],
        "evidence_label": "ASSUMPTION", "evidence_note": "Maqsad/awareness taxmin; mijoz tasdiqlaguncha ASSUMPTION",
    }
    hdr.update(extra or {})
    return hdr


def _generate_sales(lang_key: str, niche: str, product: str, problem: str, duration: int, hooks: int, awareness: str, price: float | None, currency: str) -> dict[str, Any]:
    L = _L[lang_key]
    prod = product.strip() or L["ph"]
    pb = _short(problem.strip(), 5) or _a(L, "muammo")
    mechs = ["pain", "fact", "contrarian", "result", "direct"]
    hook_mods = []
    for i in range(hooks):
        vis, txt, spoken, label = L["hooks"][mechs[i]]
        fmtd = lambda s: s.format(pb=pb, prod=_short(prod, 3))
        hook_mods.append({"hook_id": f"H{i + 1}", "mechanism": mechs[i], "mechanism_label": label, "visual_0_3s": fmtd(vis),
                          "on_screen_text": fmtd(txt), "spoken_line": fmtd(spoken)})
    cta_len = 4 if duration <= 15 else (7 if duration <= 30 else 8)
    body_start, body_end = 3.0, float(duration - cta_len)
    window = body_end - body_start
    n_beats = max(4, math.ceil(window / 4.0))
    seq = ["problem", "mechanism", "proof", "objection"]
    extras = ["mechanism", "proof"]
    beat_stages = list(seq)
    for k in range(n_beats - 4):
        beat_stages.insert(2 + k, extras[k % 2])
    durs = _split(window, n_beats)

    def body_rows(variant: int) -> list[dict[str, Any]]:
        stages = list(beat_stages)
        if variant == 1:  # case-led: isbot mexanizmdan oldin
            i_m, i_p = stages.index("mechanism"), stages.index("proof")
            stages[i_m], stages[i_p] = stages[i_p], stages[i_m]
        rows, t = [], body_start
        for st, d in zip(stages, durs):
            rows.append(_stage_row(L, st, t, t + d, prod))
            t += d
        return rows

    bodies = [{"body_id": f"B{i + 1}", "approach": L["bodies"][i], "rows": body_rows(i)} for i in range(2)]
    offer_line = L["vo"]["offer"]
    price_note = f"{price:,.2f}".rstrip("0").rstrip(".").replace(",", " ") + (f" {currency}" if currency else "") if price else ""
    ctas = []
    for i in range(2):
        start = float(duration - cta_len)
        half = start + (cta_len - 2)
        offer = _row(start, half, L["stage"]["offer"], L["visual"]["text_card"], offer_line, (price_note or _text_for(L, "offer")), L["cam"]["text_card"],
                     hint="USER_PROVIDED narx" if price_note else "")
        cta = _row(half, float(duration), L["stage"]["cta"], L["visual"]["end_card"], _vo_for(L, "cta", prod), _text_for(L, "cta"), L["cam"]["end_card"])
        ctas.append({"cta_id": f"C{i + 1}", "type": "direct" if i == 0 else "soft", "approach": L["ctas"][i], "rows": [offer, cta]})

    h0 = hook_mods[0]
    hook_row = _row(0.0, 3.0, L["stage"]["hook"], h0["visual_0_3s"], h0["spoken_line"], h0["on_screen_text"], L["cam"]["a_roll"] + ", punch-in + hit",
                    hint=f"{h0['hook_id']} ({h0['mechanism_label']})")
    av_table = [hook_row] + bodies[0]["rows"] + ctas[0]["rows"]
    chk = check_av_table(av_table, duration, hooks)
    for hm in hook_mods:  # har hook 0-3 s ga sig'ishi kerak
        if _words(hm["spoken_line"]) > int(3 * VO_WORDS_PER_SEC):
            chk["vo_within_word_limit"] = False
            chk["issues"].append(f"{hm['hook_id']}: hook gapi 3 s uchun uzun")
    return {
        "schema": "tyrion.video_script/v8", "mode": "sales", "lang": lang_key, "duration_sec": duration,
        "brief": _brief_header(L, "sales", niche, prod, problem, "Lead / Sale", awareness, "9:16", duration,
                               {"test_hypothesis": {"variable": "hook (H1..H%d)" % hooks, "success_metric": "3s hook rate vs account baseline",
                                                    "decision_rule": "[ADD: minimal namuna va qaror qoidasi, ishga tushirishdan oldin]"}}),
        "modules": {"hooks": hook_mods, "bodies": bodies, "ctas": ctas,
                    "combinations": [f"H{h}xB{b}xC{c}" for h in range(1, hooks + 1) for b in (1, 2) for c in (1, 2)]},
        "av_table": av_table,
        "production_notes": {"delivery": L["pn"]["delivery"].format(x=prod), "lighting_audio": L["pn"]["light"], "broll": L["pn"]["broll"],
                             "three_capture": L["pn"]["capture"], "open_placeholders": "[ADD ...] / [ADD VERIFIED ...] qatorlarini mijoz ma'lumoti bilan to'ldiring",
                             "safe_zone": "720x1200 (yagona manba: skills/video/references/sales-video-scripting.md §8)"},
        "self_audit_checklist": _self_audit(chk, "sales"),
        "evidence_label": "HEURISTIC_PRIOR_MODEL",
        "note": "Skelet: strategiya, isbot va da'volar mijoz ma'lumotidan; to'qilgan statistika/sharh yo'q.",
    }


def _generate_organic(lang_key: str, niche: str, product: str, problem: str, duration: int, hooks: int, awareness: str, content_format: str) -> dict[str, Any]:
    L = _L[lang_key]
    prod = product.strip() or L["ph"]
    pb = _short(problem.strip(), 5) or _a(L, "auditoriya savoli")
    skeleton = _ORGANIC_SKELETONS[content_format]
    mechs = [_ORGANIC_HOOK_BY_FORMAT[content_format]] + [m for m in ("pain", "fact", "contrarian", "direct", "result") if m != _ORGANIC_HOOK_BY_FORMAT[content_format]]
    hook_mods = []
    for i in range(hooks):
        vis, txt, spoken, label = L["hooks"][mechs[i]]
        f = lambda s: s.format(pb=pb, prod=_short(prod, 3))
        hook_mods.append({"hook_id": f"H{i + 1}", "mechanism": mechs[i], "mechanism_label": label, "visual_0_3s": f(vis), "on_screen_text": f(txt), "spoken_line": f(spoken)})
    n = len(skeleton)
    durs = [3.0] + _split(float(duration - 3), n - 1)
    rows, t = [], 0.0
    point_i = 0
    for idx, (st, d) in enumerate(zip(skeleton, durs)):
        suffix = ""
        if st in ("point", "item"):
            point_i += 1
            suffix = f" {point_i}"
        if idx == 0:
            h = hook_mods[0]
            rows.append(_row(t, t + d, L["stage"]["hook"], h["visual_0_3s"], h["spoken_line"], h["on_screen_text"], L["cam"]["a_roll"] + ", punch-in", hint=h["hook_id"]))
        else:
            rows.append(_stage_row(L, st, t, t + d, prod, suffix))
        t += d
    # >4 s qatorlarni retention uchun bo'lib chiqamiz
    expanded: list[dict[str, Any]] = []
    for r in rows:
        span = r["end_s"] - r["start_s"]
        if span <= 4.0:
            expanded.append(r)
            continue
        parts = math.ceil(span / 4.0)
        sub = _split(span, parts)
        s0 = r["start_s"]
        for j, d in enumerate(sub):
            rr = dict(r)
            rr.update(_row(s0, s0 + d, r["stage"], r["visual"], r["vo"] if j == 0 else L["vo"]["generic"].format(x=r["stage"].lower()),
                           r["on_screen_text"] if j == 0 else L["text"]["generic"], (r["camera_rhythm_sfx"] if j == 0 else L["cam"]["b_roll"]),
                           hint=("pattern interrupt: B-roll / matn kartochkasi / zoom" if j else r["hint"])))
            expanded.append(rr)
            s0 += d
    chk = check_av_table(expanded, duration, hooks)
    return {
        "schema": "tyrion.video_script/v8", "mode": "organic", "lang": lang_key, "duration_sec": duration, "content_format": content_format,
        "brief": _brief_header(L, "organic", niche, prod, problem, "Trust / Reach", awareness, "9:16", duration,
                               {"content_format": content_format, "primary_metric": _ORGANIC_METRIC[content_format],
                                "funnel_stage": "[ADD: TOFU|MOFU|BOFU]", "pillar": _a(L, "kontent ustuni"),
                                "save_or_share_reason": _a(L, "saqlash/ulashish sababi")}),
        "modules": {"hooks": hook_mods},
        "av_table": expanded,
        "production_notes": {"delivery": L["pn"]["delivery"].format(x=prod), "lighting_audio": L["pn"]["light"], "broll": L["pn"]["broll"],
                             "open_placeholders": "[ADD ...] qatorlarini haqiqiy mavzu/keys bilan to'ldiring; to'qilgan hikoya yo'q",
                             "safe_zone": "720x1200 (yagona manba: skills/video/references/sales-video-scripting.md §8)"},
        "self_audit_checklist": _self_audit(chk, "organic"),
        "evidence_label": "HEURISTIC_PRIOR_MODEL",
        "note": "Organik skelet: mavzu va keys mijozdan (USER_PROVIDED) yoki ASSUMPTION.",
    }


def _interleave(counts: dict[str, int]) -> list[str]:
    """Funnel bosqichlarini bir tekis taqsimlaydi (deterministik)."""
    total = sum(counts.values())
    seq: list[str] = []
    acc = {k: 0.0 for k in counts}
    for _ in range(total):
        for k in counts:
            acc[k] += counts[k] / total
        pick = max((k for k in counts if counts[k] > sum(1 for s in seq if s == k)), key=lambda k: acc[k])
        seq.append(pick)
        acc[pick] -= 1.0
    return seq


def _generate_plan(lang_key: str, niche: str, product: str, duration: int, weeks: int, per_week: int, platforms: str, start_date: str | None) -> dict[str, Any]:
    L = _L[lang_key]
    if weeks not in (1, 2, 4):
        raise ValueError("weeks 1|2|4 bo'lishi kerak")
    if not 1 <= per_week <= 14:
        raise ValueError("per-week 1..14 oralig'ida bo'lishi kerak")
    total = weeks * per_week
    bofu = max(1, round(total * 0.2))
    mofu = max(1 if total >= 3 else 0, round(total * 0.3))
    tofu = total - bofu - mofu
    if tofu < 1:
        tofu, mofu = max(1, total - bofu), max(0, total - bofu - 1)
    counts = {"TOFU": tofu, "MOFU": mofu, "BOFU": bofu}
    counts = {k: v for k, v in counts.items() if v > 0}
    funnel_seq = _interleave(counts)
    pool = {"TOFU": ["listicle", "myth", "series", "bts"], "MOFU": ["expert", "story", "versus", "qa"], "BOFU": ["sales"]}
    ctas = {"TOFU": "soft", "MOFU": "soft-to-direct", "BOFU": "direct"}
    plats = [p.strip() for p in platforms.split(",") if p.strip()] or ["instagram"]
    base = _dt.date.fromisoformat(start_date) if start_date else None
    used: dict[str, int] = {}
    matrix: list[dict[str, Any]] = []
    prev_fmt = ""
    step = max(1, 7 // per_week) if per_week <= 7 else 1
    for i, stage in enumerate(funnel_seq):
        opts = pool[stage]
        k = used.get(stage, 0)
        fmt = opts[k % len(opts)]
        if fmt == prev_fmt and len(opts) > 1:
            k += 1
            fmt = opts[k % len(opts)]
        used[stage] = k + 1
        prev_fmt = fmt
        week, slot = divmod(i, per_week)
        day_offset = week * 7 + min(6, slot * step)
        label = (base + _dt.timedelta(days=day_offset)).isoformat() if base else f"W{week + 1}-D{min(7, slot * step + 1)}"
        mode = "sales" if fmt == "sales" else "organic"
        matrix.append({
            "n": i + 1, "date": label, "platform": " + ".join(plats), "funnel": stage, "format": fmt, "script_mode": mode,
            "pillar": _a(L, "kontent ustuni"), "topic_hook": _a(L, "haqiqiy mijoz savoli #{n}", n=i + 1),
            "topic_source": "USER_PROVIDED yoki ASSUMPTION (to'ldirilganda belgilang)",
            "primary_metric": "DM / Lead" if stage == "BOFU" else _ORGANIC_METRIC.get(fmt, "Watch time"),
            "cta": ctas[stage], "duration_sec": duration,
        })
    per_day = 10
    days = max(1, math.ceil(total / per_day))
    shoot_days = []
    for d in range(days):
        chunk = matrix[d * per_day:(d + 1) * per_day]
        n_out = min(3, max(1, len(chunk) // 3))
        shoot_days.append({
            "shoot_day": d + 1, "videos": [m["n"] for m in chunk], "video_count": len(chunk),
            "before": ["Ssenariylar telefonda/chop etilgan, mavzu bo'yicha guruhlangan", "Rekvizit va jihoz ro'yxati", "Ruxsatlar: mijoz, litsenziya, joy"],
            "locations": [_a(L, "lokatsiya {n}", n=j + 1) for j in range(min(3, max(2, len(chunk) // 4)))],
            "outfits": n_out, "lighting": L["pn"]["light"],
            "shooting_order": "lokatsiya, keyin kiyim, keyin format; murakkab (ko'p matnli) videolar boshida",
            "three_capture": L["pn"]["capture"], "common_broll": [_a(L, "umumiy B-roll: qo'llar, jarayon, ekran, mijoz bilan muloqot, detal (20-30 klip)")],
            "spare_hooks": "har videoga +1 zaxira hook varianti (bir joyda)", "file_naming": "YYYYMMDD_<id>_<hookN>",
        })
    chk = {"funnel_counts_sum_matches_total": sum(counts.values()) == total, "formats_per_week_ok": True, "bofu_present": "BOFU" in counts, "issues": []}
    for w in range(weeks):
        wk = matrix[w * per_week:(w + 1) * per_week]
        if per_week >= 3 and len({m["format"] for m in wk}) < 3:
            chk["formats_per_week_ok"] = False
            chk["issues"].append(f"hafta {w + 1}: 3 dan kam xil format")
    return {
        "schema": "tyrion.video_script/v8", "mode": "plan", "lang": lang_key, "duration_sec": duration, "weeks": weeks, "videos_per_week": per_week, "total_videos": total,
        "brief": _brief_header(L, "plan", niche, product.strip() or L["ph"], "", "Trust / Lead", "mixed", "9:16", duration,
                               {"platforms": plats, "pillars": [_a(L, "ustun {n}", n=i) for i in (1, 2, 3)]}),
        "funnel_mix": {"counts": counts, "target_shares": {"TOFU": 0.5, "MOFU": 0.3, "BOFU": 0.2}, "evidence_label": "HEURISTIC_PRIOR_MODEL",
                       "note": "Boshlang'ich taxmin; 4 haftalik o'z natijangiz (MEASURED_ACCOUNT_DATA) bilan sozlanadi"},
        "content_matrix": matrix,
        "batch_shooting_plan": shoot_days,
        "self_audit_checklist": _self_audit(chk, "plan"),
        "evidence_label": "HEURISTIC_PRIOR_MODEL",
        "note": "Reja skeleti: mavzular haqiqiy mijoz savollaridan (USER_PROVIDED) to'ldiriladi; ssenariylar uchun --mode organic|sales.",
    }


def _generate_motion(lang_key: str, niche: str, product: str, problem: str, duration: int, motion_type: str, ratio: str) -> dict[str, Any]:
    L = _L[lang_key]
    labels = _MOTION_LABELS[lang_key]
    prod = product.strip() or L["ph"]
    roles = _MOTION_SCENES[motion_type]
    n = len(roles)
    if n == 3:
        durs = _split(float(duration), 3)
    else:
        first, last = 2.5, 2.5
        mid_total = duration - first - last
        durs = [first] + _split(float(mid_total), n - 2) + [last]
    scenes, t = [], 0.0
    counters: dict[str, int] = {}
    for i, (role, d) in enumerate(zip(roles, durs)):
        counters[role] = counters.get(role, 0) + 1
        suffix = f" {counters[role]}" if roles.count(role) > 1 else ""
        cue, sfx = _MOTION_CUES[role]
        limit = int(d * VO_WORDS_PER_SEC)
        scenes.append({
            "scene": f"S{i + 1}", "time": f"{_fmt_t(t)}-{_fmt_t(t + d)}", "start_s": round(t, 2), "end_s": round(t + d, 2), "duration_s": round(d, 2),
            "role": labels[role] + suffix,
            "vo": _a(L, "VO, <= {n} so'z", n=limit) if limit >= 1 else "",
            "vo_word_limit": limit,
            "on_screen_text": _a(L, "3-5 so'z, kalit so'z urg'uli") if role not in ("logo_in", "logo_out") else _a(L, "logo / tagline"),
            "visual_assets": _a(L, "fon, UI karta, ikona, mahsulot yoki grafik: nima qayerda"),
            "motion_cue": cue, "sfx_music": sfx,
        })
        t += d
    chk = check_av_table([{"start_s": s["start_s"], "end_s": s["end_s"], "time": s["time"], "vo": "", "on_screen_text": ""} for s in scenes], duration)
    chk["scenes_min_len_ok"] = all(s["duration_s"] >= 1.5 for s in scenes)
    chk["hook_scene_max_3s"] = scenes[0]["duration_s"] <= 3.0 or motion_type == "bumper"
    chk["vo_limit_defined_per_scene"] = all("vo_word_limit" in s for s in scenes)
    if not chk["scenes_min_len_ok"]:
        chk["issues"].append("sahna 1.5 s dan qisqa")
    safe = "720x1200 (yagona manba: skills/video/references/sales-video-scripting.md §8)" if ratio == "9:16" else "title-safe zona, pastki subtitr zonasi bo'sh"
    return {
        "schema": "tyrion.motion_blueprint/v8", "mode": "motion", "lang": lang_key, "duration_sec": duration, "motion_type": motion_type,
        "brief": {
            "concept": L["idea"], "motion_type": motion_type, "format": ratio, "duration_sec": duration, "product": prod, "niche": niche,
            "problem": problem or L["ph"], "goal": "Lead / Sale / Reach / Trust", "awareness_stage": "[ADD]",
            "tempo_bpm": _MOTION_BPM[motion_type], "tempo_evidence_label": "HEURISTIC_PRIOR_MODEL",
            "palette": {"primary": "[ADD HEX]", "accent": "[ADD HEX]", "background": "[ADD HEX]", "text": "[ADD HEX]"},
            "typography": {"headline": "[ADD: shrift, lotin+kirill glif tekshirilgan]", "keyword_accent": "[ADD]", "secondary": "[ADD]"},
            "safe_zone": safe, "voice": _a(L, "diktor uslubi, til, tezlik"), "tone": _a(L, "3 sifat + 1 'bo'lmasin'"),
            "evidence_label": "ASSUMPTION",
        },
        "storyboard": scenes,
        "asset_checklist": [{"asset": a, "owner": "[ADD]", "status": "todo"} for a in _MOTION_ASSETS[motion_type] + _MOTION_ASSETS_COMMON],
        "self_audit_checklist": _self_audit(chk, "motion"),
        "render_handoff": "Faqat so'ralsa: video-motion-graphics.md va tools/video-run.py blueprint'ni kirish sifatida oladi; bu generator render qilmaydi.",
        "evidence_label": "HEURISTIC_PRIOR_MODEL",
        "note": "Motion blueprint skeleti: matn, raqam va UI mazmuni mijoz materialidan (to'qilmaydi).",
    }


def generate_video_blueprint(
    mode: str, niche: str = "ecom", product: str = "", problem: str = "", lang: str = "uz", duration_sec: int = 30,
    hooks: int = 3, awareness: str = "problem_aware", price: float | None = None, currency: str = "",
    content_format: str = "expert", motion_type: str = "kinetic", ratio: str = "9:16", weeks: int = 2, per_week: int = 5,
    platforms: str = "instagram,tiktok,youtube", start_date: str | None = None,
) -> dict[str, Any]:
    """`video-script --mode sales|organic|plan|motion` skelet generatori (0 token, stdlib). ValueError — noto'g'ri parametr."""
    if mode not in VIDEO_MODES:
        raise ValueError(f"mode '{mode}' noto'g'ri; ruxsat: {', '.join(VIDEO_MODES)}")
    lang_key = _validate_common(lang, int(duration_sec), allow_extra=(mode == "motion"))
    if not 3 <= hooks <= 5:
        raise ValueError("hooks 3..5 oralig'ida bo'lishi kerak")
    if awareness not in AWARENESS_STAGES:
        raise ValueError(f"awareness noto'g'ri; ruxsat: {', '.join(AWARENESS_STAGES)}")
    if content_format not in ORGANIC_FORMATS:
        raise ValueError(f"content-format noto'g'ri; ruxsat: {', '.join(ORGANIC_FORMATS)}")
    if motion_type not in MOTION_TYPES:
        raise ValueError(f"motion-type noto'g'ri; ruxsat: {', '.join(MOTION_TYPES)}")
    if ratio not in MOTION_RATIOS:
        raise ValueError(f"ratio noto'g'ri; ruxsat: {', '.join(MOTION_RATIOS)}")
    if start_date:
        try:
            _dt.date.fromisoformat(start_date)
        except ValueError as exc:
            raise ValueError("start-date YYYY-MM-DD bo'lishi kerak") from exc
    duration_sec = int(duration_sec)
    if mode == "motion" and motion_type == "bumper" and duration_sec > 10:
        raise ValueError("bumper uchun duration 5, 8 yoki 10 s (5-10 soniyalik brend lahzasi)")
    if mode == "sales":
        return _generate_sales(lang_key, niche, product, problem, duration_sec, hooks, awareness, price, currency)
    if mode == "organic":
        return _generate_organic(lang_key, niche, product, problem, duration_sec, hooks, awareness, content_format)
    if mode == "plan":
        return _generate_plan(lang_key, niche, product, duration_sec, weeks, per_week, platforms, start_date)
    return _generate_motion(lang_key, niche, product, problem, duration_sec, motion_type, ratio)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="creative-matrix.py", description="Tyrion v8.2 Global Creative Matrix, Video Script & Ad Copy Engine")
    sub = parser.add_subparsers(dest="command", required=True)

    p_mat = sub.add_parser("matrix", help="3x3 Angle x Format creative testing matrix with market BNPL anchor & falsifiable hypotheses")
    p_mat.add_argument("--niche", default="ecom")
    p_mat.add_argument("--product", required=True)
    p_mat.add_argument("--price", type=tcore.positive_float, default=None, help="Haqiqiy narx (berilmasa narx-anchor hisoblanmaydi, taxminiy narx o'ylab topilmaydi)")
    p_mat.add_argument("--market", default="global", help="Market pack (global, uz, us, eu, uk, mena, latam, sea, in)")
    p_mat.add_argument("--currency", default="", help="ISO 4217 currency override (USD, EUR, GBP, JPY, UZS, etc.)")
    p_mat.add_argument("--json", action="store_true")

    p_hk = sub.add_parser("hooks", help="Multilingual 3-second Hook generator (any BCP 47 language)")
    p_hk.add_argument("--niche", default="ecom")
    p_hk.add_argument("--offer", required=True)
    p_hk.add_argument("--languages", default="", help="Comma-separated BCP 47 language codes (e.g. en,de,fr,ar,uz_latin,ru)")
    p_hk.add_argument("--json", action="store_true")

    p_it = sub.add_parser("iterate", help="Real ko'rsatkichlardan voronka bo'yicha diagnostik gipotezalar: nimani o'zgartirish, nimani saqlash")
    for _m in ("hook-rate", "hold-rate", "outbound-ctr", "lp-cvr", "qualified-lead-rate"):
        p_it.add_argument(f"--{_m}", type=tcore.finite_float, default=None, help="Foiz (%)")
        p_it.add_argument(f"--baseline-{_m}", type=tcore.finite_float, default=None, help="Akkaunt o'rtachasi (%)")
    p_it.add_argument("--cpa", type=tcore.finite_float, default=None)
    p_it.add_argument("--breakeven-cpa", type=tcore.finite_float, default=None)
    p_it.add_argument("--impressions", type=int, default=None)
    p_it.add_argument("--metrics", default=None, help="metrics.v1 fayl: hook/hold/CTR/CPA shu yerdan (qo'lda argument ustun)")
    p_it.add_argument("--entity-id", default=None)
    p_it.add_argument("--json", action="store_true")

    p_fat = sub.add_parser("fatigue", help="Creative fatigue diagnostics via Hook Rate, Hold Rate, FTIR & UTIS")
    p_fat.add_argument("--hook-rate", type=tcore.finite_float, default=None)
    p_fat.add_argument("--hold-rate", type=tcore.finite_float, default=None)
    p_fat.add_argument("--ctr-drop-pct", type=tcore.finite_float, default=None)
    p_fat.add_argument("--frequency", type=tcore.finite_float, default=None)
    p_fat.add_argument("--ftir", type=tcore.finite_float, default=70.0)
    p_fat.add_argument("--metrics", default=None, help="metrics.v1 fayl: hook/hold/frequency/CTR trendi shu yerdan (qo'lda argument ustun)")
    p_fat.add_argument("--entity-id", default=None)
    p_fat.add_argument("--json", action="store_true")

    p_vid = sub.add_parser("video-script", help="Ready-to-shoot 9:16 video ad script & scene-by-scene storyboard (720x1200 safe zone)")
    p_vid.add_argument("--niche", default="ecom")
    p_vid.add_argument("--product", required=True, help="Product, service, or offer")
    p_vid.add_argument("--problem", default="", help="Main customer problem or pain point")
    p_vid.add_argument("--format", dest="format_name", default="ugc_reaction_demo", choices=list(META_FORMAT_TAXONOMY.keys()))
    p_vid.add_argument("--duration", type=int, default=30, help="Target video duration in seconds (default: 30)")
    p_vid.add_argument("--price", type=tcore.positive_float, default=None, help="Haqiqiy narx (berilmasa narx-anchor hisoblanmaydi, taxminiy narx o'ylab topilmaydi)")
    p_vid.add_argument("--market", default="global")
    p_vid.add_argument("--currency", default="")
    p_vid.add_argument("--language", default="uz_latin")
    p_vid.add_argument("--mode", choices=list(VIDEO_MODES), default=None,
                       help="Video pre-production rejimi: sales|organic|plan|motion (berilmasa eski 7 formatli generator o'zgarishsiz ishlaydi)")
    p_vid.add_argument("--lang", default=None, help="Rejim tili: uz|ru|en (--mode bilan; --language dan ustun)")
    p_vid.add_argument("--hooks", type=int, default=3, help="Hook variantlari soni 3..5 (sales/organic)")
    p_vid.add_argument("--awareness", default="problem_aware", choices=list(AWARENESS_STAGES))
    p_vid.add_argument("--content-format", default="expert", choices=list(ORGANIC_FORMATS), help="organic rejimi formati")
    p_vid.add_argument("--motion-type", default="kinetic", choices=list(MOTION_TYPES), help="motion rejimi turi")
    p_vid.add_argument("--ratio", default="9:16", choices=list(MOTION_RATIOS), help="motion rejimi nisbati")
    p_vid.add_argument("--weeks", type=int, default=2, help="plan rejimi: 1|2|4 hafta")
    p_vid.add_argument("--per-week", type=int, default=5, help="plan rejimi: haftasiga videolar soni")
    p_vid.add_argument("--platforms", default="instagram,tiktok,youtube", help="plan rejimi: vergul bilan platformalar")
    p_vid.add_argument("--start-date", default=None, help="plan rejimi: YYYY-MM-DD (berilmasa W1-D1 yorliqlari)")
    p_vid.add_argument("--json", action="store_true")

    p_pda = sub.add_parser("pda-matrix", help="Andromeda Entity-ID & Persona-Desire-Awareness (PDA) Creative Diversity Plan")
    p_pda.add_argument("--niche", default="ecom")
    p_pda.add_argument("--product", required=True)
    p_pda.add_argument("--price", type=tcore.positive_float, default=None, help="Haqiqiy narx (berilmasa narx-anchor hisoblanmaydi, taxminiy narx o'ylab topilmaydi)")
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
    p_copy.add_argument("--price", type=tcore.positive_float, default=None, help="Haqiqiy narx (berilmasa narx-anchor hisoblanmaydi, taxminiy narx o'ylab topilmaydi)")
    p_copy.add_argument("--currency", default="")
    p_copy.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "matrix":
        res = build_matrix(args.niche, args.product, args.price, market=args.market, currency=args.currency)
    elif args.command == "hooks":
        langs = [x.strip() for x in args.languages.split(",") if x.strip()] if args.languages else None
        res = generate_hooks(args.niche, args.offer, languages=langs)
    elif args.command == "fatigue":
        sig: dict = {}
        if args.metrics:
            try:
                sig = metrics_creative_signals(_load_metrics_rows(args.metrics), args.entity_id)
            except ValueError as exc:
                print(f"Xato: {exc}", file=sys.stderr)
                return tcore.EXIT_VALIDATION
        pick = lambda cli, key, dflt: cli if cli is not None else (sig.get(key) if sig.get(key) is not None else dflt)
        hook, hold = pick(args.hook_rate, "hook_rate", None), pick(args.hold_rate, "hold_rate", None)
        if hook is None or hold is None:
            print("Xato: --hook-rate va --hold-rate kerak (yoki video_3s/thruplay bor --metrics)", file=sys.stderr)
            return tcore.EXIT_VALIDATION
        res = analyze_fatigue(hook, hold, pick(args.ctr_drop_pct, "ctr_drop_pct", 0.0), pick(args.frequency, "frequency", 1.5), args.ftir)
        if sig:
            res["metrics_source"] = {"file": args.metrics, "evidence_label": "MEASURED_ACCOUNT_DATA", **sig}
    elif args.command == "iterate":
        keys = ("hook_rate", "hold_rate", "outbound_ctr", "lp_cvr", "qualified_lead_rate")
        sig = {}
        if args.metrics:
            try:
                sig = metrics_creative_signals(_load_metrics_rows(args.metrics), args.entity_id)
            except ValueError as exc:
                print(f"Xato: {exc}", file=sys.stderr)
                return tcore.EXIT_VALIDATION
        cur = {k: (getattr(args, k) if getattr(args, k) is not None else sig.get(k)) for k in keys}
        res = diagnose_creative_iteration(
            cur,
            {k: getattr(args, f"baseline_{k}") for k in keys},
            cpa=args.cpa if args.cpa is not None else sig.get("cpa"), breakeven_cpa=args.breakeven_cpa,
            impressions=args.impressions if args.impressions is not None else sig.get("impressions"),
        )
        if sig and isinstance(res, dict):
            res["metrics_source"] = {"file": args.metrics, "evidence_label": "MEASURED_ACCOUNT_DATA", **sig}
    elif args.command == "video-script" and args.mode:
        try:
            res = generate_video_blueprint(
                mode=args.mode, niche=args.niche, product=args.product, problem=args.problem, lang=args.lang or args.language,
                duration_sec=args.duration, hooks=args.hooks, awareness=args.awareness, price=args.price, currency=args.currency,
                content_format=args.content_format, motion_type=args.motion_type, ratio=args.ratio, weeks=args.weeks,
                per_week=args.per_week, platforms=args.platforms, start_date=args.start_date,
            )
        except ValueError as exc:
            print(f"Xato: {exc}", file=sys.stderr)
            return tcore.EXIT_VALIDATION
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

    if isinstance(res, dict) and args.command in ("video-script", "hooks", "pda-matrix", "ad-copy", "matrix"):
        res["claim_safety"] = lint_unverified_claims(res)

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 72)
    print(f"  🎨 TYRION v8.2 CREATIVE & VIDEO STUDIO — {args.command.upper()}")
    print("=" * 72)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
