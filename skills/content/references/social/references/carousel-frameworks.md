# Karusel freymvorklari

Karusellar uchun slayd-ba-slayd beshta rivoyat arxitekturasi — Instagram karusellari va LinkedIn hujjat postlari. Har bir freymvork — *scroll qilishni davom ettirish uchun* alohida sabab; kontent uchun to'g'ri freymvorkni tanlash alohida slaydlarni sayqallashdan ko'ra muhimroq.

Karusel — kvadratlarga bo'laklangan blog post emas. Bu har bir slaydda ikkita vazifasi bor swipe: bitta g'oyani yetkazish va keyingi swipe'ni qarshilik qilib bo'lmaydigan qilish. Bu freymvorklar yuqori natijali karusellarda qayta-qayta uchraydigan tuzilmalarni aks ettiradi; ularni qat'iy formula emas, moslashtiriladigan boshlang'ich tuzilma deb biling — va o'z analitikangizga qarshi tekshirishni kuting.

## Freymvork tanlash

| Kontentingiz... | Foydalaning | Nega |
|---|---|---|
| Resurslar, asboblar yoki maslahatlar ro'yxati | **A: Value-Stack** | To'liqlik — va'da; son — hook |
| Ortida tizimi bor shaxsiy natija | **B: Problem-Proof** | Isbot siklni ochadi va yopadi; tizim — asosiy qism |
| Bitta mavzu bo'yicha bir nechta nomlangan texnika | **C: Hack List** | Har bir hack swipe'ni mustaqil qayta qozonadi |
| Keng tarqalgan amaliyot haqida kuchli fikr | **D: Rant Callout** | Ishonch — kontent; tuzilma uni adolatli saqlaydi |
| Ko'rsatsa bo'ladigan mahsulot yoki ish jarayoni | **E: Demo Walkthrough** | Qadamlarni ko'rish ularni tasvirlashdan ko'ra ishontiruvchi |

Tafsilotlardan oldin ikkita freymvorklar-aro qoida:

- **1-slayd — thumbnail.** U feedda yolg'iz raqobatlashadi, hech kim karusel davom etishini bilmasdan oldin. Uni mustaqil scroll-to'xtatuvchi sifatida loyihalang va yozing.
- **Karusel uchun bitta vizual shablon.** Har bir ichki slaydda bir xil maket, shrift shkalasi va palitra. Slaydlar o'rtasidagi xilma-xillik tartibsizlik bo'lib o'qiladi; izchillik ramka o'zgarmay turganda *kontent* o'zgarishiga imkon beradi.

---

## A freymvork: Value-Stack (4–14 slayd)

"Sizga kerak bo'lgan hamma narsa" karuseli. U ishlaydi, chunki cover to'liqlik da'vosini — aniq son va aniq yetkaziladigan narsani — bildiradi va har bir swipe uni to'laydi.

| Slayd | Vazifa | Naqsh |
|---|---|---|
| 1 — Cover | Aniq son + aniq yetkaziladigan narsani ayting. Aniqlik masshtabni oldindan isbotlaydi. | "[Rol/natija] uchun [N] ta [resurs turi]" |
| 2 dan N−1 gacha — Qiymat yetkazish | Har bir slaydda bitta element yoki kategoriya, har biri uchun 3–6 aniq kichik element. Bir xil vizual shablon, bo'sh slaydlar yo'q. | "[Kategoriya/element] — [kichik elementlar]" |
| N — Yakun | Swipe'ni harakatga aylantiring. | "[Foyda] uchun [harakat]" — kalit so'z izohlang, follow qiling, bio'dagi havola |

**Nega aniq son muhim:** "27 ta bepul asbob" "eng yaxshi bepul asboblar" dan yaxshiroq ishlaydi, chunki raqam tekshirsa bo'ladigan va'da — o'quvchi yetkazganingizni tekshira oladi. Ortiqcha to'ldirish bilan yaxlitlash son yaratgan ishonchni buzadi.

*SaaS misoli:* "SaaS onboarding emaillari uchun 12 ta ChatGPT prompt" → har bir slaydda bitta prompt va foydalanish holati → "PROMPTS deb izohlang, to'liq hujjatni yuboraman."

**Nosozlik rejimi:** kattaroq songa erishish uchun bo'sh slaydlar. Haqiqiy songacha qisqartiring; ixcham 8 ta to'ldirilgan 14 tadan yaxshi.

---

## B freymvork: Problem-Proof (6–10 slayd)

"Men X qildim, mana tizim" karuseli. Hook — maslahat emas, *fakt sifatida aytilgan natija* — va oxirgi slayd 1-slayd ochgan siklni yopib, kvitansiyani ko'rsatadi.

| Slayd | Vazifa | Naqsh |
|---|---|---|
| 1 — Hook | Raqamli aniq shaxsiy da'vo. Natija, maslahat emas. | "[Men/biz X qildik]. [Aniq natija, raqam bilan]." |
| 2 — Muammoni qayta freymlash | *Aslida* nima noto'g'ri ketayotganini nomlang, o'quvchi o'zini tanisin. | "Haqiqiy muammo — [nomlangan masala]" |
| 3–4 — Mexanizm | Haqiqiy tizimni ko'rsating: nomlangan asboblar, nomlangan qadamlar. Aniqlik noaniqlikdan yaxshi. | "Tizim — [nomlangan asboblar/qadamlar]" |
| 5 dan N−1 gacha — Tafsilot | So'zma-so'z prompt matni, shablon yoki qadamma-qadam. Bu saqlashga loyiq qism. | "[So'zma-so'z prompt yoki jarayon tafsiloti]" |
| N — Isbot | Haqiqiy natija artefakti. Tavsif emas, skrinshot. | "[Natija skrinshoti] — kvitansiya" |

**Ochiq sikl — dvigatel:** 1-slayd da'vo qiladi, oxirgisi uni isbotlaydi, oradagi hamma narsa qanday ekanini tushuntiradi. O'quvchilar kvitansiya haqiqiy ekanini ko'rish uchun swipe qiladi.

*SaaS misoli:* "Bitta onboarding emaili bilan churn'ni 22% ga kamaytirdik." → haqiqiy muammo (narx emas, aktivatsiya) → ketma-ketlik tuzilmasi → so'zma-so'z email matni → retention grafigi.

**Nosozlik rejimi:** noaniq mexanizm slaydlari ("ish jarayoningizni optimallashtiring") — o'rtadagi slaydlar asboblar va qadamlarni nomlamasa, isbot slaydi tizim emas, omad bo'lib o'qiladi.

---

## C freymvork: Hack List (6–10 slayd)

"Raqamlangan texnikalar" karuseli. Qarama-qarshi cover maqom tashvishini yaratadi — ko'pchilik buni noto'g'ri qilmoqda — va har bir raqamlangan hack swipe'ni mustaqil qayta qozonadi.

| Slayd | Vazifa | Naqsh |
|---|---|---|
| 1 — Qarama-qarshi hook | Ko'pchilik bunda muvaffaqiyatsiz bo'lishini bildiruvchi statistika yoki da'vo. | "[Ko'pchilik X da muvaffaqiyatsiz ekanini bildiruvchi statistika]" |
| 2 — Muammo | Umumiy yondashuv nega ishlamaydi, ideal holda analogiya bilan. | "Muammo — [nega ishlamaydi]" |
| 3 dan N−1 gacha — Raqamlangan hack'lar | Har bir slaydda bitta nomlangan texnika. Yomon-va-yaxshi kontrasti har bir hack'ni bir zumda yetkazadi. | "Hack #[n] — [nomlangan texnika]" |
| N — Sintez + yakun | Hack'larni bog'laydigan bir qatorli tezis, so'ng saqlash/ulashish/follow CTA. | "[Hack'larni bog'laydigan tezis]" + [CTA] |

**Har bir texnikani nomlang.** "3 soniya qoidasi" ulashsa bo'ladigan va esda qoladigan; "qisqa qiling" — ikkalasi ham emas. Nomlangan texnikalar tarqaladi — odamlar ularni takrorlaydi va manbani eslaydi.

*SaaS misoli:* "Sinov emaillarining 90% hech qachon ochilmaydi." → nega (ular xabar emas, kvitansiyaga o'xshaydi) → Hack #1: Asoschi-from qatori, Hack #2: Bitta savolli mavzu, ... → "Sinov emaillari — tasdiqlash emas, suhbat. Keyingi ketma-ketligingiz uchun saqlang."

**Nosozlik rejimi:** bir-birini takrorlaydigan hack'lar. Har bir slayd yolg'iz o'zi turishi kerak — ikkita hack bitta g'oyaga qulasa, ularni birlashtiring va qisqaroq qiling.

---

## D freymvork: Rant Callout (4–8 slayd)

"Kimdir buni aytishi kerak edi" karuseli. Shaxsiyatga yo'naltirilgan va dizayn bo'yicha qutblantiruvchi — tuzilma qizg'inlikni *adolatli* saqlash uchun mavjud, shunda u achchiqlik emas, ishonch bo'lib o'qiladi.

| Slayd | Vazifa | Naqsh |
|---|---|---|
| 1 — Provokatsion da'vo | Keng tarqalgan amaliyot haqida mashhur bo'lmagan fikr yoki to'g'ridan-to'g'ri ayblov. | "Mashhur bo'lmagan fikr — [keng tarqalgan amaliyot]" |
| 2 dan N−2 gacha — Argumentni kuchaytirish | Sezgi orqali sezilarli, aniq tafsilot. Huquqbuzarlikni ko'rsating; mavhum ishora qilmang. Har bir slayd garovni oshiradi. | "[Kuchayib boruvchi, aniq shikoyat]" |
| N−1 — Adolat burilishi | "Meni noto'g'ri tushunmang…" — nimani *hujum qilmayotganingizni* aniqlang. Dangasalikka qarshi, asbobga emas; amaliyotga qarshi, odamga emas. | "Muammo [X] emas, [Y]" |
| N — Yakun | Qat'iy, shaxsiyatga yo'naltirilgan xayrlashuv. Imzolangan rant'lar egalik qilingan fikr, anonimlari esa yerdan otilgan o'q bo'lib o'qiladi. | "[Qat'iy xayrlashuv] — imzo [ism/persona]" |

**Adolat burilishi uni ishlatadi.** Usiz siz baqiryapsiz; u bilan aniq chiziq chizyapsiz, aniq chiziqlar esa iqtibos qilinadi. U shuningdek eng yomon dushmanlik izohini oldindan to'xtatadi.

*SaaS misoli:* "AI yaratgan LinkedIn postlaringiz sizga mijozlarga qimmatga tushmoqda." → aniq tafsilotlar (bir xil em-dash ritmi, bir xil 'game-changer' lug'ati, nol real tafsilot) → "Meni noto'g'ri tushunmang — men AI'dan har kuni foydalanaman. Muammo asbob emas, birinchi qoralamani nashr qilishda." → "Gapirganingizdek yozing. — [Ism]"

**Nosozlik rejimlari:** burilishni o'tkazib yuborish (aqldan ozgandek o'qiladi, hujumlarni taklif qiladi) yoki o'z mahsulotingiz/kontentingiz ko'rinib turgan narsa haqida rant qilish (izohlar buni topadi).

---

## E freymvork: Demo Walkthrough (5–11 slayd)

Mahsulot yoki ish jarayoni kontenti uchun "ishlaganini ko'ring" karuseli. Avval tugallangan natijani, keyin qadamlarni ko'rsating — natija jarayon uchun e'tibor qozonadi.

| Slayd | Vazifa | Naqsh |
|---|---|---|
| 1 — Mahsulot + natija | Brend/mahsulot plyus tugallangan natija. Ular nima olishidan boshlang. | "[Mahsulot] + [natija], tugallangan natija" |
| 2 — U hal qiladigan muammo | Bu almashtiradigan aniq asabiylashish. | "[Bu almashtiradigan aniq og'riq]" |
| 3 — Jarayonga umumiy nazar | Tafsilotdan *oldin* ko'rsatiladigan raqamlangan qadamlar ro'yxati. Butun yo'lni ko'rish swipe o'rtasidagi tashlab ketishni kamaytiradi — o'quvchilar yo'l qancha uzunligini bilganda majburiyat oladi. | "[Vaqt] ichida [natija]ga [N] qadam" |
| 4 dan N−1 gacha — Qadamma-qadam | Har bir qadam uchun bitta haqiqiy UI skrinshoti qisqa caption bilan. Haqiqiy skrinshotlar; mockup'lar vaporware bo'lib o'qiladi. | "[n]-qadam — [skrinshot] — [caption]" |
| N — Natija + pozitsiyalash | To'liq o'lchamli natija plyus bitta brend-falsafa qatori. | "[Yakuniy natija] + [pozitsiyalash qatori]" |

**Tafsilotdan oldin umumiy nazar — asosiy harakat** (retsept saytlari ko'rsatmalardan oldin ingredientlarni ro'yxatlashining sababi bilan bir xil): 3-slaydda "4 qadam, 10 daqiqa" ni ko'rgan o'quvchi tugatadi; xaritasiz to'g'ridan-to'g'ri 1-qadamga tushgan o'quvchi 2-qadamda ketib qoladi.

*SaaS misoli:* "CSV'dan jonli dashboardga 4 qadamda" → og'riq (haftalik qo'lda hisobot) → 4 qadamli umumiy nazar → har bir qadam uchun bitta skrinshot → tugallangan dashboard + "Analitiklar emas, marketologlar uchun qurilgan."

**Nosozlik rejimi:** juda ko'p UI'li skrinshotlar. Harakatgacha kesing, tegishli boshqaruvni zoom qiling, bitta o'q bilan belgilang — har bir skrinshot thumbnail o'lchamida ham mantiqli bo'lishi kerak.

---

## Platforma eslatmalari

**Instagram:** 1080×1350 (4:5) slaydlar; 20 gacha slayd, lekin yuqoridagi freymvork diapazonlari tugallash darajalari saqlanadigan joyni aks ettiradi. Caption qidiriladigan matnni olib yuradi — hook'ni qayta bayon qiling va kontekst qo'shing, shunchaki 1-slaydni takrorlamang. Birinchi slayd grid thumbnail vazifasini ham o'taydi.

**LinkedIn (hujjat postlari):** PDF sifatida yuklang. Kvadrat yoki 4:5. LinkedIn "N sahifa" nishonini ko'rsatadi — Value-Stack'ning aniq sonli cover'i bu yerda ayniqsa yaxshi ishlaydi. B2B Instagram'dan ko'ra har bir slaydda zichroq matnni qabul qiladi, lekin har bir slaydda bitta g'oya qoidasi baribir amal qiladi. Hujjat ustidagi post matni — ikkinchi hook: uni "ilovaga qarang" kabi tashlab yuboriladigan emas, alohida post sifatida yozing.

**TikTok photo mode:** Bir xil freymvorklar ishlaydi; sur'at tezroq — har bir freymvorkni minimal slaydlar soniga qarab qisqartiring.

## Ishlab chiqarish cheklisti

- [ ] 1-slayd mustaqil feed posti sifatida ishlaydi (sinov: orqasida karusel bo'lmasa, scroll'ni to'xtatarmidi?)
- [ ] Har bir slaydda bitta g'oya — slaydga ikki gaplik setup kerak bo'lsa, bo'ling
- [ ] Har bir ichki slaydda bir xil vizual shablon
- [ ] Cover'da va'da qilingan har qanday son aynan yetkazilgan (bo'sh to'ldirish yo'q, yaxlitlash yo'q)
- [ ] Da'volar va raqamlar haqiqiy va sizniki — to'qilgan statistika yoki olingan skrinshotlar yo'q
- [ ] Matn thumbnail o'lchamida o'qiladi (1080px kenglikda minimal ~28pt)
- [ ] Oxirgi slaydda uchta emas, bitta CTA
- [ ] Caption/post matni 1-slaydni takrorlash emas, o'z hook sifatida yozilgan

## Nima ishlaganini o'lchash

Karusellarni yoqishlar emas, **saqlash va tugatish** bo'yicha baholang — saqlashlar ma'lumotnoma qiymatini bildiradi (karusellar uchun algoritmik g'alaba) va slayd bo'yicha analitika mavjud bo'lgan joyda (Instagram professional insights, LinkedIn document analytics yoki uchinchi tomon asboblari) tashlab ketish pozitsiyasi qaysi slayd swipe zanjirini uzganini aytadi. Karusel yomon ishlasa, tuzatish odatda 1-slayd (scroll'ni to'xtatmadi) yoki freymvork tanlovi (ro'yxat kontenti rant tuzilmasiga majburlangan), o'rtadagi slaydlar emas. Har bir freymvork bo'yicha natijani kuzating va auditoriyangizga mos ikkitasiga ko'proq e'tibor bering — tahlil ish jarayoni uchun [reverse-engineering.md](reverse-engineering.md) ga qarang.
