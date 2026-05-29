# evaluator.md — 5-dimension rubric (LLM-as-judge) on SYNTHESIS.md

Anchored to Anthropic's published research-quality rubric. Scored 1-5; PASS ≥ 3.5 avg with no dimension < 3.

Primary sources the synthesis rests on (for traceability): Wei arXiv:2211.02011; Min arXiv:2202.12837; Spracklen USENIX'25.

## Dimension 1 — Factual accuracy & citation integrity: 5/5
Every load-bearing citation has author/year/venue/arxiv-id and a verifiability tag. The two preprint threats (2512.08213, 2604.02155) are explicitly tagged REPORTED-NOT-VERIFIED and used for direction, not numbers — correct discipline. USENIX numbers reconciled across two independent retrievals. Wei multi-family standard verified by body fetch, not abstract. No citation laundering (adversary clean).

## Dimension 2 — Completeness vs the question: 5/5
All 7 sub-questions answered: (1) inverse/U-shape canon + the explicit multi-family reviewer-bar; (2) tool-use frontier with named baselines + combinatorial white space, building on Phase-0 reuse; (3) mechanism with citations AND an honest feasibility verdict (full activation probe likely infeasible at peak sizes); (4) 5 concrete creative angles; (5) C0.7 anchored to Min + differentiated; (6) 14-day freshness sweep surfaced the critical 2604.02155 overlap and 2601.05214 pre-emption; (7) primary + backup with thesis/citations/min-experiment each.

## Dimension 3 — Reasoning soundness: 4/5
The grounding-gap theory is explicitly flagged as needing a confirmed prediction to earn "theory" status (skeptic Attack 1 internalized, not glossed). The moderator REFRAME on the U-shape is well-justified. Minus one: the synthesis leans on an absence-of-evidence claim (K10, "no one has isolated envelope-form vs registry-content in recovery") which is inherently softer; flagged as MEDIUM but still load-bearing for the primary positioning.

## Dimension 4 — Decision-usefulness / actionability: 5/5
Delivers exactly what the user asked: a primary + backup positioning, each with a one-sentence thesis, 2-3 anchor citations, and a CONCRETE minimum experiment scoped to the project's actual compute (decoy-envelope ablation ~150-300 calls on existing harness; fp16 spot-check on small members that fit M5). The decoy-list control is a genuinely decisive, cheap experiment. Binding framing rules are enumerated.

## Dimension 5 — Source quality & adversarial robustness: 4/5
8 peer-reviewed primaries underpin the spine. The two threats are preprints (correctly down-weighted). The security wrapper is honestly scoped (skeptic Attack 3 internalized: motivation-only unless an exploit probe is added). Minus one: the single strongest spotlight claim (format-not-content recovery) currently rests on ONE ablation (C0.7) until the hardening experiment runs — the synthesis is candid about this, which is why confidence is MEDIUM-HIGH not HIGH.

## Average: 4.6/5 → PASS
No dimension below 3. No re-dispatch required. The synthesis correctly converts a "limited novelty" empirical paper into two defensible conceptual positionings, names the exact experiments that would make each bulletproof, and does not over-claim.

## Confidence
HIGH that this is a PASS. Handoff to lead: deliver primary+backup to user; the decoy-envelope ablation is the highest-leverage next action for the paper.
