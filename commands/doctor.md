---
name: doctor
description: "Tyrion tizimi sog'lig'i — katalog, plugin manifesti, asbob yo'llari, jonli MCP ulanishi, versiya, xavfsizlik va unit-testlar"
---

# `/doctor` — Tizim Sog'lig'i Diagnostikasi

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/tools/doctor.py"              # To'liq hisobot (unit-testlar va eval bilan)
python3 "${CLAUDE_PLUGIN_ROOT}/tools/doctor.py" --quick      # Tezkor tekshiruv (1 soniyada)
python3 "${CLAUDE_PLUGIN_ROOT}/tools/tyrion-shield.py" scan  # 5-qavatli TyrionShield xavfsizlik skaneri
```

`doctor.py` quyidagi 15 qatlamni tekshiradi: majburiy fayllar, bilim qatlami (`vault-audit`), YAML frontmatter, katalog (`catalog.json`), buyruq nusxalari, hujjatlardagi sonlar, skill reyestri (`62` skill ↔ `36` agent), `/learn` instinktlari, TyrionShield (`5/5`), `MEMORY.md` (`<=90` qator), MCP Server & Eval qatlami, bilim grafi (`graph.json`), sirlar (`0` sizish), Git tozaligi va unit-testlar.
