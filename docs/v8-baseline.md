# Tyrion v8.0 — Baseline (o'lchangan, 2026-11-19)

| O'lchov | Qiymat | Buyruq |
|---|---|---|
| Testlar | `364 passed, 1 skipped` | `python3 -m pytest -q tests` |
| Doctor | `19 tekshiruv, 0 ogohlantirish, 0 xato` (bu muhitda bilim grafi yangi) | `python3 tools/doctor.py` |
| Katalog / drift / vault gate | yashil (449 element, 27 juftlik) | `catalog.py check`, `catalog.py drift`, `vault-audit.py . --gate` |
| `claude plugin validate .` | `Validation passed with warnings` (ogohlantirish: README'da `/plugin install tyrion --marketplace ...` qatori yo'q — Bosqich 6 da tuzatiladi) | |
| Doimiy description narxi | **41 273 belgi ≈ 10 363 token** | `python3 tools/token-budget.py` |
| — skill | 61 ta · 26 926 belgi · 6 756 token | |
| — agent | 36 ta · 11 259 belgi · 2 828 token | |
| — buyruq | 27 ta (hammasi model ko'radi) · 3 088 belgi · 779 token | |
| 300 belgidan uzun description | 64 ta | |
| Eng qimmat 10 | social 1005, offers 969, customer-research 953, prospecting 829, tyrion-universal 770, copywriting 753, analytics 700, seo-audit 679, content-strategy 659, cro 654 (belgi) | |

Token = belgilar/4 (`HEURISTIC_PRIOR_MODEL`); haqiqiy tokenizer emas.

## Eng katta fayllar (git ls-files, bayt)

graphify-out/graph.json 318 394 · manifests/catalog.json 197 934 · tools/skill-search.py 134 322 ·
tools/meta-targeting-engine.py 131 202 · tools/meta-audience.py 81 493 · tools/creative-matrix.py 62 087 ·
manifests/workflows.json 44 978 · tools/catalog.py 31 549 · tools/ad-export-analyzer.py 27 314 · tools/doctor.py 26 620.

## Inventar

36 agent · 61 skill · 27 buyruq · 30 asbob · 100 wiki · 9 playbook · 9 qoida · 6 kontekst · 617 git fayl.

## Eslatma

`docs/v8-roadmap.md` mavjud emas (topshiriqda "bor bo'lsa" deyilgan) — raqobatchi tahlili/KPI manbasi sifatida faqat topshiriq matni ishlatiladi.
