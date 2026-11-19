---
name: tracking
description: "Measurement: Pixel, CAPI, server-side events, dedup, UTM, GA4, attribution and Telegram bot funnels. Use for 'tracking', 'pixel', 'capi', 'utm', 'atributsiya', 'event ishlamayapti', трекинг, пиксель."
triggers:
- "atributsiya"
- "attribution"
- "attribution window"
- "7d click"
- "1d view"
- "mmm"
- "incrementality"
- "roas farqi"
- "атрибуция"
- "окно атрибуции"
- "атрибуция хатоси"
- "capi"
- "conversions api"
- "pixel"
- "event_id"
- "emq"
- "event match quality"
- "server-side tracking"
- "sgtm"
- "deduplikatsiya"
- "пиксель"
- "конверсии апи"
- "capi текшириш"
- "ga4"
- "google analytics"
- "gtm"
- "google tag manager"
- "dataLayer"
- "analitika"
- "voronka analitikasi"
- "аналитика сайта"
- "гугл аналитика"
aliases:
- "attribution"
- "mmm"
- "incrementality"
- "view-through"
- "ads-attribution"
- "capi"
- "meta-capi"
- "sgtm"
- "pixel-debug"
- "emq"
- "ads-server-side-tracking"
- "ga4"
- "gtm"
- "web-analytics"
- "datalayer"
- "analytics"
domains:
- "tracking"
- "analytics"
- "attribution"
- "technical"
platforms:
- "meta"
- "google"
- "tiktok"
- "multi-platform"
- "web"
attached_agents:
- "tracking-specialist"
related_skills: []
references:
- "skills/tracking/references/ads-attribution.md"
- "skills/tracking/references/ads-server-side-tracking.md"
- "skills/tracking/references/analytics.md"
risk_level: medium
output_contract: "Structured deliverable with evidence labels, assumptions, tools actually run and an honest execution report"
---

# tracking

Measurement: Pixel, CAPI, server-side events, dedup, UTM, GA4, attribution and Telegram bot funnels. Use for 'tracking', 'pixel', 'capi', 'utm', 'atributsiya', 'event ishlamayapti', трекинг, пиксель.

## Qoidalar
Pixel + CAPI `event_id` bilan dedup; PII faqat SHA-256 hash; consent darvozasi.

## Manbalar (v7.1 dan ko'chirilgan to'liq matnlar)

Kerakli faylni `Read` bilan och; hammasini yoppasiga o'qima.

| Eski skill | Fayl | Qachon |
|---|---|---|
| `ads-attribution` | `skills/tracking/references/ads-attribution.md` | Audit cross-platform attribution, conversion definitions, reporting windows, GA4, AdServices and AdAttributionKit, MMPs, browser and server events, of… |
| `ads-server-side-tracking` | `skills/tracking/references/ads-server-side-tracking.md` | Audit server-side paid-media measurement including server-side tag management, platform conversion APIs, event taxonomy, browser/server deduplication,… |
| `analytics` | `skills/tracking/references/analytics.md` | When the user wants to set up, improve, or audit analytics tracking and measurement. Also use when the user mentions "set up tracking," "GA4," "Google… |

Eski nomlar `manifests/migration-v8.json` da; router ularni alias sifatida taniydi.
