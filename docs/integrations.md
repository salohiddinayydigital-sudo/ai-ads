# Optional Live Ad-Platform MCP Integrations (`meta-ads`, `google-ads`)

By default only `tyrion-core` is enabled (`node <root>/hooks/run-hook.cjs --mcp`; declared in `.claude-plugin/plugin.json` for the installed plugin and in `.mcp.json` for the opened repository) so that every session starts in `<100ms` across Windows, macOS, and Linux without external network or OAuth timeouts.

> **Why optional MCP servers are not in `.mcp.json` by default:** Claude Code attempts to launch all entries inside `mcpServers` even if `"disabled": true` is set, causing a 30-second startup timeout when credentials or `uvx`/`pipx` are not configured.

---

## 1. Live Meta Ads MCP (`meta-ads-mcp`)

- **Official Repository:** [pipeboard-co/meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp)
- **Package Registry:** `meta-ads-mcp` via `uvx` ([PyPI / ModelScope MCP Reference](https://www.modelscope.cn/mcp/servers/@pipeboard-co/meta-ads-mcp))
- **Verified Date:** 2026-10-21

### How to Enable
Add the following entry to your project or user `.mcp.json` (`~/.claude.json` or `.mcp.json`):

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "uvx",
      "args": ["meta-ads-mcp"],
      "env": {
        "META_ACCESS_TOKEN": "YOUR_META_SYSTEM_USER_OR_OAUTH_TOKEN",
        "PIPEBOARD_API_TOKEN": "OPTIONAL_PIPEBOARD_TOKEN"
      }
    }
  }
}
```

> **Note:** Tyrion also includes a zero-dependency built-in live Meta Graph API client (`tools/meta-targeting-engine.py` and `tools/meta-insights-sync.py`) that works directly with `META_ACCESS_TOKEN` (from the environment, the plugin setting `Meta access token`, or a project `.env`) without requiring `uvx`.

---

## 2. Google Ads (faqat o'qish) — bir qadamli ulash

- **Rasmiy repozitoriy:** [googleads/google-ads-mcp](https://github.com/googleads/google-ads-mcp) · [hujjat](https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server)
- **Tekshirilgan:** 2026-11-11 (README bo'yicha)

Rasmiy server `search`, `customers_list_accessible_customers`, `metadata` asboblaridan tashqari hisobga **yozadigan**
asboblarni ham beradi (`assets_*`, `labels_*`). Tyrion hisobga yozmaydi, shuning uchun ulagich serverni doim
`tools_config.yaml` bilan `labels: false`, `assets: false` holatida ishga tushiradi. Server tomonida ham yozuv
"Propose & Confirm" bilan himoyalangan, lekin Tyrion uchun asbobning o'zi yo'q bo'lgani ishonchliroq.

### Ulash

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-.}/tools/connect-google-ads.py"          # tekshiradi, rejani ko'rsatadi
python3 "${CLAUDE_PLUGIN_ROOT:-.}/tools/connect-google-ads.py" --apply  # ulaydi
```

Ulagich quyidagilarni o'zi topadi: Developer token (`GOOGLE_ADS_DEVELOPER_TOKEN`), kirish ma'lumoti
(`GOOGLE_APPLICATION_CREDENTIALS` yoki `~/.config/gcloud/application_default_credentials.json`), loyiha
(`GOOGLE_PROJECT_ID`), ixtiyoriy MCC (`GOOGLE_ADS_LOGIN_CUSTOMER_ID`). Nima yetishmasa, aniq buyruq bilan aytadi
va hech narsa o'zgartirmaydi. `--apply` `claude mcp add --scope user google-ads ...` ni bajaradi va faqat o'qish
sozlamasini `~/.tyrion/google-ads/tools_config.yaml` ga yozadi. Olib tashlash: `--remove`.

Oldindan bir marta kerak: `pipx`, Google Cloud loyihasida Google Ads API yoqilgan bo'lishi va
`gcloud auth application-default login --scopes https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform`.

> **Eslatma:** developer token `claude mcp add -e` orqali foydalanuvchi sozlamasiga yoziladi (repozitoriyga emas).
> `.mcp.json` ga qo'lda server qo'shmang: Claude Code ro'yxatdagi barcha serverni ishga tushiradi va sozlanmagan
> bo'lsa, sessiya sekin ochiladi.

---

## 3. Sarf kuzatuvchisi (`monitors/monitors.json`)

Plugin o'rnatilganda Claude Code `tools/spend-watch.py` ni sessiya bilan birga fonda ishga tushiradi. U har 30
daqiqada Meta akkauntining bugungi sarfini kunlik byudjet va kun o'tgan ulushga solishtiradi, **holat
o'zgargandagina** xabar beradi:

| Holat | Qachon |
|---|---|
| `OVERPACE` | kunning 15% idan keyin sarf rejadagidan 20% dan ko'p |
| `OVER_BUDGET` | sarf kunlik byudjetdan oshdi |
| `UNDERPACE` | kunning 60% idan keyin sarf rejaning yarmidan kam |

Faqat Graph API GET so'rovlari; pauza yoki byudjet o'zgartirish yo'q. Kunlik byudjet = faol CBO kampaniyalar +
byudjeti adset darajasida bo'lgan faol adsetlar (lifetime byudjet hisobga kirmaydi, bu haqda aytiladi).

**Muhim:** monitor jarayoni plugin sozlamalarini (`/plugin configure tyrion`) olmaydi. Token va akkaunt muhit
o'zgaruvchisidan (`META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`) yoki loyiha `.env` dan olinadi. Ular yo'q bo'lsa,
monitor bitta satr yozib jim turadi. Qo'lda sinash: `python3 tools/spend-watch.py --once`.
