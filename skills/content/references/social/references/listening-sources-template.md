# Listening manbalari — shablon

Ushbu faylni loyihangizdagi `.agents/listening-sources.md` ga (yoki `.claude/listening-sources.md` ga) nusxalang va qavslarni to'ldiring. Claude [listening ish jarayoni](listening.md) ni bajarayotganda uni o'qiydi.

Ishlatmaydigan bo'limlarni o'chiring. Qisqa va dolzarb saqlang — eskirgan manbalar manbasizlikdan yomonroq.

---

## Nimani tinglayapmiz

**Brend / mahsulot:** [Mahsulotingiz nomi]
**Kategoriya:** [masalan, "AI yozuv yordamchisi", "Postgres GUI"]
**Maqsad:** [masalan, "Notion'dan o'tayotgan odamlarni topish", "50–200 xodimli B2B SaaS asoschilari bilan jalb qilish"]

## ICP (ballash uchun)

ICP moslikni baholash uchun [ballash rubrikasi](listening.md#scoring-rubric) tomonidan ishlatiladi.

- **Rol:** [masalan, "asoschi, marketing rahbari, marketing ops lead"]
- **Kompaniya bosqichi:** [masalan, "seed'dan Series B gacha SaaS, 10–200 xodim"]
- **Soha:** [masalan, "B2B SaaS, infra, devtools"]
- **Mos kelishini bildiruvchi signallar:** [masalan, "GTM haqida yozadi, pullik reklama yuritadi, yaqinda investitsiya olgan"]

---

## Nishon akkauntlar

Tegishli bo'lganda bu akkauntlarning **har bir** postiga javob bering. Ro'yxatni 20–50 tagacha saqlang.

### LinkedIn (brauzer orqali — feedni ko'rish uchun dev-browser ishlating)
- [Ism] — `linkedin.com/in/handle`
- [Ism] — `linkedin.com/in/handle`

### X / Twitter (brauzer orqali)
- [@handle]
- [@handle]

### Reddit
- u/[username]
- u/[username]

### Bluesky
- [handle.bsky.social]

### Bloglar / Newsletter'lar (RSS)
- [Ism] — `https://example.com/feed/`
- [Ism] — `https://example.substack.com/feed`

### YouTube kanallari (RSS)
- [Ism] — kanal ID `UCxxxxxxxx`

---

## Kalit so'zlar (intent signallari)

Barcha platformalar bo'ylab qidiring. Claude bularni [kundalik siklda](listening.md#the-daily-triage-loop) Reddit, HN, Bluesky orqali ishga tushiradi.

### Yuqori intent (kimdir izlayapti yoki o'tayapti)
- `"alternative to [competitor]"`
- `"looking for a [category] tool"`
- `"recommend a [category]"`
- `"switching from [competitor]"`
- `"frustrated with [competitor]"`

### Muammo signallari (kimdir og'riqda)
- `"[category] is so [bad/hard/expensive]"`
- `"why is [category] [problem]"`
- `"hate [pain point]"`

### Brend eslatmalari
- `"[sizning brend]"`
- `"[brendning yozilishidagi xatolar]"`
- `"[sizning domen]"`

### Raqobatchi eslatmalari (o'tish tilini kuzating)
- `"[raqobatchi 1]"`
- `"[raqobatchi 2]"`

---

## Subreddit'lar

Kundalik siklda Reddit JSON API orqali tortiladi.

- r/SaaS
- r/Entrepreneur
- r/[sizning nisha, masalan, "marketing", "devtools"]
- r/[yondosh hamjamiyat]

---

## Saqlangan qidiruvlar (qo'lda / brauzer orqali)

Claude skanerlash uchun dev-browser orqali ochadigan URL'lar.

### LinkedIn Sales Navigator
- [Qidiruv nomi] — `https://linkedin.com/sales/search/people?...`

### LinkedIn (oddiy)
- Post hashtag — `https://linkedin.com/feed/hashtag/yourtopic/`

### X kengaytirilgan qidiruv
- [Qidiruv nomi] — `https://x.com/search?q=...&f=live`

---

## Jalb qilmaslik kerak

O'zingizni pushaymondan saqlang.

- Yomon niyatli kamsitish bilan tanilgan akkauntlar: [@handle], [@handle]
- Bloklangan brendlar / skrinshot qiladigan raqobatchilar: [ro'yxat]
- Qochish kerak bo'lgan mavzular: [siyosat, [asoschingizning hot take'lari] va h.k.]

---

## Claude uchun eslatmalar

- "Bugungi top 10" so'ralganda, [listening.md](listening.md#the-daily-triage-loop) da belgilangan formatda chiqaring
- LinkedIn va X uchun doimiy sessiyali dev-browser'dan foydalaning (foydalanuvchi tizimga kirgan)
- Qolgan hamma narsa uchun [listening.md](listening.md#sources--light-tooling-curl-recipes) dagi curl retseptlaridan foydalaning
- Standart ortga qarash muddati: 24 soat. Foydalanuvchi o'zgartirishi mumkin.
- Post qilishdan oldin doim so'rang — qoralamalarni chiqaring, foydalanuvchi tasdiqlab, qo'lda post qiladi
