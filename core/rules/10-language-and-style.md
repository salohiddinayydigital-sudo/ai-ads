# Rule 10 — Language Auto-Detection & Native Ad Copy

1. **Response Language = User Prompt Language:** Automatically detect and reply in the language of the user's prompt (English, German, French, Spanish, Portuguese, Arabic, Hindi, Japanese, Korean, Russian, Uzbek, etc.). Never force Uzbek unless the user writes in Uzbek or explicitly selects `market=uz` with Uzbek output.
2. **Native Ad Copywriting:** Write ad headlines, hooks, and primary text natively in each target `--language` (BCP 47 code) rather than mechanically translating.
3. **RTL Formatting Note:** When generating copy in Right-to-Left languages (`ar`, `he`, `fa`, `ur`), preserve logical punctuation placement, keep numbers/currency symbols bidi-safe, and avoid left-aligned text overlays on video hooks.
