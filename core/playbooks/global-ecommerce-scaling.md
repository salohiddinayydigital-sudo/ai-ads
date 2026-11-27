# Playbook: Global E-Commerce va DTC pullik media masshtablash

1. **Avval unit-iqtisodiyot:** Kampaniyalarni ishga tushirishdan oldin `python3 tools/calculator.py breakeven --aov <AOV> --margin <MARGIN> --currency <ISO>` ni ishga tushiring.
2. **Treking va rozilik:** CAPI Event Match Quality (`EMQ >= 8.0`), `event_id` deduplikatsiyasi va bozorga xos rozilik darvozalarini tekshiring (`eu`/`uk` da `GDPR Consent Mode v2`, `us` da `Meta LDU`, `latam` da `LGPD`, `in` da `DPDP`).
3. **3 bosqichli Spend-Guard launch:** Sandbox (10–15%) -> Validation (25–30%) -> Scale (55–65%, har 48–72 soatda ko'pi bilan +20% byudjet qadami).
