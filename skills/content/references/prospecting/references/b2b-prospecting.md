# B2B Prospecting bo'yicha reference

Foydalanuvchi SaaS bo'lmagan B2B segmentiga sotganda — xizmatlar, agentliklar, ishlab chiqaruvchilar, o'rta bozor va enterprise kompaniyalar, professional xizmat firmalari.

---

## Muhim ICP signallari (B2B yo'nalishi)

### Firmografik signallar

- **Soha / vertikal** — aniqlik muhim bo'lsa NAICS yoki SIC kodlari
- **Kompaniya hajmi** — xodimlar soni diapazoni, daromad diapazoni, filiallar soni
- **Geografiya** — vaqt zonalari, tartibga solish, joyida ishlash talablari uchun muhim
- **Biznes modeli** — xizmat va mahsulot va distributsiya; B2B va B2B2C
- **Egalik** — mustaqil, PE-qo'llab-quvvatlagan, ommaviy, oilaviy — xarid harakatiga ta'sir qiladi

### Xarid signallari

- **Trigger hodisalar**: yangi C-level yollash, yaqinda sotib olish yoki ajratib yuborish, IPO/investitsiya, yangi filial ochish, yaqinda rebrending, kengayish e'loni
- **Vendor signallari**: ommaviy RFP e'lon qilish, so'nggi choraklik hisobotda o'tish xarajatlari, shartnoma yangilanish oynalari
- **Operatsion signallar**: yaqinda ishdan bo'shatish (xarajat bosimi) yoki tez yollash (quvvat bosimi)
- **Yangiliklarda eslatmalar**: yangi tashabbusni ishga tushirish, yangi bozorga kirish, harakatga majbur qiluvchi tartibga solish o'zgarishi
- **PR / matbuot**: "bu kompaniya hozir o'zgarmoqda" degan signal beradigan har qanday narsa

### Pasayish signallari

- Bir nechta bankrotlik yoki PE tomonidan bo'shatilgan operatsiyalar
- Salbiy o'sish + xarajatlarni qisqartirish sarlavhalari
- Egalik turg'unligi (kichik oilaviy, o'sish rag'bati yo'q)
- Xaridorlar almashinuvi (2 yilda 3+ Marketing direktori)

---

## Kashf manbalari (B2B yo'nalishi)

### 1-daraja — asosiy kashf

- **Apollo**: eng yaxshi umumiy B2B firmografik + kontakt kashfi
- **ZoomInfo**: enterprise B2B + intent signallari (o'rta bozor+)
- **LinkedIn Sales Navigator**: soha + rol + signal bo'yicha qidiruv; qaror qabul qiluvchilarni xaritalashning oltin standarti (qo'lda)
- **Clay**: maxsus waterfall qidiruvlar kerak bo'lganda (masalan, Apollo yozuvlarini Hunter + Clearbit bilan boyitish)

### 2-daraja — sohaga xos kataloglar

- **Crunchbase / Pitchbook**: investitsiya olgan bizneslar
- **D&B Hoovers**: yirik an'anaviy B2B firmografikasi
- **Davlat / milliy biznes reestrlari**: tasdiqlangan ro'yxatdan o'tish ma'lumotlari uchun
- **Soha assotsiatsiyalarining a'zolar ro'yxatlari**: savdo guruhlari ko'pincha a'zolar ro'yxatini e'lon qiladi
- **Ko'rgazma ishtirokchilari ro'yxatlari**: vertikalda faol ishtirokni bildiradi
- **Xaridlar ma'lumotlar bazalari** (masalan, qurilish uchun Procore): vertikalga xos signallar

### 3-daraja — trigger hodisalar monitoringi

- **Google Alerts / Feedly**: trigger kalit so'zlar ("acquired," "hires," "expansion," "raises," "announces")
- **PR Newswire / Business Wire**: kompaniya tomonidan nazorat qilinadigan e'lonlar
- **SEC hujjatlari** (ommaviy kompaniyalar): muhim o'zgarishlar oshkor qilinishi
- **Davlat hujjatlari**: yangi yuridik shaxs tashkil etish, tugatish

---

## Malakalash cheklisti (B2B yo'nalishi)

- [ ] Soha / vertikal ICP'ga mos (iloji bo'lsa tan olingan tasnifdan foydalaning)
- [ ] Kompaniya hajmi diapazon ichida (xodimlar yoki daromad)
- [ ] Geografiya mos
- [ ] So'nggi 90–180 kunda kamida bitta trigger hodisa
- [ ] Qaror qabul qiluvchi rol mavjud (CEO, COO, VP Operations, X direktori — xaridor profiliga moslang)
- [ ] Email kontakt tekshirilishi mumkin (nomlangan rol > info@ catchall)
- [ ] Firmografik da'volar uchun manba URL'lar saqlangan
- [ ] Diskvalifikatorlar yo'q (yopilgan, sotib olingan-to'xtatilgan, ko'p marta bankrot, ICP'dan tashqari)

---

## Chiqish ustunlari (B2B yo'nalishi)

Tavsiya etilgan CSV ustunlari:

```csv
score,company,domain,industry,naics_code,size_band,revenue_band,country,city,trigger_event,trigger_date,contact_name,contact_title,contact_email,email_status,linkedin_url,source_urls,why_prospect,confidence,verified_date,notes
```

Chat jadvali uchun qisqartiring: Score | Company | Industry | Size | Trigger | Contact | Email status | Confidence.

---

## Top outreach nishonlarini tanlash (B2B)

Eng yaxshi 3–5 ta hot lid uchun ustuvorlik:

1. **Trigger hodisaning yangiligi** — 30 kun 6 oydan yaxshi
2. **Trigger hodisaning aniqligi** — xaridoringiz rolida yangi CMO yollash "kompaniya yangiliklarda" dan yaxshi
3. **Qaror qabul qiluvchiga kirish** — tekshirilgan email + LinkedIn bilan nomlangan kontakt faqat rol dan yaxshi
4. **Vertikal moslik aniqligi** — aniq NAICS mosligi "yondosh soha" dan yaxshi

Har bir top nishon asoslamasi trigger va qaror qabul qiluvchini nomlaydi: "14 kun oldin yangi VP of Marketing yollagan; tekshirilgan email; ICP'ga mos o'rta bozor ishlab chiqaruvchisi."

---

## Keng tarqalgan xatolar (B2B)

1. **B2B'ga SaaS kabi qarash** — investitsiya raundlari kamroq ahamiyatli; PE egaligi va sotib olish faolligi ko'proq muhim.
2. **Xususiy kompaniya daromadini aniq tekshirishga urinish** — ko'pchilik ommaviy ma'lumotlar bazalari taxminiy. Nuqtaviy baholar emas, hajm diapazonlaridan foydalaning.
3. **Enterprise miqyosida xarid murakkabligini e'tiborsiz qoldirish** — kontaktlar ro'yxatingizda haqiqiy tasdiqlovchi bo'lmasligi mumkin.
4. **Ijrochi yordamchilarga cold email yuborish** — ular xaridor emas va murojaatingizni spam deb belgilaydi.
5. **Manba URL gigiyenasi** — manba izisiz GDPR DSAR yoki CAN-SPAM e'tirozi ostida kontaktni himoya qila olmaysiz.
6. **Bitta manbada to'xtash** — Apollo kichik bizneslarda 60% aniq bo'lishi mumkin. LinkedIn yoki biznes veb-sayti bilan o'zaro tekshiring.
