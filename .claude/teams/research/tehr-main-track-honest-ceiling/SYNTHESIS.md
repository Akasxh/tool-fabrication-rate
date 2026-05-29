# SYNTHESIS — Strongest defensible main-track framing for the TEHR/RVR paper

Full user-facing deliverable: `/Users/cero/Desktop/PROJECTS/icml/research/POSITIONING_v2.md`.

## Answer
Adopt a **gap-led synthesis** framing: HEADLINE = the per-call commercial-vs-open-weight tool-existence reliability gap (frontier APIs ≤0.14% floor vs open-weight up to 1.87%); INSTRUMENT = per-call TFR (the reason the gap is visible where composite scores hide it); FIX = RVR (training-free, 14/14, tier-conditional); MECHANISM = the non-monotone curve + format-not-content, both carried at the paper's own hedged level as SUPPORTING. Reject "format-not-content (once powered)" as the headline on TWO grounds: §6 disowns it ("absence of evidence, not equivalence") and the team's own panel already scored that lead 14% vs 18% bounded-honest. Frame the gap as a measured phenomenon, never a causal weights-claim (precision×serving stack co-varies). The honest ceiling AS-IS is workshop-strong→borderline-main-track-weak-reject; framing raises the ceiling by single-digit points but the BINDING constraint is breadth. The single highest-leverage result — named independently by all three hostile personas — is a **2nd benchmark with a non-zero base that reproduces the gap** (BFCL single-turn irrelevance is on-disk today; τ-bench higher-value/higher-effort). NOT the powered decoy (it only upgrades a supporting claim).

## Confidence
MEDIUM-HIGH. All five gates closed: synthesist (claim matrix), moderator (REFRAME on H4-vs-H5), skeptic (three hostile personas, FATAL/SURVIVABLE split), adversary-addendum (new-cite corpus audit), evaluator (PASS 4.74/5). Not HIGH because the ceiling is qualitative and the highest-leverage result is named-but-not-landed.

## Key evidence
- Framing honesty gate: §6 disowns format-not-content; gap uses the paper's own "open-vs-closed split" language. `EVIDENCE/linguist.md`.
- Decisive empirical input: format-not-content lead scored 14% vs 18% on the team's panel. `EVIDENCE/empiricist.md` (from PROGRESS.md).
- New verified related work: HalluWorld (arXiv:2605.19341), AgentHallu (2601.06818), Spectral-Guardrails (2602.08082); scoop-risk = cell unoccupied. `EVIDENCE/historian-addendum.md`, `EVIDENCE/web-miner-addendum.md`.
- Triple-persona convergence on "2nd benchmark" as the single cure. `EVIDENCE/skeptic.md`.
- Highest-leverage ranking (2nd benchmark > 2nd family > fp16 > decoy). `EVIDENCE/empiricist.md`, `EVIDENCE/moderator.md`.

## Counter-evidence
- H5: the ~20% may be a pure scope verdict no framing fixes (moderator REFRAME: framing necessary, not sufficient — both true).
- HalluWorld nuance: "near-solved for frontier" is one hallucination class, not all (adversary-addendum AT-N1) — cite bounded or it backfires.
- Noisy-Channels is a confound-gift (AT-N2): omit or use once-with-quant-caveat.

## Moderator verdicts
- C1 (framing-sufficient vs breadth-binding): **REFRAME → COMPLEMENTARITY**. H4 framing + H5 ceiling diagnosis; 2nd-benchmark gap reproduction is the lift.
- C2 (security lead vs motivation): **B_WINS** — keep security as honest motivation absent a collision probe.

## Evaluator scores
4.74/5 (instruction 4.7, evidence 4.7, reasoning 4.8, calibration 4.9, efficiency 4.6). PASS. See `EVIDENCE/evaluator.md`.

## Open questions
- Does the gap reproduce on a 2nd benchmark? (The ceiling-setter; named-but-not-landed.)
- Does the powered 14B decoy produce events? (Upgrades a supporting note only.)
- Does the hump survive fp16? (Protects the supporting curve.)
