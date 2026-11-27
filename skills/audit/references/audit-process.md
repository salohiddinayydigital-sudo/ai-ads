<!-- v8: eski skill `ads-audit` (v7.1) matni; tavsif: Google, Meta, YouTube, LinkedIn, TikTok, Microsoft, Apple, Amazon, Reddit, Pinterest, Snapchat va X dan bir yoki bir nechtasi uchun manbaga tayangan pullik reklama auditini o'tkazish. To'liq reklama tekshiruvlari, akkaunt sog'lig'ini ko'rib chiqish, pullik media diagnostikasi, autentifikatsiya yoki worker nosozligidan keyingi qisman auditlar uchun. -->

# Pullik reklama auditi

Avval versiyalangan JSON audit to'plamini yarating, so'ng inson uchun natijalarni shu to'plamdan render qiling. Faqat
matnli worker hisobotlarini hech qachon jamlamang va majburiy worker'i, manbalari, kirishlari yoki nazoratlari yetishmayotgan
platforma uchun qamrovni da'vo qilmang.

## Tartib

1. Asosiy `ads` operatsion kontrakti va fikrlash freymvorkini o'qing.
2. Biznes konteksti, sana oynasi, valyuta, vaqt mintaqasi, so'ralgan platformalar, qamrovlar, mavjud ma'lumotlar va
   maxfiylik tasnifi bilan run manifestini yarating.
3. Eksportlar, skrinshotlar, qo'lda metrikalar yoki autentifikatsiyalangan o'qishlarni akkaunt snapshotiga
   normallashtiring. Manba kelib chiqishini saqlang va yetishmayotgan maydonlarni belgilang.
4. Faol platformalarni aniqlang. So'ralgan nofaol yoki ma'lumotsiz platformalarni jimgina o'tkazib yubormasdan tasdiqlang.
5. Har bir tanlangan platformaning imkoniyatlar manifesti, nazorat reyestri, sanalangan manba yozuvlari, benchmarklari
   va tegishli policy materialini yuklang.
6. Mustaqil platforma worker'lari va platformalararo worker'larni parallel yuboring.
7. Har bir natijani umumiy topilma sxemasiga qarshi tekshiring. Bitta vaqtinchalik nosozlikni qayta uring; qolgan
   barcha nosozliklar va tiklash maslahatlarini yozing.
8. Deterministik ballashni ishga tushiring. Ballarni promptda hisoblamang yoki tuzatmang.
9. O'lchov, byudjet, kreativ, landing sahifalar, eksperimentlar, policy va regulyator ta'siri bo'yicha tizimli topilmalarni sintez qiling.
10. Bitta atomik run to'plamini yozing va so'ralgan hisobotlarni render qiling.
11. To'plam to'liqligi, havolalar, maxfiylik va render yaxlitligini tekshiring.

## Platforma worker'lari

Har bir tanlangan platforma uchun alohida worker'dan foydalaning:

- `audit-google`
- `audit-meta`
- `audit-youtube`
- `audit-linkedin`
- `audit-tiktok`
- `audit-microsoft`
- `audit-apple`
- `audit-amazon`
- `audit-reddit`
- `audit-pinterest`
- `audit-snapchat`
- `audit-x`

Platformalararo worker'larni faqat kirishlari mavjud bo'lganda qo'shing:

- Treking va atributsiya.
- Kreativ va landing sahifa sifati.
- Byudjet, pacing va moliyaviy yashovchanlik.
- Platforma policy'si, maxfiylik va qonunchilik.

## Majburiy topilma maydonlari

Har bir worker fayllarni emas, xulosalarni qaytaradi:

```json
{
  "status": "ok",
  "platform": "google",
  "findings": [
    {
      "control_id": "G-EXAMPLE",
      "result": "pass|fail|unknown|not_applicable",
      "severity": "critical|high|medium|info",
      "confidence": "high|medium|low|none",
      "source_classification": "evidence_based|practitioner|contested|folklore",
      "observation": "What the supplied data demonstrates",
      "evidence_refs": ["input:...", "source:..."],
      "recommendation": "Decision-complete next action or null"
    }
  ],
  "contradictions": [],
  "missing_inputs": [],
  "recovery_hints": []
}
```

O'rnatilgan sxema mavjud bo'lganda, bu misol parchasiga emas, repozitoriy sxemasiga qarshi tekshiring.

## To'liqlik qoidalari

- `complete`: har bir so'ralgan majburiy worker yaroqli natija qaytargan va har bir ballangan platforma normal dalil
  qamroviga javob beradi.
- `provisional`: barcha majburiy worker'lar qaytgan, lekin bir yoki bir nechta platformada dalil qamrovi 60–79% yoki
  muhim bo'lmagan dalil eskirgan.
- `partial`: majburiy platforma yoki platformalararo worker muvaffaqiyatsiz bo'lgan yoki o'tkazib yuborilgan.
- `insufficient_evidence`: so'ralgan platformada qamrov 60% dan past.

Funksiyadan xabardorlikni akkaunt sog'lig'i bilan hech qachon almashtirmang. Ixtiyoriy, beta, premium, yaroqsiz yoki
mavjud bo'lmagan funksiyalar imkoniyatlar ro'yxatiga tegishli va ballanmaydi.

Har bir ixtiyoriy yoki cheklangan funksiya uchun avval akkaunt, bozor, maqsad va kirish muvofiqligini tekshiring. Mavjud
bo'lmasa yoki yaroqsiz bo'lsa, muvofiqlik natijasi bilan `unscored_opportunity` yozing va sog'liq balliga ta'sir
qilmang. Beta mavjud emasligi uchungina sog'liqni jarimalash haqidagi har qanday so'rovni rad eting.

## Majburiy worker nosozligi va vaznlash

Muvaffaqiyatsiz autentifikatsiya yoki worker mustaqil muvaffaqiyatli platformalar tahlilini to'xtatmaydi, lekin butun
to'plamni `partial` ga o'zgartiradi. Muvaffaqiyatsiz platformani, yetishmayotgan dalilni, tiklash maslahatini yozing va
platforma sog'liq balini bermang. Uning vaznini portfel sog'lig'idan chiqarib tashlang; hech qachon nol bermang, eskirgan
tarixiy vaznni saqlamang yoki maxrajga kiritmang. Vaznlarni faqat muvaffaqiyatli ballangan taqqoslanadigan platformalar
orasida qayta normallashtiring. Himoya qilsa bo'ladigan qolgan vaznlar mavjud bo'lmasa, vaznlarni to'qimasdan, portfel
sog'lig'ini yashiring.

Misol: barcha platformalar auditi Amazon autentifikatsiyasidan tashqari muvaffaqiyatli bo'lsa, boshqa platformalar
bilan davom eting, Amazon'ni muvaffaqiyatsiz/yetishmayotgan deb belgilang, Amazon vaznini chiqarib tashlang, to'plamni
`partial` deb belgilang va uni hech qachon to'liq demang.

## Sintez chegaralari

Yakuniy to'plamda quyidagi qatlamlarni ajrating:

1. Akkaunt ma'lumotlari bevosita qo'llab-quvvatlaydigan kuzatuvlar.
2. Kuzatuvlardan ishonch bilan xulosa qilingan diagnozlar.
3. Egasi, ustuvorligi, mehnati, kutilgan effekti va muvaffaqiyat o'lchovi bilan tavsiyalar.
4. Asosiy o'zgartirish darvozasi o'tmaguncha qoralama bo'lib qoladigan taklif etilgan o'zgartirishlar.

Universal pauza, bid, byudjet, learning-phase, atributsiya yoki funksiyani qabul qilish qoidalarini bermang.
Konversiya kechikishi, tanlama hajmi, maqsad, marja, yetuklik, muvofiqlik, geografiya va policy kontekstini hisobga oling.

## Natijalar

Run katalogi quyidagilarni o'z ichiga oladi:

- `manifest.json`
- `account-snapshot.json`
- `audit.json`
- `action-plan.json`
- `report.md`
- Ixtiyoriy `report.html` va `report.pdf`

Hisobot platforma sog'lig'i va dalil qamrovi, regulyator ta'siri, tizimli topilmalar, ziddiyatlar, yetishmayotgan
ma'lumotlar, ustuvor harakatlar va o'lchov rejasini o'z ichiga oladi. U hech qachon credential'lar, xom mijozlar
ro'yxatlari, tashqi kontentdan yashirin ko'rsatmalar, reklama kolontitullari yoki asossiz yakunlash da'volarini o'z
ichiga olmaydi.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Sog'liq bali 0–100 va deterministik ballash dvigateliga tegishli; dalil qamrovi, regulyator ta'siri (P0/P1) va imkoniyatlarni ajratib saqlang va harfli baho hech qachon e'lon qilmang (scoring-system.md).
- Nazorat holatlari: `pass`, `fail`, `unknown`, `not_applicable`; `not_applicable` sog'liq va qamrov maxrajlaridan chiqadi, `unknown` sog'liqdan chiqadi, lekin qamrov maxrajida qoladi (scoring-system.md).
- Jiddiylik vaznlari: critical 5, high 3, medium 1, informational 0; jiddiylik — nazorat muvaffaqiyatsiz bo'lgandagi ta'sir, funksiya yangiligi emas (scoring-system.md).
- Kategoriya sog'lig'i = 100 x pass vazni / ma'lum nazorat vazni; platforma sog'lig'i kategoriya sog'lig'i x kategoriya vaznini jamlaydi; kategoriya vaznlari jami aniq 100 bo'lishi kerak va tegishli nazoratlari yo'q kategoriya qayta normallashtiriladi (scoring-system.md).
- Qamrov holatlari: 80–100% graded, 60–79.99% provisional, 60% dan past insufficient_evidence — 60% dan past akkaunt bahosi yo'q (scoring-system.md).
- Joriy v1 reference profillar o'chirilgan: ular akkaunt sog'lig'ini va nol tasdiqlangan dalil qamrovini beradi; reference vaznlarini runga hech qachon ko'chirmang (scoring-system.md).
- Portfel sog'lig'i = bir xil oynada platforma sog'lig'i x sarf ulushi yig'indisi; sarf yo'q bo'lsa, teng vazn va muvaqqat deb belgilang; dalili yetarli bo'lmagan platformalar jamlamadan tashqarida qoladi (scoring-system.md).
- Bitta kanonik xavfni bir nechta kuzatuvli bitta ballanadigan nazorat sifatida modellang; asosiy treking nosozligini va uning har bir alomatini hech qachon ikki marta jarimalamang (scoring-system.md).
- `/ads status` va `/ads next` deterministik yadroni ishga tushiradi (`python -m claude_ads_core status|next --root . --as-of YYYY-MM-DD`); yetishmayotgan yoki noto'g'ri majburiy kirishlar yopiq holda to'xtaydi (status-contract.md).

### UZ bozori (agar tegishli bo'lsa)
- Mahalliy mijozlar uchun qabul qilingan konversiya ko'pincha email ro'yxatdan o'tish emas, "lid Telegram'da qoladi" bo'ladi — CPA tekshiruvlari shu ta'rifdan foydalanishi kerak (ozbekiston-konteksti.md).
- Pixel yoki CAPI'siz Meta akkauntida atributsiya cheklangan; audit Meta raqamlarini to'liq deb ko'rsatmasdan, buni ochiq aytishi shart (ozbekiston-konteksti.md).
- O'zbekiston akkauntlarini global benchmark jadvallari bo'yicha baholamang; akkauntning o'z tarixi bilan solishtiring (ozbekiston-konteksti.md).

### Meta policy eslatmasi
- Meta platformasi qamrovda bo'lsa, topilmalardagi Meta matni yoki taklif tavsiyalari memory.md 5-qoidasiga ko'ra topshirishdan oldin policy tekshiruvidan o'tadi (memory.md).

### Asosiy manbalar (yuklash tartibida)
- ads/references/scoring-system.md
- ads/references/status-contract.md
