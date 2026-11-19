# Rasmiy Meta Ads MCP

`source_status: verified` — rasmiy Meta hujjatidan o'qildi (2026-11-19): [Get started](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-get-started), [Overview](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-overview), [Ad creation and management](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-tools-ad-creation-and-management), [Rules best practices](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-rules-best-practices). Hujjat indeksi: https://developers.facebook.com/documentation/ads-commerce/llms.txt

- **Manzil:** `https://mcp.facebook.com/ads` — Meta hosting qiladigan masofaviy MCP server.
- **Ulash (Claude Code):** `claude mcp add --transport http --client-id <META_APP_ID> meta-ads https://mcp.facebook.com/ads` (rasmiy hujjatdagi buyruq). Meta ilovasi egasi bo'lish shart emas: ilovasiz yo'l — [How to set up Meta ads AI connectors](https://www.facebook.com/business/help/1456422242197840) (bu sahifa bu muhitdan ochilmadi, o'qilmadi).
- **Meta ilovasi bilan:** developers.facebook.com/apps da ilova yarating yoki mavjudini oching va **Create & manage ads with ads MCP server** use case'ini qo'shing. OAuth uchun ilovadagi *redirect URL* MCP klient bilan mos bo'lishi kerak (Facebook Login for Business).
- **Autentifikatsiya (3 usul):** OAuth (Facebook Login for Business) · user access token (Graph API Explorer yoki o'z OAuth oqimi) · system user access token (**faqat Employee-rol**; Admin-rol tokenlari serverga kira olmaydi). Dasturiy ulanish: `Authorization: Bearer <ACCESS_TOKEN>` sarlavhasi.
- **Ruxsatlar:** kamida `ads_mcp_management` va `ads_read` yoki `ads_management`; qo'shimcha asboblar uchun `ads_management`, `catalog_management`, `business_management`, `pages_show_list`, `instagram_basic`.
- **Yozish asboblari entity'ni PAUSED holatda yaratadi;** `ads_activate_entity` esa uni faol qiladi va **sarf boshlanadi**. Hujjat: faollashtirishdan oldin AI klient tasdiq so'raydi. Tyrion Spend-Guard bu oldiga qo'shimcha darvoza qo'yadi.

## O'qish asboblari (erkin ishlatiladi)

`ads_get_ad_accounts`, `ads_get_ad_entities`, `ads_insights_performance_trend`, `ads_insights_anomaly_signal`, `ads_insights_industry_benchmark`, `ads_insights_performance_vs_peers`, `ads_get_opportunity_score`, `ads_get_dataset_quality`, `ads_library_search`, `ads_account_get_activity_logs`, `ads_experiment_abtest_create_test` / `ads_experiment_lift_create_test` (nomida `create` bor, lekin test tayyorlaydi: faqat change packet bilan, `skills/connect/references/snapshot-pattern.md`).

Nomlar sessiyada kuzatilgan; yozish asboblarining rasmiy ro'yxati (2026-11-19, hujjatdan): `ads_create_campaign`, `ads_create_ad_set`, `ads_create_ad` (paused), `ads_update_entity`, `ads_activate_entity`, `ads_create_creative`, `ads_boost_ig_post`, `ads_create_custom_audience`, `ads_update_custom_audience`, `ads_update_custom_audience_users` (hashlangan shaxsiy ma'lumot yuklaydi), `ads_delete_custom_audience`. `ads_get_ad_entities` — asosiy hisobot asbobi. Versiyaga qarab o'zgarishi mumkin.

## Yozish asboblari (Spend-Guard bilan himoyalangan)

`ads_create_*`, `ads_update_entity`, `ads_activate_entity`, `ads_duplicate_entity`, `ads_delete_*`, `ads_creative_*`.

1. Avval `python3 tools/spend-guard.py packet ...` bilan change packet tayyorlanadi: `clients/<slug>/changes/<id>.json`.
2. Packet'da **rollback rejasi majburiy**: o'qilgan rasmiy sahifalardagi asboblar ro'yxatida o'zgarishni qaytaruvchi (undo) asbob ko'rsatilmagan; Tyrion uni mavjud deb hisoblamaydi.
3. Foydalanuvchi packet'ni ko'rib `approved_by_user: true` qiladi; packet 24 soatdan eski bo'lmasligi va entity mos kelishi kerak.
4. PreToolUse hook (`strict` profilda `deny`, `standard` da `ask`) packet'siz yozishni to'xtatadi ([[40-xavfsizlik-va-hisob]]).

## Dalil yorliqlari

- Hisob ma'lumoti: `MEASURED_ACCOUNT_DATA`.
- `ads_insights_industry_benchmark` / `ads_insights_performance_vs_peers` natijasi: `PLATFORM_BENCHMARK` ([[00-manba]]).

## Meta tomonidagi qoidalar (server-side Rules) — ikkinchi himoya qatlami

Hujjat (2026-11-19): *ads MCP server rules* AI agentning aniq harakatini aniq reklama hisobi yoki katalogda **rad etadi**. Masalan: byudjetni 20% dan ortiq oshirishni yoki yetkazib berish holatini o'zgartirishni taqiqlash. Harakatlar: `create_campaign`, `create_ad_set`, `create_ad`, `edit_budget` (`percentage_change` / `absolute_change` / `absolute_max`), `edit_targeting`, `edit_creative`, `edit_status`, `all`. API: `https://ads-api.facebook.com/v25.0/marketing-api/businesses/<BUSINESS_ID>/accounts/act_<AD_ACCOUNT_ID>/ads_mcp_rules`. **Cheklangan mavjudlik:** biznes ro'yxatdan o'tmagan bo'lsa, hisob endpoint'i xato kodi 10, katalog endpoint'i HTTP 403 qaytaradi. Avtomatlashtirish uchun system user tokeni tavsiya etiladi. Tyrion hook'i (lokal) va Meta qoidalari (server) bir-birini almashtirmaydi: ikkalasini yoqing.
