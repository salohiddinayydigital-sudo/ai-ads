---
description: Boshlash — demo yoki yangi mijoz uchun 5 savolli wizard, birinchi tezkor natija va HTML hisobot
argument-hint: [demo | <mijoz>]
---

# /start — Tyrion 8 bilan boshlash

Vazifa: **$ARGUMENTS**

## `demo` bo'lsa (savolsiz, jonli hisobsiz)

`python3 tools/tyrion.py demo` — sintetik `examples/demo-brand` → `client-workspace init` → baseline → `pulse` → **HTML hisobot** (`output/demo/demo-brand-report.html`). Natijani foydalanuvchiga 5 qatorda tushuntir (topilgan 3 ogohlantirish: CPA drift, tracking uzilishi, charchoq) va `/connect` ni taklif qil.

## Yangi mijoz bo'lsa — ketma-ketlik (qadamni o'tkazib yuborma)

1. **Muhitni aniqla.** Qaysi harness (Claude Code / Codex / Cursor / Windsurf) va qaysi konnektorlar bor: sessiyadagi asboblar NOMI bo'yicha (`ads_get_ad_accounts` — rasmiy Meta Ads MCP; Google Ads MCP; yo'q bo'lsa CSV/screenshot). Batafsil: `skills/connect/SKILL.md`.
2. **Ko'pi bilan 5 ta savol** (95% qonun: javobsiz taxmin qilma; allaqachon ma'lum bo'lganini so'rama):
   1. Biznes nima va qaysi bozor/til (UZ/RU/EN)?
   2. Offer va narx (o'rtacha chek)?
   3. Marja yoki maqsadli CPA?
   4. Oylik/kunlik byudjet?
   5. Asosiy kanal (Meta, Telegram, Google, TikTok…)?
3. **Mijoz ish maydoni:** `python3 tools/client-workspace.py init --client <slug> --market <uz|…> --lang <uz|ru|en> --budget <…> --target-cpa <…> --aov <…> --margin-pct <…> --event <Lead|Purchase> --scaffold`.
4. **Birinchi tezkor natija** (bittasini tanla): CSV eksport → `python3 tools/normalize.py generic_csv --input <fayl> --out clients/<slug>/data/metrics.v1.json` va `python3 tools/ad-export-analyzer.py analyze --metrics …`; screenshot → qo'lda o'qib `UNVERIFIED` yorlig'i bilan audit; MCP → `connect` skilli (snapshot → normalize → tahlil); hech narsa yo'q → demo.
5. **HTML hisobot:** `python3 tools/report-html.py --client <slug> --root clients --lang <uz|ru|en> --out output/<slug>-report.html`.

Oxirida: client state yangilangan (`client-workspace.py state get`), keyingi qadamlar egasi va metrikasi bilan, hisobga yozish faqat Spend-Guard change packet orqali.
