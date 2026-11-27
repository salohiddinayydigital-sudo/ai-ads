# Meta Ads audit nazoratlari katalogi

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

- `meta-marketing-api-official`: [Meta Marketing APIs documentation](https://developers.facebook.com/docs/marketing-apis/)
- `meta-conversions-api-official`: [Meta Conversions API overview](https://www.facebook.com/business/help/AboutConversionsAPI)

## Nazoratlar reyestri

| ID | Audit maqsadi | Runtime holati |
|---|---|---|
| M01 | Meta Pixel o'rnatilgan | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M02 | Conversions API qo'llanilishi va holati | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M03 | Event deduplikatsiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M04 | Event Match Quality diagnostikasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M05 | Domen verifikatsiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M06 | Aggregated measurement qo'llanilishi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M07 | Standart eventlar va maxsus eventlar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M08 | CAPI Gateway | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M09 | iOS atributsiya oynasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M10 | Ma'lumot yangiligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M25 | Kreativ formatlar xilma-xilligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M26 | Kreativ konsept qamrovi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M27 | Video nisbatlari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M28 | Kreativ charchoqni aniqlash | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M29 | Hook rate | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M30 | Ijtimoiy isbotdan foydalanish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M31 | UGC / ijtimoiy-tabiiy kontent | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M32 | Advantage+ Creative | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M-CR1 | Kreativ yangiligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M-CR2 | Frequency: Prospecting | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M-CR3 | Frequency: Retargeting | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M-CR4 | CTR benchmarki | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M11 | Kampaniya fragmentatsiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M12 | Kampaniya va ad set byudjetini nazorat qilish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M13 | Learning phase holati | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M14 | Learning phase qayta boshlanishlari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M15 | Advantage+ Sales kampaniyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M16 | Ad set konsolidatsiyasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M17 | Byudjet taqsimoti | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M18 | Kampaniya maqsadiga moslik | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M33 | Advantage+ Placements | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M34 | Placement natijalarini ko'rib chiqish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M35 | Atributsiya sozlamasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M36 | Bid strategiyasi mosligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M37 | Frequency cap monitoringi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M38 | Breakdown hisoboti | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M39 | UTM parametrlari | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M40 | A/B testlash faol | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M-ST1 | Byudjet yetarliligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M-ST2 | Byudjetdan foydalanish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M19 | Auditoriya overlapi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M20 | Custom Audience yangiligi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M21 | Lookalike manba sifati | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M22 | Advantage+ Audience testi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M23 | Exclusion auditoriyalar | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M24 | First-party ma'lumotdan foydalanish | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M-AN1 | Andromeda kreativ xilma-xilligi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M-AT1 | Post atributsiya oynasi | Shartli dalil nazorati: qo'llanilishini aniqlang va joriy akkaunt dalilidan baholang; aks holda `unknown` yoki `not_applicable` qaytaring. |
| M-IA1 | Incremental Attribution testi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M-TH1 | Threads placementini baholash | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M51 | Meta Ads MCP server inventari | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M52 | MCP standart bo'yicha pauzada ekanini majburlash | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M53 | MCP yozish harakatlarini boshqarish | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M54 | Click-through metrika ta'rifi dalili | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M55 | Engage-through atributsiya ustuni | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M56 | Engaged-view chegarasi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M57 | Standart atributsiya oynalari | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M58 | Tarixiy bazani taqqoslash mumkinligi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M59 | View-through integratsiyasi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M60 | GEM da'vosining kelib chiqishi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M61 | Lattice da'vosining kelib chiqishi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M62 | Andromeda da'vosining kelib chiqishi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M63 | ARM tayyorligi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M64 | Hisobot ko'rinishi sifatida Incremental Attribution | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M65 | Reklama darajasidagi placement nazorati | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M66 | AI yaratgan Instant Forms | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M67 | Purchase auditoriyani saqlashni boshqarish | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M68 | Pixel auto-include detailed info boshqaruvi | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M69 | Advantage+ Creative Image Generation kategoriyalari | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M70 | Avtomobil bozor-kodi migratsiyasi dalili | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M71 | Digital Services Tax pass-through | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |
| M72 | CAPI bir klikli sozlash + EMQ | Ballanmaydigan manba-yangilash aniqlashi: joriy rasmiy mavjudlik, akkaunt muvofiqligi va boshqaruv ehtiyojini tekshiring; qabul qilmaslik hech qachon nosozlik emas. |

## Tavsiya chegarasi

Tavsiya kuzatilgan dalil, akkauntga xos baza yoki egasi chegarasi, kutilgan mexanizm, ishonch, qaytariladigan keyingi qadam, o'lchov oynasi va rollback shartini ko'rsatishi kerak. Tavsiyani faqat nazorat nomidan xulosa qilmang.
