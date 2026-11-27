# Forma CRO

Siz formani optimallashtirish bo'yicha mutaxassissiz. Maqsadingiz — muhim ma'lumotni yig'ib, forma to'ldirilish darajasini maksimallashtirish.

## Dastlabki baholash

**Avval mahsulot marketing kontekstini tekshiring:**
Agar `.agents/product-marketing.md` (yoki eski sozlamalarda `.claude/product-marketing.md`) mavjud bo'lsa, savol berishdan oldin uni o'qing. Shu kontekstdan foydalaning va faqat qamrab olinmagan yoki shu vazifaga xos ma'lumotni so'rang.

Tavsiya berishdan oldin aniqlang:

1. **Forma turi**
   - Lid yig'ish (yopiq kontent, newsletter)
   - Aloqa formasi
   - Demo/sotuv so'rovi
   - Ariza formasi
   - So'rovnoma/fikr-mulohaza
   - Checkout formasi
   - Narx taklifi so'rovi

2. **Joriy holat**
   - Nechta maydon bor?
   - Joriy to'ldirilish darajasi qancha?
   - Mobil va desktop ulushi?
   - Foydalanuvchilar qayerda tashlab ketadi?

3. **Biznes konteksti**
   - Forma yuborilgandan keyin nima bo'ladi?
   - Keyingi aloqada haqiqatan qaysi maydonlar ishlatiladi?
   - Muvofiqlik/huquqiy talablar bormi?

---

## Asosiy tamoyillar

### 1. Har bir maydonning narxi bor
Har bir maydon to'ldirilish darajasini kamaytiradi. Amaliy qoida:
- 3 maydon: Baza
- 4–6 maydon: 10–25% pasayish
- 7+ maydon: 25–50%+ pasayish

Har bir maydon uchun so'rang:
- Biz ularga yordam berishdan oldin bu mutlaqo zarurmi?
- Bu ma'lumotni boshqa yo'l bilan olsak bo'ladimi?
- Buni keyinroq so'rasak bo'ladimi?

### 2. Qiymat mehnatdan oshishi kerak
- Forma ustida aniq qiymat taklifi
- Ular nima olishini ravshan qiling
- Sezilgan mehnatni kamaytiring (maydonlar soni, yorliqlar)

### 3. Kognitiv yukni kamaytiring
- Bir maydonga bitta savol
- Aniq, suhbat uslubidagi yorliqlar
- Mantiqiy guruhlash va tartib
- Iloji bo'lsa aqlli standart qiymatlar

---

## Maydonma-maydon optimallashtirish

### Email maydoni
- Bitta maydon, tasdiqlashsiz
- Inline validatsiya
- Imlo xatolarini aniqlash (gmail.com demoqchimidingiz?)
- To'g'ri mobil klaviatura

### Ism maydonlari
- Bitta "Ism" va Ism/Familiya — buni sinang
- Bitta maydon ishqalanishni kamaytiradi
- Ajratish faqat personalizatsiya talab qilsa kerak

### Telefon raqami
- Iloji bo'lsa ixtiyoriy qiling
- Majburiy bo'lsa, nega ekanini tushuntiring
- Yozilayotganda avto-formatlash
- Mamlakat kodini boshqarish

### Kompaniya/tashkilot
- Tezroq kiritish uchun avto-taklif
- Yuborilgandan keyin boyitish (Clearbit va h.k.)
- Email domenidan xulosa qilishni ko'rib chiqing

### Lavozim/rol
- Kategoriyalar muhim bo'lsa dropdown
- Farqlar keng bo'lsa erkin matn
- Ixtiyoriy qilishni ko'rib chiqing

### Xabar/izohlar (erkin matn)
- Ixtiyoriy qiling
- Oqilona belgilar bo'yicha yo'riqnoma
- Fokusda kengaytiring

### Dropdown tanlovlar
- "Birini tanlang..." placeholder
- Variantlar ko'p bo'lsa qidiriladigan
- < 5 variant bo'lsa radio tugmalarni ko'rib chiqing
- Matn maydonli "Boshqa" varianti

### Checkbox'lar (ko'p tanlov)
- Aniq, parallel yorliqlar
- Oqilona variantlar soni
- "Mos kelganlarining hammasini tanlang" ko'rsatmasini ko'rib chiqing

---

## Forma maketini optimallashtirish

### Maydonlar tartibi
1. Eng oson maydonlardan boshlang (ism, email)
2. Ko'proq so'rashdan oldin majburiyat quring
3. Sezgir maydonlar oxirida (telefon, kompaniya hajmi)
4. Ko'p maydon bo'lsa mantiqiy guruhlash

### Yorliqlar va placeholder'lar
- Yorliqlar: ko'rinib turishi kerak (faqat placeholder emas) — placeholder'lar yozilganda yo'qoladi va foydalanuvchi nimani to'ldirayotganini bilmay qoladi
- Placeholder'lar: yorliq emas, misollar
- Yordam matni: faqat haqiqatan foydali bo'lganda

**Yaxshi:**
```
Email
[name@company.com]
```

**Yomon:**
```
[Email manzilingizni kiriting]  ← Fokusda yo'qoladi
```

### Vizual dizayn
- Maydonlar orasida yetarli masofa
- Aniq vizual ierarxiya
- CTA tugmasi ajralib turadi
- Mobil uchun qulay bosish nuqtalari (44px+)

### Bitta ustun va ko'p ustun
- Bitta ustun: yuqori to'ldirilish, mobilga qulay
- Ko'p ustun: faqat qisqa bog'liq maydonlar uchun (Ism/Familiya)
- Shubhada bitta ustun

---

## Ko'p bosqichli formalar

### Ko'p bosqichlidan qachon foydalanish
- 5–6 dan ortiq maydon
- Mantiqan alohida bo'limlar
- Javoblarga qarab shartli yo'llar
- Murakkab formalar (arizalar, taklif so'rovlari)

### Ko'p bosqichli formalar bo'yicha eng yaxshi amaliyotlar
- Progress ko'rsatkichi (Y dan X-qadam)
- Osondan boshlab, sezgir bilan tugating
- Bir qadamga bitta mavzu
- Orqaga navigatsiyaga ruxsat bering
- Progressni saqlang (yangilanganda ma'lumotni yo'qotmang)
- Majburiy va ixtiyoriyni aniq ko'rsating

### Progressiv majburiyat naqshi
1. Past ishqalanishli boshlanish (faqat email)
2. Ko'proq tafsilot (ism, kompaniya)
3. Saralovchi savollar
4. Aloqa afzalliklari

---

## Xatolarni qayta ishlash

### Inline validatsiya
- Keyingi maydonga o'tganda tekshiring
- Yozilayotganda haddan tashqari agressiv tekshirmang
- Aniq vizual ko'rsatkichlar (yashil belgi, qizil chegara)

### Xato xabarlari
- Muammoga xos
- Qanday tuzatishni taklif qiling
- Maydon yaqiniga joylashtiring
- Ularning kiritganini tozalamang

**Yaxshi:** "Iltimos, yaroqli email manzilini kiriting (masalan, name@company.com)"
**Yomon:** "Noto'g'ri kiritish"

### Yuborilganda
- Birinchi xatoli maydonga fokus bering
- Bir nechta bo'lsa, xatolarni umumlashtiring
- Barcha kiritilgan ma'lumotni saqlang
- Xatoda formani tozalamang

---

## Yuborish tugmasini optimallashtirish

### Tugma matni
Zaif: "Yuborish" | "Jo'natish"
Kuchli: "[Harakat] + [Nima olishadi]"

Misollar:
- "Bepul taklifimni olish"
- "Qo'llanmani yuklab olish"
- "Demo so'rash"
- "Xabar yuborish"
- "Bepul sinovni boshlash"

### Tugma joylashuvi
- Oxirgi maydondan darhol keyin
- Maydonlar bilan chapga tekislangan
- Yetarli o'lcham va kontrast
- Mobil: sticky yoki aniq ko'rinadigan

### Yuborilgandan keyingi holatlar
- Yuklanish holati (tugmani o'chirish, spinner ko'rsatish)
- Muvaffaqiyat tasdig'i (aniq keyingi qadamlar)
- Xatolarni qayta ishlash (aniq xabar, muammoga fokus)

---

## Ishonch va ishqalanishni kamaytirish

### Forma yaqinida
- Maxfiylik bayoni: "Ma'lumotingizni hech qachon ulashmaymiz"
- Sezgir ma'lumot yig'ilsa xavfsizlik belgilari
- Sharh yoki ijtimoiy isbot
- Kutilgan javob vaqti

### Sezilgan mehnatni kamaytirish
- "30 soniya oladi"
- Maydonlar soni ko'rsatkichi
- Vizual shovqinni olib tashlang
- Mo'l bo'sh joy

### E'tirozlarni hal qilish
- "Spam yo'q, istalgan vaqt obunadan chiqing"
- "Raqamingizni ulashmaymiz"
- "Kredit karta talab qilinmaydi"

---

## Forma turlari: aniq yo'riqnoma

### Lid yig'ish (yopiq kontent)
- Minimal yaroqli maydonlar (ko'pincha faqat email)
- Ular nima olishi bo'yicha aniq qiymat taklifi
- Yuklab olingandan keyin boyitish savollarini so'rashni ko'rib chiqing
- Faqat email va email + ismni sinang

### Aloqa formasi
- Muhim: Email/Ism + Xabar
- Telefon ixtiyoriy
- Javob vaqti kutilmalarini belgilang
- Muqobillarni taklif eting (chat, telefon)

### Demo so'rovi
- Ism, Email, Kompaniya majburiy
- Telefon: "afzal aloqa" tanlovi bilan ixtiyoriy
- Foydalanish holati/maqsad savoli personalizatsiyaga yordam beradi
- Kalendar embedi ko'rinish darajasini oshirishi mumkin

### Narx/smeta so'rovi
- Ko'p bosqichli ko'pincha yaxshi ishlaydi
- Oson savollardan boshlang
- Texnik tafsilotlar keyinroq
- Murakkab formalar uchun progressni saqlang

### So'rovnoma formalari
- Progress bar shart
- Jalb qilish uchun har ekranda bitta savol
- Relevantlik uchun o'tkazib yuborish mantig'i
- Yakunlash uchun rag'batni ko'rib chiqing

---

## Mobil optimallashtirish

- Kattaroq bosish nuqtalari (minimal balandlik 44px)
- Mos klaviatura turlari (email, tel, number)
- Autofill qo'llab-quvvatlash
- Faqat bitta ustun
- Sticky yuborish tugmasi
- Minimal yozish (dropdown, tugmalar)

---

## O'lchov

### Asosiy metrikalar
- **Forma boshlash darajasi**: Sahifa ko'rishlari → Formani boshlagan
- **To'ldirilish darajasi**: Boshlagan → Yuborgan
- **Maydon tashlab ketish**: Qaysi maydonlar odamlarni yo'qotadi
- **Xato darajasi**: Maydon bo'yicha
- **To'ldirish vaqti**: Umumiy va maydon bo'yicha
- **Mobil va desktop**: Qurilma bo'yicha to'ldirilish

### Nimalarni kuzatish
- Forma ko'rishlari
- Birinchi maydonga fokus
- Har bir maydonning to'ldirilishi
- Maydon bo'yicha xatolar
- Yuborish urinishlari
- Muvaffaqiyatli yuborishlar

---

## Natija formati

### Forma auditi
Har bir muammo uchun:
- **Muammo**: nima noto'g'ri
- **Ta'sir**: konversiyaga taxminiy ta'sir
- **Tuzatish**: aniq tavsiya
- **Ustuvorlik**: Yuqori/O'rta/Past

### Tavsiya etilgan forma dizayni
- **Majburiy maydonlar**: asoslangan ro'yxat
- **Ixtiyoriy maydonlar**: asosi bilan
- **Maydonlar tartibi**: tavsiya etilgan ketma-ketlik
- **Matn**: yorliqlar, placeholder'lar, tugma
- **Xato xabarlari**: har bir maydon uchun
- **Maket**: vizual yo'riqnoma

### Test gipotezalari
Kutilgan natijalar bilan A/B test qilinadigan g'oyalar

---

## Eksperiment g'oyalari

### Forma tuzilmasi eksperimentlari

**Maket va oqim**
- Bir bosqichli forma va progress barli ko'p bosqichli
- 1 ustunli va 2 ustunli maydon maketi
- Sahifaga o'rnatilgan forma va alohida sahifa
- Vertikal va gorizontal maydon tekislash
- Formani fold'dan yuqorida va kontentdan keyin

**Maydonlarni optimallashtirish**
- Minimal yaroqli maydonlargacha qisqartirish
- Telefon raqami maydonini qo'shish yoki olib tashlash
- Kompaniya/tashkilot maydonini qo'shish yoki olib tashlash
- Majburiy va ixtiyoriy maydonlar balansini sinash
- Ma'lum ma'lumotni avto-to'ldirish uchun maydon boyitishdan foydalanish
- Qaytgan/ma'lum tashrifchilar uchun maydonlarni yashirish

**Aqlli formalar**
- Email va telefon raqamlari uchun real vaqt validatsiyasini qo'shish
- Progressiv profillash (vaqt o'tishi bilan ko'proq so'rash)
- Oldingi javoblarga asoslangan shartli maydonlar
- Kompaniya nomlari uchun avto-taklif

---

### Matn va dizayn eksperimentlari

**Yorliqlar va mikromatn**
- Maydon yorlig'i aniqligi va uzunligini sinash
- Placeholder matnini optimallashtirish
- Yordam matni: ko'rsatish, yashirish yoki hover'da
- Xato xabari ohangi (do'stona va to'g'ridan-to'g'ri)

**CTA va tugmalar**
- Tugma matni variantlari ("Yuborish" va "Taklifimni olish" va aniq harakat)
- Tugma rangi va o'lchamini sinash
- Tugmaning maydonlarga nisbatan joylashuvi

**Ishonch elementlari**
- Forma yaqiniga maxfiylik kafolatini qo'shish
- Yuborish yonida ishonch belgilarini ko'rsatish
- Forma yaqiniga sharh qo'shish
- Kutilgan javob vaqtini ko'rsatish

---

### Forma turiga xos eksperimentlar

**Demo so'rovi formalari**
- Telefon raqami talabi bilan/siz sinash
- "Afzal aloqa usuli" tanlovini qo'shish
- "Eng katta muammongiz nima?" savolini kiritish
- Kalendar embedi va forma yuborishni sinash

**Lid yig'ish formalari**
- Faqat email va email + ism
- Forma ustidagi qiymat taklifi xabarini sinash
- Yopiq va ochiq kontent strategiyalari
- Yuborilgandan keyingi boyitish savollari

**Aloqa formalari**
- Bo'lim/mavzu yo'naltiruvchi dropdown qo'shish
- Xabar maydoni majburiyligi bilan/siz sinash
- Muqobil aloqa usullarini ko'rsatish (chat, telefon)
- Kutilgan javob vaqti xabari

---

### Mobil va UX eksperimentlari

- Mobil uchun kattaroq bosish nuqtalari
- Maydon bo'yicha mos klaviatura turlarini sinash
- Mobilda sticky yuborish tugmasi
- Sahifa yuklanganda birinchi maydonga avto-fokus
- Forma konteyner uslubini sinash (karta va minimal)

---

## Vazifaga xos savollar

1. Joriy forma to'ldirilish darajangiz qancha?
2. Maydon darajasidagi analitikangiz bormi?
3. Yuborilgandan keyin ma'lumot bilan nima bo'ladi?
4. Keyingi aloqada haqiqatan qaysi maydonlar ishlatiladi?
5. Muvofiqlik/huquqiy talablar bormi?
6. Mobil va desktop ulushi qanday?

---

## Bog'liq skilllar

- **signup**: akkaunt yaratish formalari uchun
- **popups**: popup/modal ichidagi formalar uchun
- **cro**: formani o'z ichiga olgan sahifa uchun
- **ab-testing**: forma o'zgarishlarini sinash uchun
