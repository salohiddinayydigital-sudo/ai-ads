# Headless CMS bo'yicha qo'llanma

Marketing kontenti uchun headless CMS'ni tanlash, modellashtirish va joriy etish bo'yicha reference.

## Qachon foydalaniladi

Yangi loyiha uchun CMS tanlaganda, marketing saytlari uchun kontent modellarini loyihalashda, tahririyat ish jarayonlarini sozlashda yoki CMS kontentini programmatic sahifalarga ulashda foydalaning.

---

## Headless va an'anaviy CMS

Headless CMS kontentni boshqarishni taqdimotdan ajratadi. Kontent tuzilgan backend'da saqlanadi va API orqali istalgan frontend'ga yetkaziladi.

### Headless qachon mantiqli

- Bir xil kontentni bir nechta frontend ishlatadi (veb, mobil, email)
- Dasturchilar frontend steki ustidan to'liq nazorat xohlaydi
- Kontentni kanallar bo'ylab qayta ishlatish kerak
- Zamonaviy freymvork bilan quryapsiz (Next.js, Remix, Astro)
- Marketingga tuzilgan, qayta ishlatiladigan kontent bloklari kerak

### An'anaviy CMS qachon yaxshiroq

- Maxsus dasturchilari yo'q kichik jamoa
- Oddiy blog yoki vizitka sayt
- WYSIWYG tahrirlash qat'iy talab
- Byudjet tor va WordPress/Webflow ishni bajaradi

### Qaror cheklisti

| Omil | Headless | An'anaviy |
|------|----------|-----------|
| Ko'p kanalli yetkazib berish | Ha | Cheklangan |
| Dasturchi nazorati | To'liq | Cheklangan |
| Texnik bo'lmagan tahrirlash | Sozlash talab qiladi | O'rnatilgan |
| Ishga tushirish vaqti | Uzoqroq | Tezroq |
| Kontentni qayta ishlatish | Tabiiy | Qo'lda |
| Hosting moslashuvchanligi | Istalgan frontend | Platformaga bog'liq |

---

## Marketing uchun kontent modellashtirish

### Asosiy tamoyillar

1. **Sahifalar emas, turlar bilan fikrlang.** "Landing Page" — maydonlari bor kontent turi, HTML fayl emas. Bu komponentlarni sahifalar bo'ylab qayta ishlatish imkonini beradi.
2. **Kontentni taqdimotdan ajrating.** Bezatilgan sarlavhani emas, sarlavha matnini saqlang. Taqdimot frontend'ga tegishli.
3. **Qayta ishlatishni loyihalang.** Agar testimoniallar 5 sahifada chiqsa, Testimonial turini yarating va unga havola qiling — nusxalamang.
4. **Modellarni yassi saqlang.** Chuqur ichma-ich tuzilmalarni so'rash va yuritish qiyin. Ichma-ich o'rniga havolalarni afzal ko'ring.

### Keng tarqalgan marketing kontent turlari

| Tur | Asosiy maydonlar | Izohlar |
|------|-----------|-------|
| **Landing Page** | title, slug, hero, sections[], seo | Moslashuvchanlik uchun modulli bo'limlar |
| **Blog Post** | title, slug, body, author, category, tags, publishedAt, seo | Rich text yoki Portable Text body |
| **Case Study** | title, customer, challenge, solution, results, metrics[], logo | Tegishli mahsulot/funksiyalarga havola |
| **Testimonial** | quote, author, role, company, avatar, rating | Landing sahifalardan havola qilinadi |
| **FAQ** | question, answer, category | Programmatic sahifalar uchun kategoriya bo'yicha guruhlang |
| **Author** | name, bio, avatar, social links | Blog postlardan havola qilinadi |
| **CTA Block** | heading, body, buttonText, buttonUrl, variant | Sahifalar bo'ylab qayta ishlatiladi |

### SEO maydonlari cheklisti

Har bir sahifa darajasidagi kontent turiga kerak:

- `metaTitle` — 50–60 belgi
- `metaDescription` — 150–160 belgi
- `ogImage` — 1200x630px ijtimoiy preview
- `slug` — URL yo'lining segmenti
- `canonicalUrl` — ixtiyoriy override
- `noIndex` — qidiruvdan chiqarish uchun boolean
- `structuredData` — ixtiyoriy JSON-LD override

---

## Tahririyat ish jarayonlari

### Qoralama → Ko'rib chiqish → Nashr sikli

1. **Qoralama** — Muallif kontent yaratadi yoki tahrirlaydi
2. **Ko'rib chiqish** — Muharrir aniqlik, brend ovozi va SEO bo'yicha tekshiradi
3. **Tasdiqlash** — Manfaatdor tomon imzolaydi
4. **Rejalashtirish** — Nashr sanasi/vaqtini belgilang
5. **Nashr** — Kontent API orqali jonli bo'ladi

### Preview API'lar

Barcha yirik headless CMS platformalari qoralama preview'ni qo'llab-quvvatlaydi:

- **Sanity**: `useLiveQuery` yoki Presentation tool bilan real vaqtli preview
- **Contentful**: alohida access token bilan Preview API (`preview.contentful.com`)
- **Strapi**: `status=draft` so'rov parametri bilan Draft & Publish tizimi (v5; v4'dagi `publicationState` o'rniga)

Frontend'ingizda autentifikatsiya qiladigan va qoralama kontentni render qiladigan preview marshrutini (masalan, `/api/preview`) sozlang.

### Rollar va ruxsatlar

| Rol | Yarata oladi | Tahrirlay oladi | Nashr qila oladi | O'chira oladi |
|------|:----------:|:--------:|:-----------:|:-----------:|
| Muallif | Ha | O'zinikini | Yo'q | O'z qoralamalarini |
| Muharrir | Ha | Hammasini | Ha | Qoralamalarni |
| Admin | Ha | Hammasini | Ha | Hammasini |

Aniq ruxsat modellari platformaga qarab farq qiladi. Sanity rolga asoslangan kirishdan foydalanadi. Contentful'da space darajasidagi rollar bor. Strapi'da batafsil RBAC mavjud.

---

## Platformalar taqqoslash

| Xususiyat | Sanity | Contentful | Strapi |
|---------|--------|------------|--------|
| Hosting | Cloud (boshqariladigan) | Cloud (boshqariladigan) | O'z serveringizda yoki Cloud |
| So'rov tili | GROQ | REST / GraphQL | REST / GraphQL |
| Bepul tarif | Saxiy | Cheklangan | Ochiq manba (bepul) |
| Real vaqtli hamkorlik | Ha (o'rnatilgan) | Cheklangan | Yo'q |
| Eng mos | Dasturchi moslashuvchanligi | Enterprise ko'p-lokalli | Byudjet / self-hosted |
| Kontent modellashtirish | Schema-as-code | Web UI | Web UI yoki kod |
| Media bilan ishlash | O'rnatilgan DAM | O'rnatilgan | Plagin asosida |

### Sanity

**Kuchli tomonlari**: GROQ so'rov tili kuchli va moslashuvchan. Sxema kodda aniqlanadi (versiyalanadi). Real vaqtli hamkorlikdagi tahrirlash. Boy kontent uchun Portable Text. Saxiy bepul tarif.

**E'tiborga olinadigan jihatlar**: Dasturchi bo'lmaganlar uchun o'rganish egri chizig'i keskinroq. Studio'ni moslashtirish React bilimini talab qiladi. GROQ so'rovlarida vendor lock-in.

**Marketingga mosligi**: Dasturchilar va marketologlar yaqin hamkorlik qilganda eng yaxshi. Murakkab modelli, kontentga boy saytlar uchun kuchli.

### Contentful

**Kuchli tomonlari**: Yetuk enterprise platforma. Ajoyib ko'p-lokal qo'llab-quvvatlash. Integratsiyalarning kuchli ekotizimi. Studio bilan kompozitsion kontent. Yaxshi hujjatlangan API'lar.

**E'tiborga olinadigan jihatlar**: Narx kontent turlari va lokallar bilan o'sadi. Ikkita alohida API (Delivery va Management). Quyi tariflarda rate limit'lar tor bo'lishi mumkin.

**Marketingga mosligi**: Ko'p bozorli kontent kerak bo'lgan enterprise'lar uchun eng yaxshi. Tasdiqlangan vendor ishonchliligi kerak bo'lganda yaxshi.

### Strapi

**Kuchli tomonlari**: Ochiq manba, self-hosted imkoniyati. Ma'lumotlar ustidan to'liq nazorat. O'rindiq (per-seat) uchun to'lov yo'q. Moslashtiriladigan admin panel. Plagin ekotizimi. Standart REST, plagin orqali GraphQL.

**E'tiborga olinadigan jihatlar**: Self-hosting infratuzilmani o'zingiz boshqarishingizni anglatadi. Ekotizimi Sanity/Contentful'dan kichikroq. V4 dan V5 ga o'tish sezilarli bo'lishi mumkin.

**Marketingga mosligi**: To'liq nazorat va vendor lock-in'siz xohlaydigan, DevOps imkoniyatiga ega jamoalar uchun eng yaxshi. Byudjetni tejaydigan loyihalar uchun yaxshi.

### Boshqa e'tiborga loyiq variantlar

- **Hygraph** — GraphQL-native, federatsiya va ko'p manbali kontent uchun kuchli
- **Keystatic** — Git asosida, dasturchi-kontent gibrid ish jarayonlari uchun yaxshi
- **Payload** — TypeScript-first, self-hosted, Sanity kabi kod orqali sozlanadi
- **Builder.io** — Headless backend'li vizual muharrir, texnik bo'lmagan marketologlar uchun yaxshi
- **Prismic** — Slice asosidagi kontent modellashtirish, Next.js bilan kuchli integratsiya

---

## Marketing skilllari bilan integratsiya

### Programmatic SEO

CMS'ni programmatic sahifalar uchun ma'lumot manbai sifatida ishlating. Tuzilgan ma'lumotlarni (FAQ'lar, taqqoslashlar, shahar sahifalari) kontent turlari sifatida saqlang va so'rovlardan sahifalar yarating. **programmatic-seo** skillga qarang.

### Copywriting

CMS kontent modellari izchil tuzilmani majbur qiladi. Copy freymvorklaringizga mos maydonlarni belgilang (sarlavha, sub-sarlavha, ijtimoiy isbot, CTA). **copywriting** skillga qarang.

### Sayt arxitekturasi

URL tuzilmasi, navigatsiya ierarxiyasi va ichki bog'lanish — barchasi kontent CMS'da qanday tashkil etilganiga bog'liq. Kontent modeli va sayt arxitekturasini birgalikda rejalang. **site-architecture** skillga qarang.

### Email ketma-ketliklari

Veb va email bo'ylab izchil xabar uchun CMS kontentini email shablonlariga torting. Keyslar, testimoniallar va blog postlar email nurture ketma-ketliklarini oziqlantirishi mumkin. **emails** skillga qarang.

---

## Joriy qilish cheklisti

- [ ] Kontent turlarini sahifa turlari va qayta ishlatiladigan bloklar asosida belgilang
- [ ] Har bir sahifa darajasidagi kontent turiga SEO maydonlarini qo'shing
- [ ] Frontend'ingizda preview/qoralama rejimini sozlang
- [ ] Jamoangiz uchun rollar va ruxsatlarni sozlang
- [ ] Frontend qurishdan oldin har bir tur uchun namunaviy kontent yarating
- [ ] Kontent o'zgarishlari uchun webhook bildirishnomalarini sozlang (qayta qurish triggerlari)
- [ ] Muharrirlar uchun kontent yo'riqnomalarini hujjatlashtiring (maydon tavsiflari, belgi limitlari)
- [ ] Kontent yetkazib berish unumdorligini sinang (CDN, keshlash, ISR)
- [ ] Mavjud CMS'dan ko'chirilsa, migratsiya strategiyasini rejalang

---

## Tegishli integratsiya qo'llanmalari

- [Sanity](../../../tools/integrations/sanity.md) — GROQ so'rovlari, mutatsiyalar, CLI
- [Contentful](../../../tools/integrations/contentful.md) — Delivery/Management API'lar, nashr qilish
- [Strapi](../../../tools/integrations/strapi.md) — REST CRUD, filtrlar, document API
