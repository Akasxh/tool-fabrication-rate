# Revision Spec — TEHR paper → SCALE camera-ready + main-track-spotlight foundation

Branch `camera-ready-spotlight`. Restore point `b6ca532`. Authored 2026-05-29.
Authoritative source on current paper state: the live-`.tex` inventory (not the stale PHASE0 self-reviews).

## 1. Strategic pivot (the spotlight bet)

The accepted paper leads with **a metric (TEHR)** and **a fix (RVR)** — both have close precedents
(Xu et al. 2412.04141 already names "tool type hallucination"; "retry with the tool list" reads as
trivial). That is *why* all three reviewers said "limited novelty / trivial intervention."

**New lead: "format-not-content recovery."** The genuinely novel, counterintuitive result is the
C0.7 ablation — a structured `tool_not_found` envelope *without* the registry list already drives
hallucination to zero. Reframed: reactive error-recovery in tool-using agents is a **re-grounding /
format** phenomenon, not an information-delivery one. This is a mechanism-of-the-fix claim, strictly
stronger than the classic format-over-content ICL result (Min et al., EMNLP'22), in a new regime.

- **Decisive experiment to convert "suggested" → "proven": C0.8 decoy condition** — structured
  envelope listing a *wrong* tool set. If a decoy list still recovers, "registry content is
  decorative" is demonstrated, not inferred.
- **Demote the non-monotonic curve** from headline to "a predicted signature of a grounding-gap."
  A single 4-bit family is below the multi-family bar Wei et al. (2211.02011) set for U-shaped-scaling
  claims. Control it with the quantization spot-check before using any U-shape language.

Backup framing (if C0.8 fails to recover, i.e. content DOES matter): "the grounding-gap" — generative
tool-name prior matures faster than registry-grounding control → curve + distractor-shift + frontier-zero.
Falsifiable prediction testable on existing data: RVR gain should be largest at the 14B peak, ~zero at endpoints.

## 2. Citations — locked decisions

SAFE (verified): Min 2202.12837 (EMNLP'22) · Wei 2211.02011 (confirm EMNLP'23 venue) · Olsson 2209.11895 ·
McKenzie 2306.09479 (TMLR'23) · Spracklen 2406.10279 (USENIX Sec'25; open 21.7% vs commercial 5.2% verbatim) ·
Fission-GRPO 2601.15625 (cite "+5.7% = error-recovery rate") · Brief-Is-Better 2604.02155 (concurrent — MUST
cite-and-distinguish: their axis is CoT budget on Qwen2.5-1.5B; ours is scale at fixed thinking) ·
Internal-Reps 2601.05214 (concurrent activation-probe; distinguish — we are behavioral, not activation).

PRIOR-ART TO DIFFERENTIATE: Xu 2412.04141 (tool-type hallucination = our metric; their fix is training-based
action-space expansion, ours is training-free re-prompt) · Yin 2510.22977 (SimpleToolHalluBench, *monotonic*
reasoning→hallucination — contrast with our non-monotonic).

DO NOT USE: 2512.08213 for any "quantization→non-monotonic-size" claim (it's monotonic, Go packages).
DO NOT attribute orthographic→semantic maturation to Ren 2402.13055 (no such claim in it).

RULE: every 0% cell gets a Clopper-Pearson upper bound. Never print a bare "0%".

## 3. Experiment queue (M5, sequential; free local compute)

Code prereqs (do first, smoke-test each): C0_8 decoy condition (new `harness/intervention/decoy_list.py`
+ register in `loop.py` + allow in `run_probe.py`); Llama `<|python_tag|>`/`parameters` parser branch in
`mlx_adapter.py` (cross-family quick win); B4 downstream-utility analysis script.

Priority order (highest-value results land first):
- **B1 N-expansion** — 14B & 32B & 8B, C0, n=50, all 4 distractor types. Tightens/confirms peak + collapse.
- **Bdecoy C0.8** — 8B, 4B, 14B. The spotlight experiment.
- **B3 C-ladder** — {C0,C0_5,C0_7,C1} on 4B and 14B (8B already done). Robustness of the ablation across tiers.
- **B2 quant confound** — 8B {4bit(have),8bit,bf16} + 14B-8bit, C0. (14B-bf16 OOMs on 32GB — excluded.)
- **B7 cross-family** — Llama-3.1-8B C0 after parser fix (+ Mistral if cheap). Phi/gemma structurally can't tool-call → drop honestly.
- **B4 downstream utility** — task-success Δ / abstention / latency / round-trips, C0 vs C1, from traces (analysis, no new runs).
- **B5 tau-bench** — only if env.reset/respond wiring + litellm install land cleanly. Riskiest; second benchmark to break "BFCL-only."
- **B6 contamination probe** — paraphrase BFCL tool names / membership check on the Anthropic null. Stretch.

Known risk: near_name distractor is low-yield (8B 1/219, 14B 0/63); use all 4 types and verify TEHR>0 on a smoke before big N.

## 4. Writing plan (parallel with compute)

Correctness (from existing data; recompute & lock all numbers via aggregate_all.py):
- Reconcile Qwen3-8B C0 denominator (258/268/269) — recompute, pick canonical, sweep every instance.
- Make pooled 0/2,599 reconstructable from tables (or restate to the dedup'd number that IS reconstructable).
- Fix "~944"→"945"; reconcile Anthropic C1 "0/678" vs "0/539"; delete stale "0/3231" comment.
- Add a model×split coverage matrix (abstract sells "5 versions"; regime grid is 2 models — clarify).
- CP upper bounds on every 0% cell.

Reframing:
- Reorder narrative to lead with format-not-content recovery + C0.8.
- Trim §3.3 mechanism apparatus (M-Retrieve/Constrain/Metacog) — reviewer "over-framed"; keep what the data adjudicates, cut the rest, OR tie the C0.7/C0.8 result to it directly.
- Position curve as predicted signature; add quant-confound control; cite-and-distinguish concurrent work.
- De-anonymize, add acknowledgments (Max plan / YC credits per funding), keep LLM-disclosure section.
- Add downstream-utility paragraph (answers huDR/Gox1) and the prior-art differentiation paragraph (Xu/Yin).

## 5. Review gate (Phase E)

Drive `paper-review-toolkit/` 12 personas in rounds (hostile_statistician, adversarial, novelty_stickler,
reproducibility_skeptic, brutally_honest_AC, industry_practitioner, three_line_skim, contamination_researcher,
…) → revise → re-review until convergence. Then evaluator PASS. Simulate the rebuttal to each of the 3 real
reviews (esp. the reject, huDR).

## 6. Out of scope (do not relitigate — prior rounds settled these)
FLOPs/energy; multimodal eval; causal mechanism claims; registry-size sweep beyond 25 tools;
cross-platform M5-vs-GPU comparison; publishing code before notification.
