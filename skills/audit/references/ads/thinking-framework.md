# 10 tamoyilli fikrlash freymvorki

Har bir claude-ads buyrug'i ostida ishlaydigan umumiy kognitiv intizom. Har qanday audit, reja yoki kreativ natija
vazifasi boshida shu faylni yuklang. Bu cheklist yoki bosqichlar modeli emas — fikrlash darvozasi. Freymvork raqamlarni
hisoblaydigan hisobotni strategik natijadan ajratadi.

Tamoyillar beshta juftlikka birlashadi: ikkita **OBSERVE** rejimi (tashqariga va ichkariga qarash), bitta **LISTEN**
rejimi (faol qabul qilish), bitta **THINK** rejimi (tanqidiy qayta ishlash), ikkita **CONNECT** rejimi (lateral idrok va
tizim orkestratsiyasi), bitta **FEEL** rejimi (hissiy intellekt), bitta **ACCEPT** rejimi (intellektual kamtarlik),
bitta **CREATE** rejimi (generativ natija) va bitta **GROW** rejimi (siklni yopadigan iterativ halqa).

Shubhada o'zingizdan so'rang: *hozir men qaysi tamoyildaman va qaysinisini o'tkazib yuboryapman?* O'tkazib yuborilgan
tamoyil odatda ish eng zaif bo'lgan joy.

---

## 1. OBSERVE — Tashqi kirish

**Ta'rif.** Fikrlash ma'lumot yig'ishdan boshlanadi. Muhitga qarang, manzarani tahlil qiling, naqshlar va samarasizliklarni
*ularni hal qilishga shoshilmasdan* aniqlang. Vaziyatning xom kirishlarini o'qing.

**Reklama ishida.**
- Har qanday gipoteza shakllantirishdan oldin haqiqiy akkaunt ma'lumotlarini eksport qiling — qidiruv iboralari hisobotlari,
  GAQL so'rovlari, ad library skrinshotlari, MMP dashboardlari.
- SERP va raqobatchi reklama yuzasini yozib oling. Foydalanuvchi mijozingiz reklamasini bosishdan oldin nimani ko'radi?
- Landing sahifani reklama auditoriyasi ochgandek oching (mobil, pullik manba, yangi sessiya). Reklama PDP'ga olib borsa,
  bosh sahifani audit qilmang.

**Anti-pattern.** Akkauntni ochmasdan, xotiradan yoki umumiy cheklistdan muammoni diagnostika qilish. Konversiya hajmini
tekshirmay Smart Bidding'ni tavsiya qilish. Xavfsiz zona overlayini ko'rmasdan kreativni tanqid qilish.

**Misol trigger.** Har bir `/ads audit`, `/ads competitor`, `/ads dna` ning birinchi qadami. `ads/SKILL.md` dagi Context
Intake bo'limi bu darvozani majburlaydi.

---

## 2. OBSERVE — Ichki metakognitsiya

**Ta'rif.** O'zingizni kuzating. Qanday fikrlayotganingizni audit qiling. Taxminlarga tayanyapsizmi? Bu tahlilda
noxolisligingiz bormi? Aniqlik uchun orqaga qadam tashlab, o'z mental modellaringizni tekshirish kerak.

**Reklama ishida.**
- B2B-SaaS evristikalarini mahalliy santexnikka yoki e-commerce ROAS maqsadlarini brend xabardorligi kampaniyasiga qo'llayotganingizni payqang.
- Akkauntni *siz yoqtirgan* tuzilmaga (SKAG va broad-match, manual va Smart Bidding) mos kelmagani uchun jarimalayotganingizni payqang.
- Birinchi ko'rgan KPI'ga ankerlanib, uning ostidagi voronkani e'tiborsiz qoldirayotganingizni payqang.

**Anti-pattern.** Qarama-qarshi gipotezaga qarshi sinab ko'rilmagan tavsiyaga ishonch. Kampaniya sizga hali ko'rinmaydigan
atributsiyada yuk ko'taruvchi bo'lishi mumkinligini tan olmasdan "bu kampaniyani to'xtatish kerak".

**Misol trigger.** Har qanday auditda ustuvor harakat rejasini yakunlashdan oldin. Tuzilmaviy o'zgarishni (qayta qurish va
optimallashtirish) tavsiya qilishdan oldin.

---

## 3. LISTEN — Faol qabul qilish

**Ta'rif.** Egoni o'chirib, tashqi fikr-mulohazani qabul qiling. Foydalanuvchi niyati, hamjamiyat muhokamalari va shovqindagi
nozik signallarga e'tibor bering — odamlarga *aslida* nima kerakligini, siz nima kerak deb o'ylayotganingizni emas.

**Reklama ishida.**
- Kampaniya brifini so'zma-so'z o'qing. Mijoz maqsadini o'z so'zlari bilan nima dedi? "Ko'proq lidlar"ni shuni
  nazarda tutganini tekshirmasdan "past CPL" ga tarjima qilmang.
- Funksiyani tavsiya qilishdan oldin platforma yo'riqnomasini tinglang (Google blog, Meta engineering, Microsoft Advertising blog, Apple WWDC sessiyalari).
- Hamjamiyatni tinglang: PPC subredditlari, reklama beruvchilar Slack guruhlari, vendor da'volaridan farq qiladigan haqiqiy natijalarni
  xabar qilayotgan agentlik amaliyotchilari.

**Anti-pattern.** Brend xabardorligi reklama beruvchisiga ko'p auditlar shuni tavsiya qilgani uchun ROAS uchun optimallashtirishni
aytish. Vendor'ning rasmiy natija liftini mustaqil reklama beruvchi ma'lumotlari bilan tekshirmasdan keltirish.

**Misol trigger.** `/ads create` va `/ads dna` — bu buyruqlar mohiyatan tinglash haqida (mos ravishda mijozni va brendni).
Shuningdek: har bir audit boshidagi Context Intake qadami.

---

## 4. THINK — Tanqidiy qayta ishlash

**Ta'rif.** Kirishlar bo'lgach, muammoni birinchi tamoyillargacha parchalang. Mantiqni tuzing, ish jarayonlarini xaritalang,
cheklovlarni baholang va xom ma'lumotni izchil strategiyaga sintez qiling.

**Reklama ishida.**
- Unit-iqtisodni qo'lda hisoblang. Platforma atributsiyalagan ROAS'ga ishonmang — CAC, LTV:CAC, qoplanish davri va MER'ni xom
  ma'lumotdan chiqaring. Matematika uchun `references/budget-allocation.md` ga qarang.
- Voronkani quring: ko'rsatuv → klik → landing → mikro-konversiya → asosiy konversiya → daromad → takror. Sizib ketish qayerda?
- Cheklovlarni joriy muvofiqlik, akkaunt tarixi, konversiya kechikishi, ma'lumot hajmi, iqtisod va rasmiy hujjatlardan baholang.
  Platforma misollari va amaliyotchi nisbatlari — gipotezalar, universal byudjet yoki hajm pollari emas.

**Anti-pattern.** Akkaunt shartlarga javob berishini tekshirmasdan "best practice"ni ko'chirish. MMP, server-side va platforma
raqamlari sezilarli farq qilganda, avval ta'riflar, oynalar, identifikatsiya, rozilik, deduplikatsiya, valyuta va vaqt
mintaqasini moslashtirmasdan platforma atributsiyasini haqiqat deb qabul qilish.

**Misol trigger.** `/ads math`, `/ads budget`, `/ads test`. Shuningdek har bir auditning ballash va ustuvorlashtirish qadami.

---

## 5. CONNECT — Assotsiativ / lateral fikrlash

**Ta'rif.** Ajoyib idrok kesishmalarda yashaydi. Bir-biriga aloqasiz ko'ringan ikki tushunchani bog'lab, yangi kuzatuv
hosil qiling. Ikki alohida o'zgaruvchi o'rtasidagi yashirin munosabatni topishning "aha" lahzasi.

**Reklama ishida.**
- Kreativ-o'xshashlik naqshi yetkazib berishni faqat akkaunt dalili konsept, auditoriya, placement, bid, byudjet va o'rganish
  ta'sirlarini ajratgandan keyingina tushuntirishi mumkin.
- Qidiruv avtomatlashtirishi va feed asosidagi inventar kalit so'zlar rolini o'zgartirishi mumkin, lekin joriy so'rov dalili va
  kampaniya nazoratlari match turlari bu akkaunt uchun muhim bo'lib qoladimi-yo'qmi, hal qiladi.
- Ilova atributsiyasi, rozilik signallari, brauzer va server eventlari hamda analitika o'lchov tizimini tashkil qiladi. Bir qatlamdagi
  tavsiya boshqalar bilan va tegishli geografiya va rozilik holati bilan izchil bo'lishi kerak.

**Anti-pattern.** Platformalararo ta'sirni o'tkazib yuboradigan yakkalangan platforma auditlari. Meta kreativ xilma-xillik
o'zgarishlarini tavsiya qilib, xuddi shu tamoyil yetkazib berish dalili tekshirilgandan keyin boshqa platformaga ham tegishli
bo'lishi mumkinligini payqamaslik.

**Misol trigger.** `/ads plan`, `/ads competitor`, sub-agentlar qaytgandan keyin `/ads audit` sintez qadami.

---

## 6. CONNECT — Tizim orkestratsiyasi

**Ta'rif.** Yakkalangan g'oyadan integratsiyalangan tizimga o'ting. Alohida fikrlar, asboblar va agentlar bir-biriga qanday
ulanib, uzluksiz ishlaydigan butunlikni yaratadi? Simlarni qurish tamoyili.

**Reklama ishida.**
- Kreativ pipeline — ulangan tizim: `/ads dna` → `/ads create` → `/ads generate` → `/ads photoshoot`. Har bir chiqish
  keyingisini oziqlantiradi. Ularni alohida ishlatmang.
- Treking pipeline — tizim: brauzer signallari, server eventlari, rozilik, analitika, ilova atributsiyasi va biznes natijalari.
  `/ads tracking` dagi tavsiya `/ads attribution` bilan izchil bo'lishi kerak.
- `/ads audit` dagi chegaralangan worker'lar faqat parallel emas, orkestratsiya qilinadi. Ularning sxemaga mos topilmalari bitta
  dirijyor va deterministik dvigatelga qaytadi; muvaffaqiyatsiz majburiy worker'lar natijani yo'qotmasdan, qisman qiladi.

**Anti-pattern.** Bir-biriga zid tuzatishlarni tavsiya qilish. Bir auditda savdo-sotiqni tan olmasdan "byudjetni oshiring" va
"bu kampaniyani to'xtating". Foydalanuvchidan oltita sub-skillni qo'lda yurgizishni so'rash, ularni orkestratsiya qilish o'rniga.

**Misol trigger.** Har bir to'liq audit (`/ads audit`). Har bir ko'p qadamli natija (`/ads plan` → `/ads create` → `/ads generate`).

---

## 7. FEEL — Hissiy intellekt va intuitsiya

**Ta'rif.** Sof mantiq hamdardliksiz mo'rt. Inson omilini hisobga oling: foydalanuvchi tajribasi, xabarning hissiy rezonansi
va ma'lumot noaniq bo'lganda qiyinchilik bilan orttirilgan intuitsiya.

**Reklama ishida.**
- Reklama matnini hissiy o'qing. Sarlavha foydalanuvchida *u his qilishni istagan* narsani uyg'otadimi? Oltita sinalgan hissiy
  freymvork uchun `references/copy-frameworks.md` ga qarang.
- Landing sahifaga birinchi marta kelgan tashrif buyuruvchidek qarang. Qiziqish qayerda? Yechim qayerda? CTA to'g'ri paytdami?
- Ma'lumot noaniq bo'lganda kreativ gipotezalarni taklif qilish uchun asoslangan intuitsiyadan foydalaning, so'ng ularni
  belgilang va sinang. Spetsifikatsiyaga mos reklama baribir zaif gipoteza bo'lishi mumkin; sifatiy rezonansni deterministik
  platforma-sog'liq ballashidan ajrating.
- Brend ovozi xaritasi: `references/voice-to-style.md` hissiy atributlarni aniq vizual tanlovlarga o'giradi.

**Anti-pattern.** "Spetsifikatsiyaga muvofiqlik"ni mukofotlab, hissiy yassilik uchun hech narsa jarimalamaydigan ballash rubrikasi.
Xavfsiz zona metrikalarini sanab o'tib, reklama kimgadir biror narsa his qildiradimi, deb hech so'ramaydigan kreativ ko'rib chiqish.

**Misol trigger.** `/ads creative`, `/ads landing`, `/ads create`, `/ads generate`, `/ads photoshoot`.

---

## 8. ACCEPT — Intellektual kamtarlik

**Ta'rif.** Hech bir reja haqiqat bilan birinchi to'qnashuvdan omon qolmaydi. Cheklovlarni qabul qiling, gipoteza muvaffaqiyatsiz
bo'lganini tan oling, bozor siz qurganingizdan boshqa narsani xohlayotganini anglang. Samarali burilish uchun cho'kkan xarajatlardan voz keching.

**Reklama ishida.**
- Kampaniya konversiya kechikishi va yetarli qaror oynasidan keyin egasi tasdiqlagan iqtisodga yetmasa, dalilni qabul qiling
  va pauza, qayta dizayn, qayta taqsimlash yoki o'rganishni davom ettirishni solishtiring. Qat'iy CPA karrali qiymati yoki
  urinishlar soni universal to'xtatish qoidasi emas va hech qachon akkauntni o'zgartirishga ruxsat bermaydi.
- Audit tavsiyasi amalga oshirilib, o'lchov oynasida ko'rsatkichni siljitmagan bo'lsa, buni qabul qilib davom eting —
  ustiga ikki baravar tikmang.
- Mijozning e'lon qilingan maqsadi ma'lumot signaliga mos kelmasa ("lidlar" deydi, lekin faqat daromad eventlari kuzatiladi),
  uni oqlamasdan, bo'shliqni nomlang.

**Anti-pattern.** Akkaunt tarixi ikki marta muvaffaqiyatsizlikni ko'rsatganda "best practice" tavsiyasini himoya qilish.
O'layotgan kampaniyani optimallashtirishni davom ettirish, chunki pauza qilish mag'lubiyatni tan olishdek tuyuladi.

**Misol trigger.** `/ads budget` (kill qoidalari), `/ads audit` oxiridagi ustuvor harakat rejasi, `/ads test` dan keyingi test ko'rib chiqishi.

---

## 9. CREATE — Generativ natija

**Ta'rif.** Tahlil falajligi — taraqqiyot dushmani. Bir nuqtada strategiya tuzishni to'xtatib, ishlab chiqarishni boshlaysiz.
Iste'moldan harakatga o'ting: kodni yozing, kontentni qoralang, natijani topshiring.

**Reklama ishida.**
- Audit hisobotini topshiring. Aniq tavsiyalarsiz yoki har bir harakat bandi uchun egasisiz 50 betlik tahlil yaratmang.
- Haqiqiy reklama matnini yozing, matn haqidagi matn brifi haqida brif emas.
- Reklama aktivlarini `/ads generate` orqali yarating — konseptual bosqichda to'xtamang.
- So'ralgan formatlarni kanonik JSON to'plamdan render qiling. Repozitoriyda hujjatlashtirilgan joriy hisobot va reliz tekshiruv
  buyruqlarini ishga tushiring, so'ng topshirishdan oldin natijani ko'zdan kechiring. Mavjud bo'lmagan skript yoki formatni nomlamang.

**Anti-pattern.** Cheksiz "ko'proq tahlil kerak" tsikllari. Har bir konseptni chetlab o'tib, keyingi hamkorni har bir qiyin
qarorni qabul qilishga majbur qiladigan kampaniya brifi.

**Misol trigger.** `/ads create`, `/ads generate`, `/ads photoshoot`, `/ads report`. Shuningdek har qanday auditning yakuniy sintez qadami.

---

## 10. GROW — Iterativ halqa

**Ta'rif.** Fikrlash to'g'ri chiziq emas; u fikr-mulohaza halqasi. Qurgan narsangizni (CREATE) oling, uning haqiqatda qanday
ishlashini ko'ring va bu saboqlarni keyingi sikl uchun ko'nikmalaringizni yangilash va imkoniyatingizni kengaytirish uchun ishlating.

**Reklama ishida.**
- Har bir audit tavsiyasiga o'lchov rejasi biriktirilgan. Ishlaganini o'lchay olmasangiz, undan o'sa olmaysiz.
- `/ads test` dagi A/B test dizayni: gipoteza → ahamiyat → davomiylik → natija → keyingi gipoteza. Halqaning o'zi maqsad.
- Qarorga mos kuzatuv oynasidan keyin qayta audit qiling. Oldingi auditda yozilgan baza bilan solishtiring va konversiya
  kechikishi, mavsumiylik, eksperiment davomiyligi va oraliqdagi muhim o'zgarishlarni hisobga oling.
- Nima ishlagani va nima ishlamaganini keyingi kampaniya brifiga olib o'ting. `brand-profile.json` qotib qolmasdan, rivojlanishi kerak.

**Anti-pattern.** Kuzatuvsiz bir martalik auditlar. O'lchov mezonlarisiz tavsiyalar. Har bir kampaniyaga oxirgisidan olingan
saboqlar tegishli emasdek munosabat qilish.

**Misol trigger.** Har bir yirik natijaning yakunlovchi qadami. `/ads test` ga va `/ads audit` bevosita taklif qiladigan
qayta audit siklining ichiga o'rnatilgan.

---

## Ish jarayoni xaritasi

Kanonik ish jarayonining har bir qadamida qaysi tamoyil ustun:

| Bosqich | Ustun tamoyillar | Nega |
|---|---|---|
| Context Intake (har bir buyruq boshi) | OBSERVE (tashqi), LISTEN | Akkauntni o'qing, brifni o'qing |
| `/ads dna <url>` | OBSERVE, LISTEN | Aniq ifodalangan brendni tinglash |
| `/ads audit` — ma'lumot yig'ish | OBSERVE, OBSERVE-ichki | Ma'lumot oling; o'z noxolisligingizni tekshiring |
| `/ads audit` — tahlil | THINK, CONNECT-lateral | Birinchi tamoyillar matematikasi; platformalararo sintez |
| `/ads audit` — sintez va ballash | CONNECT-tizim, ACCEPT | Topilmalarni bog'lang; noaniqlik va muvaffaqiyatsiz gipotezalarni qabul qiling |
| `/ads plan` | THINK, CONNECT-lateral, FEEL | Strategiya = matematika + idrok + hamdardlik |
| `/ads create` | LISTEN, FEEL, CREATE | Brendni eshiting; auditoriyani his qiling; brifni topshiring |
| `/ads generate` / `/ads photoshoot` | FEEL, CREATE | Hissiy niyat bilan yarating |
| `/ads report` | CREATE | Natijani render qiling; halqani yoping |
| Natijadan keyin | GROW | O'lchang, o'rganing, keyingi siklni tayyorlang |

Hozirgi bosqichda ustun tamoyil ishga tushmagan bo'lsa, siz qila oladigandan zaifroq ish chiqarayapsiz. Sekinlashing va qaysi
tamoyil yetishmayotganini toping.
