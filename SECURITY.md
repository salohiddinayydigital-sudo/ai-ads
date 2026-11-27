# Xavfsizlik siyosati va Spend-Guard arxitekturasi (`SECURITY.md`)

## 1. Qo'llab-quvvatlanadigan versiyalar va inventar

| Versiya | Holat | Arxitektura inventari |
|---|---|---|
| **8.3.x** | Qo'llab-quvvatlanadi (joriy global reliz) | **19 ta agent**, **19 ta skill**, **42 ta slash buyruq**, **40 ta CLI asbob**, 101 ta wiki qayd |
| **5.0.x** | Texnik xizmat | Yagona ildizli ECC (O'zbekiston standarti) |

## 2. Zaiflik haqida xabar berish

Agar xavfsizlik zaifligi, prompt injection yo'li yoki credential sizib chiqish xavfini topsangiz:
- **GitHub Security Advisories:** [https://github.com/salohiddinayydigital-sudo/ai-ads/security/advisories](https://github.com/salohiddinayydigital-sudo/ai-ads/security/advisories)
- **Repozitoriy maintaineri:** [@salohiddinayydigital-sudo](https://github.com/salohiddinayydigital-sudo)
- Jonli tokenlar, reklama akkaunt ID'lari yoki exploit payload'lari bor **ochiq issue ochmang**.

## 3. Spend-Guard va reklama hisobini o'zgartirish xavfsizligi (6 majburiy darvoza)

Tyrion qat'iy "faqat o'qish" rejimida ishlaydi. Jonli reklama hisobini o'zgartiradigan har qanday amal (byudjetni o'zgartirish, kampaniyani pauza qilish, bid o'zgartirish) 6 ta darvozaning hammasi o'tmaguncha `tools/spend-guard.py` va Universal Auto-Router tomonidan bloklanadi:
1. **Oldindan ko'rish farqi (`1_preview_diff`)**
2. **Inson tomonidan aniq tasdiq (`2_human_approval` / `--approved`)**
3. **Byudjet tezligi chegarasi (`3_budget_velocity_le_20pct` — 48–72 soatda ko'pi bilan +20%)**
4. **Qat'iy kunlik shift (`4_max_daily_cap`)**
5. **Avtomatik stop-loss qoidasi (`5_stop_loss_rule`)**
6. **Zudlik bilan rollback rejasi (`6_rollback_plan`)**

## 4. Maxfiylik, rozilik darvozasi va PII himoyasi

- **CAPI rozilik darvozasi (`tools/capi-utm-builder.py`):** `--no-consent` (`consent_granted=False`) berilganda Tyrion hash qilish yoki uzatishdan oldin barcha PII'ni (`ph`, `em`, `fn`, `ct`, `fbp`, `fbc`) olib tashlaydi (`BLOCKED_PII_NO_CONSENT`), Google Consent Mode v2 (`denied`) ni majburiy qiladi va Meta Limited Data Use (`data_processing_options=['LDU']`) ni yoqadi.
- **Sirlarni yashirish (`tools/tyrion_core.py` va `tools/tyrion-shield.py`):** Meta (`EAA...`), OpenAI (`sk-...`), Anthropic (`sk-ant-...`), Google (`AIza...`), Telegram va GitHub tokenlarini avtomatik skanerlaydi va maskalaydi.
