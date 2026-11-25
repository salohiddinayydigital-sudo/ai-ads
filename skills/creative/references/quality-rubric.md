<!-- v8.2 Charter v2: creative-strategist Self-Audit rubrikasi (>= 85/100). Ref: rules/70-charter-baseline.md §6 -->

# Kreativ sifati rubrikasi — 100 ball, o'tish chegarasi 85

> `creative-strategist` (`creative_audit`, `matrix_3x3`, `copy_sprint`, `fatigue_recovery`) natijani qaytarishdan oldin shu rubrika bo'yicha o'zini baholaydi. < 85 yoki bloker → **1 marta** ichki qayta yozish. Video ssenariy rubrikasi alohida: `skills/video/references/script-quality-rubric.md`.

| Mezon | Maks. | Tekshiruv |
|---|---:|---|
| **Awareness mosligi** | 15 | Har angle awareness bosqichiga (unaware → most aware) bog'langan; kirish shu bosqichga mos |
| **Mexanizm xilma-xilligi** | 20 | >= 3 mustaqil psixologik mexanizm (og'riq, ijtimoiy isbot, kontrast, qiziqish, status...); bir angle 5 xil so'z bilan takrorlanmagan (Andromeda PDA) |
| **Test gipotezasi** | 20 | Har test: bitta o'zgaruvchi, metrika (hook rate, CTR, CPA), minimal sarf va qaror qoidasi |
| **Tabiiy til (UZ/RU/EN)** | 15 | Jonli og'zaki til; AI-klishe yo'q ("Innovatsion yechim", "Game-changer", "Hayotingizni o'zgartiring"); til versiyalari alohida yozilgan, tarjima emas |
| **Platforma limitlari va safe-zone** | 15 | Belgi sanog'i (Meta primary 125, headline 40; Telegram 160), 9:16/4:5 safe-zone, format spetsifikatsiyasi |
| **Halollik va compliance** | 15 | Isbotsiz foiz/kafolat yo'q; `[ADD VERIFIED ...]` ochiq; Personal Attributes ("Siz semizmisiz?") yo'q |

**Avtomatik blokerlar:** to'qilgan sharh/statistika; bitta testda >1 o'zgaruvchi; platforma belgi limiti buzilgan; tibbiy/moliyaviy kafolat.

**Chiqish bloki:** `self_audit: { gate: "score>=85", score: <n>, failed_checks: [...], rewrites: <0|1>, label: "HEURISTIC_PRIOR_MODEL" }`
