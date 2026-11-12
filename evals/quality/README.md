# Sifat Evalida (evals/quality/)

Tyrion agentlar jamoasining **jamoaviy ish sifatini** o'lchaydigan eval to'plami.
5 asosiy ish x 2-3 stsenariy, barchasi `examples/demo-brand` sinov namunasi asosida.

## Tuzilma

| Fayl | Vazifasi |
|---|---|
| `scenarios.json` | 12 stsenariy (5 ish: audit, budget, kreativ, hisobot, tracking) — har birida worker prompti, manba aktivlar va deterministik tekshiruvlar |
| `rubric.json` | Hakam-agent rubrikasi: 4 mezon (evidence, accuracy, actionability, language_clarity) x 0-2 ball |
| `judge-prompt.md` | Hakam-agentga beriladigan ko'rsatma |
| `run.py` | Deterministik tekshiruv runneri (0 token) + hakam ballarini birlashtirish |
| `runs/baseline/` | Hozirgi agentlar bilan yuritilgan baseline artifactlari |
| `baseline.json` | Baseline ball — 3-4-qadamlar solishtiradigan boshlang'ich natija |

## 5 asosiy ish

1. **audit** — dalilga asoslangan platforma auditi (Meta, Google, Telegram)
2. **budget** — byudjet reja va Spend-Guard bo'ysunishi
3. **kreativ** — platforma limitlariga mos sotuv matni (Reels 125, Telegram 160 belgi)
4. **hisobot** — blended metrika va manba shaffofligi (MEASURED vs HEURISTIC)
5. **tracking** — Pixel/CAPI diagnostika (dedup, EMQ)

## Ball

- **Deterministik** (run.py): har stsenariyda 2-6 tekshiruv, pass/fail — skript yuritadi.
- **Hakam** (hakam-agent): har stsenariyda 4 mezon x 0-2 = maks 8 ball.
- Jami: deterministik 44 + hakam 96 = **140 maksimum**.

## Yuritish

```bash
# 1. Worker agentlar artifactlarni yozadi:
#    evals/quality/runs/<run-name>/<stsenariy-id>/artifact.md
# 2. Hakam-agent rubrika asosida ball qo'yadi va judge-scores.json yozadi
# 3. Birlashtirish:
python3 evals/quality/run.py --runs evals/quality/runs/baseline \
  --judge evals/quality/judge-scores.json \
  --out evals/quality/baseline.json
```

Baseline solishtirish (3-4-qadamlarda): xuddi shu buyruq yangi `--runs` papkasi
bilan yuritiladi va `--out` natijasi `baseline.json` bilan yonma-yon qo'yiladi.
Qabul mezoni: hech bir stsenariyda ball boshlang'ichdan pasaymagan, umumiy ball yuqori.
