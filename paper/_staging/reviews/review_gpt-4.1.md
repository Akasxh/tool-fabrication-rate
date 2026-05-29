# gpt-4.1

**(1) 2-line summary:**  
This paper introduces a per-call Tool Fabrication Rate (TFR) to measure tool-name hallucination in LLM agents, auditing Anthropic 4.x, OpenAI GPT-4.x, and Qwen3 families. It finds zero TFR for commercial models but nonzero, non-monotonic TFR for Qwen3, and proposes a training-free Registry-Visible Reprompting (RVR) middleware that eliminates all observed fabrications in Qwen3.

**(2) Score: 6/10**  
**Accept probability:** 25% (borderline, workshop-level, not main-track ICML)

---

**(3) Top 5 weaknesses (with severity):**

1. **Limited Generalizability (High):**  
   The main finding—nonzero TFR in Qwen3 but not in Anthropic/OpenAI—rests on a single open-weight family (Qwen3) and a single quantization (4-bit MLX), with no full-precision or cross-family controls. This makes it unclear whether the effect is model-specific, quantization-specific, or general.

2. **Underpowered Ablations (High):**  
   The content-vs-format ablation is inconclusive: all arms are zero-event, so the claim that content is not needed is not supported, only bounded. The authors themselves note this is "absence of evidence, not evidence of equivalence" (Section 6), and a powered test is "in progress."

3. **Confounded Experimental Design (High):**  
   The Anthropic–Qwen3 gap is confounded by multiple factors: parameter count, quantization, training recipe, and provider guardrails all co-vary. No attempt is made to isolate these, and the authors admit they "cannot disentangle" the causes (Section 7).

4. **Benchmark Limitations (Medium):**  
   The BFCL v4 benchmark is not production-realistic: it is strictly typed, lacks runtime registry reachability, and may let agents route around missing tools rather than hallucinate. This may explain the zero-event regime for Anthropic and limits external validity.

5. **Overstated Practical Impact (Medium):**  
   The RVR fix is only needed for models with TFR > 0, which in this study is only Qwen3 at certain scales. For commercial models, the intervention is a no-op. The practical recommendation is thus narrow, and the claim of "actionable ablation" is overstated.

---

**(4) Highest-leverage fix:**  
**Run the ablation and scaling experiments on a full-precision (bf16) Qwen3 family and at least one other open-weight model (e.g., Llama-3), to disentangle quantization and family effects.** This would clarify whether the observed TFR is a general property of open models, an artifact of quantization, or specific to Qwen3.

---

**(5) Unsupported/inconsistent numbers or claims:**

- The claim that "commercial models...also log 0% TFR (0/2,117 pooled, ≤ 0.18%)" (Abstract, Section 5.2) is based on a relatively small N and only on the specific BFCL probe; prior work (Spracklen et al., 2025) reports nonzero rates in production. The authors mention this but do not reconcile the discrepancy.
- The non-monotonic scaling claim for Qwen3 is based on only six points, with wide confidence intervals at the endpoints (e.g., 0/224 at 32B, ≤ 1.63%), so the "collapse" at 32B could be a sampling artifact.
- The ablation claims (C0.7, C0.8, C1 all zero-event) are not evidence of equivalence; the authors are careful but the abstract and some prose overstate the conclusiveness.
- The practical claim that "a deployer can ship the structured rejection without echoing internal tool names and lose nothing detectable" is only supported for Qwen3-8B at this N, not for other models or settings.

---

**(6) Does the prose read AI-generated?**

**No, the prose does not read as AI-generated.**  
It is dense, technical, and at times self-consciously cautious, with hedged claims, explicit limitations, and references to ongoing work. The writing style is more reminiscent of a careful, slightly over-verbose human researcher than an LLM:  
- Frequent use of hedging ("we do not claim", "we cannot disentangle", "absence of evidence, not evidence of equivalence")  
- Self-referential and meta-scientific commentary ("we do not over-read this", "the data cannot separate copying from cueing, so we drop that apparatus")  
- Explicit referencing of statistical methods and confidence intervals  
- Section 6 and 7 are particularly careful in bounding claims and discussing limitations, which is rare in AI-generated text  
- The prose is sometimes awkward or overly dense, but not in the typical LLM way (e.g., no generic filler, repetition, or hallucinated citations).

**Specific examples:**  
- Section 6: "We are careful about what this can and cannot show. All three arms are zero-event, so we detect no content effect at this sample size — this is absence of evidence, not evidence of equivalence."
- Section 7: "We cannot disentangle the Anthropic–Qwen3 gap: parameter count, 4-bit MLX quantization, training recipe, and provider guardrails co-vary..."

**Conclusion:**  
The writing is rigorous, cautious, and human in tone, with no clear signs of AI generation.

---

**Overall:**  
This is a careful, well-executed workshop paper with a clear negative result and a practical fix, but the main findings are limited by confounds, underpowered ablations, and narrow scope. The highest-leverage improvement is to expand the experimental matrix to other models and precisions. The prose is human-written and appropriately hedged. Not ready for main-track ICML, but a solid workshop contribution.