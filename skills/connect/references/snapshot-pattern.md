# MCP → snapshot → kod

KPI hech qachon "xayolda" hisoblanmaydi. Tartib:

1. **O'qish.** MCP o'qish asbobi chaqiriladi (jonli hisobga yozmaydi).
2. **Snapshot.** Xom javob `clients/<slug>/data/raw/<YYYY-MM-DD>-<source>.json` ga saqlanadi (masalan `2026-11-19-meta_mcp.json`). PII va tokenlar saqlanmaydi.
3. **Normalizatsiya.** `python3 tools/normalize.py meta_mcp --input clients/<slug>/data/raw/<fayl>.json --out clients/<slug>/data/metrics.v1.json --account-id <id> --currency <KOD>`. Xato bo'lsa exit 2 va tushunilmagan ustunlar ro'yxati qaytadi; to'qib to'ldirilmaydi. Tekshirish: `python3 tools/normalize.py validate <fayl>`.
4. **Tahlil.** `python3 tools/pulse.py run --client <slug>`, `ad-export-analyzer.py`, `calculator.py`, `creative-analytics.py`.
5. **Holat.** Natija `client-workspace.py state set` / `decision add` bilan yoziladi.

Yozish (o'zgartirish) alohida yo'l: change packet → foydalanuvchi tasdig'i → hook → asbob (`skills/connect/references/meta-ads-mcp.md`).
