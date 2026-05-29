# R2 — Out-of-Distribution Skeptic Review
*Reviewer angle: generalization stress-test. The question I keep asking: **what's outside the support of your evaluation, and which claims silently assume in-support behavior?***

**Materials**: PAPER_PLAN_v3.1.md + ADDENDUM_R1.md (R1 overrides) + paper/sections/04_setup.tex + PHASE0/dataset_status.md.

**Verdict**: **Major Revision — generalization claims overshoot the evaluation envelope by 1-2 orders of magnitude.** The work is methodologically tightening up nicely post-R1, but the headline still reads as a universal statement about "tool-using agents" when every axis of the evaluation is narrow. Either the language downscopes or the evaluation widens; "stronger language at the same support" is not an option.

---

## Top-3 OOD failure modes (ranked by likelihood the claim breaks)

### OOD-1. Vendor monoculture inside a "diverse" label
Two vendor *families* (Anthropic + OpenAI) is the entire API surface. Both Anthropic models share post-training. Both OpenAI models share post-training. Effective vendor-N is **2**, not 4. Likely OOD failures: Gemini's tool-call grammar (different schema dialect), Llama-3/Mistral's lower instruction-following on registry-length stress, DeepSeek's tendency to emit Chinese-language tool names under prompt drift. The cost defense ("we only have $5,500") does not survive scrutiny — Gemini, Llama, and Mistral are all available either free-tier or via cheap routing (OpenRouter, Together, Groq), and the choice was made *before* the credits arrived. **Most likely concrete break**: RVR's pass-rate gain on small-tier collapses on Llama-3-8B because Llama treats the registry list as additional system prompt rather than tool-routing context.

### OOD-2. Benchmark-distribution narrowness
BFCL multi-turn registries cap at ~22 tools per task (vehicle_control); τ-bench retail is fixed at 16. Real enterprise scenarios run **100-500 tools per registry**, version-suffixed names (`get_user_v2_async_internal`), namespace prefixes (`internal.crm.users.get`), non-English tokens, and dynamically-generated tool names. TEHR's curve in this regime is unknown. RVR's "include the registry list in the re-prompt" is a 100×-token intervention at 500 tools and breaks the <2% token-overhead claim immediately. **Most likely concrete break**: at registry size ≥100 the small-tier+RVR cost advantage evaporates because re-prompt token cost scales linearly with |registry| while frontier baselines do not need the re-prompt.

### OOD-3. Hallucination taxonomy under-specified
TEHR captures **only** name-not-in-registry. The §6 probe explores three distractor types within that one failure class. Adjacent failures the metric does not catch:
- **Namespace hallucination**: model emits `internal.get_user` when registry has `get_user`. By a strict-string membership test this is TEHR=1; by intent it's a near-miss the model could self-correct from. Current loader normalization gives no clear answer.
- **Signature hallucination**: right name, fabricated argument (`get_order_details(order_id, secret_token=...)`). TEHR=0 but the call still fails.
- **Return-shape hallucination**: model assumes a key in the response that the tool never returns; failure shows up downstream as a downstream-tool TEHR or a refusal — the metric assigns blame to the wrong call.

These are **tool-existence-adjacent failures the metric explicitly does not measure**. Either the metric expands or the paper carves out the precise envelope.

---

## Other OOD-axis weaknesses (briefer)

**OOD-4 / Prompt-template generalization (low severity, easy fix)**. Two prompt templates is a robustness *spot-check*, not a prompt-distribution claim. The paper's §4 says "two prompt templates --- a default template and a paraphrased variant --- to provide a coarse check on prompt sensitivity." Good — that language is appropriately scoped. **But the abstract / §1 must not generalize past it.** Reviewer recommendation: real prompt OOD would be ReAct vs. Chain-of-Thought vs. structured-XML vs. plain-imperative scaffolds; you have one (ReAct). Acknowledge.

**OOD-5 / Task-distribution (medium severity)**. BFCL multi-turn-base + τ-bench retail are both *transactional* (book, fetch, exchange). The paper makes no claim about *creative* tool use (compose a workflow), *exploratory* tool use (discover a registry), or *adversarial* tool use (red-team prompt injection that induces hallucinated tools). Title says "tool-using agents" — that's ~3× the support actually evaluated. Downscope.

**OOD-6 / Time-distribution (medium severity, reproducibility-adjacent)**. Sonnet-4.6 and the rest are pinned for reproducibility (good — see ADDENDUM D.4). But all four API models receive periodic refresh in production. A reader six months out applies RVR to `gpt-4.2`; does the result hold? §7 limitations should explicitly say **"results are at-snapshot; we make no claim about temporal stability across silent provider refreshes"**, AND the paper should discuss whether TEHR is expected to *decay* (frontier models get better at registry adherence over time → gap-closure-ratio shrinks → RVR's advantage shrinks). This is a known mechanism the paper should pre-empt rather than have a future reader discover.

**OOD-7 / Local-tier panel is N=1 (high severity for the local-tier claim specifically)**. Qwen3-8B-4bit on Apple Silicon MLX is *one* model on *one* runtime. "Open-source local models" is the headline label; the actual support is a single point. **Recommendation**: either run Phi-3-mini and Llama-3.1-8B alongside Qwen3 (both fit in 32GB at 4-bit, ~30 min added wall-clock per model per benchmark), or rename §5.5 from "local-OSS tier" to "**Qwen3-8B feasibility anchor**" and never use the plural "models" for this panel.

---

## Downscope language to add (concrete, drop-in)

Add to §1 (abstract or first paragraph):
> *"Our evaluation covers two API vendor families, two transactional benchmarks, two prompt templates, and a single open-source local model on Apple Silicon. We make no claim about generalization to additional vendors (Gemini, Llama, Mistral, DeepSeek), to enterprise-scale registries (≥100 tools), to non-transactional task distributions, or to silent provider model refreshes."*

Add to §7 (limitations), separate from the existing multimodal bridge:
> *"The Tool-Existence Hallucination metric measures registry-membership violations only. Adjacent failure modes — namespace-prefix hallucination, argument-signature hallucination, and return-shape hallucination — are out of scope; future work should expand the failure taxonomy. The local-tier panel reports a single open-source model and is best read as a consumer-hardware feasibility anchor, not as a claim about open-source models broadly."*

Replace any §5 sentence of the form "across small-tier models" with "across two small-tier API models (Haiku 4.5, GPT-4.1-mini)."

---

**Bottom line**: this paper survives if the language matches the support. As written, the headline is a vendor-Diverse, model-Diverse, benchmark-Diverse, prompt-Diverse claim built on N=2 / N=2 / N=2 / N=2. Tighten the envelope and the contribution stands.

*(Word count: ~870.)*
