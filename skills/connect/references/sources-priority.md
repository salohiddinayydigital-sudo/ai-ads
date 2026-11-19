# Manbalar ustuvorligi

Bir xil ma'lumot bir necha yo'ldan kelsa, yuqoridagisi olinadi. Har snapshot'ga `source` (metrics.v1: `meta_mcp | google_mcp | meta_graph | csv | screenshot`) va dalil yorlig'i yoziladi ([[00-manba]]).

| # | Manba | Qachon | Eslatma |
|---|---|---|---|
| 1 | Rasmiy Meta Ads MCP | sessiyada `ads_get_ad_accounts` kabi asboblar bor | OAuth; o'qish asboblari erkin, yozish — change packet bilan |
| 2 | Google Ads MCP | sessiyada Google Ads MCP asboblari bor | `source_status: unverified` (qarang: `skills/connect/references/google-ads-mcp.md`) |
| 3 | Graph API token | MCP yo'q, `META_ACCESS_TOKEN` bor | `python3 tools/meta-insights-sync.py pull` (faqat o'qish) |
| 4 | CSV/JSON eksport | foydalanuvchi fayl berdi | `python3 tools/normalize.py generic_csv ...` |
| 5 | Screenshot | boshqa yo'l yo'q | qo'lda ko'chirilgan raqamlar, ishonch past, `USER_PROVIDED` |

## Sessiyadagi asboblarni aniqlash

Asboblar **nomi bo'yicha** aniqlanadi (server prefiksi har muhitda har xil: `mcp__<server>__ads_get_ad_accounts`). Nomda `ads_get_ad_accounts` bo'lgan asbob bor bo'lsa, Meta MCP ulangan hisoblanadi. Hech narsa topilmasa, 3–5 yo'lga o'tiladi va foydalanuvchiga ulash yo'li aytiladi (`skills/connect/references/meta-ads-mcp.md`).

Hech qachon asbob mavjudligini taxmin qilma: ro'yxatdan nomini ko'rmasang, ishlatilmaydi.
