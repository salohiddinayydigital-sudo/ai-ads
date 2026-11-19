# Google Ads MCP

- **Rasmiy loyiha:** https://github.com/googleads/google-ads-mcp (README, 2026-11-19 holatida o'qilgan; `source_status: unverified` — to'liq hujjat sahifasi bu yerda tekshirilmagan).
- **O'rnatish (README bo'yicha):** `gcloud auth application-default login`, so'ng `pipx` orqali `.mcp.json` yozuvi; Python 3.11+ va pipx kerak; Google Cloud loyihasida Google Ads API yoqilgan, scope `https://www.googleapis.com/auth/adwords`. Namuna: `docs/integrations.md`.
- **Eslatma:** server sukut bo'yicha faqat o'qish emas — yozuv asboblari bor (`assets_create_asset`, `assets_upload_video_asset`, `labels_manage_labels`, `labels_manage_label_associations`). Faqat o'qish uchun `tools_config.yaml` da bu toifalarni o'chiring. Yozuv asboblari ham change packet bilan (`skills/connect/references/meta-ads-mcp.md` dagi tartib).
- GAQL natijasi `clients/<slug>/data/raw/` ga saqlanadi, `python3 tools/normalize.py google_ads --input ...` bilan `metrics.v1` ga o'tadi.
