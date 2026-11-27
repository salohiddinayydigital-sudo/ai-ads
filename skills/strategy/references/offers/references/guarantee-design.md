# Kafolat dizayni

Kafolat *erishishning sezilgan ehtimolini* bevosita oshiradi (xaridor o'ylaydi: "ular buni faqat ishonch komil bo'lsagina taklif qiladi") va *mehnat va qurbonlikni* kamaytiradi (hissiy xavf kamroq). U taklif dizaynidagi eng yuqori ta'sirli richaglardan biri.

Noto'g'ri kafolat umuman kafolat bo'lmagandan ko'ra ko'proq zarar qiladi. Biznes modelingizga mos turni tanlang.

## Sakkiz kafolat turi

| Tur | Nimani va'da qiladi | Qachon ishlaydi | Qachon teskari ta'sir qiladi |
|------|------------------|---------------|-------------------|
| 1. **Shartsiz pulni qaytarish** | "X kun ichida istalgan vaqt savolsiz qaytarish" | Past narxli axborot, yuqori ishonchli auditoriya | Qimmat/yuqori-aloqali; qaytarish xavfi marjani yeydi |
| 2. **Shartli pulni qaytarish** | "X ni bajarsangiz va baribir Y ko'rmasangiz, qaytaramiz" | Mehnat talab qiladigan kurslar, dasturlar | Tajribali xaridorlar; ommaviy sharaflash qiyinroq |
| 3. **Pulni qaytarishdan yaxshiroq** | "Ishlamasa, to'liq qaytarish + $X" | Ishonchli yetkazib berish, yetarli marja | Muvaffaqiyatsiz bo'lsangiz; kam nosozliklar ommaviy portlaydi |
| 4. **Xizmat darajasi / SLA** | "Agar Y gacha X ni yetkazmasak, pulingiz qaytariladi" | Productized xizmatlar, agentlik ishi | O'lchay olmaydigan noaniq SLA'lar |
| 5. **Natijaga asoslangan** | "Faqat X sodir bo'lganda to'lang" (rev share, natijaga asoslangan) | Tajribali B2B, ishonchli yetkazib berish | Uzun sikllar, atributsiyasi qiyin natijalar |
| 6. **Anti-kafolat** | "Qaytarish yo'q. Buni xohlashingizga ishonch hosil qiling." | Premium auditoriya, yetuk xaridorlar | Chalkash / birinchi marta xaridorlar; sovuq o'qiladi |
| 7. **Natija-yoki-uzaytirish** | "Y gacha X ga erishmasangiz, bepul davom etamiz" | Koucing, vaqtni uzaytirsa bo'ladigan xizmatlar | Cheksiz xarajat; ehtiyotkorlik bilan tanlang |
| 8. **Taqqoslash kafolati** | "[Raqobatchi] natijasidan o'zing — yoki qaytarish" | Ishonchli taqqoslay olganda | Raqobatchini toza o'lchay olmaganda |

---

## To'g'risini tanlash

Qaror daraxti:

1. **Xaridoringizning eng katta sezilgan xavfi nima?**
   - "Ishlamasa-chi?" → pulni qaytarish oilasi (1, 2, 3)
   - "Vaqtida yetkazmasangiz-chi?" → SLA (4)
   - "To'lab, natija olmasam-chi?" → natijaga asoslangan (5) yoki natija-yoki-uzaytirish (7)
   - "Bu haqiqiymi yoki firibgarlikmi?" → taqqoslash yoki aniqlikka asoslangan (8)

2. **Qaytarishga toqatingiz qanday?**
   - Ko'lamda qaytarishlarni ko'tara olsangiz → shartsiz (1)
   - Qaytarish so'ragunlarni saralash kerak → shartli (2)
   - Ustiga bonus qo'shadigan darajada ishonchli → pulni qaytarishdan yaxshiroq (3)
   - Umuman qaytarishlarni ko'tara olmaysiz → anti-kafolat (6) yoki kafolat yo'q + kuchli isbot

3. **Xaridor tajribasi qanday?**
   - Premium / yetuk xaridorlar → anti-kafolat ishlashi mumkin; "biz qaytarish qilmaymiz" ishonch sifatida o'qiladi
   - Kategoriyada birinchi marta kelgan xaridorlar → kuchli qaytarish kafolati; ularga sinab ko'rishga ruxsat kerak
   - Tajribali B2B → SLA yoki natijaga asoslangan; ular tijoriy shartlarni kutadi

4. **Natija qanchalik o'lchanadi?**
   - Toza va o'lchanadigan → natijaga asoslangan, taqqoslash yoki natija-yoki-uzaytirish
   - Xira / sub'ektiv → shartli darvozali pulni qaytarish oilasi (siz ishni bajardingiz)

---

## Biznes turi bo'yicha misollar

### Kurs / kogorta

**Kuchli:** "60 kun ichida barcha oltita modulni yakunlang, yakuniy mashqni topshiring va agar [aniq natija] bo'lmasa, to'liq qaytaramiz." Mehnatga shartli, natijada aniq.

**Zaif:** "100% pulni qaytarish kafolati." Shartlarsiz = hech qachon qatnashmagan xaridorlar uchun qaytarish magniti.

### Koucing / konsalting

**Kuchli:** "Dastlabki ikki sessiyadan keyin, agar hamkorlik natija bermaydi deb o'ylasangiz, uni tugatamiz va ishlatilmagan qoldiqni qaytaramiz." Hamkorlik o'rtasidagi chiqish yo'li ishonch quradi.

**Zaif:** "Qoniqish kafolatlangan." Hech narsani anglatmaydi.

### Productized xizmat / agentlik retainer

**Kuchli:** "Birinchi oy — pullik pilot. Oxirida, agar [aniq bosqich] ko'rmasangiz, 2-oy uchun to'lamaysiz va yaxshi shartlarda tugatamiz." Aniq darvoza, aniq chiqish.

**Zaif:** "Siz mamnun bo'lguncha ishlaymiz." Cheksiz xarajat. Qilmang.

### Qimmat axborot mahsuloti (hamjamiyat, mastermind)

**Kuchli (premium auditoriya):** "Qaytarish yo'q. Ariza jarayoni qat'iy, chunki qiymat haqiqiy. Ishonchingiz komil bo'lmasa, hali ariza bermang." Anti-kafolat bu yerda ishlaydi.

**Zaif (premium auditoriya):** Umumiy 30 kunlik qaytarish. Arzon o'qiladi.

### Arzon axborot mahsuloti (shablon, swipe fayl)

**Kuchli:** "30 kunlik savolsiz qaytarish." Tranzaksion mezon: "sotib oldim, ko'rdim, xohlamadim." Shartsiz mos keladi.

**Zaif:** Kafolat yo'q. Narxga nisbatan xaridor xavfi juda yuqori.

### SaaS

**Kuchli:** Bepul sinov *yoki* birinchi 30 kunda pulni qaytarish bilan yillik oldindan to'lov. Norozi foydalanuvchilarni qamamasdan ishqalanishni kamaytiradi.

**Zaif:** Yolg'iz "istalgan vaqt bekor qiling" — kafolat emas, standart SaaS shartlari.

### Direct response / pullik trafik

**Kuchli:** Pulni ikki baravar qaytarish yoki shunga o'xshash xavfni teskari qilish. Direct-response xaridorlari xavfni qaytarishga boy takliflarni kutadi.

**Zaif:** Oddiy 30 kunlik qaytarish. Platformadagi boshqa har bir reklamadan farqlamaydi.

---

## Kafolatni yozish

Kafolat matni muhim. Ishlaydigan naqshlar:

**Aniq shartlar:**
> Agar dasturning dastlabki 4 haftasini tugatgandan keyin erishgan bitta aniq biznes natijangizni ko'rsata olmasangiz, bizga email yozing va 100% qaytaramiz.

**Ishonchli ohang:**
> Biz buning ishlashini bilamiz. Agar siz uchun ishlamasa, pulingizni xohlamaymiz.

**Noqulaylikni tan oling:**
> Kafolatlar yoqimsiz tuyuladi. Mana baribir bizniki: agar 1–3 modullardagi ishni bajarib, sezilarli tortishuv ko'rmasangiz, qaytaramiz.

**Ishlamaydigan naqshlar:**

- "100% qoniqish kafolatlangan!" — umumiy, past ishonch
- "Umrbod kafolat" — shartlarsiz ma'nosiz
- Bir nechta to'plangan kafolatlar — tajribani yo'q qiladi
- Huquqiy jargonga to'la kafolatlar — xaridorlar ko'z yugurtiradi va eng yomonini taxmin qiladi

---

## Keng tarqalgan xatolar

### Yetkaza oladiganingizdan ko'proq va'da qilish

"Daromadingizni ikki baravar oshiring yoki pulingiz qaytariladi + $1 000." Agar 50 xaridordan hatto 1 tasi muvaffaqiyatsiz bo'lib, bonusli qaytarish olsa va ommaviy sharh yozsa, taklif doimiy zarar ko'radi.

Stress-test: xaridorlarning 10% kafolatdan foydalansa nima bo'ladi?

### Haddan tashqari ko'p shartli kafolatlar

"Barcha 24 modulni ko'rgan, 6 mashqni bajargan, har bir jonli qo'ng'iroqda qatnashgan va hamjamiyatda haftasiga kamida bir marta post yozgan bo'lsangiz, qaytaramiz."

Xaridorlar buni "ular qaytarish olishni amalda imkonsiz qilgan" deb o'qiydi. Ishonch pasayadi.

Ko'pi bilan ikki shart. Uchtasi faqat bir-biriga yaqin bog'liq bo'lsa (masalan, "kursni tugatdi VA yakuniy loyihani topshirdi VA bizga savol yubordi").

### Kafolatni mayda yozuvda yashirish

Agar kafolatingiz sezilgan ehtimoldagi eng kuchli richagingiz bo'lsa, *uni sotuv sahifasida 24pt matnda qo'ying*. Uni sotib olish tugmasidan yuqoriga ko'chiring.

### Uni sinashni unutish

Kafolat matnini har olti oyda qayta o'qing. Bir yil oldin ishlagan so'zlash endi taklifingizda o'zgartirgan biror narsa bilan buzilgan bo'lishi mumkin.

### Kafolatlarni isbot o'rniga ishlatish

Kuchli isbot + zaif kafolat > kuchli kafolat + zaif isbot. Tartib muhim. Avval isbotni quring, so'ng ustiga kafolatni qo'ying.

---

## Kafolat BO'LMASLIGINING halol holati

Anti-kafolatlar ("qaytarish yo'q, bu yakuniy") quyidagi hollarda ishlaydi:

- Xaridor tajribasi yuqori
- Sotuvdan oldin ariza yoki saralash jarayoni bor
- Narx premiumdan hashamatgacha
- Brend mustahkam
- Isbot ustun

Aytayotganingiz: "bizga kafolat kerak emas, chunki ish haqiqiy, xaridor o'zini saralab oldi va biz tranzaksion qaytarish o'yinlariga kirishmaymiz."

Noto'g'ri auditoriya buni sovuq yoki firibgar deb o'qiydi. To'g'ri auditoriya buni ishonch deb o'qiydi. Xaridoringizni biling.

---

## Diagnostika

Kafolatsiz (yoki zaif kafolatli) taklifni audit qilganda so'rang:

1. **Xaridorning haqiqiy xavfi nima?** Uni aniq qiling. ("$2K va ehtimol ko'proq mijoz topa olmayman.")
2. **Qaysi kafolat tuzilmasi aynan shu xavfni teskari qiladi?** Uni sakkiz turdan biriga moslang.
3. **Halol qaytarishga toqatingiz qanday?** Qaytarish darajasi × qaytarish xarajatini hisoblang; bardosh bera olasizmi?
4. **Kafolat auditoriya tajribasiga mos keladimi?** Premium xaridorlar anti-kafolatni, birinchi marta xaridorlar shartsizni xohlaydi.

Ko'pgina takliflarda noto'g'ri kafolat emas, *umuman* kafolat yo'q. Har qanday kafolat qo'shish deyarli doim ko'tarilishdir. To'g'risini qo'shish — richagning o'zi.
