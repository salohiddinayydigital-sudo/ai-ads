---
name: creative
description: "3x3 kreativ test matritsasi, Andromeda PDA xilma-xillik rejasi, 9:16 video reklama ssenariylari, ko'p tilli 3 soniyalik hooklar, BNPL narx ankerlari va charchoq diagnostikasi (Aliaslar: /ad-creative, /kreativ)"
alias_of: kreativ
argument-hint: "<mahsulot/taklif> [--niche ecom|edu|real-estate|medical|b2b|beauty|auto|local] [--price 100] [--market global|uz|eu|us]"
---

# `/creative` (Aliaslar: `/ad-creative`, `/kreativ`) — Kreativ strategiya, video ssenariylar va Hook studiyasi

Vazifa: **$ARGUMENTS**

## Bajarish tartibi (hech qachon `--help` da to'xtamang!)

1. Foydalanuvchi tilini va faol bozor paketini aniqlang (`markets/<market>/pack.json`, standart `global`).
2. Deterministik kreativ, video-ssenariy va hook dvigatellarini ishga tushiring:
   ```bash
   python3 tools/creative-matrix.py pda-matrix --niche <niche> --product "<product>" --price <price> --market <market> --currency <ISO>
   python3 tools/creative-matrix.py video-script --niche <niche> --product "<product>" --format ugc_reaction_demo --language <lang>
   python3 tools/creative-matrix.py hooks --niche <niche> --offer "<product>" --languages <lang>
   ```
3. 3x3 Angle x Format matritsasi, Andromeda PDA xilma-xillik rejasi, vaqt kodli 9:16 video ssenariy, belgilar soni tekshirilgan matn va inkor qilinadigan test gipotezalarini foydalanuvchi tilida umumlashtiring.
