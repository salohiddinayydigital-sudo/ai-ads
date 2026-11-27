# Prospecting ma'lumot manbalari

Barcha uchta yo'nalish bo'yicha prospecting uchun asbob tanlash qo'llanmasi.

---

## Maqsad bo'yicha asbob tanlash

| Maqsad | Asosiy asboblar | Izohlar |
|------|--------------|-------|
| **Dastlabki firmografik ro'yxat tuzish (B2B / SaaS)** | Apollo, ZoomInfo, Clay | Apollo — kenglik uchun, ZoomInfo — enterprise + intent uchun, Clay — maxsus ish jarayonlari uchun |
| **Qaror qabul qiluvchilarni xaritalash** | LinkedIn Sales Navigator (qo'lda), Apollo, ZoomInfo | Sales Nav — oltin standart. Hech qachon ommaviy scrape qilmang. |
| **Tech stack malakalash (SaaS)** | BuiltWith, Wappalyzer | BuiltWith kengroq qamrov + ommaviy uchun pullik tariflarga ega; Wappalyzer yengilroq + kichik foydalanish uchun bepul |
| **Investitsiya signallari (SaaS)** | Crunchbase, Pitchbook | Crunchbase bepul tarifi dastlabki signallar uchun yetarli; Pitchbook chuqurroq investor ma'lumotlari uchun |
| **Email naqshini aniqlash** | Hunter, Snov, Apollo | Naqshni taxmin qilish — keyin tekshirish |
| **Email deliverability tekshiruvi** | Truelist, Hunter, NeverBounce, ZeroBounce | Murojaat ro'yxatlariga qo'shishdan oldin doim tekshiring |
| **Tashrifchi identifikatsiyasi (iliq intent)** | RB2B, Clearbit Reveal | Anonim trafik → kompaniya identifikatsiyasi |
| **Intent ma'lumotlari** | ZoomInfo Intent, 6sense, Bombora | Oldindan isitilgan signallar; o'rta bozor+ narxlari |
| **Trigger hodisalar monitoringi** | Google Alerts, Feedly, LinkedIn Sales Nav alertlari | Ko'pchilik uchun bepul variantlar yetarli |
| **Mahalliy biznes kashfi** | Google Maps (qo'lda), Yelp, Facebook Pages | Brauzer-yordamli, ommaviy ajratib olinmaydi |

---

## Apollo

**Nima uchun**: Umumiy B2B / SaaS firmografik + kontakt ma'lumotlari. Hali ro'yxatingiz bo'lmasa, eng yaxshi boshlang'ich nuqta.

**Kuchli tomonlari**:
- Katta ma'lumotlar bazasi (>200M kontakt, >60M kompaniya)
- Kuchli filtr UI (soha, hajm, texnologiyalar, signallar)
- Integratsiyalangan email + LinkedIn topuvchi
- Pay-as-you-go va darajali tariflar

**E'tibor bering**:
- Ma'lumotlar yangiligi farq qiladi — "Hot" deb ballashdan oldin qayta tekshiring
- Email aniqligi ~60–80% — doim tekshiring
- Ommaviy eksport limitlari qo'llanadi

**Integratsiya**: [apollo.md](../../../tools/integrations/apollo.md) ga qarang

---

## Clay

**Nima uchun**: Ko'p manbali boyitish, waterfall qidiruvlari, maxsus ballash mantig'i. Ro'yxat sifati ro'yxat hajmidan muhimroq bo'lganda.

**Kuchli tomonlari**:
- Waterfall mantig'i: avval Apollo → ZoomInfo'ga zaxira → Clearbit'ga zaxira
- 100+ ma'lumot provayderi integratsiyasi
- AI-asosli boyitish (URL'lardan LLM-boshqariladigan ajratib olish)
- Maxsus ustunlar + ballash formulalari
- Native MCP server

**E'tibor bering**:
- Kredit bo'yicha narx katta ro'yxatlarda keskin oshishi mumkin
- Murakkablik ortiqcha yuki — ish jarayonlarini haddan tashqari murakkablashtirish oson

**Integratsiya**: [clay.md](../../../tools/integrations/clay.md) ga qarang

---

## ZoomInfo

**Nima uchun**: Enterprise B2B + intent ma'lumotlari. O'rta bozor+ xaridor profillari.

**Kuchli tomonlari**:
- Enterprise darajadagi firmografik chuqurlik
- Intent signallari (taklifingizga tegishli mavzularni qidirayotgan kompaniyalar)
- >$50K ACV B2B sotuvlar uchun eng yaxshisi
- Native MCP server

**E'tibor bering**:
- Qimmat (boshlang'ich $15K+/yil)
- SMB prospecting uchun ortiqcha
- Odatda ko'p yillik shartnomalarga bog'langan

**Integratsiya**: [zoominfo.md](../../../tools/integrations/zoominfo.md) ga qarang

---

## Clearbit

**Nima uchun**: Email → kompaniya boyitish, anonim tashrifchi identifikatsiyasi (Clearbit Reveal).

**Kuchli tomonlari**:
- Kuchli kompaniya boyitish (soha, hajm, investitsiya, tech stack)
- Domen bo'yicha email qidirish
- Reveal: anonim sayt tashrifchilarini kompaniya darajasida aniqlash
- API-first

**E'tibor bering**:
- HubSpot tomonidan sotib olingan (2023) — endi HubSpot Breeze Intelligence ga kiritilgan
- Mustaqil API hali mavjud, lekin narx/kirish tarifga bog'liq

**Integratsiya**: [clearbit.md](../../../tools/integrations/clearbit.md) ga qarang

---

## Hunter / Snov

**Nima uchun**: Email naqshini aniqlash + kichik ro'yxatlarda yengil tekshirish.

**Hunter kuchli tomonlari**:
- Domenga asoslangan email kashfi
- O'rnatilgan deliverability tekshiruvi
- Vaqti-vaqti bilan foydalanish uchun oqilona bepul tarif

**Snov kuchli tomonlari**:
- Email topuvchi + drip kampaniyalar (murojaat asboblari bilan kesishadi)
- Ommaviy tekshirish
- Katta hajmda Hunter'dan arzonroq

**E'tibor bering**:
- Ikkalasi ham naqshni taxmin qiluvchi asboblar — aniqlik maqsadli kompaniya email naqshini xulosa qilish mumkinligiga bog'liq
- Murojaatdan oldin natijalarni doim maxsus validator (Truelist yoki shunga o'xshash) orqali o'tkazing

**Integratsiyalar**: [hunter.md](../../../tools/integrations/hunter.md), [snov.md](../../../tools/integrations/snov.md) ga qarang

---

## Truelist

**Nima uchun**: Kontaktlarni murojaat ro'yxatlariga qo'shishdan oldin email deliverability validatsiyasi. Muhim xavfsizlik qadami.

**Kuchli tomonlari**:
- Bitta email sinxron tekshiruvi (`/api/v1/verify_inline`) + ommaviy asinxron (`/api/v1/verify`)
- `email_state` (ok / email_invalid / risky / unknown / accept_all) + `email_sub_state` (email_ok / is_disposable / is_role / unknown_error / failed_smtp_check) + did-you-mean xato takliflarini qaytaradi
- Catch-all domenlar, rol akkauntlari, spam trap'lar, bir martalik provayderlarni ushlaydi
- Agent boshqariladigan ish jarayonlari uchun rasmiy MCP server (Claude, Cursor, VS Code)
- 7 tildagi rasmiy SDK'lar + freymvork integratsiyalari (Django, Laravel, Next.js, Rails, React, Svelte, Vue, WordPress)
- Mailchimp, Klaviyo, HubSpot, Zapier, Make, n8n, Clay, Salesforce va boshqalar bilan native integratsiyalar
- Har bir email uchun to'lov narxlash

**Nega muhim**: Bounce darajasi 2% dan oshganda cold email obro'si qulaydi. Yuborishdan oldin tekshirish muzokarasiz. Apollo/ZoomInfo/Hunter ma'lumotlari ko'pincha 60–80% aniq — Truelist qolganini ushlaydi.

**Integratsiya**: [truelist.md](../../../tools/integrations/truelist.md) ga qarang

---

## LinkedIn Sales Navigator

**Nima uchun**: Qaror qabul qiluvchilarni qo'lda topish. B2B / SaaS prospecting uchun oltin standart, lekin faqat tadqiqot vositasi sifatida ishlatilganda.

**Kuchli tomonlari**:
- Sohadagi eng aniq qaror qabul qiluvchi ma'lumotlari
- Real vaqtda ish o'zgarishlari, postlar, signallar
- Lid ro'yxatlari, alertlar, saqlangan qidiruvlar
- Inmail kreditlari (cold emaildan alohida kanal)

**Qat'iy qoidalar**:
- **Hech qachon ommaviy scrape qilmang**. LinkedIn scraper'larni agressiv bloklaydi. Akkaunt bloklanish xavfi haqiqiy va doimiy.
- Sales Nav'dan tadqiqot interfeysi sifatida foydalaning — profillarni oching, o'qing, qaydlar oling, asosiy ma'lumotlarni qo'lda yig'ing.
- Apollo va boshqa asboblar LinkedIn ma'lumotlarini hamkorlik / ommaviy aks ettirish orqali da'vo qiladi — compliance deb taxmin qilishdan oldin manba qonuniyligini tekshiring.

**Integratsiya**: iste'molchi darajasida MCP yoki API kirishi yo'q. Faqat qo'lda tadqiqot.

---

## BuiltWith / Wappalyzer

**Nima uchun**: Tech stack malakalash (SaaS yo'nalishi).

**BuiltWith**:
- ~50K+ texnologiya kuzatiladi
- API + ommaviy qidiruvlar (pullik)
- Tarixiy ma'lumotlar (stack qachon o'zgargan)

**Wappalyzer**:
- Bepul brauzer kengaytmasi; pullik API
- BuiltWith'dan yengilroq qamrov
- Bir martalik qidiruvlar uchun tezroq

Ishonchli tech stack signallari uchun ikkalasini o'zaro solishtiring.

---

## Crunchbase

**Nima uchun**: Investitsiya signallari (SaaS yo'nalishi).

**Kuchli tomonlari**:
- Bepul tarif so'nggi investitsiya hodisalarini ko'rsatadi
- Pullik (Pro / Enterprise) alertlar va chuqur tarixni ochadi
- Pullik foydalanuvchilar uchun API kirish

**E'tibor bering**:
- Qamrov VC-qo'llab-quvvatlagan kompaniyalar uchun eng yaxshi; bootstrap va kichik bizneslar kam aks etgan
- O'zi xabar qilgan ma'lumotlar — investitsiya summalarini mustaqil tekshiring

---

## GitHub (stargazer / fork / watcher)

**Nima uchun**: Dasturchi-intent prospecting. Ayniqsa dev-tool SaaS uchun kuchli — raqobatchi yoki kategoriyani belgilovchi repo'larning stargazer'lari bozordagi signal.

**Kuchli tomonlari**:
- Ommaviy API, scraping tashvishlari yo'q
- Yuqori signal sifati (yulduzlangan repo = aniq qiziqish)
- Fork'lar yanada kuchli signal (shunchaki xatcho'p emas, o'zgartirish niyati)
- Birga keladigan `github-prospects.js` CLI sahifalash + boyitish + CSV chiqishini bajaradi
- Autentifikatsiyalangan 5 000 req/soat limit bilan bepul

**E'tibor bering**:
- Foydalanuvchilarning faqat ~5–20% i email e'lon qiladi — boyitish uchun Apollo/Clay/Hunter bilan juftlang
- Juda mashhur repo'lar (100K+ yulduz) asosan shovqin; kichikroq nishonli repo'lar (5K–25K) signal zichligini yaxshiroq beradi
- Ko'p prospektlar alohida shaxslar, to'g'ridan-to'g'ri kompaniya kontaktlari emas — `company` maydoni yoki LinkedIn'dan kompaniyasini aniqlash kerak

**Integratsiya**: [github.md](../../../tools/integrations/github.md) ga qarang

---

## Firecrawl / Browserbase (bitta nishonli sayt tadqiqoti)

**Nima uchun**: Google Maps, Yelp yoki LinkedIn kabi platformalarda kashf orqali allaqachon topilgan **prospektning o'z veb-saytidan** kontentni dasturiy ajratib olish. O'sha platformalarni scrape qilish uchun emas.

### Firecrawl

- **Eng mos**: "Sahifani markdown sifatida bering" — Local SMB veb-sayt holati tekshiruvlari, B2B kompaniya about/jamoa sahifasini ajratib olish, tuzilgan maydonlarni ajratib olish
- **Kuchli tomonlari**: Past ortiqcha xarajat, toza LLM-tayyor markdown qaytaradi, ko'pchilik JS-render qilingan saytlarni boshqaradi, MCP serveri bor
- **API + MCP + SDK'lar**: Node, Python, Go, Rust

### Browserbase

- **Eng mos**: Haqiqiy Chromium kerak bo'lganda — JS-og'ir sahifalar, cookie rozilik oynalari, kontakt sahifasiga yetish uchun forma yuborish, sessiya holati
- **Kuchli tomonlari**: Playwright/Puppeteer orqali to'liq brauzer nazorati; Stagehand AI-qulay tabiiy-til ajratib olishni ta'minlaydi; nosozliklarni tuzatish uchun sessiya yozuvlari
- **API + MCP (Stagehand) + SDK'lar**: Node, Python

### Muhim compliance chegarasi

Ikkala asbob ham texnik jihatdan istalgan URL'ga yo'naltirilishi mumkin. Qat'iy qoida:

- ✓ **OK**: qo'lda kashf orqali topilgan bitta biznesning o'z veb-saytidan (`joescoffeeshop.com`) kontentni ajratib olish
- ✗ **OK EMAS**: ularni `google.com/maps`, LinkedIn qidiruv natijalari, Yelp ro'yxatlari yoki ToS'i ommaviy ajratib olishni taqiqlaydigan har qanday platformaga yo'naltirish

Kashf platformalarda (qo'lda brauzer-yordamli tadqiqot) amalga oshadi. Ajratib olish alohida ommaviy biznes saytlarida amalga oshadi.

**Integratsiyalar**: [firecrawl.md](../../../tools/integrations/firecrawl.md), [browserbase.md](../../../tools/integrations/browserbase.md) ga qarang

---

## RB2B / Clearbit Reveal

**Nima uchun**: Anonim sayt tashrifchilarini iliq intent signali sifatida aniqlash.

**Kuchli tomonlari**:
- Pixel asosidagi tashrifchi → kompaniya identifikatsiyasi
- Yuqori intent: ular saytingizga kelgan, allaqachon tadqiqot rejimida
- Muhim tashriflar bo'yicha Slack / email alertlar

**E'tibor bering**:
- Maxfiylik/GDPR jihatlari — maxfiylik siyosatingiz oshkor qilishlarini tekshiring
- Shaxs darajasidagi identifikatsiya kompaniya darajasidagidan yuqoriroq tashvish tug'diradi

**Integratsiya**: [rb2b.md](../../../tools/integrations/rb2b.md) ga qarang

---

## Bepul / faqat brauzer zaxiralari

Foydalanuvchida pullik asboblar bo'lmasa, quyidagilarga tayaning:

- **Google Search** — aniq biznes nomi + shahar + rol qidiruvlari
- **LinkedIn** (qo'lda, scraping yo'q) — kompaniya sahifalari, xodimlarni qidirish
- **Crunchbase bepul tarifi** — investitsiya hodisalari
- **Wappalyzer brauzer kengaytmasi** — tech stack bir qarashda
- **Hunter.io bepul tarifi** — oyiga 25 ta qidiruv
- **Google Maps** — Local SMB kashfi uchun
- **Biznes veb-saytlari + About sahifalari** — har qanday da'vo uchun asosiy manba
- **Yangilik saytlari + press-relizlar** — Google Alerts orqali trigger hodisalar monitoringi

Asboblarga ega ish jarayonlaridan sekinroq, lekin foydalanuvchi mehnat qilishga tayyor bo'lsa, yuqori sifatli kichikroq ro'yxatlar beradi.

---

## Ketma-ketlik bo'yicha tavsiyalar

Odatiy to'liq-stek prospecting ish jarayoni:

1. product-marketing kontekstidan **ICP'ni aniqlang** (asbob kerak emas)
2. Apollo yoki ZoomInfo'dan **dastlabki ro'yxat** (firmografik filtr)
3. Clay bilan **boyiting** (waterfall: tech stack, investitsiya, trigger hodisalar)
4. LinkedIn Sales Nav'da **qaror qabul qiluvchilarni xaritalash** (qo'lda)
5. Hunter yoki Apollo'ning o'rnatilgan funksiyasi bilan **email naqshini aniqlash**
6. Yakuniy ro'yxatdan oldin Truelist bilan **email validatsiyasi**
7. Murojaat matni uchun cold-email skilliga **topshiring**

Ketma-ketlikni foydalanuvchida haqiqatan mavjud asboblarga qarab moslang.
