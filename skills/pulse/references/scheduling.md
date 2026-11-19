# Pulse'ni rejalashtirish

Pulse faqat o'qiydi va hisobot beradi. Buyruq (`python3 tools/pulse.py run --help` dan):

```
python3 tools/pulse.py run --client <slug> [--metrics f.json] [--anomaly-signal f.json] --format both --write --fail-on critical
```

Chiqish kodi: 0 — ok; 1 — `--fail-on` darvozasi (critical/warning topildi); 2 — kirish xatosi. `--write` natijani `clients/<slug>/pulse/<sana>.json|md` ga yozadi. Metrics yo'q bo'lsa standart: `clients/<slug>/data/metrics.v1.json`.

Avval yangi ma'lumotni snapshot + normalize qiling (`skills/connect/references/snapshot-pattern.md`), keyin pulse.

## Variantlar

1. **Claude Code scheduled tasks yoki `/loop`.** Masalan `/loop 1d /pulse <slug>`; vazifa matni: "MCP orqali kechagi insights'ni snapshot qil, normalize, pulse ishga tushir, topilmalarni ayt". (Aniq sintaksis Claude Code versiyasiga bog'liq: `/loop` skill tavsifiga qarang.)
2. **cron (Linux/macOS)**, CSV eksport avtomat tushadigan papka bo'lsa:
   `0 8 * * * cd /yo'l/ai-ads && python3 tools/normalize.py generic_csv --input inbox/ads.csv --out clients/demo/data/metrics.v1.json --currency UZS --date $(date +\%F) && python3 tools/pulse.py run --client demo --format md --write`
3. **Windows Task Scheduler:** amal `python`, argumentlar `tools\pulse.py run --client demo --format md --write`, "Start in" — repo papkasi.
4. **GitHub Actions (CSV bilan):**
```yaml
name: pulse
on:
  schedule: [{cron: "0 4 * * *"}]
jobs:
  pulse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: python3 tools/pulse.py run --client demo --format md --write --fail-on critical
```
   Haqiqiy mijoz ma'lumoti va sirlarni ommaviy repoga qo'ymang; faqat sintetik yoki shaxsiy repo.

Rejalashtirilgan ishda ham hisobga yozish yo'q: `needs_approval` topilmalar foydalanuvchiga hisobot sifatida yetkaziladi.
