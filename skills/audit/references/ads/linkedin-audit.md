# LinkedIn Ads audit nazoratlari katalogi

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

- `linkedin-marketing-api-official`: [LinkedIn Marketing Developer Platform](https://learn.microsoft.com/en-us/linkedin/marketing/overview)
- `linkedin-conversion-tracking-official`: [LinkedIn conversion tracking](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/conversion-tracking)
- `linkedin-conversions-api-official`: [LinkedIn Conversions API use cases](https://learn.microsoft.com/en-us/linkedin/marketing/conversions/conversions-usecase)

## Nazoratlar reyestri

| ID | Audit maqsadi | Runtime holati |
|---|---|---|
| L01 | Insight Tag o'rnatilgan | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L02 | Conversions API qo'llanilishi va holati | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L03 | Lavozim nomi targetingi aniqligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L04 | Kompaniya hajmi bo'yicha filtrlash | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L05 | Staj/lavozim darajasi targetingi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L06 | Matched Audiences | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L07 | ABM kompaniya ro'yxati qo'llanilishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L08 | Auditoriyani kengaytirish sozlamasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L09 | Predictive auditoriyalar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L10 | Thought Leader Ads qo'llanilishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L11 | Reklama formatlari xilma-xilligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L12 | Video reklamalar mavjud | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L13 | Kreativni yangilash kadansi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L14 | Lead Gen Form ishqalanishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L15 | Lead Gen Form CRM integratsiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L16 | Bid strategiyasi mosligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L17 | Byudjet yetarliligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L18 | Ad Set maqsadiga moslik | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L19 | A/B testlash faol | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L20 | Frequency monitoringi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L21 | CTR benchmarki | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L22 | CPC benchmarki | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L23 | Lid sifatini kuzatish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L24 | Konversiya trekingi atributsiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L25 | Demografiya hisobotini ko'rib chiqish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L-CRM1 | Daromad atributsiyasi uchun CRM integratsiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L-EU1 | EU Sponsored Messaging muvofiqligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| L28 | Off-Platform Event Ads | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L29 | Campaign Manager terminologiyasini qayta nomlash tuzog'i | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L30 | Accelerate avto-kampaniya yaratish | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L31 | AI Ad Variants | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L32 | Career Journey targetingi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L33 | Reserved Ads | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L34 | First Impression Ads | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L35 | BrandLink kengayishi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L36 | Wire | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L37 | Thought Leader Event Ads | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L38 | CTV kengayishi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L39 | Revenue Attribution Report'da Company Attribution | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L40 | Video metrikalar uchun MRC akkreditatsiyasi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L41 | Company Intelligence API | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L42 | Flexible Ad Creation mavjudligi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L43 | SMB Auto-targeting + Draft with AI | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L44 | Campaign Manager'da real vaqt CRM ma'lumotlari | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L45 | Ads Agency Certification | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| L46 | Organik signal relevantligi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |

## Tavsiya chegarasi

Tavsiya kuzatilgan dalil, akkauntga xos baza yoki egasi chegarasi, kutilgan mexanizm, ishonch, qaytariladigan keyingi qadam, o'lchov oynasi va rollback shartini ko'rsatishi kerak. Tavsiyani faqat nazorat nomidan xulosa qilmang.
