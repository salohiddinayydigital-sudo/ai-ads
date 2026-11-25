<!-- v8.2 Charter v2: data-analyst Self-Audit (Pass/Fail). Ref: rules/70-charter-baseline.md §6 -->

# Tahlil sifat darvozasi — Pass/Fail

> `data-analyst` (`export_normalize`, `weekly_pulse`, `experiment_readout`, `client_report`) natijani qaytarishdan oldin shu cheklistdan o'tadi. Bitta **kritik** `FAIL` → **1 marta** qayta tahlil. Metodologiya: `skills/analyze/references/data-analyst-playbook.md`.

| # | Band | Kritik | Pass mezoni |
|---|---|:-:|---|
| 1 | Schema | ✔ | Kirish `tools/normalize.py` orqali `metrics.v1` ga o'tgan; validatsiya xatolari ro'yxatlangan |
| 2 | Tanlama hajmi | ✔ | Xulosa uchun minimal hajm (konversiya, sarf) qayd etilgan; yetmasa `inconclusive` |
| 3 | Atributsiya oynasi | ✔ | Solishtirilayotgan davrlar bir xil oyna va hisobot vaqti bilan |
| 4 | Manba ajratish | ✔ | `MEASURED_ACCOUNT_DATA` va `HEURISTIC_PRIOR_MODEL` aralashtirilmagan |
| 5 | Anomaliya triage | — | Spend/CPA sakrashi tracking uzilishi, pacing yoki haqiqiy o'zgarishga ajratilgan |
| 6 | Takrorlanuvchanlik | — | Ishlatilgan buyruqlar va kirish fayllari `execution_evidence` da |

**Chiqish bloki:** `self_audit: { gate: "pass_fail", score: null, failed_checks: [...], rewrites: <0|1>, label: "HEURISTIC_PRIOR_MODEL" }`
