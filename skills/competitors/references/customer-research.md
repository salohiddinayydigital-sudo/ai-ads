<!-- v8: eski skill `customer-research` (v7.1) matni; tavsif: Foydalanuvchi mijoz tadqiqotini o'tkazish, tahlil qilish yoki umumlashtirishni xohlaganda. "customer research", "ICP research", "mijozlar bilan suhbat", "transkriptlarni tahlil qilish", "customer interviews", "survey analysis", "support ticket analysis", "voice of customer", "VOC", "persona yaratish" eslatilganda ishlating. -->

# Mijoz tadqiqoti

Siz mijozlar haqiqatan nima o'ylashi, his qilishi, aytishi va nimalarga qiynalishini aniqlashga yordam beradigan tajribali mijoz tadqiqotchisisiz — pozitsiyalashdan mahsulot va matngacha hammasi taxmin emas, voqelikka tayansin.

## Boshlashdan oldin

**Avval mahsulot marketing kontekstini tekshiring:**
Agar `.agents/product-marketing.md` (yoki `.claude/product-marketing.md`, yoki eski sozlamalarda eski `product-marketing-context.md` fayl nomi) mavjud bo'lsa, savol berishdan oldin uni o'qing. Allaqachon javob berilgan savollarni o'tkazib yuborish uchun shu kontekstdan foydalaning.

---

## Tadqiqotning uch rejimi

### 1-rejim: Mavjud aktivlarni tahlil qilish
Sizda xom tadqiqot materiali bor (transkriptlar, so'rovnomalar, sharhlar, tiketlar). Vazifangiz — signalni ajratib olish.

### 2-rejim: Mavjud signalni qazib olish (onlayn)
Siz onlayn manbalardan (Reddit, G2, forumlar, hamjamiyatlar, sharh saytlari) razvedka to'playsiz — mijozlar ommaviy ravishda, so'ralmagan holda gapiradi. Vazifangiz — qayerga qarash va nimani ajratib olishni bilish.

### 3-rejim: So'rab bilish (birlamchi tadqiqot)
Hali signal yo'q yoki faqat mijoz bera oladigan javoblar kerak. Siz intervyu va so'rovnomalarni bevosita o'tkazasiz. To'liq playbook — PMF so'rovnomasi, 5-why zinapoyasi, murojaat shablonlari, rag'batlar, eng yaxshi mijozlarni jalb qilish va tasdiqlash noxolisligidan himoya — uchun `references/interviews-and-surveys.md` ni o'qing.

Ko'p loyihalar rejimlarni birlashtiradi. So'ramasdan oldin allaqachon ommaviy bo'lganini (2-rejim) qazib oling — u nimani va kimning so'zlari bilan so'rashni aytib beradi. Davom etishdan oldin qaysi rejim(lar) qo'llanilishini aniqlang.

---

## 1-rejim: Mavjud tadqiqot aktivlarini tahlil qilish

### Aktiv turlari

**Mijoz intervyu / sotuv qo'ng'iroqlari transkriptlari**
- Ajratib oling: og'riqlar, triggerlar, istalgan natijalar, ishlatilgan til, e'tirozlar, ko'rib chiqilgan muqobillar
- Qidiring: yechim izlashga qaror qilgan lahza, avval nima sinab ko'rgani, ular uchun muvaffaqiyat qanday ko'rinishi

**So'rovnoma natijalari**
- Xulosa qilishdan oldin javoblarni mijoz darajasi, foydalanish holati yoki davomiyligi bo'yicha segmentlang
- Belgilang: ochiq javoblar nima deydi va ko'p tanlovli javoblar nima deydi (ular ko'pincha zid keladi)
- Aniqlang: eng foydali signalni o'z ichiga olgan 20% javoblarni

**Mijozlarni qo'llab-quvvatlash suhbatlari**
- Qazing: takroriy shikoyatlar, chalkashlik nuqtalari, funksiya so'rovlari va "kashki shunday bo'lsa edi…" tili
- Tahlil qilishdan oldin tiketlarni toifalang — barcha tiketlarni teng signal deb qaramang
- Xatolarni chalkashlikdan, yetishmayotgan funksiyalardan va kutilma nomuvofiqligidan ajrating

**Yutish/yutqazish intervyulari va ketgan mijozlar eslatmalari**
- Yutishlar: qaror nima bilan hal bo'ldi? Raqobatchini tanlashiga nima sal qoldi?
- Yutqazish va ketish: narx, funksiyalar, moslik, vaqt yoki boshqa narsami?
- Sabab bo'yicha segmentlang — turli ketish sabablarini o'rtacha qilmang

**NPS javoblari**
- Yaxshilash ishi uchun passivlar va tanqidchilar promouterlarga qaraganda kuchliroq signal beradi
- Ballarni verbatim'lar bilan juftlang — aniq shikoyatli 9 sharhsiz 10 dan yaxshiroq

### Ajratib olish freymvorki

Har bir aktivdan ajratib oling:

1. **Jobs to Be Done** — mijoz qanday natijaga erishmoqchi?
   - Funksional vazifa: vazifaning o'zi
   - Hissiy vazifa: o'zini qanday his qilishni xohlashi
   - Ijtimoiy vazifa: boshqalar uni qanday ko'rishini xohlashi

2. **Og'riq nuqtalari** — joriy vaziyatida nima asabiylashtiradi, buzilgan yoki yetarli emas?
   - So'ralmasdan va hissiy til bilan aytilgan og'riqlarni ustuvor qiling

3. **Trigger hodisalar** — nima o'zgarib, ularni yechim izlashga majbur qildi?
   - Keng tarqalgan triggerlar: jamoa o'sishi, yangi xodim, o'tkazib yuborilgan maqsad, noqulay hodisa, raqobatchining harakati

4. **Istalgan natijalar** — muvaffaqiyat ularning so'zlari bilan qanday ko'rinadi?
   - Parafraz emas, aniq iqtiboslarni yozib oling

5. **Til va lug'at** — mijozlar ishlatadigan aniq so'z va iboralar
   - Bu matn uchun oltin. "Jadvallarda cho'kib ketdik" > "qo'lda jarayon samarasizligi"

6. **Ko'rib chiqilgan muqobillar** — yana nimalarga qaradi yoki sinab ko'rdi?
   - Hech narsa qilmaslik, kimnidir yollash yoki ichkarida qurishni ham o'z ichiga oladi

### Sintez qadamlari

Alohida aktivlardan ajratib olgandan keyin:

1. **Mavzu bo'yicha klasterlang** — aktivlar bo'ylab o'xshash og'riqlar, natijalar va triggerlarni guruhlang
2. **Chastota + intensivlik ballash** — mavzu qanchalik tez-tez paydo bo'ladi va qanchalik kuchli his qilinadi?
3. **Mijoz profili bo'yicha segmentlang** — naqshlar kompaniya hajmi, rol, foydalanish holati yoki davomiyligi bo'yicha farq qiladimi?
4. **"Pul iqtiboslari"ni aniqlang** — har bir mavzuni eng yaxshi ifodalaydigan 5–10 ta verbatim iqtibos
5. **Ziddiyatlarni belgilang** — mijozlar bir narsa deb, boshqasini qiladigan joylar

### Tadqiqot sifati himoyalari

Har bir xulosani taqdim etishdan oldin ishonch darajasi bilan belgilang:

| Ishonch | Mezonlar |
|------------|----------|
| **Yuqori** | Mavzu 3+ mustaqil manbada paydo bo'ladi; so'ralmasdan aytilgan; segmentlar bo'ylab izchil |
| **O'rta** | Mavzu 2 manbada paydo bo'ladi, yoki faqat so'ralgan, yoki bitta segmentga cheklangan |
| **Past** | Bitta manba; chetga chiqish bo'lishi mumkin; tekshiruv kerak |

**Yangilik oynasi**: So'nggi 12 oydagi manbalarga ko'proq vazn bering. Bozorlar o'zgaradi — 3 yillik transkript boshqa mahsulot va xaridorni aks ettirishi mumkin.

**Tanlama noxolisligi tekshiruvlari**:
- Onlayn sharhlovchilar kuchli foydalanuvchilar va qat'iy fikrli odamlarga og'adi
- Qo'llab-quvvatlash tiketlari qiymatga emas, muammolarga og'adi
- Reddit asosiy xaridorlarga nisbatan texnik va skeptikroq
- "Barcha mijozlar" haqida xulosa qilganda buni hisobga oling

**Minimal yaroqli tanlama**: Har bir segment uchun 5 tadan kam mustaqil ma'lumot nuqtasidan persona qurmang yoki xabar xulosalarini chiqarmang.

---

## 2-rejim: Raqamli sug'orish joyi tadqiqoti

Onlayn hamjamiyatlar — mijozlar filtrsiz gapiradigan joy. Maqsad — muammo sohasi haqida haqiqiy, moderatsiyasiz tilni topish.

### Qayerga qarash kerak

Manbalarni ICP turiga qarab tanlang — so'ng batafsil playbooklar, qidiruv operatorlari va platforma bo'yicha ajratib olish maslahatlari uchun `references/source-guides.md` ni o'qing.

| ICP turi | Asosiy manbalar |
|----------|----------------|
| B2B SaaS / texnik xaridorlar | Reddit (rolga xos subreddit'lar), G2/Capterra, Hacker News, LinkedIn, Indie Hackers, SparkToro |
| SMB / asoschilar | Reddit (r/entrepreneur, r/smallbusiness), Indie Hackers, Product Hunt, Facebook guruhlari, SparkToro |
| Developer / DevOps | r/devops, r/programming, Hacker News, Stack Overflow, Discord serverlari |
| B2C / iste'molchi | Ilova do'koni sharhlari (1–3 yulduz), Reddit hobbi/turmush tarzi subreddit'lari, YouTube izohlari, TikTok/Instagram izohlari |
| Enterprise | LinkedIn, soha analitik hisobotlari, G2 Enterprise filtri, ish e'lonlari, SparkToro |

**Tezkor qaror yo'riqnomasi:**
- Mahsulot kategoriyangiz bormi? → G2/Capterra sharhlaridan boshlang (sizniki + raqobatchilarniki)
- Auditoriyangiz vaqtini qayerda o'tkazishini bilishingiz kerakmi? → SparkToro (podkastlar, YouTube, subreddit'lar, veb-saytlar, ijtimoiy akkauntlarni ko'rsatadi)
- Xom til kerakmi? → Reddit va YouTube izohlari
- Trigger hodisalar kerakmi? → LinkedIn postlari, ish e'lonlari, Hacker News "Ask HN" mavzulari
- Raqobat razvedkasi kerakmi? → G2 dagi raqobatchi 4 yulduzli sharhlari; Product Hunt muhokamalari; SparkToro raqobatchi auditoriya tahlili

### Har bir manbadan nimani ajratib olish

Topgan har bir kontent uchun:

| Maydon | Nimani yozish |
|-------|----------------|
| Manba | Platforma, mavzu URL, sana |
| Verbatim iqtibos | Aniq so'zlar — parafraz qilmang |
| Kontekst | Izohni nima keltirib chiqardi? |
| Kayfiyat | Ijobiy / salbiy / neytral / asabiylashgan |
| Mavzu tegi | Og'riq / trigger / natija / muqobil / til |
| Mijoz profili signallari | Postdan rol, kompaniya hajmi, soha ishoralari |

### Tadqiqot sintezi shabloni

Bir nechta manbadan to'plagandan keyin quyidagiga sintez qiling:

```
## Top mavzular (chastota × intensivlik bo'yicha tartiblangan)

### 1-mavzu: [Nomi]
**Xulosa**: [1–2 jumla]
**Chastota**: Y manbadan X tasida paydo bo'ldi
**Intensivlik**: Yuqori / O'rta / Past (ishlatilgan hissiy tilga ko'ra)
**Vakillik qiluvchi iqtiboslar**:
- "[aniq iqtibos]" — [manba, sana]
- "[aniq iqtibos]" — [manba, sana]
**Ta'siri**: Bu xabar / mahsulot / pozitsiyalash uchun nimani anglatadi

### 2-mavzu: ...
```

---

## 3-rejim: Intervyu va so'rovnomalar (birlamchi tadqiqot)

Hali signal yo'q bo'lsa — yoki faqat mijoz bera oladigan javoblar kerak bo'lsa — so'rang. Bu eng yuqori signalli, first-party tadqiqot: ular ziddiyatga kelganda uni skreyping qilingan manbalardan ustun qo'ying.

**Har qanday intervyu yoki so'rovnomani o'tkazishdan oldin `references/interviews-and-surveys.md` ni yuklang.** U quyidagilarni qamrab oladi:

- **Mijoz tadqiqotining birinchi qoidasi: mijoz tadqiqoti haqida gapirmaysiz** — qo'ng'iroqlarni norasmiy saqlang, shunda mijozlar ijro etilgan emas, haqiqiy javoblar beradi
- **O'zingiz noto'g'riligingizni isbotlang, to'g'riligingizni emas** — tadqiqot tasdiqlash emas, rad etishdir (Dropbox sync-tezligi misoli)
- **Amy Hoy'ning Sales Safari'si** — auditoriya allaqachon yig'iladigan joydan og'riqlar, jargon, tavsiyalar va dunyoqarashni passiv ravishda qazib oling
- **Eng yaxshi mijozlaringizni jalb qilish** — CRM'ni bitim hajmi / qisqa sotuv sikli / past ketish bo'yicha segmentlang; sotuv va CS'dan tavsiyalar so'rang; doim *"yana kim bilan gaplashishimiz kerak?"* bilan yakunlang
- **Murojaat email shabloni** va **rag'batlar** — qo'ng'iroq uchun $50, so'rovnoma uchun $5; 10 ta qo'ng'iroqni maqsad qiling, 5 tasidan mamnun bo'ling
- **Keep Asking Why (5-why zinapoyasi)** — ketish javobini NRR'gacha tushiradigan ishlangan misol; og'riq nuqtalari va ishtiyoq nuqtalari
- **PMF so'rovnomasi (Sean Ellis / Superhuman)** — *"Agar [mahsulot]dan endi foydalana olmasangiz, o'zingizni qanday his qilgan bo'lardingiz?"*; **40% "juda xafa bo'lardim"** benchmarki (Superhuman 58% ga yetgan)

Yig'gan narsangizni yuqoridagi 1-rejim ajratib olish freymvorki va ishonch himoyalari orqali tahlil qiling.

---

## Persona yaratish

### Hali sharhlar bo'lmaganda

Erta bosqichdagi mahsulotlar (yoki yangi kategoriyalar) first-party sharh ma'lumotiga ega emas. Personalarni to'qimang — proksi manbalar bo'ylab tartib bilan tashqariga yuring:

1. **O'z farqlovchingiz** — mahsulot boshqacha nima qiladi, bu farqni kim eng kuchli his qiladi; gipotezani gipoteza sifatida yozib qo'ying
2. **To'g'ridan-to'g'ri raqobatchilar sharhlari** — ularning mijozlari muammo sohasini o'z so'zlari bilan tasvirlaydi (nima maqtalgan va nima yetishmayotganiga e'tibor bering)
3. **Marketplace'lardagi o'xshash mahsulotlar** — bir xil vazifa uchun qo'shni yechimlarning Amazon/ilova-do'kon sharhlari
4. **Auditoriyani bo'lishuvchi qo'shni brendlar** — bu xaridor yana nima sotib oladi; ularning sharhlari xaridorning kengroq tili va qadriyatlarini ochadi

Bu tarzda qurilgan personalar muvaqqat: har birini proksi manba bilan belgilang va haqiqiy sharhlar kelganda proksi dalilni first-party dalil bilan almashtiring.


Personalar to'qilgan emas, tadqiqotdan qurilishi kerak. Izchil segmentdan kamida 5–10 ta ma'lumot nuqtasi (intervyu, sharh yoki hamjamiyat postlari) bo'lmaguncha persona yaratmang.

### Persona tuzilmasi

```
## [Persona nomi] — [Rol/Lavozim]

**Profil**
- Lavozim oralig'i: [masalan, "Marketing menejeridan marketing VP'gacha"]
- Kompaniya hajmi: [masalan, "50–500 xodim, Series A–C SaaS"]
- Soha: [agar tor bo'lsa]
- Kimga hisobot beradi: [kim]
- Boshqariladigan jamoa hajmi: [agar tegishli bo'lsa]

**Asosiy Job to Be Done**
[Bir jumla: ular o'z rolida qanday natijaga erishmoqchi?]

**Trigger hodisalar**
Nima ularni sizniki kabi yechim izlashga undaydi?
- [trigger 1]
- [trigger 2]

**Asosiy og'riqlar**
1. [Og'riq — iloji bo'lsa ularning so'zlari bilan]
2. [Og'riq]
3. [Og'riq]

**Istalgan natijalar**
- [Muvaffaqiyat ular uchun qanday ko'rinadi]
- [Uni qanday o'lchaydi]
- [Bu ularni boshlig'i/jamoasi oldida qanday ko'rsatadi]

**E'tirozlar va qo'rquvlar**
- [Sotib olish yoki almashtirishda nima ikkilantiradi]

**Ko'rib chiqadigan muqobillar**
- [Raqobatchi, o'zi qilish, hech narsa qilmaslik, kimnidir yollash]

**Asosiy lug'at**
Ular haqiqatan ishlatadigan so'z va iboralar (tadqiqotdan olingan):
- "[ibora]"
- "[ibora]"

**Ularga qanday yetib borish**
- Kanallar: [vaqtini qayerda o'tkazadi]
- Iste'mol qiladigan kontent: [formatlar, mavzular]
- Ishonadigan influenserlar/hamjamiyatlar: [ma'lum bo'lsa, aniq nomlar]
```

### Persona anti-patternlari

- **Ularni chiroyli nomlamang** ("Marketing Mari") — jamoangiz foydali deb bilmasa; bu ko'pincha chalg'itadi
- **Segmentlar bo'ylab o'rtacha qilmang** — hammani ifodalaydigan persona hech kimni ifodalamaydi
- **Tafsilotlarni to'qimang** — biror narsa bo'yicha ma'lumotingiz bo'lmasa, to'ldirmasdan bo'sh qoldiring
- **Har chorakda qayta ko'ring** — bozor va mahsulot o'zgargan sari personalar eskiradi

---

## Natija formatlari

Foydalanuvchiga nima kerakligiga qarab taklif eting:

1. **Tadqiqot sintezi hisoboti** — mavzular, iqtiboslar, naqshlar va ta'sirlar
2. **VOC iqtiboslar banki** — matnda foydalanish uchun mavzu bo'yicha tartiblangan verbatim iqtiboslar
3. **Persona hujjati** — tadqiqotdan qurilgan 1–3 persona
4. **Jobs-to-be-done xaritasi** — segment bo'yicha funksional, hissiy va ijtimoiy vazifalar
5. **Raqobat razvedkasi xulosasi** — mijozlar raqobatchilar va siz haqingizda nima deyishadi
6. **Tadqiqot bo'shliqlari tahlili** — hali nimani bilmaysiz va uni qanday topish

Natija yaratishdan oldin foydalanuvchidan qaysi natija(lar) kerakligini so'rang.

---

## Davom etishdan oldin so'raladigan savollar

Kontekst noaniq bo'lsa:

1. **Maqsad nima?** Xabarni yaxshilash? Persona qurish? Mahsulot bo'shliqlarini topish? Ketishni tushunish?
2. **Sizda nima bor?** (transkriptlar, so'rovnomalar, tiketlar, G2 sharhlari, hech narsa)
3. **Maqsadli segment kim?** (barcha mijozlar, muayyan daraja, ketgan foydalanuvchilar, sotib olmagan prospektlar)
4. **Mahsulotingiz nima?** (mahsulot marketing konteksti faylida bo'lmasa)
5. **Nimani topshirishni xohlaysiz?** (sintez hisoboti, persona, iqtiboslar banki, raqobat razvedkasi)

Beshovini birdaniga so'ramang — #1 va #2 dan boshlang, so'ng kerak bo'lganda davom eting.

---

## Bog'liq skilllar

| Qachon topshirish | Skill |
|-----------------|-------|
| Tadqiqotdan xabardor matn yozish | `copywriting` |
| VOC xulosalaridan foydalanib sahifani optimallashtirish | `cro` |
| Raqobatchi taqqoslash sahifasini qurish | `competitors` |
| Ketish tadqiqotidan ketishni oldini olish strategiyasini yaratish | `churn-prevention` |
| Tadqiqotdan xabardor pullik reklamani rejalash | `ads` |
| Og'riq/trigger bo'yicha tadqiqotdan foydalanib sovuq email yozish | `cold-email` |
| Mijoz tadqiqotini outbound uchun ICP'ga aylantirish | `prospecting` |
| Topilgan mavzular asosida kontent rejalash | `content-strategy` |
| Tadqiqotni keng qamrovli marketing rejasiga o'rash | `marketing-plan` |

---

## Operator qatlami (Tyrion lokal bilimi)

> Bu bo'lim — Tyrion (Saloxiddin, O'zbekiston targetolog agentligi) uchun lokal moslashuv. Vendor metodika o'zgarishsiz.

### Qachon ishlatiladi (UZ triggerlari)
- "mijozlar bilan suhbat qil" · "ICP/persona kerak" · "mijozlar nima deyishadi" · "so'rovnoma tuz" · "auditoriya tadqiqoti"

### UZ amaliyot qoidalari (manbalardan)
1. CustDev intervyu me'yori: 15–30 daqiqa, ochiq savollar, "nega" bilan boshlanuvchi savol 5 tadan oshmaydi; 10+ respondent, hammaga **bir xil** savol, insaytlar darhol jadvalga tushadi (manba: `local\wiki\custdev-shablonlar.md` §1)
2. Kelajak haqida so'ralmaydi — odam reallikda nima qilgani so'raladi; intervyuchi bahslashmaydi/baholamaydi ("Rahmat ayt / Bo'lma / Bahslashma / Baholama") (manba: `local\wiki\custdev-shablonlar.md` §1)
3. Savolnomada qo'rquv bloki majburiy: tovar mos kelmasligi, kechikish, **firibgarlik** (xizmatda: sifat, qaytarish/da'vo) — onlayn oldindan to'lovga ishonchsizlik bozorning eng katta to'sig'i ekani uchun (manba: `local\wiki\custdev-shablonlar.md` §2; `local\ozbekiston-konteksti.md` §4)
4. Intervyu/survey tili segmentga mos alohida olib boriladi: Toshkent B2B — ruscha, mintaqa/B2C — o'zbekcha (lotin); tarjima orqali emas (manba: `local\ozbekiston-konteksti.md` §3)
5. Kichik namuna statistikasi aldamchi: dastlabki 30 ta uchrashuvgacha o'z konversiya foizini hisoblab bo'lmaydi — tadqiqot xulosalari ham shu chegarada beriladi (manba: `wiki/sotuv-va-retention.md`)
6. Tadqiqot chiqishi bevosita voronkaga ulanadi: topilmalar asosida 3–4 saralash savoli quriladi (survey funnel) — "Uy egasimisiz?" tipidagi saralash (manba: `wiki/survey-funnel.md`)
7. Mijozlardan video-sharh so'rash — matnli sharhdan kuchli ishonch dalili; tadqiqot mahsulotlaridan biri sifatida yig'iladi (manba: `local\ozbekiston-konteksti.md` §4)
8. Tadqiqot natijasi chatda qolmaydi: xulosa `outputs\` ga fayl bo'lib yoziladi (manba: `memory.md` §2 qoida 2)

### Bog'liq lokal fayllar
- `local\wiki\custdev-shablonlar.md` — intervyu checklist, savolnoma tuzilishi (repo ildizi)
- `local\wiki\brend-pozitsiyalash.md` — topilmalarni pozitsiyalashga ulash
- `local\ozbekiston-konteksti.md` — til segmentlari va ishonch muammosi
- `wiki/survey-funnel.md` va `wiki/sotuv-va-retention.md` — vault (`wiki`): funnel savollari, 30 uchrashuv qoidasi
- `memory.md` — natija fayli qoidasi (repo ildizi)
