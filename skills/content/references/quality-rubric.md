<!-- v8.2 Charter v2: content-planner Self-Audit rubrikasi (>= 85/100). Ref: rules/70-charter-baseline.md §6 -->

# Kontent reja sifati rubrikasi — 100 ball, o'tish chegarasi 85

> `content-planner` (`content_calendar`, `social_series`, `seo_cluster`, `funnel_nurture`) natijani qaytarishdan oldin shu rubrika bo'yicha baholaydi. < 85 yoki bloker → **1 marta** qayta yozish.

| Mezon | Maks. | Tekshiruv |
|---|---:|---|
| **Maqsad va funnel bosqichi** | 25 | Har kontent birligida funnel bosqichi (TOF/MOF/BOF/retention) va bitta asosiy metrika |
| **Format va kanal** | 20 | Har birlikda format (reels, carousel, post, story, Telegram post, maqola) va tarqatish kanali |
| **CTA** | 15 | Har birlikda aniq CTA (saqlash, Direct'ga yozish, kanalga obuna, sayt) |
| **Ustun balansi** | 15 | Kontent ustunlari (pillar) muvozanatli; "post uchun post" yo'q |
| **Mahalliy va mavsumiy kontekst** | 15 | UZ bayramlari (Navro'z, Ramazon/Hayit, 1-sentabr, Yangi yil), til (UZ lotin/kirill, RU) va mahalliy misollar |
| **Ijrochanlik** | 10 | Mas'ul, muddat, resurs; video ssenariylar `video-producer` ga uzatilgan |

**Avtomatik blokerlar:** sotuv/reklama video ssenariysini o'zi yozgan (`video-producer` doirasi); manbasiz statistika; maqsadsiz kalendar.

**Chiqish bloki:** `self_audit: { gate: "score>=85", score: <n>, failed_checks: [...], rewrites: <0|1>, label: "HEURISTIC_PRIOR_MODEL" }`
