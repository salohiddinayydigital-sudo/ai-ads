# Rasmiy Meta Ads MCP

- **Manzil:** `https://mcp.facebook.com/ads` — `source_status: unverified`. Ikkilamchi manbadan (veb-qidiruv natijasi, 2026-11-19); rasmiy sahifa `developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-get-started` bu muhitdan ochilmadi. Tasdiqlash: o'sha sahifani brauzerda ochib URL va OAuth qadamlarini solishtiring.
- **Ulash (taxminiy, tasdiqlanmagan):** Claude Code'da `claude mcp add --transport http meta-ads https://mcp.facebook.com/ads`, so'ng OAuth oynasida ruxsat. Aniq flag'lar (masalan `--client-id`) rasmiy sahifadan tekshiriladi.

## O'qish asboblari (erkin ishlatiladi)

`ads_get_ad_accounts`, `ads_get_ad_entities`, `ads_insights_performance_trend`, `ads_insights_anomaly_signal`, `ads_insights_industry_benchmark`, `ads_insights_performance_vs_peers`, `ads_get_opportunity_score`, `ads_get_dataset_quality`, `ads_library_search`, `ads_account_get_activity_logs`, `ads_experiment_abtest_create_test` / `ads_experiment_lift_create_test` (nomida `create` bor, lekin test tayyorlaydi: faqat change packet bilan, `skills/connect/references/snapshot-pattern.md`).

Bu ro'yxat bir sessiyada kuzatilgan nomlar; versiyaga qarab o'zgarishi mumkin.

## Yozish asboblari (Spend-Guard bilan himoyalangan)

`ads_create_*`, `ads_update_entity`, `ads_activate_entity`, `ads_duplicate_entity`, `ads_delete_*`, `ads_creative_*`.

1. Avval `python3 tools/spend-guard.py packet ...` bilan change packet tayyorlanadi: `clients/<slug>/changes/<id>.json`.
2. Packet'da **rollback rejasi majburiy**: rasmiy Meta MCP'da undo yo'q.
3. Foydalanuvchi packet'ni ko'rib `approved_by_user: true` qiladi; packet 24 soatdan eski bo'lmasligi va entity mos kelishi kerak.
4. PreToolUse hook (`strict` profilda `deny`, `standard` da `ask`) packet'siz yozishni to'xtatadi ([[40-xavfsizlik-va-hisob]]).

## Dalil yorliqlari

- Hisob ma'lumoti: `MEASURED_ACCOUNT_DATA`.
- `ads_insights_industry_benchmark` / `ads_insights_performance_vs_peers` natijasi: `PLATFORM_BENCHMARK` ([[00-manba]]).
