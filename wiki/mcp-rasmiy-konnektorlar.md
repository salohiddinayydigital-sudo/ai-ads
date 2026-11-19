---
name: mcp-rasmiy-konnektorlar
description: "Rasmiy Meta Ads MCP (mcp.facebook.com/ads) va Google Ads MCP (googleads/google-ads-mcp): manzil, kirish usuli, yozish asboblari xavfi va Tyrion qoidasi"
tags: [mcp, meta-ads, google-ads, integratsiya, spend-guard]
source: "Meta developers (Ads MCP Server overview, blog 2026-07-16) va googleads/google-ads-mcp GitHub repozitoriysi; URL'lar matn ichida"
source_status: url_cited
updated: 2026-11-19
---

# Rasmiy MCP konnektorlar (Meta Ads, Google Ads)

> Bog'lanishlar: [[mcp-va-multi-harness-integratsiya]] · [[40-xavfsizlik-va-hisob]] · [[00-manba]] · [[meta-kampaniya-tuzilmalari]]

**Tekshiruv holati (2026-11-19):** rasmiy URL'lar qidiruvda topildi, lekin sahifa matni to'liq o'qilmadi; quyidagilar qidiruv xulosasi asosida (`url_cited`). Narx/limit yo'q.

## Meta Ads MCP
Manbalar: https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-overview · https://developers.facebook.com/blog/post/2026/07/16/meta-ads-mcp-server/
- Rasmiy hujjat serverni `https://mcp.facebook.com/ads` deb ko'rsatadi (qidiruv natijasi, hujjat URL'i yuqorida). Ulash: Claude Code'da `claude mcp add --transport http ... meta-ads https://mcp.facebook.com/ads`; OAuth Facebook Login for Business orqali (Meta Managed Account ham mumkin). Meta ilova ID'si (client id) talabi hujjatda qanday ekani to'liq tasdiqlanmadi: `unverified`.
- Holat: ikkilamchi manbalar open beta 2026-04-29 deydi; Meta dev blogi (2026-07-16) serverni dasturchilar uchun mavjud deb e'lon qiladi. `unverified` (aniq sana rasmiy sahifadan tasdiqlanmadi).
- Asboblar: o'qish (hisobotlar, insights, benchmark), yozish (`ads_create_*`, `ads_update_entity`, `ads_activate_entity`, `ads_duplicate_entity`, `ads_delete_*`, `ads_creative_*`) va eksperiment asboblari (A/B, lift). Ikkilamchi manba ~29 asbob deydi; rasmiy hujjat 7 toifa deydi. `unverified`.
- **Undo yo'q:** yozish asboblari o'zgartirishni qaytarmaydi. Tyrion qoidasi: yozish faqat tasdiqlangan change packet (rollback rejasi bilan) orqali, hook `PreToolUse` darvozasi bilan.

## Google Ads MCP
- Rasmiy loyiha: https://github.com/googleads/google-ads-mcp (mahalliy ishga tushirish, `gcloud auth application-default login`, adwords scope). Rasmiy hosted endpoint repoda ko'rsatilmagan.
- Standart rejimda faqat o'qish emas: yozuv asboblari (`assets_*`, `labels_*`) bor; faqat o'qish uchun `tools_config.yaml` da toifalarni o'chirish kerak. `url_cited`.

## Tyrion qoidasi
Manbalar ustuvorligi: rasmiy Meta Ads MCP → Google Ads MCP → token bilan Graph API → CSV/JSON → screenshot ([[mcp-va-multi-harness-integratsiya]]). Xom javob `clients/<slug>/data/raw/` ga saqlanadi, keyin `normalize.py`. `PLATFORM_BENCHMARK` yorlig'i faqat rasmiy benchmark asbobidan.
