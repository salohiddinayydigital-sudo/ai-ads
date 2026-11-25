<!-- v8.2 Charter v2: budget-analyst Self-Audit (Pass/Fail). Ref: rules/70-charter-baseline.md §6 -->

# Byudjet hisob-kitobi sifat darvozasi — Pass/Fail

> `budget-analyst` (`unit_economics`, `scaling_decision`, `pacing_emergency`, `channel_mix`) natijani qaytarishdan oldin quyidagi cheklistdan o'tadi. Bitta **kritik** band `FAIL` → natija qaytarilmaydi, **1 marta** qayta hisoblanadi.

| # | Band | Kritik | Pass mezoni |
|---|---|:-:|---|
| 1 | Asbob manbasi | ✔ | Har raqam `tyrion_media_calculator` / `tyrion_breakdown_effect` chiqishidan; qo'lda hisob yo'q |
| 2 | Break-even | ✔ | Break-even CPA va ROAS (marja, chek, qaytarish, soliq bilan) ko'rsatilgan |
| 3 | Breakdown Effect | ✔ | Placement/ad set kesishdan oldin marginal CPA tekshirilgan (o'rtacha CPA tuzog'i yo'q) |
| 4 | MER / blended tekshiruv | ✔ | In-platform ROAS biznes daromadi (MER, CRM) bilan solishtirilgan yoki `unknown` deb belgilangan |
| 5 | Spend-Guard | ✔ | > +20% o'zgarish yoki yangi kampaniya → `tyrion_spend_guard` draft + rollback |
| 6 | Sensitivity | — | Base / downside / upside ssenariy (CPA ±20%) jadvali |
| 7 | Valyuta va davr | — | Valyuta (UZS/USD), kurs, davr va atributsiya oynasi ochiq |
| 8 | Dalil yorliqlari | — | `MEASURED_ACCOUNT_DATA` vs `HEURISTIC_PRIOR_MODEL` vs `ASSUMPTION` ajratilgan |

**Chiqish bloki:** `self_audit: { gate: "pass_fail", score: null, failed_checks: [...], rewrites: <0|1>, label: "HEURISTIC_PRIOR_MODEL" }`
