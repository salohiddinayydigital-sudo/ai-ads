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

**Tekshiruv holati (2026-11-19):** Meta qismi rasmiy `developers.facebook.com` sahifalaridan to'g'ridan-to'g'ri o'qildi (`verified`); Google qismi repo README'si bo'yicha (`url_cited`). Narx/limit yo'q.

## Meta Ads MCP
Manbalar: https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-overview · https://developers.facebook.com/blog/post/2026/07/16/meta-ads-mcp-server/
- **Manzil (verified):** `https://mcp.facebook.com/ads`, Meta hosting qiladigan masofaviy server. Ulash: `claude mcp add --transport http --client-id <META_APP_ID> meta-ads https://mcp.facebook.com/ads`. Autentifikatsiya: OAuth (Facebook Login for Business), user token yoki system user token (faqat Employee-rol). Ruxsatlar: `ads_mcp_management` + `ads_read` yoki `ads_management`. Manba: [Get started](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-get-started).
- **Asboblar (verified):** hujjat 7 toifani ko'rsatadi: hisobotlar, reklama yaratish/boshqarish, katalog, signal/datasetlar, yordam, A/B va lift testlar, faollik jurnali. Yozish asboblari entity'ni **paused** yaratadi, `ads_activate_entity` sarfni boshlaydi; AI klient faollashtirishdan oldin tasdiq so'raydi.
- **Server-side Rules (verified, cheklangan mavjudlik):** biznes AI agent harakatlarini (budjet oshirish, status o'zgartirish va h.k.) hisob/katalog darajasida taqiqlay oladi. Batafsil: `skills/connect/references/meta-ads-mcp.md`.
- Holat sanalari: ikkilamchi manbalar open beta 2026-04-29 deydi; Meta dev blogi 2026-07-16. Bu sanalar `unverified` (sahifa to'g'ridan-to'g'ri o'qilmadi).
- **Undo:** o'qilgan rasmiy sahifalardagi asboblar ro'yxatida o'zgarishni qaytaruvchi asbob ko'rsatilmagan. Tyrion qoidasi: yozish faqat tasdiqlangan change packet (rollback rejasi bilan) orqali, `PreToolUse` hook darvozasi bilan.

## Google Ads MCP
- Rasmiy loyiha: https://github.com/googleads/google-ads-mcp (mahalliy ishga tushirish, `gcloud auth application-default login`, adwords scope). Rasmiy hosted endpoint repoda ko'rsatilmagan.
- Standart rejimda faqat o'qish emas: yozuv asboblari (`assets_*`, `labels_*`) bor; faqat o'qish uchun `tools_config.yaml` da toifalarni o'chirish kerak. `url_cited`.

## Tyrion qoidasi
Manbalar ustuvorligi: rasmiy Meta Ads MCP → Google Ads MCP → token bilan Graph API → CSV/JSON → screenshot ([[mcp-va-multi-harness-integratsiya]]). Xom javob `clients/<slug>/data/raw/` ga saqlanadi, keyin `normalize.py`. `PLATFORM_BENCHMARK` yorlig'i faqat rasmiy benchmark asbobidan.
