# Microsoft Advertising audit nazoratlari katalogi

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

- `microsoft-advertising-api-official`: [Microsoft Advertising API overview](https://learn.microsoft.com/en-us/advertising/guides/?view=bingads-13)
- `microsoft-uet-official`: [Microsoft UET setup](https://learn.microsoft.com/en-us/advertising/msa-help/hlp_ba_conc_uet_setup_master)
- `microsoft-conversions-api-official`: [Microsoft Conversions API guide](https://learn.microsoft.com/en-us/advertising/guides/uet-conversion-api-integration?view=bingads-13)
- `microsoft-google-import-official`: [Microsoft Google Ads import mapping](https://learn.microsoft.com/en-us/advertising/msa-help/hlp_ba_conc_importwhatinfo)

## Nazoratlar reyestri

| ID | Audit maqsadi | Runtime holati |
|---|---|---|
| MS01 | UET tegi o'rnatilgan | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS02 | Enhanced conversions | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS03 | Google Ads importini tekshirish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS04 | Brend sindikatsiyasi nazorati | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS05 | Audience Network sozlamalari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS06 | Bid strategiyasi mosligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS07 | Yangi mijoz optimallashtirishi qo'llanilishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS08 | Kampaniya tuzilmasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS09 | Byudjet taqsimoti | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS10 | LinkedIn profil targetingi qo'llanilishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS11 | RSA aktivlari soni | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS12 | Multimedia Ads | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS13 | Reklama matni noyobligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS19 | Action Extension | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS20 | Filter Link Extension | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS14 | Copilot va yangi placementlar qo'llanilishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS15 | Konversiya maqsadlari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS16 | Platformalararo CPC konteksti | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS17 | Konversiya darajasini taqqoslash | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS18 | Impression share | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS-SI1 | Rejalashtirilgan import holati | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS-CM1 | Consent Mode muvofiqligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS-CT1 | CTV reklama inventari qamrovi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS-VD1 | Video reklama inventaridan foydalanish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| MS25 | Search uchun AI Max qo'llanilishi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS26 | Copilot'da Offer Highlights | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS27 | Audience Generation | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS28 | PMax Final URL hisoboti | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS29 | Clarity AI Visibility | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS30 | Commerce platformalarida Brand Agents | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS31 | Merchant Center'da UCP | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS32 | Copilot Checkout | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS33 | Rewarded Portals | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS34 | Import Center | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS35 | Avtomatlashtirilgan bidding + maxsus ustunlar | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS36 | Natija siljishining asosiy sabab tahlili | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS37 | Konversiya trekingi diagnostikasi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS38 | Data-Driven Attribution qabul qilinishi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS39 | Conversion API | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS40 | Ad Studio Brand Kit | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| MS41 | API transportini ko'chirish dalili | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |

## Tavsiya chegarasi

Tavsiya kuzatilgan dalil, akkauntga xos baza yoki egasi chegarasi, kutilgan mexanizm, ishonch, qaytariladigan keyingi qadam, o'lchov oynasi va rollback shartini ko'rsatishi kerak. Tavsiyani faqat nazorat nomidan xulosa qilmang.
