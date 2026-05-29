# Cross-Paper Novelty Stickler — Round 2

*Reviewer persona: PhD student who reads arXiv daily; cites three concurrent works the authors missed. Tone: cite-by-cite, exhaustive, not mean.*

I read §2.3, ADDENDUM §B.4, the §2 LaTeX, the §3 LaTeX, `prior_art.md`, and `related_work_notes.md`. The reframe to "disaggregation" is a real improvement over v3, and L-ICL / Fission-GRPO / Engländer / API-Bank / RelyToolBench / Czapla are all named correctly. But there are at least three precedents the related-work section currently does NOT cite that any moderately-prepared reviewer will surface.

## Closest prior works not cited

1. **Huang et al., "MetaTool Benchmark for Large Language Models: Deciding Whether to Use Tools and Which to Use," ICLR 2024 (arXiv:2310.03128).**
   *Summary*: MetaTool's Sub-task 3 (*"tool selection with possible reliability issues"*) deliberately constructs the tool list `L_t` such that the correct tool `t ∉ L_t`, then measures Correct Selection Rate (CSR) — i.e., the fraction of cases where the model correctly answers ∅ instead of fabricating. The authors explicitly state *"LLMs sometimes fabricate non-existent tools, a severe hallucination issue,"* with most LLMs scoring <20% CSR.
   *Threatens*: **C1 (Benchmark + Metric + Mechanism)**. MetaTool already (a) names tool fabrication, (b) measures it on a controlled benchmark, and (c) reports it across many models. The TEHR-vs-CSR difference is denominator (per-call vs per-query) and direction (failure rate vs avoidance rate), but a reviewer will say *"this is MetaTool's Sub-task 3 with a different denominator."*
   *Severity*: **BLOCKER if uncited.** ICLR 2024, predates by 2 years, identical phenomenon. Reframe to "we measure the per-call rate of the same failure mode MetaTool measures at the per-query level, on multi-turn benchmarks where MetaTool's single-turn CSR is undefined" — and cite explicitly.

2. **Gou, Shao, et al., "CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing," ICLR 2024 (arXiv:2305.11738).**
   *Summary*: Training-free, black-box framework where an LLM iterates a Verify→Correct→Verify loop using *external tool feedback* as the corrective signal — explicitly positioned as not requiring fine-tuning, deployable on closed APIs. It corrects free-form QA, math, and toxicity but the *shape* of the intervention (re-prompt with structured tool-derived feedback, no logit access, no SFT) is essentially the abstract pattern RVR instantiates.
   *Threatens*: **C2 (RVR Intervention)**. RVR's "training-free, black-box, message-level corrective re-prompt with structured feedback" is a CRITIC-shaped intervention specialized to tool-existence errors. The §2 paragraph cites Reflexion + self-debug but skips CRITIC, which is the closest method-shape neighbor.
   *Severity*: **MAJOR.** Not a BLOCKER (different failure mode, different feedback channel) but every reviewer with a self-correction background will flag the omission. Differentiate on: (a) registry-membership-specific signal vs general external tool, (b) at-most-one retry budget, (c) the C0.5/C0.7/C1 ablation isolates *registry content* as the active ingredient — CRITIC never ablates feedback content.

3. **LangChain Forum thread #2427, "Allow graceful handling of 'Tool not found' errors in LangGraph ToolNode to enable Agent self-correction," 2025-12-05.**
   *Summary*: A LangChain community thread proposing middleware `wrapToolCall` that catches `tool_not_found` and returns a `ToolMessage` with an error string — but the proposed message is *"Tool 'X' does not exist. Please check available tools"* and *does not include the registry list*.
   *Threatens*: **C2 (RVR) on the industry-priority dimension.** A reviewer can argue "the industry already has this pattern; you contribute only the registry-list content."
   *Severity*: **MEDIUM, but actually FAVORABLE if cited correctly.** This thread is the perfect foil: it shows production engineers reaching for exactly the C0.7-shaped fix and *stopping short of the registry list*. RVR's contribution becomes "the missing ingredient." Add a footnote citing this thread; it strengthens the C0.7-vs-C1 framing.

## Other near-misses (not blockers but worth a citation each)

4. **Liu et al., "AgentHallu" (arXiv:2601.06818, Jan 2026).** Tool-Use Hallucination taxonomy includes "Missing Tool / Unnecessary Tool / Incorrect Argument / Parallel Conflict" — does *not* have a "non-existent tool" category. Cite as taxonomy precedent and explicitly note the gap TEHR fills.

5. **Tang et al. / Wang et al., "NoisyToolBench" (ACL Findings 2024).** Robustness under noisy/ambiguous instructions; AwN framework asks-when-needed. Different intervention (clarifying-question vs registry-list re-prompt) but same "training-free decode-time fix on tool-use failures" shape.

6. **AgentNoiseBench (arXiv:2602.11348, Feb 2026).** Adversarial tool-noise injection. Does NOT inject distractor tools into the registry — only corrupts tool *outputs*. Cite explicitly to differentiate the §6 probe: AgentNoiseBench injects noise at execution; we inject distractors into the registry itself.

7. **MCP-Atlas (Scale AI, Dec 2025) / StableToolBench (Guo et al., arXiv:2403.07714).** MCP-Atlas attaches 10 distractor servers (~100+ extra tools) per task to test irrelevance-resistance; StableToolBench evaluates "tool relevance hallucination" over solvable-pass criteria. Both predate the §6 probe with a *similar in spirit* registry perturbation, though both target relevance not membership-with-distractor-types. Cite at least MCP-Atlas in §6.

8. **Anthropic "Equipping Agents with Skills" (anthropic.com/engineering, 2025-10-16) + "Tool Search Tool" (Nov 2025 release).** Anthropic's stance is *progressive disclosure* of tool metadata — the explicit alternative to RVR's "show the whole registry on error." Cite in §2 as the contrasting industry approach, and pre-empt the reviewer question "why not just use Tool Search Tool?" in §7 limitations.

## Per-contribution novelty assessment

- **C1 (TEHR + probe): PARTIAL.**
  *Closest precedent*: MetaTool Sub-task 3 (fabrication of non-existent tools, ICLR 2024) at per-query CSR; API-Bank's API Hallucination at per-task. TEHR's true novelty is *per-call denominator on multi-turn traces* + *the distractor-type taxonomy in the §6 probe*. The metric alone is a renaming with a denominator change; the metric + probe + cross-tier characterization holds, marginally.
- **C2 (RVR): PARTIAL.**
  *Closest precedent*: CRITIC (ICLR 2024) for the abstract shape (training-free, black-box, external-feedback-driven re-prompt); the LangChain forum thread (Dec 2025) for the concrete industry pattern that stops one step short. RVR's defensible novelty is the *content-controlled ablation* (C0.5 / C0.7 / C1) that isolates *the registry list* as the active ingredient — no prior work runs that ablation. The intervention itself is not novel; the *evidence about which part of the intervention does the work* is.
- **C3 (Cost-quality-gap closure): CLEAR.**
  No prior work I can find runs RVR-or-equivalent across 3 capability tiers + 2 vendor families + open-source local with an explicit gap-closure ratio. RelyToolBench/Relign trains for it; Fission-GRPO trains for it on a single model. The cross-tier inference-time efficiency framing is genuinely new at workshop caliber.

## Required additional citations

Add to `refs.bib` and §2 cite-points:

- `huang2024metatool` — Huang et al., ICLR 2024, arXiv:2310.03128. Cite at: §2 Prior tool-hallucination metrics paragraph; §6 probe motivation.
- `gou2024critic` — Gou et al., ICLR 2024, arXiv:2305.11738. Cite at: §2 Constrained decoding and self-correction paragraph (currently lists only Reflexion + self-debug).
- `langchain_forum_2427` — LangChain Forum thread, 2025-12-05. Cite at: §2 Empirical analysis paragraph as industry production-pattern reference; pairs naturally with Czapla.
- `liu2026agenthallu` — Liu et al., arXiv:2601.06818. Cite at: §2 Prior tool-hallucination metrics paragraph (taxonomy precedent that omits TEHR's category).
- `wang2024noisytool` — NoisyToolBench, ACL Findings 2024. Cite at: §2 Self-correction paragraph (training-free decode-time fix).
- `agentnoisebench2026` — arXiv:2602.11348. Cite at: §6 probe related work — explicit differentiation (output-noise vs registry-noise).
- `mcpatlas2025` — Scale AI MCP-Atlas, Dec 2025. Cite at: §6 probe — distractor-tool registry perturbation precedent.
- `anthropic_skills_2025` — Anthropic engineering blog, 2025-10-16, + Tool Search Tool Nov 2025. Cite at: §2 (industry alternative) and §7 (limitations / why-not-tool-search).

## Verdict on novelty story

**WEAKENED-BUT-DEFENSIBLE.** The reframe is essential — "we name a new metric" would be a desk-reject. With MetaTool, CRITIC, and the LangChain thread cited and the differentiations below applied, the story holds at workshop caliber. Without them, an arXiv-fluent reviewer kills it on prior-work grounds in 30 seconds.

## Recommended response strategy

For each newly-found precedent, drop-in differentiation language for §2:

- **MetaTool**: *"MetaTool \citep{huang2024metatool} introduced single-turn fabrication-avoidance under a deliberately-incomplete registry, scored at the per-query level (Correct Selection Rate). TEHR generalizes the same failure mode to multi-turn traces under a per-call denominator, where CSR is undefined because a single trace contains many tool calls of mixed legitimacy."*
- **CRITIC**: *"CRITIC \citep{gou2024critic} establishes the abstract shape of a training-free, black-box, external-feedback-driven self-correction loop. RVR specializes that shape to registry-membership errors and — crucially — runs a content-controlled ablation ($C_{0.5}$ / $C_{0.7}$ / $C_1$) that isolates the registry list itself as the active ingredient, an ablation absent from CRITIC and its descendants."*
- **LangChain Forum thread**: *"The LangChain community has independently reached for a `tool_not_found`-aware retry middleware \citep{langchain_forum_2427}, but the proposed feedback string stops short of echoing the registry. RVR is precisely the missing-content variant of this production pattern, and our $C_{0.7}$ vs $C_1$ contrast quantifies what including the registry list is worth."*
- **AgentHallu**: *"AgentHallu's tool-use taxonomy \citep{liu2026agenthallu} covers Missing/Unnecessary/Argument/Parallel-Conflict categories but does not name registry non-existence as its own subclass; TEHR fills that taxonomic gap."*
- **AgentNoiseBench**: *"AgentNoiseBench \citep{agentnoisebench2026} adversarially perturbs tool *outputs*; our §6 probe orthogonally perturbs the tool *registry*."*
- **MCP-Atlas**: *"MCP-Atlas \citep{mcpatlas2025} attaches distractor servers to stress relevance; our §6 distractor-type taxonomy (near-name, synonym, random, matched-random) targets membership-vs-similarity confounds at finer granularity."*
- **Anthropic Skills + Tool Search Tool**: *"Tool Search \citep{anthropic_tool_search_2025} restricts which tools are visible at decode time; RVR is its post-hoc dual — invoked only after a membership violation has occurred. The two are complementary."*

## Bottom line for the author

The R1 reframe was correct but incomplete. Three additions (MetaTool, CRITIC, LangChain thread #2427) close the prior-work attack surface; six more (AgentHallu, NoisyToolBench, AgentNoiseBench, MCP-Atlas, StableToolBench, Anthropic Skills) round out the citation hygiene a workshop reviewer expects. With these in, the novelty story is **WEAKENED-BUT-DEFENSIBLE** at SCALE caliber. Without MetaTool in particular, R3 will eat C1 alive.

---
*~1180 words.*
