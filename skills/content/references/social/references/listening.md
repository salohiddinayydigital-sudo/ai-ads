# Social listening va engagement triage

Har kuni tasodifiy scroll qilish o'rniga, qaysi postlarga javob berishni qanday aniqlash. Maqsad — ochiq feed emas, qisqa, ballanadigan ro'yxat ("mana izoh qoldirishingiz kerak bo'lgan top 10 post").

## Mundarija
- Qachon ishlatiladi
- Kundalik triage sikli
- Ballash rubrikasi
- Izoh sifati darajalari
- Manbalar va yengil asboblar (curl retseptlari)
- Platformaga xos eslatmalar
- Keng tarqalgan ish jarayonlari

---

## Qachon ishlatiladi

Maqsad post qilish emas, **izoh qoldirish va munosabatlar** bo'lganda listening'dan foydalaning. Odatiy so'rovlar:
- "Bugun izoh qoldirishim kerak bo'lgan top 10 postni bering"
- "Hozir kim [raqobatchi]dan shikoyat qilyapti?"
- "Meniki kabi asbob so'rayotgan odamlarni toping"
- "Oxirgi 24 soatdagi 20 ta nishon akkauntimning postlarini chiqaring"
- "Bu hafta [mavzu] atrofida qanday suhbat bor?"

Foydalanuvchi kontent **yaratmoqchi** bo'lsa, social skillning qolgan qismidan foydalaning. Listening yaratishni oziqlantiradi (burchaklar, til, e'tirozlarni ko'rsatadi), lekin natijasi boshqa.

---

## Kundalik triage sikli

Foydalanuvchi (yoki sizning nomingizdan siz) har ertalab bajarishi mumkin bo'lgan takrorlanadigan 20 daqiqalik sikl.

1. **Torting (Pull)** — belgilangan manbalardan (nishon akkauntlar, kalit so'zlar, subreddit'lar, hashtag'lar) yangi postlarni oling. [Asboblarga](#manbalar-va-yengil-asboblar-curl-retseptlari) qarang.
2. **Filtrlang** — 24 soatdan eski, past signalli yoki mavzudan tashqari hamma narsani tashlang.
3. **Ballang** — [rubrikani](#ballash-rubrikasi) qo'llang. Top 10 ni qoldiring.
4. **Qoralang** — har biri uchun postning darajasiga mos izoh qoralang.
5. **Post qiling** — foydalanuvchi ko'rib chiqadi, tahrirlaydi, post qiladi. Qaysi biri haqiqatan chiqqanini belgilang.
6. **Qayd eting** — qaysi postlarga izoh qoldirganingiz va qaysi biri javob olganini kuzating. Bu sizning engagement sikli ma'lumotlar to'plami.

Claude yaratishi kerak bo'lgan natija formati:

```
TOP 10 POSTS — 2026-06-05

1. [Score 9/10] @author — LinkedIn — 2h ago
   "We just rolled out X and the team is loving it…"
   Why: ICP fit (B2B SaaS, 50–200 employees), buying-intent signal
   Suggested comment: [draft]
   Link: https://…
```

---

## Ballash rubrikasi

Har bir postni beshta o'lchov bo'yicha 1–10 ball bilan baholang, so'ng jamlang va tartiblang.

| O'lchov | Nimani o'lchaydi | Vazn |
|-----------|------------------|--------|
| **ICP moslik** | Muallif sizning nishon mijozingiz / influenser'misiz? | 2x |
| **Intent signali** | Ular muammoni bildiryaptimi, so'rayaptimi yoki xarid qilyaptimi? | 2x |
| **Qamrov salohiyati** | Post tortish olyaptimi (yoqishlar/izohlar o'smoqda)? | 1x |
| **Izoh imkoniyati** | Umumiy emas, haqiqatan foydali narsa ayta olasizmi? | 2x |
| **Yangilik** | So'nggi 1–4 soatda post qilingan (erta izohlar yutadi, ayniqsa LinkedIn'da) | 1x |

**Intent signali misollari (yuqori qiymatli):**
- "X qiladigan asbob qidiryapman"
- "Nega [kategoriya] shunchalik og'riqli?"
- "Biz [raqobatchi]dan o'tdik, chunki…"
- "[Raqobatchi]dan foydalanadigan bormi — arziydimi?"
- Ma'lum raqobatchi haqida shikoyat

**Quyidagilardan biri to'g'ri bo'lsa tashlang:**
- Muallif ICP ham emas, influenser ham emas
- Post >24 soat eski va allaqachon 50+ izohi bor (izohingiz ko'milib ketadi)
- Umumiy motivatsion/AI-slop post
- Izohlar qamrov olmaydigan o'z-o'zini reklama qilish thread'i
- "Ajoyib post!" dan boshqa narsa qo'sha olmaysiz

---

## Izoh sifati darajalari

Izohni postga moslang. 1-daraja qoralamani 3-daraja imkoniyatga isrof qilmang.

**1-daraja — Munosabat quruvchi (nishon akkauntlar, ICP, yuqori intent)**
- Aniq insayt yoki qarama-qarshi misol qo'shing
- O'z tajribangizga aniqliklar bilan (raqamlar, nomlar, natijalar) murojaat qiling
- Javobga undaydigan o'ylangan davomiy savol bering
- Uzunligi: 2–4 gap, havolasiz

**2-daraja — Ko'rinish o'yini (yuqori qamrovli post, yondosh mavzu)**
- Bitta gapda bitta o'tkir insayt qo'shing
- Naqsh: "Kelishaman — va ko'pchilik o'tkazib yuboradigan qismi [X]"
- Uzunligi: 1–2 gap

**3-daraja — Yengil teginish (munosabatni saqlash)**
- "Yoqdi" emas, aniq reaksiya
- Aniq bir qatorni iqtibos qiling va unga munosabat bildiring
- Uzunligi: 1 gap

**Hech qachon:** "Ajoyib post!", faqat emoji, "+1", "This is gold 🔥" kabi LinkedIn-izmlar

---

## Manbalar va yengil asboblar (curl retseptlari)

Bular ommaviy JSON endpoint'lar — autentifikatsiya kerak emas. Ularni bash'dan ishga tushiring, `jq` ga yo'naltiring, Claude natijani tahlil qilib ballashi va izohlarni qoralashi mumkin.

**Talab qilinadi:** `jq` (ko'p retseptlar) va `xmllint` (faqat RSS). Bir marta o'rnating:
```bash
# macOS
brew install jq
# xmllint ships with macOS; on Linux: apt install libxml2-utils
```

### Reddit (bepul, skriptlanadigan)

**Subreddit'dagi yangi postlar:**
```bash
curl -s -A "listening/1.0" \
  "https://www.reddit.com/r/SaaS/new.json?limit=25" \
  | jq '.data.children[].data | {title, author, url: ("https://reddit.com"+.permalink), score, num_comments, created_utc, selftext: (.selftext | .[0:300])}'
```

**Reddit bo'ylab kalit so'z bo'yicha qidirish (oxirgi kun, yangi bo'yicha tartiblangan):**
```bash
curl -s -A "listening/1.0" \
  "https://www.reddit.com/search.json?q=KEYWORD&sort=new&t=day&limit=25" \
  | jq '.data.children[].data | {subreddit, title, url: ("https://reddit.com"+.permalink), author, score, created_utc}'
```

`KEYWORD` o'rniga `"alternative to notion"`, `"recommend a crm"`, raqobatchi nomlari yoki eslatmalar uchun o'z brendingizni qo'ying. Ko'p so'zli iboralar atrofida qo'shtirnoq ishlating.

### Hacker News (Algolia qidiruvi)

**Kalit so'zni eslatgan so'nggi hikoyalar (oxirgi 24 soat):**
```bash
SINCE=$(($(date +%s) - 86400))
curl -s "https://hn.algolia.com/api/v1/search_by_date?query=KEYWORD&tags=story&numericFilters=created_at_i>${SINCE}" \
  | jq '.hits[] | {title, url, author, points, num_comments, created_at, story_id: .objectID, hn_url: ("https://news.ycombinator.com/item?id="+.objectID)}'
```

**Kalit so'zni eslatgan so'nggi izohlar:**
```bash
curl -s "https://hn.algolia.com/api/v1/search_by_date?query=KEYWORD&tags=comment&numericFilters=created_at_i>${SINCE}" \
  | jq '.hits[] | {author, comment_text, story_title, hn_url: ("https://news.ycombinator.com/item?id="+.objectID)}'
```

### Bluesky (bepul, ommaviy API)

**Kalit so'z bo'yicha postlarni qidirish:**
```bash
curl -s "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=KEYWORD&limit=25&sort=latest" \
  | jq '.posts[] | {author: .author.handle, text: .record.text, likes: .likeCount, replies: .replyCount, url: ("https://bsky.app/profile/"+.author.handle+"/post/"+(.uri | split("/") | last))}'
```

### Bloglar, podkastlar, YouTube kanallari uchun RSS

RSS'ga nashr qiladigan nishon akkauntlar uchun (ko'pchilik bloglar, barcha YouTube kanallari):
```bash
# YouTube channel feed (replace CHANNEL_ID)
curl -s "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID"

# Generic blog feed
curl -s "https://example.com/feed/" | xmllint --xpath "//item[position()<6]" - 2>/dev/null
```

### LinkedIn va X — brauzerdan foydalaning

LinkedIn va X foydali ommaviy API'larni taqdim etmaydi, lekin haqiqiy brauzer sessiyasini boshqarishingiz mumkin. **dev-browser** (MCP, global sozlamada allaqachon bor) va **Playwright** ikkalasi ham doimiy holatni saqlaydi — bir marta kiring, sessiya tirik qoladi, Claude autentifikatsiyalangan feedda navigatsiya qila oladi.

**dev-browser ish jarayoni (afzal — allaqachon ulangan):**
1. Foydalanuvchi dev-browser sessiyasida LinkedIn / X'ga bir marta kiradi
2. Claude nishon URL'ga (feed, profil, saqlangan qidiruv, hashtag) o'tadi
3. Claude accessibility tree / sahifa matnini o'qiydi, postlarni ajratib oladi
4. Claude [rubrika](#ballash-rubrikasi) bo'yicha ballaydi va izohlarni qoralaydi
5. Foydalanuvchi ko'rib chiqadi va qo'lda post qiladi (avtomatik post qilmang — yuqori xavf, bot aniqlash xavfi)

**dev-browser'ga berish uchun foydali URL'lar:**

| URL naqshi | Nimani ko'rsatadi |
|-------------|---------------|
| `linkedin.com/in/HANDLE/recent-activity/all/` | Nishon akkauntning so'nggi postlari |
| `linkedin.com/feed/hashtag/TOPIC/` | Hashtag feedi |
| `linkedin.com/feed/` | Asosiy feedingiz (algoritmik — triage uchun kamroq foydali) |
| `x.com/HANDLE` | Nishon akkaunt profili |
| `x.com/search?q=QUERY&f=live` | Real vaqtli qidiruv (xronologik uchun `f=live` ishlating) |
| `x.com/i/lists/LIST_ID` | Kuratorlik qilingan ro'yxat — nishon akkauntlar uchun eng yaxshisi |

**Maslahatlar:**
- X'da nishon akkauntlarning shaxsiy ro'yxatini tuzing va ro'yxat URL'idan foydalaning. Algoritmik feeddan ancha toza.
- LinkedIn'ning `/recent-activity/all/` URL'i bir kishi postlarini algoritmsiz ko'rishning eng toza yo'li.
- Ikkala platforma uchun ham ajratib olishdan oldin ko'proq post yuklash uchun dasturiy scroll qiling (dev-browser buni qo'llab-quvvatlaydi).

**Brauzerni boshqarishni xohlamasangiz, pullik muqobillar:**

| Platforma | Asboblar |
|----------|-------|
| LinkedIn | Sales Navigator (saqlangan qidiruvlar), Taplio (engagement) |
| X | TweetDeck/X Pro (saqlangan ustunlar), Typefully, Taplio, Tweet Hunter |

**Hali yopiq (yaxshi yo'l yo'q):**
- Instagram va TikTok — yopiq API'lar, brauzer avtomatlashtirish aniqlanadi va xavfli. Native saqlangan qidiruvlar / hashtag kuzatuvlaridan foydalaning.

---

## Platformaga xos eslatmalar

### LinkedIn
- **Brauzer orqali** (doimiy sessiyali dev-browser) — [LinkedIn va X — brauzerdan foydalaning](#linkedin-va-x--brauzerdan-foydalaning) ga qarang
- **Birinchi soatdagi izohlar eng muhim** — algoritm erta jalb qilishni kuchli og'irlaydi. Nishon akkauntlarning <2 soat oldingi postlariga ustuvorlik bering.
- 5+ so'zli izohlar reaksiyalardan ko'ra ko'proq qamrov oladi
- Boshqa izoh qoldiruvchilarga javob berish sizni ularning tarmog'i oldiga qo'yishi mumkin
- Javobingizda faqat kontekst qo'shsa, muallifni belgilang

### Twitter/X
- **Brauzer orqali** (dev-browser) — nishon akkauntlarning shaxsiy ro'yxatini tuzing va dev-browser'ni ro'yxat URL'iga yo'naltiring
- Yirik akkauntlarda maksimal qamrov uchun dastlabki 30 daqiqa ichida javob bering
- Sezilarli qiymat qo'shganda quote-tweet > reply
- Javobingizni thread qilish (ko'p tweet) harakatni bildiradi
- Kamsitishga qo'shilmang — munosabatlar > obro'

### Reddit
- Izoh qoldirishdan oldin subreddit qoidalarini o'qing (ba'zilari o'z-o'zini reklama qilishni butunlay taqiqlaydi)
- O'zingizga tegishli narsaga havola qilishdan oldin sub'da karma to'plang
- Uzun, aniq javoblar yutadi. AMA'lar va "qaror qilishimga yordam bering" thread'lari — oltin
- Hech qachon mahsulotingizdan boshlamang — avval savolga javob bering

### Hacker News
- Izoh sifati talabi yuqori; kam mehnatli izohlar tez downvote qilinadi
- Asoschilarning o'z mahsuloti haqidagi thread'larga izoh qoldirishi shaffof bo'lsangiz qabul qilinadi
- Kategoriyangizning o'tgan muhokamalarini qidiring — ular ko'pincha uxlab yotgan oltin konlari

### Bluesky
- Hajm kichikroq, lekin follower'ga nisbatan engagement yuqori
- Texnologiya va indie-hacker hamjamiyatlari faol
- Maxsus feedlar (Bluesky'ning "Following" + mavzu feedlari kabi) algoritmik qidiruvni almashtiradi

---

## Keng tarqalgan ish jarayonlari

### "Bugun izoh qoldirishim kerak bo'lgan top 10 postni bering"
1. Quyidagilardan torting: nishon akkaunt RSS/saqlangan qidiruvlar + Reddit (tegishli sub'lar) + HN (oxirgi 24 soat)
2. [Rubrika](#ballash-rubrikasi) bilan ballang
3. Taklif etilgan izohlar bilan top 10 ni chiqaring

### "[Raqobatchi]dan shikoyat qilayotganlarni toping"
1. Reddit qidiruvi: `"competitor name" -site:competitor.com` yangi bo'yicha tartiblangan
2. Raqobatchi nomi uchun HN izoh qidiruvi
3. Raqobatchi handle/nomi uchun Bluesky qidiruvi
4. Intent signali bo'yicha ballang (o'tish tili bo'lsa yuqori: "moving from", "alternatives to", "frustrated with")

### "So'nggi hafta brend eslatmalarini chiqaring"
1. Brend nomi uchun Reddit qidiruvi
2. Brend nomi uchun HN qidiruvi (hikoyalar + izohlar)
3. Brend nomi + handle uchun Bluesky qidiruvi
4. Natija: javob kerakmi (ha/yo'q), ohang (ijobiy/salbiy/neytral), taklif etilgan javob

### "O'tkazib yuborgan nishon akkaunt postlarini toping"
1. RSS / Reddit foydalanuvchi nomlari / Bluesky handle'lari bilan nishon akkauntlar ro'yxatini yuriting
2. Har bir manbaning so'nggi postlarini oling
3. Oxirgi 24 soat bilan cheklang, ball bo'yicha tartiblab chiqaring

---

## Manbalar ro'yxatini sozlash

Foydalanuvchi manbalar ro'yxatini `.agents/listening-sources.md` (yoki `.claude/listening-sources.md`) da doimiy joyda yuritishi kerak. Claude kundalik siklni bajarayotganda uni o'qiydi.

**Tayyor to'ldiriladigan shablon [listening-sources-template.md](listening-sources-template.md) da.** Uni loyihaga nusxalang va tahrirlang. Manba yo'li skill qanday o'rnatilganiga bog'liq:

```bash
# Plugin / marketplace install (most common):
cp .agents/skills/content/references/social/references/listening-sources-template.md .agents/listening-sources.md
# .claude/ install:
cp .claude/skills/content/references/social/references/listening-sources-template.md .agents/listening-sources.md
# Working inside the marketingskills repo:
cp skills/content/references/social/references/listening-sources-template.md .agents/listening-sources.md
```

Shablon quyidagilarni qamrab oladi: brend/kategoriya, ICP (ballash uchun), platforma bo'yicha nishon akkauntlar, intent kalit so'zlari, subreddit'lar, saqlangan qidiruv URL'lari va jalb qilmaslik ro'yxati.
