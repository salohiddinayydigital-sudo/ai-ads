# SaaS Prospecting bo'yicha reference

Foydalanuvchi SaaS yoki raqamli xizmatlarni boshqa SaaS kompaniyalari / raqamli bizneslarga sotganda.

---

## Muhim ICP signallari (SaaS yo'nalishi)

Standart firmografikadan (soha, hajm, geografiya) tashqari, SaaS prospektlari quyidagilar bo'yicha malakalanadi:

### Texnografik signallar

- **Tech stack** — ular to'ldiruvchi asboblardan (sizning integratsiya nishoningiz) yoki raqobatchi asboblardan (o'tish imkoniyati) foydalanadimi?
- **So'nggi stack o'zgarishlari** — asboblarni qo'shish/olib tashlash faol vendor baholashini bildiradi
- **O'zi qurgan va tayyor yechim** — DIY asboblar ko'pincha mahsulotingizdan foyda ko'radigan xaridorni bildiradi
- **Bepul/freemium tarif signallari** — bepul raqobatchidan foydalanish ular yangilanishga tayyor bo'lishi mumkinligini bildiradi

### O'sish signallari

- **Investitsiya raundi** — oxirgi 6 oyda Series A / B / C = byudjet + yangi yollash + asbob ehtiyojlari
- **Xodimlar soni o'sishi** — oxirgi chorakda 10%+ o'sish masshtablash bosimini bildiradi
- **Yollash signallari** — aniq rol e'lonlari (masalan, "Head of RevOps" → revops asboblari uchun ICP)
- **Mahsulot tezligi** — tez-tez chiqarish, yangi funksiyalar, blog postlar = sog'lom o'sish harakati
- **Xaridoringiz roli uchun ochiq pozitsiyalar** — Marketing Ops'ga sotsangiz va ular uni yollayotgan bo'lsa, bu signal

### Pasayish signallari (ballni pasaytiring)

- Maqsadli bo'limda ishdan bo'shatishlar
- 2 yildan ortiq oldingi investitsiya raundi va keyingisi yo'q
- Mahsulot 6+ oy chiqmagan
- Jamoa sahifasida faqat asoschilar (juda erta — byudjeti bo'lmasligi mumkin)

---

## Kashf manbalari (SaaS yo'nalishi)

O'zaro tekshirish uchun 2+ manbani birlashtiring.

### 1-daraja — asosiy kashf

- **Apollo**: firmografik + texnografik + kontakt ma'lumotlari. Katta dastlabki ro'yxatlar tuzish uchun yaxshi.
- **Clay**: waterfall boyitish, maxsus ballash, ko'p manbali birlashtirish. Yuqori sifatli kichikroq ro'yxatlar uchun eng yaxshi.
- **ZoomInfo**: enterprise darajadagi firmografik + intent signallari. Qimmat; o'rta bozor+.
- **LinkedIn Sales Navigator**: qaror qabul qiluvchilarni xaritalash. Qo'lda ishlating, hech qachon ommaviy scraping qilmang.

### 2-daraja — texnografik / o'sish signallari

- **BuiltWith**: tech stack qidiruvlari, aniq asboblardan foydalanadigan saytlarni topish
- **Wappalyzer**: bepul brauzer kengaytmasi + API; yengilroq tech stack signali
- **Crunchbase**: investitsiya raundlari, xodimlar soni, asoschilar
- **Pitchbook**: chuqurroq investor ma'lumotlari (enterprise/pullik)
- **ProductHunt**: so'nggi launch'lar, quruvchilar auditoriyasi
- **Hacker News / Show HN**: mahsulot chiqarayotgan texnik quruvchilar

### 3-daraja — xarid signallari

- **Ish e'lonlari platformalari** (LinkedIn Jobs, Indeed, AngelList): signal sifatida rol e'lonlari
- **RB2B / Clearbit Reveal**: tashrifchi identifikatsiyasi (iliq anonim trafik)
- **Raqobatchi yoki yondosh repo'larning GitHub stars/fork'lari**: dasturchi darajasidagi intent signali (`tools/integrations/github.md` va `github-prospects.js` CLI'ga qarang). Ayniqsa dev-tool SaaS uchun kuchli — o'tgan hafta `vercel/next.js` ni yulduzlagan dasturchi yondosh Next.js infratuzilmasi uchun bozorda.
- **So'nggi blog postlar / changelog**: mahsulot yo'nalishi signallari
- **Raqobatchiga o'tishni eslatgan G2 sharhlari**: aniq norozilik signali

#### GitHub prospecting naqshi (auditoriya dasturchilar bo'lganda)

Dev-tool SaaS uchun GitHub eng yuqori sifatli kashf kanallaridan biri:

1. 3–5 ta "langar" repo'ni aniqlang: to'g'ridan-to'g'ri raqobatchilaringiz, kategoriya yetakchisi, xaridoringiz ishlatadigan to'ldiruvchi asboblar
2. `node tools/clis/github-prospects.js stargazers <owner/repo> --enrich --with-company --format csv` orqali stargazer'larni (yoki kuchliroq intent uchun fork'larni) torting
3. `company` to'ldirilgan foydalanuvchilar bilan cheklang — ularni keyinchalik boyitish eng oson
4. Ism + kompaniya bo'yicha email qidirish uchun Apollo/Clay/Hunter bilan juftlang
5. Murojaat ro'yxatiga qo'shishdan oldin Truelist bilan tekshiring

Kamchiliklari: GitHub to'g'ridan-to'g'ri foydalanuvchilarning faqat ~5–20% i uchun email beradi. Kuchi — signal sifatida: nisha dev-tool'ning stargazer'i Apollo firmografikasi bir o'zi ayta olmaydigan darajada haqiqatan bozorda.

---

## Malakalash cheklisti (SaaS yo'nalishi)

Har bir nomzod uchun tekshiring:

- [ ] Soha vertikali ICP'ga mos
- [ ] Kompaniya hajmi (xodimlar soni) diapazon ichida
- [ ] Tech stack nishon texnologiyani o'z ichiga oladi (yoki ongli ravishda o'z ichiga olmaydi)
- [ ] Investitsiya bosqichi xaridor yetukligiga mos
- [ ] So'nggi 90 kunda kamida bitta o'sish signali (investitsiya, yollash, mahsulot tezligi)
- [ ] Kompaniyada qaror qabul qiluvchi rol mavjud (nomlangan yoki ish e'lonlaridan xulosa qilsa bo'ladigan)
- [ ] Email kontakt tekshirilishi mumkin
- [ ] Diskvalifikatorlar yo'q (yopilgan, sotib olingan-to'xtatilgan, ishdan bo'shatishlar, ICP'ga mos kelmaslik)

---

## Chiqish ustunlari (SaaS yo'nalishi)

Tavsiya etilgan CSV ustunlari:

```csv
score,company,domain,industry,size_band,country,funding_stage,last_round_date,tech_stack_match,signal,signal_date,contact_name,contact_title,contact_email,email_status,linkedin_url,source_urls,why_prospect,confidence,verified_date,notes
```

Chat jadvali uchun qisqartiring: Score | Company | Industry | Size | Signal | Contact | Email status | Confidence.

---

## Top outreach nishonlarini tanlash (SaaS)

Eng yaxshi 3–5 ta hot lid uchun ustuvorlik:

1. **Eng kuchli signalning yangiligi** — 30 kun oldingi investitsiya 9 oy oldingisidan yaxshi
2. **Tech stack mosligi kuchi** — ma'lum integratsiya hamkori taxmin qilingan moslikdan yaxshi
3. **Tekshirilgan email bilan nomlangan qaror qabul qiluvchi** — rol naqshi bo'yicha taxmin qilingan emaildan yaxshi
4. **Ko'p manbali ishonch** — Apollo + Crunchbase ikkalasi kelishsa, bitta manbadan yaxshi

Har bir top nishon aniq signalni nomlaydigan bir gaplik murojaat asoslamasini oladi: "30 kun oldin Series B jalb qilgan; Head of RevOps yollayapti; tekshirilgan VP of Ops emaili."

---

## Keng tarqalgan xatolar (SaaS)

1. **Apollo'dan ro'yxatlarni ulgurji sotib olish** — emailni qayta tekshirmasdan va firmografikani qayta ko'rib chiqmasdan. Eskirgan ma'lumotlar — me'yor.
2. **Tech stack ma'lumotlarini 100% aniq deb hisoblash**. BuiltWith va Wappalyzer nimanidir o'tkazib yuboradi; Clay waterfall'lari ham. O'zaro tekshiring.
3. **Erta bosqich SaaS sotuvchilar uchun Series C+ ni nishonga olish**. Xaridor profili noto'g'ri — juda ko'p xarid to'siqlari, juda ko'p byurokratiya.
4. **Sezilarli byudjet talab qiladigan mahsulotlar uchun Pre-Seed/seed bosqichini nishonga olish**. Ularda na byudjet, na baholovchi vaqti bor.
5. **Intent ma'lumotlari mavjud bo'lganda ularni e'tiborsiz qoldirish** (ZoomInfo Intent, 6sense va h.k.) — oldindan isitilgan signallar har doim sovuqdan yaxshi.
