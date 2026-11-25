<!-- v8.2 Charter v2: strategist Self-Audit rubrikasi (>= 85/100). Ref: rules/70-charter-baseline.md §6 -->

# Strategiya sifati rubrikasi — 100 ball, o'tish chegarasi 85

> `strategist` har bir rejimda (`positioning`, `offer_architecture`, `launch_plan`, `turnaround`) natijani qaytarishdan oldin shu rubrika bo'yicha o'zini baholaydi. Ball < 85 yoki bloker bo'lsa — eng past mezonni tuzatib **1 marta** qayta yozadi. Ball `HEURISTIC_PRIOR_MODEL` — natija prognozi emas.

| Mezon | Maks. | Tekshiruv |
|---|---:|---|
| **ICP aniqligi** | 20 | Segment, og'riq, trigger hodisa, e'tiroz va xarid qaroriga ta'sir qiluvchi shaxs aniq; "hamma uchun" emas |
| **Raqobatdan farqlanish** | 15 | Kamida 2 raqobatchi bilan solishtirma (manba bilan yoki `ASSUMPTION`); UTP isbotlanadigan, klishe emas |
| **Unit-ekonomika** | 20 | Break-even CPA/ROAS `tyrion_media_calculator` dan; marja, o'rtacha chek, LTV taxminlari ochiq |
| **O'lchanadigan KPI** | 20 | Har bosqich: metrika + maqsad + muddat + mas'ul (owner); qaror qoidasi (kill/scale chegarasi) |
| **Kanal va ketma-ketlik mantiqi** | 15 | Kanal tanlovi dalilga (bozor/raqobatchi/byudjet) bog'langan; test byudjeti kanal soniga yetarli |
| **Dalil yorliqlari va mahalliy kontekst** | 10 | Har raqam yorliqli; UZ bozori uchun to'lov (Click/Payme/naqd), ishonch, Telegram/Instagram Direct omillari hisobga olingan |

**Avtomatik blokerlar:** to'qilgan raqobatchi raqami; break-even hisobisiz launch reja; KPI'siz reja; jonli hisobga o'zgarish Spend-Guard'siz.

**Chiqish bloki:** `self_audit: { gate: "score>=85", score: <n>, failed_checks: [...], rewrites: <0|1>, label: "HEURISTIC_PRIOR_MODEL" }`
