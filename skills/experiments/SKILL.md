---
name: experiments
description: "Experiment ledger: design (sample size, MDE), register, read out (z-test, Bayesian), promote lessons; Meta A/B and lift packets. Use for 'a/b test', 'eksperiment', 'test natijasi', 'split test', эксперимент."
triggers:
- "a/b test"
- "split test"
- "eksperiment"
- "gipoteza sinovi"
- "creative test"
- "а/б тест"
- "сплит тест"
- "гипотеза"
aliases:
- "ab-test"
- "experiment"
- "split-test"
- "ads-test"
domains:
- "testing"
- "creative"
- "analytics"
platforms:
- "meta"
- "google"
- "tiktok"
- "multi-platform"
attached_agents: [creative-strategist, data-analyst]
related_skills: []
references:
- "skills/experiments/references/ads-test.md"
risk_level: low
output_contract: "Structured deliverable with evidence labels, assumptions, tools actually run and an honest execution report"
---

## Ish tartibi (`python3 tools/experiments.py <buyruq>`)

1. **design** — namuna hajmi va byudjet: `design --baseline 0.05 --mde 0.2 [--mde-abs] [--alpha] [--power] [--arms] [--cost-per-unit | --daily-budget --target-cpa] [--currency]`. Hisob `calculator.py` mantig'i bilan; chiqishdagi taxminlar o'qiladi.
2. **register** — `register --client <slug> --name ... --hypothesis ... --metric ... --baseline ... --mde ... --n-per-arm ... [--owner --start --variants --domain --synthetic]` testni `clients/<slug>/ledger.jsonl` ga yozadi.
3. **readout** — `readout --client <slug> --id <EXP> --control-n --control-conv --variant-n --variant-conv [--alpha --seed]`: ikki proporsiya z-testi + Bayes "yutish ehtimoli"; hukm `WIN | LOSS | INCONCLUSIVE`. Har guruhda konversiya 30 dan kam yoki reja hajmiga yetilmagan bo'lsa — doim INCONCLUSIVE; buni foydalanuvchiga ochiq ayt.
4. **promote** — takrorlangan yoki ishonchli natijani `tools/instincts.py add` ga uzatadi (`--dry-run` bilan oldindan ko'r).
5. **packet** — Meta native A/B yoki lift test uchun change packet: `packet --client <slug> --id <EXP> --kind native_ab|lift [--stdout]`. Test avto-yaratilmaydi; `ads_experiment_abtest_create_test` / `ads_experiment_lift_create_test` faqat foydalanuvchi packet'ni tasdiqlagach.

Qoida: test davomida bitta o'zgaruvchi; to'xtash qoidasi oldindan yoziladi; natijadan keyin qaror `client-workspace.py decision add` ga.

## Manbalar

| Fayl | Mazmun |
|---|---|
| `skills/experiments/references/ads-test.md` | v7.1 test dizayni matni (gipoteza, randomizatsiya, guardrail) |
