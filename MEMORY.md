# MEMORY.md — Operator ish maydoni xotirasi va aktiv gipotezalar

> **Qoida:** Bu faylni qisqa saqlang (`<= 90` qator). Mijozlararo qayta ishlatiladigan naqshlarni `manifests/instincts.json` ga (`/learn`), mijozga xos ma'lumotni `clients/<slug>/` ga yozing.

## 1. Aktiv ish maydoni sozlamalari
- **Standart bozor paketi:** `global` (har bir mijoz uchun `--market uz|us|eu|uk|mena|latam|sea|in` yoki `TYRION_MARKET` bilan almashtiriladi).
- **Standart valyuta:** Akkaunt valyutasi, ISO 4217 (`USD`, `EUR`, `GBP`, `JPY`, `BRL`, `INR`, `AED`, `UZS`).
- **Hook profili:** `standard` (`TYRION_HOOK_PROFILE=minimal|standard|strict`).

## 2. Aktiv kampaniya gipotezalari (shablon)
| Sana | Mijoz / Akkaunt | Gipoteza | Maqsad metrika | Holat |
|---|---|---|---|---|
| 2026-10-21 | `_template_` | 3x3 Angle x Format matritsasini nazorat ad set'iga qarshi sinash | Thumbstop >= 25%, CPA <= Maqsad | `PENDING` |

## 3. Tasdiqlangan akkaunt saboqlari jurnali
- Tasdiqlangan post-mortem xulosalarini shu yerga yozing yoki `python3 tools/instincts.py add` orqali ko'taring.
