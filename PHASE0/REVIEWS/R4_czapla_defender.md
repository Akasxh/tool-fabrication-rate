# Czapla-Defender — Production-vs-Benchmark Critique

## Verdict
**WEAK REJECT** (overstated calibration claim; the title and abstract advertise a population-level recalibration that the data cannot support, while the substantively defensible finding — TEHR=0 on BFCL multi-turn — is buried under it).

## Core claim (1 paragraph)
The paper conflates two non-equivalent claims and uses evidence for the narrow one to discharge the broad one. Claim (a) — "TEHR=0/1571 on BFCL multi-turn splits and a registry-restricted distractor probe on Sonnet 4.6 / Haiku 4.5" — is well-supported, well-instrumented, and a useful contribution. Claim (b) — "Tool-Existence Hallucination Is Rarer Than Reported" (the title) and "modern Anthropic frontier and small models simply do not fabricate tool names" (§1) — is a population-level recalibration of a *production* phenomenon. The paper itself concedes in §7.7 that the production failure mode involves *ambient runtime functions reachable beyond the explicitly declared registry*, and that BFCL's "strictly-typed Python-class executor cannot emulate" this configuration (§5.4). The data therefore tests claim (a). The title, abstract, and §1 advertise claim (b). That is the central methodological move I object to.

## Specific overreaches (with line refs)

1. **Title ("Tool-Existence Hallucination Is Rarer Than Reported")** is a population claim. The evidence is a benchmark claim. The title should make the substrate explicit.

2. **Abstract sentence**: "The production phenomenon documented by Czapla does not transfer to BFCL benchmarks under any of our test conditions" (lines 49–50). This is honest. But two sentences earlier the abstract says "TEHR is exactly 0 in every condition tested" with no qualifier on what "every condition" means in deployment terms. A reader sees the unqualified zero before they reach the qualified non-transfer.

3. **§1 claim**: "modern Anthropic frontier and small models simply do not fabricate tool names" (lines 32–33). This is exactly the (a)-to-(b) slide. The data shows: *modern Anthropic models do not fabricate tool names when the executor strictly rejects unknown names and the registry contains in-class alternatives*. That is not the same statement.

4. **§1 "Czapla-style scenario" framing** (lines 26–31, 58–64). The probe is described as "a Czapla-style scenario in which the agent expects a tool to exist but the registry offers only a similarly-named distractor" (§5.2 lines 56–60). This is a *registry-shape* emulation. Czapla's actual scenario is *runtime-shape*: a `read_secret()` capability exists in the executor's reachable scope, the registry omits it, and the model's prior expectations about ambient capabilities collide with the declared interface (§7.7 lines 28–30 acknowledges this exactly). Removing a tool from a typed registry while keeping the executor's allow-list locked is not the Czapla configuration; it is Czapla minus the load-bearing variable.

5. **§5.4 (lines 124–127)** says outright: "RVR is expected to matter on deployment patterns where ambient runtime functions are reachable beyond the explicitly declared registry — a configuration that BFCL's strictly-typed Python-class executor cannot emulate." This is a frank confession that the experimental envelope excludes the failure regime. The §1 framing should match this candor; it does not.

6. **Decomposition explanation generalizes weakly.** §1 lines 46–50 explains the null result via the "redundant tool basket" — `ls`, `cd`, `mv`, `mkdir` all available. Enterprise tool catalogs at 100–500 entries (§7.4) are typically *not* redundant in this sense for the operations that fail in production: there is one `read_secret` capability, no graceful in-registry alternative, and decomposition is unavailable. The mechanism the paper invokes to explain the null result is itself regime-specific; this should be stated where the null result is reported, not buried in a separate scaling caveat.

7. **Rule-of-three overreach.** Even taking the paper's bound at face value, the upper 95% CI on TEHR is ~0.19% across 1,571 BFCL calls. That CI is conditional on the BFCL data-generating process. It does not extend to deployments with ambient executors, agent-loop-level tool registries assembled from heterogeneous MCP servers, or registries derived from natural-language tool descriptions. The abstract's "we cannot validate within this envelope" framing for RVR (line 59) is correctly scoped; the parallel scoping should also apply to the headline TEHR claim.

## Required title/abstract rewrites

- **Title**: *"Tool-Existence Hallucination Is Absent on BFCL Multi-Turn: A Per-Call Audit and a Mitigation Design for the Production Configurations BFCL Cannot Reproduce."* This makes the substrate explicit and preserves the contribution.

- **Abstract sentence 1** (replacing "LLM agents are widely reported to 'hallucinate' tool calls..."): *"LLM agents are widely reported to hallucinate tool calls in production deployments where ambient runtime functions are reachable beyond the declared registry; we ask whether the same failure mode appears on BFCL's strictly-typed multi-turn benchmark and find that, on this specific substrate, it does not."*

## What the paper SHOULD say (calibrated)

The honest summary is three-part and the paper has all the pieces but assembles them in the wrong order:

1. *On BFCL multi-turn (Sonnet 4.6 / Haiku 4.5), TEHR is indistinguishable from zero across 1,571 parsed calls.* Claim (a). Defensible. Useful as a calibration anchor for the BFCL-using community.

2. *This null result is consistent with two non-mutually-exclusive mechanisms — redundant in-class tool baskets and post-2024 tool-use hardening — that the present evaluation cannot disentangle.* §1 says this; good.

3. *The production phenomenon documented by Czapla involves a substrate (ambient executor scope) that BFCL does not contain. The current evaluation neither confirms nor refutes that phenomenon's prevalence in production.* §7.7 says this; it should be in the abstract, not §7.7.

The paper's contribution is then framed correctly as: *a clean BFCL-substrate null result*, *a per-call diagnostic worth reusing*, and *a pre-registered intervention waiting for the right substrate*. That is a coherent, defensible SCALE workshop submission. The current framing as "TEHR rarer than reported" overclaims and invites the rejection it would deserve at a stricter venue.

## What experiments would settle the (a)/(b) gap

1. **Ambient-executor harness.** Replace BFCL's strictly-typed Python-class executor with a permissive Python `exec`-style or MCP-relay executor where (i) the declared registry omits a capability and (ii) that capability is reachable via a name the model has prior expectations about (`read_file`, `read_secret`, `requests.get`, etc.). Measure TEHR. This is the minimum experiment needed to test claim (b).

2. **Natural-language registry.** Recast the registry as free-form tool descriptions (the MCP-server style) rather than typed Python signatures. Czapla's report is across Claude/Gemini/Grok agentic loops, all of which see registries as text. Typed-Python registries are a stricter prompt format than production; the null result may be a prompt-format artifact.

3. **Enterprise-scale registry (≥100 tools, no redundancy).** §1's redundant-basket explanation predicts TEHR will rise when the basket is sparse for the requested operation. Construct a 100-tool registry where the requested operation has *no* in-class alternative and rerun the miss-func protocol. If the paper's mechanism explanation is correct, TEHR will be substantially non-zero here.

4. **Weaker model tier.** Run the same six regimes on Haiku 3.5, GPT-4o-mini, Llama-3.1-8B. The "post-2024 hardening" hypothesis predicts a tier-dependent effect.

5. **Production trace replay.** Czapla's claimed observations are presumably reproducible on captured traces. Run TEHR on a sample of those traces directly. This is the only experiment that *closes* the (a)/(b) gap.

Until at least (1) and (5) are run, the paper should be titled and abstracted as a BFCL-scoped calibration study, not a population-level recalibration of the Czapla phenomenon.

---

**Word count**: ~1000.
