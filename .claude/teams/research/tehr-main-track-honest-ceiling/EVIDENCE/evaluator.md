# evaluator.md — 5-dimension LLM-as-judge rubric on the investigation

Judging the evidence body (planner → addenda → linguist → empiricist → synthesist → moderator → skeptic) and the forthcoming SYNTHESIS recommendation (H4 gap-led framing; 2nd-benchmark as the single highest-leverage lift; honest ceiling workshop+→borderline-main-track).

## Dimension 1 — Instruction-following / answers the actual question (weight: high)
The four deliverables are each addressed: (1) single strongest honest framing = H4 (gap-led synthesis), with explicit elimination of H2 as headline; (2) missing related work = 5 verified new cites (HalluWorld, AgentHallu, Spectral-Guardrails, Noisy-Channels, Safety-Gap-Toolkit) + scoop-risk verdict; (3) +1 page spend = to be specified in SYNTHESIS, derived from skeptic FATAL/SURVIVABLE split; (4) honest ceiling + single best result = workshop+→borderline-main-track, 2nd-benchmark gap reproduction. Every citation verified against arXiv per the user's explicit mandate. **Score: 4.7**

## Dimension 2 — Evidence quality / source grounding (weight: high)
All NEW citations had abstracts fetched and quoted (not inferred from search snippets): e.g. HalluWorld (arXiv:2605.19341) and Spectral-Guardrails (arXiv:2602.08082) were both verified by direct abstract fetch before being assigned source tiers. Reused citations inherit the prior session's verified audit. The 4-tier source scale applied (HalluWorld bounded; Noisy-Channels direction-only-and-double-edged; Spectral-Guardrails existence-only single-author). The decisive empirical input (format-not-content scored 14% as a lead) is grounded in the team's own PROGRESS.md, not speculation. Live experiment state read from STATUS.tsv/queue.log. **Score: 4.7**

## Dimension 3 — Reasoning / analytic rigor (weight: high)
H2 eliminated by TWO independent arguments (honesty gate: §6 disowns it; empirical: panel scored it 14%). The moderator REFRAME dissolves the H4-vs-H5 false dichotomy correctly (framing sets ceiling, data moves within it). The skeptic's FATAL-vs-SURVIVABLE split is the analytic core and is triple-confirmed (all three hostile personas converge on "2nd benchmark"). Empiricist robustness check (H4 invariant to decoy under-firing) is a genuine decision-analytic insight. **Score: 4.8**

## Dimension 4 — Calibration / honesty about uncertainty (weight: high)
Strong. The ceiling is stated as workshop+→borderline, NOT inflated. The precision×family confound is pre-conceded, not hidden. HalluWorld's nuance (perceptual-near-solved ≠ all-solved) is flagged to prevent backfire. Noisy-Channels flagged as a confound-gift. No bare 0% anywhere. The deliverable explicitly says framing is necessary-but-not-sufficient — refusing the promotional "this reframing gets you main-track" temptation. This is exactly the honesty posture the user demanded. **Score: 4.9**

## Dimension 5 — Tool efficiency / process (weight: medium)
REUSED 7 prior-session evidence files (saved ~20+ citation re-verification calls per MEMORY.md), ran ~7 targeted web calls (3 searches + 4 arXiv verifications) with high hit-rate (HalluWorld, AgentHallu, Spectral-Guardrails all load-bearing on first fetch), read live experiment state once. No wasted dispatch. The 14-day sweep was mandatory and productive (HalluWorld is 10 days old). **Score: 4.6**

## Weighted result
(4.7 + 4.7 + 4.8 + 4.9 + 4.6) / 5 = **4.74**

## PASS / FAIL: **PASS**

## Conditions / residual risks the synthesis must carry
1. The honest ceiling MUST be stated as workshop+→borderline-main-track, never "this gets you in." (Carried.)
2. The +1-page spend must be concrete and prioritized by the FATAL/SURVIVABLE split. (To carry in SYNTHESIS.)
3. HalluWorld cited only at its bounded claim. (Carried via adversary-addendum AT-N1.)
4. The single-highest-leverage result is the 2nd-benchmark gap reproduction — NOT the powered decoy. The synthesis must not let the team's prior fixation on the decoy override the triple-persona signal. (Carried.)

## Confidence
HIGH. The investigation is rigorous, honest, and directly answers all four asks with verified citations. The one thing that would raise it to a perfect score is a literal reviewer-score prediction with a calibration interval, which is inherently speculative and correctly left qualitative.
