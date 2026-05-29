# R2 Multi-Persona Review — Aggregate Synthesis
*Six fresh reviewer angles, all distinct from R1. Source files in `PHASE0/REVIEWS/R2_*.md`.*

## Aggregate verdicts

| Reviewer | Verdict |
|---|---|
| R2.1 Industry Practitioner | DEPLOY WITH CAVEATS |
| R2.2 Theory Reviewer | Weak Accept (conditional on §3.5 mechanism + headline-ratio restriction) |
| R2.3 OOD Skeptic | Major Revision |
| R2.4 Anonymization & Ethics | FIX-LIST-MANAGEABLE |
| R2.5 Three-line Skim | NEEDS-EDITS (rewrites provided) |
| R2.6 Cross-Paper Novelty Stickler | WEAKENED-BUT-DEFENSIBLE (CRUMBLES without MetaTool) |

**Aggregate**: 0 unconditional ACCEPT, 1 conditional WEAK ACCEPT, 1 DEPLOY-WITH-CAVEATS, 1 NEEDS-EDITS, 1 FIX-LIST-MANAGEABLE, 1 MAJOR REVISION. Better than R1 (which had 4 effective REJECTs); the architecture shifts from R1 are landing. **The remaining issues are tightenings, not redirections.**

---

## BLOCKERS (must fix before R3)

| # | Issue | Source | Fix status |
|---|---|---|---|
| **B-R2.1** | **MetaTool (Huang et al., ICLR 2024, arXiv:2310.03128) uncited** — closest precedent to TEHR; sub-task 3 measures registry-fabrication via per-query Correct Selection Rate. Without citing, novelty crumbles. | R2.6 | **DONE** — added to refs.bib + cited in §2 with per-query→per-call differentiation. |
| **B-R2.2** | **CRITIC (Gou et al., ICLR 2024, arXiv:2305.11738) uncited** — RVR's method-shape neighbor. | R2.6 | **DONE** — added to refs.bib + cited in §2 with content-controlled-ablation differentiation. |
| **B-R2.3** | **Mandatory LLM/agent disclosure section absent from main.tex** | R2.4 | **DONE** — wrote `paper/sections/08_llm_disclosure.tex`, added `\input` to main.tex. |
| **B-R2.4** | **§7 safety paragraph absent** (Czapla's `read_secret()` ambient-function risk) | R2.4 | **DONE** — wrote `paper/sections/07_limitations.tex` §7.7 safety. |
| **B-R2.5** | **C0.7 was framed as approximating LangChain default; actually a strawman** because real LangChain raises `OutputParserException`, doesn't emit clean JSON envelope. | R2.1 | **DONE** — §1, §3, ADDENDUM all renamed to "idealized structured-error baseline." LangChain forum thread #2427 cited as the actually-proposed-by-engineers reference. |

## MAJORS (fix during R3 fix pass or before)

| # | Issue | Source | Status |
|---|---|---|---|
| M-R2.1 | Title leads with jargon, hides phenomenon, omits headline number | R2.5 | Pending — R2.5's rewrite: *"Tool-Existence Hallucination in LLM Agents: A Per-Call Metric and a Training-Free Fix That Closes [Y]% of the Cost-Quality Gap."* Need to update v3.1 §2.1. |
| M-R2.2 | One-sentence main result (v3.1 §2.2) buries number behind 67-word setup | R2.5 | Pending — R2.5's rewrite: *"LLM agents call tools that do not exist on [X]% of calls; a single-turn re-prompt that lists the registry (RVR) recovers [Y]% of these failures and closes [Z]% of the small-vs-frontier cost-quality gap, validated across 5 models on BFCL-v4 and τ-bench at <2% token overhead."* Update v3.1 §2.2. |
| M-R2.3 | Three RVR mechanisms (Retrieve / Constrain / Metacog) not pre-registered as candidates with §6-favoring predictions | R2.2 | Pending — add §3.5 "Mechanism Hypotheses" paragraph naming the three; pre-register which §6 probe outcomes favor which. Zero experimental cost. |
| M-R2.4 | Gap-closure ratio silently attributes ALL small/frontier delta to TEHR; need to restrict the headline ratio to hallucination-tagged C0-failed subset (data already collected for McNemar) | R2.2 | Pending — update v3.1 §4.3 metric definition + 04_setup pre-reg #14. |
| M-R2.5 | Per-call denominator's i.i.d. assumption stated as "cleaner asymptotics" — actually false (within-trace dependence). | R2.2 | Pending — rewrite §3.1 to weaken to exchangeability + cluster-bootstrap (already implemented in stats/bootstrap.py per ADDENDUM C.3). |
| M-R2.6 | Constrained-decoding analog framing in §3.2(iv) doesn't acknowledge that token-level (Outlines, JSON-mode) strictly dominates message-level when logit access exists | R2.2 | Pending — rewrite §3.2(iv) honestly as "the closed-API approximation." |
| M-R2.7 | Registry-size scaling experiment missing — at 100-500 tools, registry-list overhead dominates | R2.1, R2.3 | Pending — add small ablation on synthetic registries at \|R\| ∈ {25, 50, 100, 200}. ~40 tasks × 4 sizes = 160 runs against credits. ALTERNATIVELY: explicitly downscope claim to ≤25-tool registries (already in §7.4). |
| M-R2.8 | p99 latency tax not reported (current "<2% token overhead" claim is mean-only) | R2.1 | Pending — add latency CDF (p50/p95/p99) to §5 main table. Available from trace JSONL. |
| M-R2.9 | Operational-safety: registry-list leak on every hallucination is an information-disclosure surface in adversarial multi-tenant settings | R2.1 | **DONE** — §7.7 safety paragraph addresses ambient-function risk. R2.1's specific multi-tenant-leak angle deserves 1-2 sentences in §7. |
| M-R2.10 | TEHR taxonomy narrowness — namespace-prefix, signature, return-shape hallucinations adjacent and uncaught | R2.3 | **DONE** — §7.3 hallucination-taxonomy paragraph addresses. |
| M-R2.11 | Vendor monoculture downscope language | R2.3 | **DONE** — §7.2 generalization scope addresses. |
| M-R2.12 | Citation hygiene: 6 near-misses (StableToolBench, AgentHallu, NoisyToolBench, AgentNoiseBench, MCP-Atlas, Anthropic Agent Skills + Tool Search Tool) | R2.6 | Pending — add to refs.bib (5 of 6 already added in this turn); cite as "see also" in §2 for completeness. |

---

## What's done (this turn)

- §1 introduction draft written with multimodal bridge + headline placeholders
- §7 limitations written with: multimodal extension, generalization scope, hallucination taxonomy, registry-size scaling, latency, reproducibility, safety, what-we-do-not-claim
- §8 LLM/agent usage disclosure written
- main.tex updated to `\input` §1, §7, §8
- refs.bib: added MetaTool, CRITIC, LangChain forum #2427, StableToolBench, Anthropic Agent Skills (5 of 6 R2.6 near-misses)
- §2 Related Work: cited MetaTool with per-query→per-call differentiation; cited CRITIC with content-controlled-ablation differentiation; cited LangChain forum thread for production-pattern reference

## What still needs to ship into ADDENDUM_R2 / paper updates

1. Title rewrite (M-R2.1) — update v3.1 §2.1 + main.tex \title
2. One-sentence main result rewrite (M-R2.2) — update v3.1 §2.2 + §1 paragraph 1
3. §3.5 Mechanism Hypotheses paragraph (M-R2.3) — adds ~120 words to §3
4. Gap-closure restriction to hallucination-tagged subset (M-R2.4) — affects v3.1 §4.3 + 04_setup pre-reg
5. §3.1 rewording to exchangeability + cluster-bootstrap (M-R2.5) — minor
6. §3.2(iv) honesty rewrite (M-R2.6) — minor
7. Latency CDF column (M-R2.8) — Phase 4 task; runner already collects latency
8. Optional registry-size ablation (M-R2.7) — decide to run or downscope; current §7.4 already downscopes

## Verdict for R3

The paper has matured significantly. R3 should focus on:
- **Verify** that R1+R2 fixes have actually landed (meta-reviewer)
- **Production-grade consistency audit** across all files
- **Final salty pass** — give a tired adversarial reviewer one more shot at the polished plan
- Skip Code-quality reviewer this round unless we want a deep code-correctness audit (probably worth doing once, but can be R4)

## R3 reviewer roster (proposed, 4 personas)

1. **Meta-Reviewer**: reads R1+R2 + all fixes + the current spec; verifies concerns addressed.
2. **Production-Grade Consistency Auditor**: reads ALL files, flags inconsistencies, stale references, broken cross-doc claims.
3. **Final Salty / Adversarial-2 Reviewer**: same brief as R1.4 but on the matured plan; should land at WEAK ACCEPT or higher to indicate readiness.
4. **Code-Quality Reviewer**: reads the harness code (which now exists post-Code-A/B/C/D) for correctness, race conditions, statistical-implementation accuracy.
