---
name: doctor
description: "Tyrion v7.1 tizimining ko'p qatlamli sog'liq, katalog, MCP, xavfsizlik va unit-test diagnostikasi"
---

# `/doctor` — Tizim Sog'lig'i Diagnostikasi

```bash
python3 tools/doctor.py              # To'liq hisobot (unit-testlar va eval bilan)
python3 tools/doctor.py --quick      # Tezkor tekshiruv (1 soniyada)
python3 tools/tyrion-shield.py scan  # 5-qavatli TyrionShield xavfsizlik skaneri
```

`doctor.py` quyidagi qatlamlarni tekshiradi: majburiy fayllar, bilim qatlami (`vault-audit`), YAML frontmatter, katalog (`catalog.json`), buyruq nusxalari, hujjatlardagi sonlar, skill reyestri (skill ↔ agent), `/learn` instinktlari, TyrionShield (`5/5`), `MEMORY.md` (`<=90` qator), MCP Server & Eval qatlami, bilim grafi (`graph.json`), sirlar (`0` sizish), Git tozaligi va unit-testlar.
