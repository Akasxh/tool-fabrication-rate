# Synthesis: patterns to fold into the `/spotlight-revision` skill

**Scope:** research-automation / paper-review repos — AI-Scientist (SakanaAI), AgentLaboratory
(SamuelSchmidgall), storm/Co-STORM (stanford-oval), CycleReviewer/DeepReviewer (zhu-minjun/Researcher),
paper-qa (Future-House). Plus the verified peer-review cluster (AgentReview, MARG, LLM-Rubric, etc.)
from `discover_automated_peer_revie.md` where it sharpens a pattern.

**Method:** read each `repo_*.md` (incl. adversarial-verification blocks) and the live
`~/.claude/skills/spotlight-revision/{SKILL.md,references/*}`. Recommendations are framed as
**deltas** against what the skill *already does*, not a from-scratch redesign — the skill's six-stage
gate structure, numbers ledger, parallel reviewer fan-out, and `paper-review-toolkit` wrapping are
already strong and several of these repos' core ideas (neg/pos reviewer priors, meta-reviewer, MARG
role split) are *already encoded* in `wrapped-primitives.md`'s 12-persona roster.

**Hard licensing constraint that governs HOW we fold anything in:** two of the five source repos are
NOT vendorable.
- **AI-Scientist** — `NOASSERTION` (RAIL-style "AI Scientist Source Code License v1.0"). §3.2(e)
  attaches a *machine-generated disclosure obligation to our ICML manuscript* if its code touches the
  paper; §3.3 propagates use-restrictions. **Study-only / reimplement-from-scratch. Copy zero code or
  prompt text.**
- **CycleReviewer/DeepReviewer** — `NOASSERTION` (CycleResearcher License, Mistral-AI-Research-derived):
  non-commercial, registration-gated, China jurisdiction, bars separating code from weights.
  **Study-only / clean-reimplement. Copy nothing.**
- **AgentLaboratory** (MIT), **storm** (MIT), **paper-qa** (Apache-2.0) — permissive; code *may* be
  copied with attribution, but all three are flat/heavy and the win is the *pattern*, not the code.

Bottom line: **every item below is a pattern reimplementation in our skill's orchestration layer.**
No source from any of the five is vendored. That keeps our manuscript and harness license-clean.

---

## Ranked plan

### P1 — Compile-gated section edits (Stage 4 + Stage 6 merge)
**Source:** AgentLaboratory `papersolver.py` (MIT, verified at symbol level in the adversarial block).
**Pattern:** `PaperReplace` (full rewrite) and `PaperEdit N M` (line-range edit) both route through
`compile_latex(...)`; **if LaTeX fails to compile, the edit is rejected and reverted** ("Paper was
reverted back to original state before edits"). Edits are atomic and only land if the build stays green.

**Why it's #1:** our skill currently treats compilation as a *terminal* Stage 6 gate. That means a
broken `\ref`, a mis-balanced environment, or a bad table edit introduced in Stage 4 isn't caught until
the very end, after many edits have stacked — exactly when bisecting the culprit is hardest. Folding
compile-validation *into the edit primitive* makes every Stage 4 `.tex` write self-checking.

**Concrete fold-in (SKILL.md, Stage 4 + output contract):**
- Add an operating principle: *"Every `.tex` edit is compile-gated. After showing the diff and writing
  it, run `tectonic --keep-intermediates --synctex=0` (or a fast `-X compile` no-op build); if the log
  gains an error, revert the edit and surface the failure as a finding, not a silent stack."*
- Wrap our existing `tectonic` primitive (already in `wrapped-primitives.md`) as a *per-edit* validator,
  not only the Stage 6 final build. Keep a `last_green.tex` snapshot per section so revert is O(1).
- This is a reimplementation of AgentLaboratory's idea against *our* tectonic primitive — no code copied.

### P2 — Citation-grounding as a hard gate: every claim backed by a retrieved source (Stage 2 ↔ Stage 4)
**Source:** paper-qa (Apache-2.0) "paper_search → gather_evidence → generate-with-inline-citations +
LLM re-ranking of evidence (RCS)"; reinforced by AI-Scientist's Semantic-Scholar novelty-check step.
**Pattern:** an answer/claim is only emitted once supporting evidence chunks are retrieved, scored, and
re-ranked; citations are inline and traceable to a source the agent actually fetched — not produced
from parametric memory.

**Why it's #2:** our Stage 2 already *verifies* each existing `\cite` against arXiv/venue (good, and
better than paper-qa for the "does this citation exist + is it characterized right" axis). What it does
NOT do is the inverse direction: **for each load-bearing claim in our related-work / positioning prose,
require an attached verified source before the claim is allowed to stand.** That's paper-qa's
contribution — evidence-first generation. For a TEHR paper whose related-work spans BFCL/tau-bench
lineage plus the tool-hallucination and automated-review literature, an unsourced comparative claim
("prior work does not measure per-call tool-existence") is a reviewer magnet.

**Concrete fold-in (SKILL.md, Stage 2 step 3 + Stage 4 correctness):**
- Add a "claim ledger" sibling to the numbers ledger: `claim text | location | backing source (verified
  URL) | status`. A comparative or prior-art claim with no backing source is flagged like a stale number.
- Reuse our `20-ml-paper-writing` programmatic-fetch engine (already wrapped) for the retrieval; layer
  paper-qa's *re-ranking* idea: when multiple candidate sources exist for a claim, score relevance and
  cite the strongest, rather than the first hit. Reimplemented, not vendored (Apache→Apache would *allow*
  vendoring, but the win is the workflow, and our fetch engine already exists).
- Cross-link to the verified `discover_automated_peer_revie.md` pick **ReviewGrounder** (ACL'26,
  rubric-guided *tool-integrated* reviewer that grounds critiques in retrieved prior work) as the
  conceptual analogue and the cleanest mirror of our own RVR "re-prompt-with-registry" loop — note in
  the skill that this grounding pass is the paper-side echo of the paper's own RVR intervention.
  (ReviewGrounder has no LICENSE file → design reference only, do not vendor.)

### P3 — Calibrated, reflection-refined rubric scoring with self-consistency (Stage 5)
**Source:** AI-Scientist `perform_review.py` (study-only, NOASSERTION) — `num_reviews_ensemble`
score averaging + `num_reflections` reflection rounds + `get_review_fewshot_examples` for calibration;
CycleReviewer/DeepReviewer (study-only, NOASSERTION) — per-criterion ratings → `avg_rating` →
binary `paper_decision`, and DeepReviewer's Fast/Standard/Best multi-perspective + **self-verification**
modes. Sharpened by `discover_automated_peer_revie.md` #4 **microsoft/LLM-Rubric** (MIT) — calibrated
*distributions* per rubric question + a calibration network, instead of raw scalar scores.

**Why it's #3:** Stage 5 currently collects each judge's "acceptance probability + single killing
objection" and converges on whether a new killing objection survives rebuttal. That's qualitative.
These repos add three quantitative upgrades the skill lacks:
1. **Few-shot anchoring** so persona scores are calibrated to a known scale (AI-Scientist
   `get_review_fewshot_examples`) — without anchors, LLM reviewer scores drift and our convergence
   signal is noisier than it needs to be (Sakana's own analysis flags reviewer leniency bias).
2. **Self-consistency / reflection** — run a persona's scoring more than once (or a reflection pass)
   and reconcile, rather than trusting a single sample (AI-Scientist `num_reflections` +
   `num_reviews_ensemble`; DeepReviewer self-verification).
3. **Calibrated rubric output** — LLM-Rubric's per-question distribution + calibration beats a single
   scalar for deciding convergence.

**Concrete fold-in (SKILL.md Stage 5 + pipeline-playbook.md):**
- Give each persona a small, *project-local* few-shot anchor set (2–3 example findings at known
  severities) so scores are comparable round-to-round. Reimplement the anchoring idea; do not copy
  AI-Scientist's example text (license).
- Add an optional `self_consistency_k` (default 1, bump to 3 for the final convergence round): sample
  a persona's verdict k times, take the modal killing objection + median acceptance prob. This is the
  reflection/ensemble pattern, reimplemented over our existing parallel-dispatch primitive.
- Record per-criterion scores (not just acceptance prob) in `review_synthesis_<iter>.md`, optionally as
  a confidence band per criterion (LLM-Rubric idea). MIT-licensed LLM-Rubric *could* be vendored, but
  the calibrated-distribution concept is light enough to reimplement.

### P4 — Coverage-gap "Moderator" persona: surface under-discussed evidence (Stage 5 roster)
**Source:** storm / **Co-STORM** (MIT) — the **Moderator** role injects thought-provoking questions
built from *under-used retrieved information*, and the Expert/perspective-guided **question-asking**
pattern (generate sharp questions per perspective, not just answers).
**Pattern:** a reviewer that finds what the draft *omits* (claims/evidence the authors under-discuss,
reviewer objections not pre-empted), complementing attackers that critique what's present.

**Why it's #4:** our 12-persona roster (`wrapped-primitives.md`) is heavy on *attackers*
(hostile_statistician, adversarial_reviewer, contamination_researcher) and *advocates*. None of them is
a dedicated **coverage-gap finder**. For a TEHR paper, the dangerous omissions are predictable: a
Qwen3-curve point not discussed, an RVR failure mode not pre-empted, a model family a reviewer expects
but we didn't run. A Moderator persona that asks "what perspective is under-represented here?" catches
these before a real reviewer does.

**Concrete fold-in (`references/wrapped-primitives.md` roster + SKILL.md Stage 5 Round A):**
- Add persona **`13_coverage_moderator`** (Co-STORM-derived): inputs the numbers ledger + claim ledger
  + draft; outputs the top-k results/claims the draft *under-discusses* and the reviewer perspectives
  (measurement-validity, baseline-fairness, cross-family generalization) not yet addressed. Phrase its
  output as *questions* (Co-STORM's perspective-guided question-asking), each mapping to either a
  rebuttal or a Stage 3 experiment.
- Pattern only, zero code/dep — Co-STORM's value is the role design; its pinned-old-dspy dependency
  (`dspy_ai==2.4.9` + langchain + qdrant, per the verification block) must NOT be pulled in.
- Cross-reference verified `discover_automated_peer_revie.md` #2 **AgentReview** (Apache-2.0,
  trait-conditioned reviewer/AC roles) and #3 **MARG** (Apache-2.0, specialized experiments/clarity/
  impact agents over full-text) — both are permissive and could *strengthen* the existing MARG-derived
  personas (03/04/05) and the AC (09) with explicit latent-trait conditioning.

### P5 — Resumable, value-ordered experiment iteration with an explicit solver loop (Stage 3)
**Source:** AgentLaboratory `mlesolver.py` (MIT) — iterative ML-engineering code writer/runner that
proposes → runs → reads result → revises; AI-Scientist `perform_experiments.py` (study-only) —
template-driven experiment execution with novelty-gated idea generation.
**Pattern:** an experiment is not a one-shot command but a *solve loop*: run, capture artifact, compare
to the expected artifact, and either accept or re-propose — with iteration state persisted.

**Why it's #5:** Stage 3 already emits a *queue* (`id | objection killed | command | expected artifact
| done?`) ordered by (severity × cheapness), which is good and already more disciplined than
AgentLaboratory's flat solver. The missing piece is the **inner solve loop per queue entry**: when a
queued experiment's artifact doesn't match expectation (a TEHR re-run comes back with a different N, an
RVR ablation crashes on a model family), the skill should iterate on *that entry* rather than marking it
done or silently dropping it. AgentLaboratory's mlesolver is the reference for that accept/re-propose
inner loop; AI-Scientist's novelty-check is the reference for not queueing an experiment that doesn't
actually kill a distinct objection.

**Concrete fold-in (SKILL.md Stage 3 + pipeline-playbook.md):**
- Extend each queue entry with `attempts | last_artifact | expected_artifact | accept_criterion`. On
  mismatch, re-propose (adjust command/params) up to a small cap, then escalate to the user — mirroring
  the existing Stage 5 "if the same objection recurs twice, escalate as a decision, not a fix" rule.
- Keep this firmly inside the *user-controlled compute gate* the skill already enforces; the solver loop
  proposes, the user approves heavy runs. Our harness (`harness/bench_loaders/*.py`) is the executor;
  AgentLaboratory's solver is study-only inspiration (and its backend caps at Claude-3.5 + no MLX, so
  none of its execution code is usable for us anyway — confirmed in the verification block).

---

## Already-covered (do NOT re-add — present in the skill today)
- **Harsh/lenient reviewer priors** (AI-Scientist `reviewer_system_prompt_neg`/`_pos`) → already the
  `02_adversarial_reviewer` vs `06/07/08` advocate split, run as Round A (reject) vs Round B (accept).
- **Meta-reviewer / Area-Chair aggregation** (AI-Scientist `get_meta_review`; CycleReviewer
  `paper_decision`; AgentReview AC role) → already `09_brutally_honest_AC` as Round C.
- **MARG specialized reviewers** (experiments/clarity/impact) → already personas `03/04/05`.
- **Multi-persona ensemble + merge** → already the parallel-dispatch fan-out (cap ~8) in Stage 5.
- **Structured NeurIPS rubric** (Soundness/Presentation/Contribution/Overall/Confidence) → already the
  persona output contract; P3 only *calibrates* it, doesn't introduce it.

## Net additions, in priority order
1. **P1 Compile-gated edits** — wrap tectonic as a per-edit validator with auto-revert (AgentLaboratory, MIT).
2. **P2 Claim-grounding gate** — evidence-backed claim ledger, source re-ranking (paper-qa, Apache-2.0; ReviewGrounder as design echo of RVR).
3. **P3 Calibrated rubric + self-consistency** — few-shot anchors, reflection/ensemble, per-criterion bands (AI-Scientist + CycleReviewer study-only; LLM-Rubric MIT).
4. **P4 `13_coverage_moderator` persona** — under-discussed-evidence finder via perspective question-asking (Co-STORM, MIT; AgentReview/MARG to enrich existing roles).
5. **P5 Per-entry experiment solve loop** — resumable accept/re-propose with novelty gating (AgentLaboratory mlesolver + AI-Scientist novelty-check, both study-only for execution).

**Licensing one-liner for the skill's notes:** all five additions are reimplementations in our
orchestration layer. Vendorable sources (AgentLaboratory MIT, storm MIT, paper-qa Apache-2.0,
LLM-Rubric/AgentReview/MARG permissive) are still reimplemented because the value is the pattern and our
primitives already exist. Non-vendorable sources (AI-Scientist NOASSERTION, CycleReviewer NOASSERTION)
are strictly study-only — copying their code/prompt text would attach AI-Scientist's §3.2(e) manuscript
disclaimer to our ICML paper and CycleReviewer's non-commercial/registration terms to our harness.
