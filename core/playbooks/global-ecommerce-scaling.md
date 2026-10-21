# Playbook: Global E-Commerce & DTC Paid Media Scaling

1. **Unit Economics First:** Run `python3 tools/calculator.py breakeven --aov <AOV> --margin <MARGIN> --currency <ISO>` before launching campaigns.
2. **Tracking & Consent:** Verify CAPI Event Match Quality (`EMQ >= 8.0`), `event_id` deduplication, and market-specific consent gates (`GDPR Consent Mode v2` in `eu`/`uk`, `Meta LDU` in `us`, `LGPD` in `latam`, `DPDP` in `in`).
3. **3-Stage Spend-Guard Launch:** Sandbox (10-15%) -> Validation (25-30%) -> Scale (55-65%, max +20% budget step per 48-72h).
