# AI-detection scrubbing — banned words, tools, recipes

The single most actionable artifact for polishing LLM-edited papers.

## Banned-word list (consolidated; rewrite, do not auto-replace)

**Verbs:** delve, leverage(s), foster, garner, underscore, showcase, navigate,
unlock, harness, boast(s), align, emphasize, illuminate, embark.

**Adjectives:** intricate, nuanced, multifaceted, pivotal, crucial, profound,
robust, comprehensive, seamless, vibrant, meticulous, invaluable, noteworthy,
paramount.

**Nouns:** tapestry, landscape, realm, interplay, intricacies, methodologies,
testament, cornerstone, paradigm, ecosystem (when metaphorical).

**Connectors:** Moreover, Furthermore, Additionally, In essence,
In conclusion, It is important to note, It is worth noting.

**Constructions:** "not just X, but Y"; "stands as"; "plays a (pivotal/key)
role"; "in the ever-evolving"; "a testament to"; "navigating the complexities of";
"shedding light on"; rule-of-three adjective stacks.

**Punctuation tells:** em-dash (—), en-dash (–) used for prose, curly quotes,
Title Case Headings, bolded inline lemmas in lists, U+200B / U+FEFF invisibles.

## One-liner punctuation pass (sed)

```bash
# Strip em/en dashes in prose, smart quotes, invisibles
sed -i '' $'s/—/--/g; s/–/-/g; s/‘/\x27/g; s/’/\x27/g; s/“/"/g; s/”/"/g; s/​//g; s/﻿//g' paper.tex
```

## Tools

### Detector-bypass / humanizer
- **Adversarial-Paraphrasing** (NeurIPS 2025; chengez/Adversarial-Paraphrasing).
  Apache-2.0. Beats neural, watermark, and zero-shot detectors
  (avg 87.88% T@1%F drop). https://github.com/chengez/Adversarial-Paraphrasing
- **Humanize-AI** (OrbitWebTools/Humanize-AI). Client-side JS PWA;
  word replacement + sentence shuffling. Source-available.
- **berenslab/llm-excess-vocab** — score your draft against the LLM-marker
  frequency list from Kobak et al.

### Em-dash / smart-quote scrubbers
- GPT Cleanup em-dash replacer — https://www.gptcleanup.com/em-dash-replacer
- Em Dash Destroyer — https://brighterwebsites.com.au/blog/em-dash-destroyer/
- Leap AI text formatter — https://www.tryleap.ai/tools/ai-text-formatter
- Originality.ai invisible-text detector

### Style guidance
- **Wikipedia: Signs of AI writing** —
  https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing — best free checklist
- **Kobak et al. 2024 — Delving into ChatGPT usage…** arXiv:2406.07016
- **Reinhart et al., PNAS 2025 — Do LLMs write like humans?** Flags noun-heavy
  density, present-participial clauses, nominalizations, passive voice
- **ACL 2025 Findings — implicit author style**

## 30-minute pipeline

1. `sed` punctuation pass (em-dash, smart quotes, invisibles)
2. Grep banned-word list above; manually rewrite each hit (synonyms are
   ALSO tells, do not auto-replace)
3. Run `llm-excess-vocab` scorer; iterate until top words are
   domain-specific, not stylistic
4. Burstiness pass: read aloud, shorten one sentence per paragraph
   to ≤8 words, lengthen another to ≥25
5. Strip Moreover / Furthermore / Additionally sentence starters;
   convert nominalizations ("the implementation of X") to verbs
   ("we implemented X")
6. Optional: Adversarial-Paraphrasing on suspect prose blocks only
   (poor with citations + math)
