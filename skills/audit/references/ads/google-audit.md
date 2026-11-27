# Google Ads audit nazoratlari katalogi

<!-- Katalog ID'lari eski runtime'dan saqlangan; joriy platforma faktlari sanalangan manba yoki akkaunt dalilini talab qiladi. -->

## Runtime baholash kontrakti

- Maqsad, geografiya, akkaunt turi, kampaniya turi, ma'lumot oynasi, konversiya kechikishi, tanlama hajmi va funksiyaga kirishdan boshlang.
- Yuza yoki talab qo'llanilmasa `not_applicable`, kerakli dalil yo'q bo'lsa `unknown` qaytaring.
- Shartli nazorat sog'liqqa faqat joriy akkaunt dalili, egasi belgilagan iqtisod va tegishli rasmiy manba kutilmani belgilagandagina ta'sir qilishi mumkin.
- Mahsulotni qabul qilish, mavjudlik, beta kirish, e'lonlardan xabardorlik va vendor xabar qilgan natijalar sog'liq nazoratlari emas. Ularni faqat ballanmaydigan aniqlash sifatida yozing.
- Bu katalogdan platforma bo'yicha qat'iy chegaralar, keng benchmarklar, ishga tushirish sanalari, to'xtatish sanalari yoki universal tarmoq, bidding, byudjet, auditoriya, kreativ yoki atributsiya qoidalarini ishlatmang.
- O'zgaruvchan faktlarni runtime'da tekshiring. Tasdiqlangan policy, qo'llab-quvvatlash holati yoki migratsiya talabi topilma yaratishdan oldin o'zining joriy da'vo qamroviga muhtoj.

## Manba qamrovi chegarasi

Quyidagi ro'yxatdan o'tgan manbalar faqat da'vo ledgerida ko'rsatilgan o'lchov, API va import asoslarini qamrab oladi. Ular bu katalogdagi har bir nomlangan mahsulot yoki nazoratni qo'llab-quvvatlamaydi. Torroq joriy da'vo paydo bo'lguncha bu nomlarni marshrutlash yorliqlari deb qarang va yangi rasmiy yoki akkaunt ichidagi dalilni to'plang.

## Rasmiy dalil

- `google-ads-api-official`: [Google Ads API documentation](https://developers.google.com/google-ads/api/docs/start)
- `google-ads-conversion-goals-official`: [Google Ads conversion goals](https://support.google.com/google-ads/answer/10995103)
- `google-ads-enhanced-conversions-official`: [Google Ads enhanced conversions](https://support.google.com/google-ads/answer/9888656)

## Nazoratlar reyestri

| ID | Audit maqsadi | Runtime holati |
|---|---|---|
| G42 | Konversiya harakatlari belgilangan | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G43 | Enhanced conversions qo'llanilishi va holati | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G44 | Server-side treking | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G45 | Rozilik signallari va hududiy talablar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G46 | Konversiya oynasi mosligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G47 | Mikro va makro ajratish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G48 | Atributsiya modeli | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G49 | Konversiya qiymatini belgilash | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-CT1 | Takroriy hisoblash yo'q | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-CT2 | GA4 ulangan va ma'lumot oqmoqda | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-CT3 | Google Tag ishlayapti | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G13 | Qidiruv iboralari auditi yangiligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G14 | Negativ kalit so'zlarni boshqarish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G15 | Akkaunt darajasidagi negativlar qo'llangan | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G16 | Muhim bo'lgan tegishli bo'lmagan qidiruv iboralari sarfi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G17 | Broad-match nazorati | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G18 | Close variant ifloslanishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G19 | Qidiruv iboralari ko'rinishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-WS1 | Nol konversiyali kalit so'zlarni tekshirish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G01 | Kampaniya nomlash konvensiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G02 | Ad group nomlash konvensiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G03 | Ad group mavzu izchilligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G04 | Kampaniya fragmentatsiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G05 | Brend va Non-Brand ajratish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G06 | Performance Max qo'llanilishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G07 | Search + PMax overlapi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G08 | Byudjet taqsimoti ustuvorlikka mos | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G09 | Byudjet pacing | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G10 | Reklama jadvali sozlangan | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G11 | Geografik targeting aniqligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G12 | Tarmoq sozlamalari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G20 | O'rtacha Quality Score | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G21 | Kritik QS kalit so'zlari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G22 | Expected CTR komponenti | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G23 | Reklama relevantligi komponenti | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G24 | Landing sahifa tajribasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G25 | Top kalit so'z QS | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-KW1 | Ko'rsatuvsiz kalit so'zlar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-KW2 | Kalit so'z va reklama relevantligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G26 | Har bir ad group uchun RSA | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G27 | RSA sarlavhalar soni | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G28 | RSA tavsiflar soni | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G29 | RSA Ad Strength | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G30 | RSA pinning strategiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G31 | PMax aktivlar qamrovi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G32 | PMax video aktivlari mavjud | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G33 | PMax asset group soni | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G34 | PMax final URL kengaytirishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G35 | Reklama matnining kalit so'zlarga relevantligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-AD1 | Reklama yangiligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-AD2 | CTR konteksti | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G50 | Sitelink extension'lar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G51 | Callout extension'lar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G52 | Structured snippets | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G53 | Image extension'lar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G54 | Call extension'lar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G55 | Lead form extension'lar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G56 | Qo'llangan auditoriya segmentlari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G57 | Customer Match ro'yxatlari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G58 | Placement exclusion'lar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G59 | Landing sahifa mobil tezligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G60 | Landing sahifa relevantligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G61 | Landing sahifa schema markup | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-PM1 | Auditoriya signallari sozlangan | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-PM2 | PMax Ad Strength | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-PM3 | Brend inkrementalligini ko'rib chiqish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-PM4 | Search themes | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-PM5 | Negativ kalit so'zlar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-PM6 | PMax negativ kalit so'zlari qo'llanilishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-AI1 | Search uchun AI Max baholash | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G-DG1 | Demand Gen tasvir aktivlari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-DG2 | VAC migratsiya holati | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-DG3 | Demand Gen frequency cap yo'qolishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G-CTV1 | CTV Floodlight treking cheklovi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G36 | Smart bidding strategiyasi faol | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G37 | Target CPA/ROAS asosliligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G38 | Learning phase holati | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G39 | Byudjet bilan cheklangan kampaniyalar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G40 | Manual CPC asosi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G41 | Portfel bid strategiyalari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| G81 | Ask Advisor boshqaruvi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G82 | Business Agent for Leads muvofiqligi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G83 | Direct Offers kengayishi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G84 | AI Mode reklama formati tayyorligi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G85 | Journey-aware bidding | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G86 | PMax + Shopping'da Smart Bidding Exploration | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G87 | Kampaniya umumiy byudjetlari | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G88 | Talabga asoslangan pacing | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G89 | Meridian o'lchovi qo'llanilishi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G90 | Qualified Future Conversions | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G91 | Attributed Branded Searches | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G92 | Asset Studio Gemini Omni tayyorligi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G93 | Demand Gen funksiyalar steki | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G94 | Ads Advisor xavfsizlik funksiyalari | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| G95 | DSA migratsiyaga tayyorlik dalili | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |

## Tavsiya chegarasi

Tavsiya kuzatilgan dalil, akkauntga xos baza yoki egasi chegarasi, kutilgan mexanizm, ishonch, qaytariladigan keyingi qadam, o'lchov oynasi va rollback shartini ko'rsatishi kerak. Tavsiyani faqat nazorat nomidan xulosa qilmang.
