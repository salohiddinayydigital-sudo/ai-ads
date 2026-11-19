# Integratsiyalar va ma'lumot manbalari (v8)

`.mcp.json` sukut bo'yicha faqat `tyrion-core` ni yoqadi (`node "${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cjs" --mcp`): sessiya tez ochiladi, OAuth/tarmoq kutilmaydi. Reklama platformalari MCP'lari **ixtiyoriy** va foydalanuvchi o'zi ulaydi (`.mcp.json` ga qo'shilsa, sozlanmagan server 30 soniyalik timeout berishi mumkin).

## 1. Manbalar ustuvorligi

1. Rasmiy Meta Ads MCP → 2. Google Ads MCP → 3. Graph API token → 4. CSV/JSON eksport → 5. Screenshot.

Tafsilot: `skills/connect/references/sources-priority.md`. Asboblar **nomi bo'yicha** aniqlanadi (`ads_get_ad_accounts` va h.k.); ro'yxatda ko'rinmagan asbob ishlatilmaydi.

## 2. MCP → snapshot → kod

O'qish asbobi → `clients/<slug>/data/raw/<YYYY-MM-DD>-<source>.json` → `python3 tools/normalize.py <adapter> --input ... --out clients/<slug>/data/metrics.v1.json` → `pulse.py`, `ad-export-analyzer.py --metrics`, `calculator.py`. KPI xayolda hisoblanmaydi. Adapterlar: `meta_mcp`, `meta_graph`, `google_ads`, `tiktok_csv`, `telegram_csv`, `generic_csv` (`python3 tools/normalize.py list`). Sxema: `schemas/metrics.v1.json`. Batafsil: `skills/connect/references/snapshot-pattern.md`.

## 3. Rasmiy Meta Ads MCP

- Manzil: `https://mcp.facebook.com/ads` — **`source_status: unverified`**. Ikkilamchi manbadan (2026-11-19); rasmiy sahifa (`developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-get-started`) bu muhitdan ochilmadi. Ulashdan oldin o'sha sahifada URL va OAuth qadamlarini tasdiqlang.
- Taxminiy ulash: `claude mcp add --transport http meta-ads https://mcp.facebook.com/ads`, so'ng OAuth.
- O'qish asboblari: `ads_get_ad_accounts`, `ads_get_ad_entities`, `ads_insights_performance_trend`, `ads_insights_anomaly_signal`, `ads_insights_industry_benchmark`, `ads_insights_performance_vs_peers`, `ads_get_opportunity_score`, `ads_get_dataset_quality`, `ads_library_search`, `ads_account_get_activity_logs`.
- Yozish asboblari: `ads_create_*`, `ads_update_entity`, `ads_activate_entity`, `ads_duplicate_entity`, `ads_delete_*`, `ads_creative_*`, `ads_experiment_*_create_test` — **Spend-Guard hook** bilan himoyalangan: tasdiqlangan change packet (`clients/<slug>/changes/<id>.json`, rollback rejasi bilan) kerak. Rasmiy Meta MCP'da undo yo'q.
- Benchmark asboblari natijasi `PLATFORM_BENCHMARK` yorlig'i bilan (`rules/00-manba.md`).

## 4. Google Ads MCP (rasmiy)

- Loyiha: https://github.com/googleads/google-ads-mcp · hujjat: https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server (2026-10-21 da tekshirilgan; README holati 2026-11-19).
- Talab: Python 3.11+, `pipx`, Google Cloud loyihasida Google Ads API, scope `https://www.googleapis.com/auth/adwords`, `gcloud auth application-default login`.
- Diqqat: server faqat o'qish bilan cheklanmagan — yozuv asboblari bor (`assets_*`, `labels_*`); `tools_config.yaml` da o'chirish mumkin.

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "pipx",
      "args": ["run", "--spec", "git+https://github.com/googleads/google-ads-mcp.git", "google-ads-mcp"],
      "env": {
        "GOOGLE_ADS_CREDENTIALS": "/path/to/google-ads.yaml",
        "GOOGLE_ADS_DEVELOPER_TOKEN": "YOUR_DEVELOPER_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "YOUR_MCC_ID"
      }
    }
  }
}
```

(`env` nomlari oldingi hujjatdan saqlangan; rasmiy README'da tasdiqlang.) Batafsil: `skills/connect/references/google-ads-mcp.md`.

## 5. Graph API (token bilan)

`META_ACCESS_TOKEN` (system user tokeni) bilan: `python3 tools/meta-insights-sync.py pull` (insights, faqat o'qish), `python3 tools/meta-targeting-engine.py` (interest tekshiruvi). Qo'shimcha uchinchi tomon MCP (ixtiyoriy): [pipeboard-co/meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp) (`uvx meta-ads-mcp`, 2026-10-21 da tekshirilgan) — uni ulasangiz ham yozish asboblari change packet siyosatiga bo'ysunadi.

## 6. CSV/JSON va screenshot

Eksportni `normalize.py generic_csv` (yoki `tiktok_csv`, `telegram_csv`) bilan `metrics.v1` ga aylantiring. Screenshot — oxirgi chora: raqamlar `USER_PROVIDED`, ishonch past.

## 7. CRM

`python3 tools/crm-bridge.py` — AmoCRM/Bitrix24/CSV → lid sifati hisoboti va CAPI payload (standart dry-run). Qarang: `skills/lead-quality/SKILL.md`.

## 8. Xavfsizlik

Token va kalitlar faqat env'da; commit qilinmaydi (`tyrion-shield.py scan`). Jonli hisobga o'zgartirish — faqat tasdiqlangan change packet bilan.
