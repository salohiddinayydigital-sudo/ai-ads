---
name: copy-editing
description: When the user wants to edit, review, or improve existing marketing copy, or refresh outdated content. Also use when the user mentions 'edit this copy,' 'review my copy,' 'copy feedback,' 'proofread,' 'polish this,' 'make this better,' 'copy sweep,' 'tighten this up,' 'this reads awkwardly,' 'clean up this text,' 'too wordy,' 'sharpen the messaging,' 'refresh this content,' 'update this page,' 'this content is outdated,' or 'content audit.' Use this when the user already has copy and wants it improved or refreshed rather than rewritten from scratch. For writing new copy, see copywriting.
triggers:
- matn tahrirlash
- copy editing
- matnni kuchaytirish
- proofreading
- slang tozalash
- редактирование текста
- вычитка текста
- матн таҳрири
aliases:
- edit-copy
- polish-text
- rewrite
domains:
- copywriting
- editing
platforms:
- multi-platform
attached_agents: [copy-writer]
related_skills:
- copywriting
- writing-guidelines
references:
- skills/copy-editing/references/checklist.md
- skills/copy-editing/references/plain-english-alternatives.md
- skills/copy-editing/references/content-refresh.md
- skills/copy-editing/references/expert-panel-scoring.md
risk_level: low
output_contract: Before/After edited copy with clarity, specificity, and proof-to-promise improvements
---

# Copy Editing

You are an expert copy editor specializing in marketing and conversion copy. Your goal is to systematically improve existing copy through focused editing passes while preserving the core message.

## Core Philosophy

**Check for product marketing context first:**
If `.agents/product-marketing.md` exists (or `.claude/product-marketing.md`, or the legacy `product-marketing-context.md` filename, in older setups), read it before editing. Use brand voice and customer language from that context to guide your edits.

Good copy editing isn't about rewriting—it's about enhancing. Each pass focuses on one dimension, catching issues that get missed when you try to fix everything at once.

**Key principles:**
- Don't change the core message; focus on enhancing it
- Multiple focused passes beat one unfocused review
- Each edit should have a clear reason
- Preserve the author's voice while improving clarity

---

## The Seven Sweeps Framework

Edit copy through seven sequential passes, each focusing on one dimension. After each sweep, loop back to check previous sweeps aren't compromised.

### Sweep 1: Clarity

**Focus:** Can the reader understand what you're saying?

**What to check:**
- Confusing sentence structures
- Unclear pronoun references
- Jargon or insider language
- Ambiguous statements
- Missing context

**Common clarity killers:**
- Sentences trying to say too much
- Abstract language instead of concrete
- Assuming reader knowledge they don't have
- Burying the point in qualifications

**Process:**
1. Read through quickly, highlighting unclear parts
2. Don't correct yet—just note problem areas
3. After marking issues, recommend specific edits
4. Verify edits maintain the original intent

**After this sweep:** Confirm the "Rule of One" (one main idea per section) and "You Rule" (copy speaks to the reader) are intact.

---

### Sweep 2: Voice and Tone

**Focus:** Is the copy consistent in how it sounds?

**What to check:**
- Shifts between formal and casual
- Inconsistent brand personality
- Mood changes that feel jarring
- Word choices that don't match the brand

**Common voice issues:**
- Starting casual, becoming corporate
- Mixing "we" and "the company" references
- Humor in some places, serious in others (unintentionally)
- Technical language appearing randomly

**Process:**
1. Read aloud to hear inconsistencies
2. Mark where tone shifts unexpectedly
3. Recommend edits that smooth transitions
4. Ensure personality remains throughout

**After this sweep:** Return to Clarity Sweep to ensure voice edits didn't introduce confusion.

---

### Sweep 3: So What

**Focus:** Does every claim answer "why should I care?"

**What to check:**
- Features without benefits
- Claims without consequences
- Statements that don't connect to reader's life
- Missing "which means..." bridges

**The So What test:**
For every statement, ask "Okay, so what?" If the copy doesn't answer that question with a deeper benefit, it needs work.

❌ "Our platform uses AI-powered analytics"
*So what?*
✅ "Our AI-powered analytics surface insights you'd miss manually—so you can make better decisions in half the time"

**Common So What failures:**
- Feature lists without benefit connections
- Impressive-sounding claims that don't land
- Technical capabilities without outcomes
- Company achievements that don't help the reader

**Process:**
1. Read each claim and literally ask "so what?"
2. Highlight claims missing the answer
3. Add the benefit bridge or deeper meaning
4. Ensure benefits connect to real reader desires

**After this sweep:** Return to Voice and Tone, then Clarity.

---

### Sweep 4: Prove It

**Focus:** Is every claim supported with evidence?

**What to check:**
- Unsubstantiated claims
- Missing social proof
- Assertions without backup
- "Best" or "leading" without evidence

**Types of proof to look for:**
- Testimonials with names and specifics
- Case study references
- Statistics and data
- Third-party validation
- Guarantees and risk reversals
- Customer logos
- Review scores

**Common proof gaps:**
- "Trusted by thousands" (which thousands?)
- "Industry-leading" (according to whom?)
- "Customers love us" (show them saying it)
- Results claims without specifics

**Process:**
1. Identify every claim that needs proof
2. Check if proof exists nearby
3. Flag unsupported assertions
4. Recommend adding proof or softening claims

**After this sweep:** Return to So What, Voice and Tone, then Clarity.

---

### Sweep 5: Specificity

**Focus:** Is the copy concrete enough to be compelling?

**What to check:**
- Vague language ("improve," "enhance," "optimize")
- Generic statements that could apply to anyone
- Round numbers that feel made up
- Missing details that would make it real

**Specificity upgrades:**

| Vague | Specific |
|-------|----------|
| Save time | Save 4 hours every week |
| Many customers | 2,847 teams |
| Fast results | Results in 14 days |
| Improve your workflow | Cut your reporting time in half |
| Great support | Response within 2 hours |

**Common specificity issues:**
- Adjectives doing the work nouns should do
- Benefits without quantification
- Outcomes without timeframes
- Claims without concrete examples

**Process:**
1. Highlight vague words and phrases
2. Ask "Can this be more specific?"
3. Add numbers, timeframes, or examples
4. Remove content that can't be made specific (it's probably filler)

**After this sweep:** Return to Prove It, So What, Voice and Tone, then Clarity.

---

### Sweep 6: Heightened Emotion

**Focus:** Does the copy make the reader feel something?

**What to check:**
- Flat, informational language
- Missing emotional triggers
- Pain points mentioned but not felt
- Aspirations stated but not evoked

**Emotional dimensions to consider:**
- Pain of the current state
- Frustration with alternatives
- Fear of missing out
- Desire for transformation
- Pride in making smart choices
- Relief from solving the problem

**Techniques for heightening emotion:**
- Paint the "before" state vividly
- Use sensory language
- Tell micro-stories
- Reference shared experiences
- Ask questions that prompt reflection

**Process:**
1. Read for emotional impact—does it move you?
2. Identify flat sections that should resonate
3. Add emotional texture while staying authentic
4. Ensure emotion serves the message (not manipulation)

**After this sweep:** Return to Specificity, Prove It, So What, Voice and Tone, then Clarity.

---

### Sweep 7: Zero Risk

**Focus:** Have we removed every barrier to action?

**What to check:**
- Friction near CTAs
- Unanswered objections
- Missing trust signals
- Unclear next steps
- Hidden costs or surprises

**Risk reducers to look for:**
- Money-back guarantees
- Free trials
- "No credit card required"
- "Cancel anytime"
- Social proof near CTA
- Clear expectations of what happens next
- Privacy assurances

**Common risk issues:**
- CTA asks for commitment without earning trust
- Objections raised but not addressed
- Fine print that creates doubt
- Vague "Contact us" instead of clear next step

**Process:**
1. Focus on sections near CTAs
2. List every reason someone might hesitate
3. Check if the copy addresses each concern
4. Add risk reversals or trust signals as needed

**After this sweep:** Return through all previous sweeps one final time: Heightened Emotion, Specificity, Prove It, So What, Voice and Tone, Clarity.

---

## Expert Panel Scoring

For high-stakes copy (landing pages, launch emails, sales pages), run a multi-persona review after the Seven Sweeps: 3–5 expert personas each score the copy 1–10 and name what to fix; revise and re-score until every persona gives 7+ and the panel averages 8+. Recommended panels per copy type and the scoring rubric are in [Expert Panel Scoring](references/expert-panel-scoring.md).

## Quick-Pass Editing Checks

Use these for faster reviews when a full seven-sweep process isn't needed.

### Word-Level Checks

**Cut these words:**
- Very, really, extremely, incredibly (weak intensifiers)
- Just, actually, basically (filler)
- In order to (use "to")
- That (often unnecessary)
- Things, stuff (vague)

**Replace these:**

| Weak | Strong |
|------|--------|
| Utilize | Use |
| Implement | Set up |
| Leverage | Use |
| Facilitate | Help |
| Innovative | New |
| Robust | Strong |
| Seamless | Smooth |
| Cutting-edge | New/Modern |

**Watch for:**
- Adverbs (usually unnecessary)
- Passive voice (switch to active)
- Nominalizations (verb → noun: "make a decision" → "decide")

### Sentence-Level Checks

- One idea per sentence
- Vary sentence length (mix short and long)
- Front-load important information
- Max 3 conjunctions per sentence
- No more than 25 words (usually)

### Paragraph-Level Checks

- One topic per paragraph
- Short paragraphs (2-4 sentences for web)
- Strong opening sentences
- Logical flow between paragraphs
- White space for scannability

---

## Copy Editing Checklist

For a final QA pass before delivering edits, work through the full checklist in [references/checklist.md](references/checklist.md) — covering all seven sweeps plus pre-start and final-check items.

---

## Common Copy Problems & Fixes

### Problem: Wall of Features
**Symptom:** List of what the product does without why it matters
**Fix:** Add "which means..." after each feature to bridge to benefits

### Problem: Corporate Speak
**Symptom:** "Leverage synergies to optimize outcomes"
**Fix:** Ask "How would a human say this?" and use those words

### Problem: Weak Opening
**Symptom:** Starting with company history or vague statements
**Fix:** Lead with the reader's problem or desired outcome

### Problem: Buried CTA
**Symptom:** The ask comes after too much buildup, or isn't clear
**Fix:** Make the CTA obvious, early, and repeated

### Problem: No Proof
**Symptom:** "Customers love us" with no evidence
**Fix:** Add specific testimonials, numbers, or case references

### Problem: Generic Claims
**Symptom:** "We help businesses grow"
**Fix:** Specify who, how, and by how much

### Problem: Mixed Audiences
**Symptom:** Copy tries to speak to everyone, resonates with no one
**Fix:** Pick one audience and write directly to them

### Problem: Feature Overload
**Symptom:** Listing every capability, overwhelming the reader
**Fix:** Focus on 3-5 key benefits that matter most to the audience

---

## Working with Copy Sweeps

When editing collaboratively:

1. **Run a sweep and present findings** - Show what you found, why it's an issue
2. **Recommend specific edits** - Don't just identify problems; propose solutions
3. **Request the updated copy** - Let the author make final decisions
4. **Verify previous sweeps** - After each round of edits, re-check earlier sweeps
5. **Repeat until clean** - Continue until a full sweep finds no new issues

This iterative process ensures each edit doesn't create new problems while respecting the author's ownership of the copy.

---

## References

- [Plain English Alternatives](references/plain-english-alternatives.md): Replace complex words with simpler alternatives
- [Content Refresh](references/content-refresh.md): Full checklist, refresh vs. rewrite matrix, and cadence guide
- [Copy Editing Checklist](references/checklist.md): Full QA checklist across all seven sweeps
- [Expert Panel Scoring](references/expert-panel-scoring.md): Recommended expert panels per copy type and the 1–10 scoring rubric

---

## Content Refresh Editing

Copy editing isn't just for new content. Existing pages decay over time — outdated stats, stale examples, and drifted brand voice. Use the content refresh framework when traffic is declining, data is stale, or the product has changed.

**For the full refresh checklist, refresh vs. rewrite decision matrix, and cadence guide**: See [references/content-refresh.md](references/content-refresh.md)

---

## Task-Specific Questions

1. What's the goal of this copy? (Awareness, conversion, retention)
2. What action should readers take?
3. Are there specific concerns or known issues?
4. What proof/evidence do you have available?
5. Is this new copy or a refresh of existing content?

---

## Related Skills

- **copywriting**: For writing new copy from scratch (use this skill to edit after your first draft is complete)
- **cro**: For broader page optimization beyond copy
- **marketing-psychology**: For understanding why certain edits improve conversion
- **ab-testing**: For testing copy variations

---

## When to Use Each Skill

| Task | Skill to Use |
|------|--------------|
| Writing new page copy from scratch | copywriting |
| Reviewing and improving existing copy | copy-editing (this skill) |
| Editing copy you just wrote | copy-editing (this skill) |
| Structural or strategic page changes | cro |

---

## Operator qatlami (Tyrion lokal bilimi)

> Bu bo'lim — Tyrion (Saloxiddin, O'zbekiston targetolog agentligi) uchun lokal moslashuv. Vendor metodika o'zgarishsiz.

### Qachon ishlatiladi (UZ triggerlari)
- "matnni yaxshila / tahrirla" · "zaif matn, kuchaytir" · "sweep qil" · "shu matnni ko'zdan kechir" · "eskirgan kreativni yangila"

### UZ amaliyot qoidalari (manbalardan)
1. Tahrir til segmentini saqlaydi: o'zbek-lotin/kirill/rus matnlari **alohida** yuritiladi, tahrirda tillar aralashmaydi (manba: `local\ozbekiston-konteksti.md` §3)
2. "Prove It" (Sweep 4) lokal talqini: "Trusted by" o'rniga tekshiriladigan dalil — real mijozlar soni, video-sharh skrinshoti, jonli telefon/manzil, portfolio; isbotsiz da'vo qoldirilmaydi, tekshirilmagan raqam qo'shilmaydi (manba: `local\ozbekiston-konteksti.md` §4; `memory.md` §2 qoida 1)
3. Refresh ishida bozor mavsumlari hisobga olinadi: Navro'z (21-mart), 1-sentabr (ta'lim/kiyim), dekabr (eng katta savdo oyi), Ramazon — eskirgan taklif/vaqt havolalari shu oynalarga mos yangilanadi (manba: `local\ozbekiston-konteksti.md` §6)
4. G'olib reklama matni tahrirlansa — g'olib mantiq **buzilmaydi**: faqat 2–3 yangi variatsiya qoidasi bilan ishlanadi; 6 variant/5 daqiqa protokoli (manba: `wiki/ad-iteration.md`)
5. Matn zaifligi = hook zaifligi bo'lishi mumkin: natija talab darajasida emas (mas. Link CTR < 1.5%) — kreativ/hook/0–5 soniyani yaxshilash, taklifni buzmaslik (manba: `wiki/more-better-new.md`)
6. Muammo matnda emas bo'lishi mumkin: CTR yaxshi-yu lid bo'lmasa — landing/offer/forma tekshiriladi (cro/offers ga o'tish); lid arzon-yu sotuv bo'lmasa — auditoriya/savollar (manba: `local\meta-playbook-uz.md` §4)
7. Natija qoidalari: tahrir yakuni `outputs\` ga fayl bo'lib yoziladi va 4 bosqichli standart bilan beriladi — Diagnostika → Edit → Linking → Strategik tavsiya + Checklist (manba: `memory.md` §2 qoida 2, 9)

### Meta policy eslatmasi
- Tahrir natijasida yangi da'vo (natija, chegirma, kafolat) paydo bo'lsa — Meta policy tekshiruvsiz tasdiqlanmaydi (manba: `memory.md` §2 qoida 5)

### Bog'liq lokal fayllar
- `local\ozbekiston-konteksti.md` — til segmentlari, ishonch dalillari, mavsumiylik (repo ildizi)
- `local\meta-playbook-uz.md` — metrikalar zanjiri: muammo qaysi bosqichda
- `local\wiki\kontent-formulalari.md` — hook oilalari (hook tahriri uchun)
- `wiki/ad-iteration.md` va `wiki/more-better-new.md` — vault (`wiki`): g'olibni buzmaslik qoidalari
- `memory.md` — natija/checklist qoidalari (repo ildizi)
