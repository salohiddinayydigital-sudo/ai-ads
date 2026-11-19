# ChatGPT Ads (OpenAI) — audit reference

source_status: url_cited (rasmiy post URL'i qidiruv natijasida; mazmun asosan savdo matbuoti xulosasi orqali ko'rildi, OpenAI sahifasi to'liq o'qilmadi)
checked: 2026-11-19
recheck: 2026-11-19 — `ads.openai.com` Cloudflare 403 ("Just a moment...") qaytardi, rasmiy Ads Manager sahifasi o'qilmadi; hammasi `unverified` qoladi
official_url: https://openai.com/index/new-ways-to-buy-chatgpt-ads
Qolgan manbalar (ikkilamchi, unverified): https://www.searchenginejournal.com/openai-launches-self-serve-ads-manager-for-chatgpt/ · https://ppc.land/openai-opens-chatgpt-ads-manager-to-all-us-businesses-with-cpc-bidding/

## Nimaga ishonish mumkin (ikkilamchi manbalar mos keladi, rasmiy sahifa bilan qayta tekshirilmagan)
- Self-serve beta Ads Manager (`ads.openai.com`) 2026-05-05 da boshlangan; agentlik hamkorlar (Dentsu, Omnicom, Publicis, WPP) orqali sotib olish saqlanadi. `unverified`
- Maqsadlar: Reach (CPM) va Clicks (CPC). CPC uchun maksimal bid qo'lda belgilanadi. `unverified`
- Hisobot maydonlari: impressions, clicks, spend, CTR, avg CPC, avg CPM, conversions (konversiya o'lchovi sozlangan bo'lsa). `unverified`
- O'lchov: Conversions API e'lon qilingan; UTM va pixel haqida ikkilamchi manbalar bor, sozlash tafsiloti topilmadi. `unverified`

## Zid yoki tasdiqlanmagan (raqam KO'CHIRILMAGAN)
- Minimal sarf va CPM/CPC narxlari manbalarda bir-biriga zid (pilot bosqichi va keyingi bosqich aralashgan). Narx, minimal sarf va bid tavsiyalari yozilmaydi: `source_status: unverified`. Foydalanuvchi o'z kabinetidan olgan qiymat `USER_PROVIDED` deb belgilanadi.
- Geografiya (AQSh bilan cheklanganmi), O'zbekiston/MDH mavjudligi: tasdiqlanmagan.
- Pixel va Conversions API maydonlari, event_id dedup talabi: tasdiqlanmagan; hujjatga qarab to'ldiriladi.

## Audit tekshiruvlari (id, severity, nima tekshiriladi)
Barchasi dalilga bog'liq: dalil yo'q bo'lsa `unknown`. Optional/beta imkoniyat yo'qligi nosozlik emas.

| id | severity | Tekshiruv |
|---|---|---|
| CG01 | high | Ads Manager hisobi va to'lov holati faol; hisob egasi/rollar aniq |
| CG02 | critical | Konversiya o'lchovi sozlangan (Conversions API yoki pixel) va hodisalar hisobotda ko'rinadi |
| CG03 | high | Landing URL'larda statik UTM (utm_source/medium/campaign) bor va analitika bilan mos |
| CG04 | high | Maqsad (Reach/Clicks) biznes maqsadiga mos; CPC bo'lsa maksimal bid break-even CPA bilan asoslangan (`tools/calculator.py`) |
| CG05 | medium | Kreativ ChatGPT javob muhitiga mos (reklama sifatida aniq belgilanadi, aldamchi emas) va platforma siyosatiga mos |
| CG06 | medium | Platforma konversiyalari CRM/analitika bilan solishtirilgan (reconciliation), fark izohlangan |
| CG07 | medium | Test byudjeti va muddati belgilangan; natija o'qish qoidasi (`experiments`) |
| CG08 | high | Siyosat va cheklangan toifalar (sog'liq, moliya, siyosiy) tekshirilgan (`compliance-reviewer`) |
| CG09 | low | Maxfiylik: foydalanuvchi ma'lumotini yuborishda rozilik va hash qoidalari |

## Tracking eslatmasi
Conversions API mavjudligi ikkilamchi manbalarda e'lon qilingan; maydonlar va dedup qoidasi `unverified`. Payload yasash `tracking` skilli orqali faqat dry-run; yuborish — foydalanuvchi tasdig'i bilan.
