# Claude Ads prompt naqshlari

Bu original misollar marshrutlash, worker kontraktlari, noaniqlik va o'zgartirish xavfsizligini belgilaydi. Ulardan
xatti-harakat nozik bo'lganda foydalaning; oddiy hisob-kitoblar yoki aniq marshrutlangan platforma savoli uchun yuklamang.

## 1. Mo'ljallangan artefakt bo'yicha marshrutlash

Foydalanuvchi: "Shu mahsulot fotosuratidan to'rtta Meta reklama konsepti yarat."

- Foydalanuvchiga konseptlar, xabarlar, hooklar yoki brifler kerak bo'lganda `ads-create` ga yo'naltiring.
- `ads-generate` ga faqat tasdiqlangan brif mavjud va tasvir fayllari so'ralganda yo'naltiring.
- Asosiy so'rov kompozitsiyalangan reklama konseptlari emas, mahsulot fotosuratini o'zgartirish bo'lsa, `ads-photoshoot` ga yo'naltiring.
- So'rov ham konsept, ham renderni o'z ichiga olsa, create ni ishga tushiring, tasdiq oling, so'ng generate. Oraliq manifestni o'tkazib yubormang.

## 2. Chegaralangan platforma worker'i

```json
{
  "objective": "Audit Google conversion measurement for the supplied window",
  "scope": ["conversion taxonomy", "tag and enhanced-conversion evidence", "deduplication"],
  "exclusions": ["creative", "budget", "account mutation"],
  "evidence_policy": ["account export", "official current sources"],
  "privacy_class": "confidential",
  "mutation_authority": "read-only",
  "inputs": ["run:20260711-demo/account-snapshot.json"],
  "output_contract": "Finding[] v1.0.0",
  "verification": ["schema validate", "cite every failed control"],
  "recovery": ["return needs_input for missing tag evidence"]
}
```

Worker topilmalar va tiklash maslahatlarini dirijyorga qaytaradi. U `google-audit-results.md` ni yozmaydi, platforma
balini hisoblamaydi va byudjet ishiga kengaymaydi.

## 3. Yetishmayotgan dalil

Foydalanuvchi: "Mening Meta CPA'm ikki baravar oshdi. Eng yomon reklamalarni pauza qil."

Berilgan ma'lumotlarda konversiya kechikishi, atributsiya ta'rifi, sarf, tanlama hajmi, so'nggi o'zgarishlar yoki joriy
masofaviy holat yetishmasa:

1. Kuzatilgan CPA o'zgarishini faqat oynalar taqqoslanadigan bo'lsa yozing.
2. O'zgartirish uchun `needs_input` qaytaring.
3. Faqat o'qish diagnostikasi va aniq ma'lumot so'rovini taklif eting.
4. Qat'iy CPA karrali qiymatini qo'llamang va kuzatilgan eng yomon reklama akkaunt darajasidagi o'zgarishga sabab bo'lgan deb xulosa qilmang.

## 4. Tasdiqlangan o'zgartirish

Tasdiq faqat taqdim etilgan aniq o'zgartirish rejasi uchun yaroqli:

```json
{
  "account_id": "redacted-demo",
  "object_id": "campaign-123",
  "operation": "pause",
  "before": {"status": "ACTIVE"},
  "after": {"status": "PAUSED"},
  "reason": "Operator-approved policy containment",
  "blast_radius": "one campaign",
  "idempotency_key": "sha256:...",
  "verification_window": "immediate plus 15 minutes",
  "rollback": {"operation": "restore_status", "value": "ACTIVE"}
}
```

Masofaviy holat `before` ga mos kelmasa, to'xtang va rejani qayta yarating. Bir kampaniya, byudjet yoki sana uchun tasdiq
boshqasiga o'tmaydi.

## 5. Tadqiqot va mustaqil tekshiruv

Tadqiqot worker'i manba yozuvlari va ta'sirlangan da'volarni taklif qiladi. Alohida manba tekshiruvchisi vakolat, sana,
qamrov, geografiya, metodologiya, litsenziya va da'vo-manba mosligini tekshiradi. Faqat shundan keyingina dirijyor
kanonik referenslar va testlarni yangilashi mumkin. Hamjamiyat posti tadqiqot izini yaratishi mumkin; u rasmiy API yoki
policy da'vosini o'rnata olmaydi.

## 6. Qisman to'liq audit

Google, Meta va treking muvaffaqiyatli bo'lib, so'ralgan Amazon worker'i autentifikatsiyadan o'tmasa:

- Muvaffaqiyatli platforma natijalarini saqlang.
- To'plamni `partial` deb belgilang.
- Amazon'ni raqamli portfel sog'lig'idan chiqarib tashlang va uning yetishmayotgan vaznini ko'rsating.
- Autentifikatsiyani tiklash qadamini qaytaring.
- Natijani hech qachon "to'liq ko'p platformali audit" deb nomlamang.
