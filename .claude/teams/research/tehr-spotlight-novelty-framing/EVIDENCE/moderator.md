# moderator.md — structured debates on load-bearing contradictions

Verdict types: A_WINS / B_WINS / COMPLEMENTARITY / REFRAME / DEFER.

Primary sources debated: Wei et al. arXiv:2211.02011; Min et al. arXiv:2202.12837; quant-confound arXiv:2512.08213; CoT-budget overlap arXiv:2604.02155.

---

## Debate C1 — Is the single-family Qwen3 TEHR hump a legitimate "U-shaped scaling" instance?

**Position A (pro-headline)**: Lead with the non-monotonic curve as a new U-shaped-scaling instance in the tool-use domain. It has a Wei-compatible distractor-decomposition (distractor-type shift), which is more than most U-shape claims offer.

**Position B (anti-headline)**: The curve is below Wei's evidentiary bar (multi-family, K2), is confounded by 4-bit quantization (K8/AT-1), and is partially scooped on the "non-monotonic Qwen function hallucination" surface by 2604.02155 (K9). Leading with it invites a methodology-driven reject.

### Round 1
- A: The distractor-shift is a genuine mechanistic decomposition; Wei rewards exactly this.
- B: Wei rewards it BECAUSE he showed it across PaLM+Chinchilla+GPT-3. One quantized family with a 5-point ladder where both endpoints read 0% is fragile — and 0%-at-both-ends is suspiciously consistent with a quantization×size artifact (2512.08213 shows quantization alone produces non-monotonic size curves).

### Round 2
- A: We can disarm the quantization confound cheaply — an fp16 spot-check at 2 ladder points; the small Qwen3 members fit on M5 in fp16. And thinking is disabled, so it is NOT the 2604.02155 CoT-budget effect.
- B: Even disarmed, it is still N=1 family. The HEADLINE cannot be "U-shaped scaling" without a second family. But the curve can be a SUPPORTING result under a different headline.

### Round 3
- A concedes: single-family cannot carry the spotlight headline alone.
- B concedes: with (i) an fp16 control and (ii) the distractor-shift decomposition, the curve is a legitimate, publishable U-shaped *instance* — just not the load-bearing novelty.

### VERDICT: REFRAME.
The right question is not "is this a U-shaped scaling law?" (N=1 says no) but "what does this curve EVIDENCE?" It evidences the **grounding-gap theory (H3)**: the curve, the distractor-shift, and frontier-zero are three signatures of one mechanism (prior matures before control). So the U-shape becomes a *predicted signature of the theory*, not a standalone scaling-law claim. **Mandatory controls before any U-shape language**: (1) fp16 spot-check at ≥2 ladder points to kill the quantization confound; (2) explicit "thinking disabled" statement + ideally a thinking on/off check to distinguish from 2604.02155; (3) Clopper-Pearson CI on the 0% endpoints (AT-5), never bare "0%". With these, "a U-shaped *instance* explained by a grounding-gap mechanism" is defensible. Without them, drop U-shape language entirely.

---

## Debate C2 — Is "format-not-content recovery" (C0.7) a genuine contribution or a restatement of Min et al. 2022?

**Position A (genuine)**: C0.7 shows a structured error envelope with NO registry list recovers fully — the FORM of the corrective signal, not its content, drives recovery. Novel in the RECOVERY regime and stronger than Min (the withheld content is the literal solution set).

**Position B (incremental)**: Min et al. (2022) already established format-over-content for in-context demonstrations. This is "known effect, new task."

### Round 1
- A: Min studied FORWARD prediction with random LABELS. C0.7 studies REACTIVE error-recovery and withholds the actual answer (the registry). The model recovers without ever being told the right tools — that is a qualitatively stronger and more surprising claim.
- B: A skeptic will still file it under "format effects, known since 2022."

### Round 2
- A: The surprise is operational: it means the dominant deployed mitigation (re-inject the full tool list on error) is solving the WRONG variable. The fix works because of structural re-entry, not information delivery. That is an actionable, counterintuitive mechanism-of-the-fix, not a relabel.
- B: Agreed that the OPERATIONAL claim ("registry content is decorative; envelope shape is the active ingredient") is non-obvious and not in Min. But it needs hardening: multiple envelope shapes + content-matched controls, or it is a single-ablation anecdote.

### Round 3
- Both converge.

### VERDICT: B_WINS on framing, A_WINS on substance → COMPLEMENTARITY.
"Format-over-content" as a PHENOMENON is NOT novel (cite Min prominently — do not claim discovery). But the SPECIFIC operational result — *in reactive agentic error-recovery, the structural envelope is the active ingredient and the registry content is decorative* — IS a genuine, counterintuitive, deployable contribution that Min does not contain. The contribution is the **recovery-regime instantiation + the practical inversion** ("stop re-injecting tool lists; fix the envelope"), anchored to Min as theoretical lineage. **Hardening required**: ≥2 additional envelope shapes and at least one content-matched control (e.g. envelope with a WRONG/decoy tool list) to prove content is truly inert, not just redundant. Without hardening it is a one-ablation observation, not a contribution.

---

## Net guidance to lead
- C1 → REFRAME: the U-shape is a *signature of the grounding-gap theory*, not a standalone headline. Demote H1 from lead to evidence.
- C2 → COMPLEMENTARITY: format-not-content recovery is a real contribution IF hardened and IF anchored to Min, not claimed as discovery.
- The two surviving spotlight-grade candidates are therefore: **(H3) the grounding-gap theory that unifies all four findings**, and **(H2-hardened) the format-not-content recovery inversion**. The security reframe (web-miner #1) is the strongest MOTIVATION wrapper for either. → skeptic pressure-tests these.

## Confidence
HIGH on both verdicts; both are convergent debates with explicit concessions, not forced. Handoff: skeptic must attack (a) whether H3 over-claims a mechanism the data only correlates, and (b) whether the security wrapper is a stretch given the paper has no exploit demonstration.
