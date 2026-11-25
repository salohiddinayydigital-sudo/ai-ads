<!-- v8.3 Targetolog Copilot Pack: daily-optimizer metodologiyasi. Ref: agents/daily-optimizer.md, rules/40-xavfsizlik-va-hisob.md -->

# Ertalabki 5 daqiqalik triage — KILL / HOLD / ITERATE / SCALE

> Har ertalab har bir Ad Set / Ad uchun bitta qaror. Barcha chegaralar `HEURISTIC_PRIOR_MODEL` — akkaunt tarixi (`MEASURED_ACCOUNT_DATA`) bo'lsa, u ustun.

## 1. Kirish

Oxirgi **1 / 3 / 7 kun**: spend, natija (lid/xarid), CPA/CPL, CTR (link), CPM, frequency, hook rate (3s view / impressions), CVR (natija / link click). Maqsadli CPA va break-even CPA (`tyrion_media_calculator`).

## 2. Qaror daraxti

| Holat (7 kun asosida, 1–3 kun tasdiq) | Qaror | Harakat |
|---|---|---|
| Spend < 1.5 × maqsadli CPA va natija 0 | **HOLD** | Kutish — ma'lumot yetarli emas (kill taqiqlangan) |
| Spend ≥ 2 × maqsadli CPA va natija 0 | **KILL** | Pauza tavsiyasi (Spend-Guard draft) |
| CPA ≤ maqsad, natija ≥ 5–10 (haftalik ≥ 50 bo'lsa ideal) | **SCALE** | +15–20% / 48–72 soat yoki gorizontal (yangi kreativ/angle) |
| CPA maqsaddan 0–30% yuqori, CTR sog'lom | **ITERATE** | Offer/landing/CVR tekshiruvi |
| CPA maqsaddan yuqori, CTR pasaygan, frequency ↑ | **ITERATE** | Kreativ rotatsiya (fatigue) |
| CPA > break-even, spend ≥ 3 × CPA | **KILL** | Pauza + sabab tahlili |
| Learning Phase ichida (< 50 konversiya / 7 kun, oxirgi tahrirdan < 72 soat) | **HOLD** | Tegma (agar KILL sharti bo'lmasa) |

Har KILL/SCALE qarorida: spend, natija soni, minimal sarf chegarasi bajarilganmi (`spend_threshold_met`).

## 3. CPL sakrashi tashxisi — CPM × CTR × CVR

`CPL = CPM / (1000 × CTR × CVR)` — qaysi omil o'zgarganini ajrat:

| O'zgargan omil | Ehtimoliy sabab | Kimga |
|---|---|---|
| **CPM ↑** | auksion raqobati (bayram, oy oxiri), tor auditoriya, frequency ↑, past sifat reytingi | `daily-optimizer` (auditoriya kengaytirish) / `audience-architect` |
| **CTR ↓** | kreativ charchog'i, hook zaif, mos kelmagan auditoriya | `creative-strategist` (fatigue brief) |
| **CVR ↓** | landing/Direct javobi sekin, offer o'zgargan, forma buzilgan, tracking uzilgan | `funnel-cro-doctor` / `tracking-specialist` |

Bir vaqtda faqat bitta ildiz sabab bo'yicha harakat — aks holda nima ishlaganini bilmaysiz.

## 4. Charchoq (fatigue) signallari

- Frequency (7 kun) > 3–4 (prospecting) va CTR 3 kunda > 20% tushgan.
- Hook rate pasaygan, hold rate (ThruPlay / 3s) barqaror → hook almashtir, body qolsin.
- Ikkalasi tushgan → yangi angle (`creative-strategist`).

## 5. Xavfsiz masshtablash

- **Vertikal:** +15–20% har 48–72 soatda; > +20% → majburiy `tyrion_spend_guard` paketi (rollback bilan).
- **Gorizontal:** yangi kreativ/angle mavjud g'olib ad set ichida yoki yangi auditoriya.
- **Taqiq:** byudjetni bir kunda 2× oshirish, learning ichida kuniga bir necha marta tahrirlash.

## 6. Breakdown Effect eslatmasi

Placement/ad set CPA yuqori ko'rinsa ham, marginal CPA `tyrion_breakdown_effect` bilan tekshirilmaguncha kesilmaydi — algoritm arzon natijalarni shu qimmat segment hisobiga olayotgan bo'lishi mumkin.
