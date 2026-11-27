# Kontekstual benchmarklar

**Tekshirilgan:** 2026-07-11
**Yangilash:** har chorakda va keltirilgan dataset o'zgarganda
**Dalil holati:** hech bir raqamli benchmark universal akkaunt chegarasi sifatida kiritilmagan

Benchmarklar — taqqoslash dalili, pass/fail nazoratlari emas. Ulardan savol shakllantirish uchun
foydalaning, so'ng qarorni reklama beruvchining iqtisodi, kogortasi va xuddi shu oynadagi akkaunt
ma'lumotlaridan chiqaring. Akkauntni faqat sohalararo mediandan farq qilgani uchun past ballamang.

## Dalil kontrakti

Har qanday tashqi benchmarkni keltirishdan oldin yozing:

| Maydon | Majburiy qiymat |
| --- | --- |
| Manba | Nashriyotchi, to'g'ridan-to'g'ri URL va source-ledger ID |
| Kelib chiqish | Platforma, mustaqil tadqiqotchi, agentlik/vendor yoki akkaunt ma'lumoti |
| Nashr | Nashr sanasi va olingan sana |
| Populyatsiya | Platforma, maqsad, format, geografiya, soha va tanlama hajmi |
| Statistika | O'rtacha, mediana, persentil, modellashtirilgan natija yoki case study |
| O'lchov | Surat, maxraj, atributsiya oynasi, valyuta va soliq/to'lovlar |
| Vaqt | Kuzatuv oynasi va mavsumiylik |
| Moslik | Kogorta nega bu akkauntga taqqoslanadi |
| Cheklovlar | Homiylik, istisnolar, survivorship bias yoki metodologiya yo'qligi |

Xulosani o'zgartirishi mumkin bo'lgan biror maydon noma'lum bo'lsa, benchmarkni `provisional` deb
belgilang. Platforma e'lon qilgan uplift ko'rsatkichlari — `vendor-supplied`; case study umumiy baza emas.

## Taqqoslash tartibi

Eng tor himoya qilsa bo'ladigan taqqoslashdan foydalaning:

1. Xuddi shu akkaunt, xuddi shu maqsad, xuddi shu atributsiya ta'rifi, avvalgi taqqoslanadigan davr.
2. Kelishilgan muvaffaqiyat metrikali xuddi shu akkaunt eksperimenti yoki holdout.
3. Sarfga bog'langan first-party CRM yoki daromad kogortasi.
4. Metodologiyasi oshkor qilingan taqqoslanadigan peer kogorta.
5. Keng soha yoki platforma benchmarki, faqat yo'nalish ko'rsatuvchi deb belgilangan.

Turli atributsiya oynalari, valyutalar, konversiya ta'riflari yoki voronka bosqichlari bo'lgan manbalarni
normallashtirmasdan va konversiyani oshkor qilmasdan hech qachon aralashtirmang.

## Akkauntga xos baza

Bazani faqat to'liq davrlardan quring:

```text
baseline_window = periods before the evaluated change, excluding known outages
comparison_window = same duration and conversion-lag maturity
delta = (comparison - baseline) / baseline
```

Platforma, maqsad, kampaniya turi, geografiya, yangi/qaytuvchi mijoz va qurilma bo'yicha segmentlarni faqat
segmentda qaror uchun yetarli kuzatuv bo'lgandagina ajrating. Kam hajmli segmentlarni soha o'rtachasi bilan
almashtirmay, noaniq deb xabar qiling.

Xarajat va qiymat metrikalari uchun solishtiring:

```text
CPA  = spend / accepted conversions
ROAS = accepted conversion value / spend
MER  = business revenue / total advertising spend
```

Daromad yalpi yoki sof ekanini va sarfga to'lovlar, kreditlar va soliqlar kiritilganini ko'rsating.
Platforma ROAS va biznes MER turli savollarga javob beradi va o'zaro almashtirilmasligi kerak.

## Metrika bo'yicha dalil savollari

| Metrika | Talqin qilishdan oldin so'rang |
| --- | --- |
| CTR | Qaysi ko'rsatuv va klik ta'riflari, placement aralashmasi va maqsad? |
| CPC/CPM | Qaysi auksion, geografiya, mavsum, valyuta va hisob-kitob asosi? |
| CVR | Qaysi konversiya, maxraj, kechikish va rozilik populyatsiyasi? |
| CPA/CPL | Lid sifati yoki keyingi qabul qilish kiritilganmi? |
| ROAS | Qaysi qiymat manbai, qaytarishlar/bekor qilishlar, atributsiya va mijoz kogortasi? |
| Frequency | Qaysi qamrov oynasi va auditoriya overlapi; o'lchangan natija yomonlashyaptimi? |
| Kreativ charchoq | Aralashma va sarf siljishlaridan keyin taqqoslanadigan bazaga nisbatan barqaror o'zgarish bormi? |

## Natija kontrakti

Har bir benchmark taqqoslashi kuzatilgan akkaunt qiymati, benchmark qiymati, kogorta mosligi, manba ID,
ishonch va u ma'lumot beradigan qarorni o'z ichiga olishi shart. Farq — kuzatuv, diagnoz emas. Tavsiya matni
farqni marginal samaradorlik, so'rov sifati, kreativ darajasidagi pasayish, konversiya sifati yoki inkrementallik
kabi akkaunt dalillariga bog'lashi kerak.

## Taqiqlangan foydalanishlar

- Platforma talabi sifatida ko'rsatilgan qat'iy minimal oylik byudjetlar.
- Universal haqiqat sifatida ko'rsatilgan qat'iy konversiyalar soni, frequency, kreativ umri yoki byudjet-CPA chegaralari.
- Kutilgan akkaunt natijasi sifatida ko'rsatilgan vendor uplift foizlari.
- Maqsad va natija sifatini normallashtirmasdan platformalararo xarajat taqqoslashlari.
- Populyatsiya va statistika ta'rifisiz "eng yaxshi natija" yoki persentil da'volari.

Platformaga xos kuzatilgan faktlar uchun tegishli audit referensi va uning sanalangan manbasidan foydalaning.
Akkauntga mos joriy manba paketi bo'lmasa, raqamni tashlab, uni o'lchov savoliga aylantiring.
