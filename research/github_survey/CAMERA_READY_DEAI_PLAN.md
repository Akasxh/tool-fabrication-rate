# Camera-Ready De-AI Plan — make the paper read as human-written

**Paper:** SCALE / TEHR — "Tool-Existence Hallucination Is Tier-Dependent and Intra-Family
Non-Monotonic on BFCL Multi-Turn" (`/Users/cero/Desktop/PROJECTS/icml/paper/`).
**Trigger:** authors flagged GPTZero concerns for the ICML camera-ready.
**Disclosure reality:** §8 (`08_llm_disclosure.tex`) already states the text + harness were
"drafted with LLM-based assistance under author supervision." ICML allows LLM-assisted
writing. So the goal is **NOT to hide assistance** (that disclosure stays). The goal is: the
*prose itself* should not trip a reviewer's reflexive "this reads like raw ChatGPT" reaction,
because a low-effort flag taints an otherwise strong empirical paper. De-AI-ing here = editing
our own authored claims into a consistent human academic register, then self-QA'ing against
open detectors before submission. This stays defensible (we are editing prose we wrote and whose
numbers are all code-reproducible), not laundering fabricated content.

---

## TL;DR — where the paper actually stands

I scanned all nine `.tex` sections plus the abstract. **The draft is already aggressively
de-AI'd** and far cleaner than typical LLM output:

- **Zero Unicode em dashes (—)** in any section. The author already used `,` / `.` / `()`.
- **Zero Tier-1 AI vocabulary** (no delve/leverage/robust/comprehensive/pivotal/underscore/
  landscape/tapestry/seamless/paradigm/cutting-edge in body prose).
- **No copula avoidance** (no "serves as / boasts / plays a key role").
- **Varied rhythm already present** — short punchy sentences ("We don't think it is.", "Qwen3
  isn't.", "Six points isn't a curve.", "The bump in the middle is what surprised us.") mixed
  with long ones. First-person voice and stated reactions are present. This is the single
  hardest signal to fake and it's already good.

So this is a **finishing pass, not a rewrite.** The work is (1) kill a small set of *residual*
AI-isms I found by exact line, (2) run the open detectors as a gate, (3) wire the two existing
skills into the `spotlight-revision` flow so the QA is repeatable. Do **not** over-edit — the
voice is the asset; sanding it smooth would *raise* the AI score (see avoid-ai-writing
"Over-polishing", SKILL.md §Rhythm).

---

## Part 1 — Concrete checklist mapped to THIS paper's residual AI-isms

Each item cites the file + line and the skill rule it maps to. Severity: P0 = a detector/reviewer
tell, P1 = obvious smell, P2 = polish.

### P0 — the only hard detector tells found

1. **Three LaTeX em dashes (`---`) in Related Work** — they render as em dashes (—) in the PDF
   GPTZero ingests, even though the source has no Unicode `—`.
   - `02_related_work.tex:43` `phenomenon directly --- "tool type hallucination,"`
   - `02_related_work.tex:44` `absent from the available set --- but their fix is a`
   - `02_related_work.tex:114` `a different axis --- chain-of-thought \emph{budget}`
   - **Rule:** avoid-ai-writing "Em dashes (— and --)"; humanizer_academic Pattern 13 (zero
     tolerance). **Fix:** lines 43–44 are one parenthetical — convert to commas or parentheses:
     `name the phenomenon directly ("tool type hallucination," where the model fabricates a tool
     absent from the available set), but their fix is...`. Line 114 is a clause break — use a
     comma or recast: `Our axis is orthogonal to both: model scale at fixed (disabled) thinking,`
     already follows, so make 114 `effect on a different axis, chain-of-thought budget at fixed
     scale`. **Target: zero `---` and zero `—` in the compiled PDF.** Verify with the grep gate below.

### P1 — light residual smells (fix, but don't manufacture new prose)

2. **"via" used 3x where "through/by" is more natural academic register.**
   - `01_introduction.tex:12` — already in a citation context; acceptable, leave.
   - `02_related_work.tex:40` `tracks the resulting fabrication via a per-query Correct
     Selection Rate` → "through a per-query Correct Selection Rate."
   - `08_llm_disclosure.tex:6` `via Anthropic's tool-use API` → leave (idiomatic API usage).
   - **Rule:** humanizer_academic Pattern 21 ("via" → "through"). Only swap the related-work one;
     the API ones are standard.

3. **"yields" as a result verb** — `05_results.tex:225`.
   - **Rule:** humanizer_academic Pattern 25. **Fix:** if it describes an analytic output
     ("yields p="), swap to "gives" / "produces". Check context first — if it's "the test yields
     p=7.1e-5", "gives" reads more human. (Note the intro already uses "gives" at
     `01_introduction.tex:57`, so this aligns the paper internally.)

4. **"non-locative where"** — `02_related_work.tex:116` `function calling, where the
   non-monotonicity appears`. Actually borderline-legitimate (defines a condition), but the
   abstract/intro elsewhere recast these. **Rule:** humanizer_academic Pattern 24. **Fix
   (optional):** "function calling; the non-monotonicity appears across the Qwen3 size ladder…"
   Low priority — this one reads fine; flag only if a detector lights up the sentence.

5. **Rule-of-three audit** — four `X, Y, and Z` triads exist (`02:126` relevance/argument/timing;
   `03:11` model/benchmark/condition; `07:5` latency/abstention/pass; `08:12`
   drafting/code/statistics). **Rule:** avoid-ai-writing "Compulsive rule of three" (max ~1 per
   piece) + humanizer_academic Pattern 10. **Assessment: these are all *enumerations of real
   things* (actual error types, actual experimental axes), not rhetorical padding — KEEP them.**
   This is exactly the false-positive the skill warns about. Do not break a true 3-item list to
   dodge a pattern matcher. Document this decision so a reviewer-persona objection is pre-empted.

### P2 — polish, only if a detector flags the specific sentence

6. **Abstract rhetorical-question opener** — `main.tex:66` "Tool-name hallucination is a known
   failure mode. Who actually does it, and how often?" **Rule:** avoid-ai-writing "Rhetorical
   question openers." **Assessment: KEEP.** A single earned rhetorical question that the paper
   then answers with hard numbers is a human move, not an AI tell; it's also the paper's hook.
   Flag only if GPTZero specifically highlights the abstract (check `gptzero_abstract_*.png`).

7. **"surprised us" / "stings" / emotional claims** — `01:8` "what stings is that", `01:60`
   "this surprised us", abstract "is what surprised us". **Rule:** avoid-ai-writing "Emotional
   flatline" warns about *unearned* claimed emotions. **Assessment: KEEP all.** These are earned
   (the data genuinely is non-monotonic/surprising) and they're the human-voice signal that keeps
   the detector score down. Removing them would hurt, not help.

8. **"Additionally / Moreover / Furthermore"** — none found in body prose. Nothing to do.
   (Confirmed by grep.) This is already handled.

**Net edit budget: ~5 lines.** Items 1–3 are the real work. Everything else is "verify and leave."

---

## Part 2 — Detector self-QA gate (the actual GPTZero-concern answer)

GPTZero is closed and rate-limited; relying on it alone is fragile. Build a **local, reproducible
multi-detector gate** from the vetted repos in `discover_AI_writing_detection.md`, run it on the
*compiled-PDF text* (what reviewers' tools see), and treat a high score as a finding to localize,
not a mandate to blanket-rewrite.

**Vetted, permissively-licensed detectors to run (all from the survey, none requiring an API):**
- **Binoculars** (BSD-3, ICML'24) — `discover_AI_writing_detection.md` #1. Primary zero-shot
  gate; strongest "will a reviewer's tool flag us" proxy. >90% TPR @ 0.01% FPR.
- **Fast-DetectGPT** (MIT, ICLR'24) — survey #2. Second independent detector; MIT-safe to vendor
  into the harness as a `bench_loaders`-style detector loader.
- **DetectGPT** (MIT, ICML'23) — survey #3. Lineage baseline; if our text is clean across
  DetectGPT → Fast-DetectGPT → Binoculars, that's a robust "reads human" signal.

Optional: **MGTBench / IMGTB** (both MIT, survey honorable mentions) bundle all three behind one
runner — use if we want a single command instead of three vendored repos.

**Do NOT use as a gate, and never on this paper:** `lynote-ai/humanize-text` and the
"bypass-detector" tools (survey #6, StealthHumanizer). The survey's own caveat applies: these are
for editing aids on *our* prose at most, and adversarially gaming a detector on a paper we'll
defend in rebuttal is the wrong risk. The detectors above are diagnostics; the *skills* are the
editor.

**Gate procedure (add as a `spotlight-revision` Stage-6 sub-check):**
1. Extract text from `main.pdf` (`pdftotext`) per section — score sections separately so a hot
   spot is localizable (the abstract/intro are what GPTZero screenshots show being checked:
   `gptzero_abstract_check.png`, `gptzero_s2.png`).
2. Run Binoculars + Fast-DetectGPT on each section's extracted text.
3. For any section above the detector's human/AI threshold, **localize** the offending sentences,
   apply `humanizer_academic` (academic register) then `avoid-ai-writing` in `detect` mode to
   confirm, edit only those sentences, recompile, re-score.
4. Stop when sections are below threshold **without** the rhythm flattening (re-read for voice —
   if the edits made it more uniform, you over-corrected; restore variance).

**Bash gate (zero-em-dash + AI-vocab, run before each recompile):**
```
cd paper/sections
grep -n -- '---' *.tex            # must return nothing (item 1)
grep -nc '—' *.tex                # every file must be 0
grep -noiE 'delve|leverage|robust|comprehensive|seamless|pivotal|underscore|crucial|nuanced|intricate|landscape|tapestry|paradigm|cutting-edge|furthermore|moreover' *.tex   # must be empty
```

---

## Part 3 — Wire the two skills + a persona into spotlight-revision (repeatable)

The two skills already exist; the gap is they're not *invoked as a gate* in the revision flow.
Fold them in as **deltas** to `/Users/cero/.claude/skills/spotlight-revision/`, consistent with
the deltas-not-rewrite framing in `synth_skill-enhancements.md`.

- **Pick the right skill per context.** Use **`humanizer_academic`** as the primary editor — it's
  built for papers (restores classical academic terms via Pattern 26: "percentage of", "purpose
  of", "was measured", nominalized hypotheses; preserves legitimate transitions like "Notably,"
  "Prior studies have shown"). Use **`avoid-ai-writing`** in **`detect` mode** with the
  **`technical-blog`** profile as the *auditor* (its technical-word exceptions stop it from
  flagging legitimate ML terms like "robust"/"comprehensive"). Running avoid-ai-writing in
  rewrite mode on a paper risks blog-voice edits, so detect-only here.
- **Add a Stage-6 "register & detector" sub-gate** to `spotlight-revision/SKILL.md`: after the
  compile gate, (a) run the Part-2 bash gate, (b) run `humanizer_academic` over any section a
  reviewer-persona flagged, (c) run `avoid-ai-writing --detect --context technical-blog` to
  confirm no new tells, (d) run Binoculars/Fast-DetectGPT on the recompiled PDF text.
- **Add a `14_ai_register_reviewer` persona** to `references/wrapped-primitives.md` (mirrors the
  proposed `13_coverage_moderator` in `synth_skill-enhancements.md` P4): inputs the compiled-PDF
  text + detector scores; outputs the top sentences a reviewer would call "LLM-sounding" and the
  *specific* skill rule each maps to — but is explicitly instructed to **respect the
  false-positive carve-outs** below so it doesn't demand breaking true enumerations or earned
  voice.
- **Licensing:** detectors are vendor-or-import as deps (Binoculars BSD-3, Fast-DetectGPT/
  DetectGPT MIT — clean). The skills are already local. Nothing here touches the manuscript's
  license posture (consistent with `synth_skill-enhancements.md` licensing one-liner).

---

## Part 4 — False-positive carve-outs (do NOT "fix" these)

The biggest camera-ready risk is **over-de-AI-ing** a paper that's already clean, which (per
avoid-ai-writing SKILL.md "Over-polishing", line ~336) pushes text *toward* the AI statistical
profile. Bake these into the persona so it stops nagging:

1. **Real enumerations stay** — error-type / experimental-axis triads (items 5 above) are content,
   not rule-of-three padding.
2. **Earned voice stays** — "what stings", "this surprised us", "The bump in the middle is what
   surprised us", "We don't think it is." These short, opinionated sentences are the human signal.
3. **The abstract's opening question stays** — answered immediately with numbers.
4. **Legitimate academic transitions stay** — "Notably," "In contrast," "Prior work" with
   citations are *standard* (humanizer_academic preserve-list); they are not AI tells in a paper.
5. **Technical terms stay** — keep ML/stats vocabulary (Clopper–Pearson, Fisher's exact,
   non-monotonic, etc.); avoid-ai-writing's technical-blog profile already exempts these.
6. **The §8 LLM-assistance disclosure stays verbatim** — ICML requires it; do not soften it to
   make the paper "look more human." Honesty here is the defensible posture.

---

## Execution order (deadline-aware)

1. Apply the 3 em-dash fixes (item 1) + the `via`/`yields` swaps (items 2–3). ~5 lines, 10 min.
2. Run the Part-2 bash gate; confirm zero `---`, zero `—`, empty vocab grep. Recompile `main.pdf`.
3. Vendor Binoculars + Fast-DetectGPT (or MGTBench); `pdftotext` the recompiled PDF per section;
   score. The abstract/intro/related-work are the priority (that's what the GPTZero screenshots
   were checking).
4. For any hot section: localize with the persona, edit with `humanizer_academic`, confirm with
   `avoid-ai-writing --detect`, recompile, re-score. Respect the Part-4 carve-outs.
5. Fold the Stage-6 sub-gate + `14_ai_register_reviewer` persona into `spotlight-revision` so
   the QA is one command on the next revision.

**Bottom line:** the prose is already in good shape; the camera-ready de-AI task is a 5-line
edit (em dashes + two verbs) plus standing up a 2–3 detector self-QA gate, then resisting the
urge to over-edit the voice that's keeping the score low.
