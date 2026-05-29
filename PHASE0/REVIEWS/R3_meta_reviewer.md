# Meta-Reviewer — Round 3
*Persona: ICML Area Chair, rebuttal/revision phase. Audit-only, fair. R1+R2 fix-list is the spec.*

## R1 BLOCKER status (from R1_synthesis §"BLOCKERS")

| # | Item | Verdict | Evidence |
|---|---|---|---|
| B1 | Multimodal bridge in §1+§7 | **ADDRESSED** | `paper/sections/01_introduction.tex:10` ("Tool registries are the substrate of multimodal AI agents..."); `paper/sections/07_limitations.tex:6-7` ("Multimodal extension"). Track switch declined; bridge accepted as deflection — see `ADDENDUM_R1.md:8-16`. |
| B2 | TOST 1pp → 5pp | **ADDRESSED** | `paper/sections/04_setup.tex:22` (pre-reg #3, 5pp margin, with explicit "TOST at 1pp would require ~1100 paired observations" justification); `ADDENDUM_R1.md:57-58`. |
| B3 | Contribution #1 reframe | **ADDRESSED** | `paper/sections/01_introduction.tex:20` collapses #1+#4 into "Benchmark + Metric + Mechanism" (3 contributions); `ADDENDUM_R1.md:46-51`. |
| B4 | Gap-closure variance + denom-near-zero policy | **ADDRESSED** | `paper/sections/04_setup.tex:33` (pre-reg #14): restriction to hallucination-tagged C0-failed subset, BCa cluster-bootstrap CI, denom $\leq$ 5pp ⇒ undefined-for-resample. `ADDENDUM_R1.md` §C.2/C.3 wires BCa + cluster bootstrap into harness. |
| B5 | §6 probe redesign (matched controls + drop "causal" + N=100) | **ADDRESSED** | `paper/sections/03_method.tex:55-65` — N=100, 4 distractor types incl. "matched-random" controlling registry-size+1 confound, Friedman+Nemenyi, "controlled comparison rather than a causal claim" (line 18 of §1, line 65 of §3). Causal language scrubbed. |
| B6 | C0.7 baseline added | **ADDRESSED** | Four conditions in `paper/sections/03_method.tex:42` and `paper/sections/04_setup.tex:14`; primary test is C1 vs C0.7. `ADDENDUM_R1.md:28-38`. |
| B7 | Explicit power calc in §4.4 | **ADDRESSED** | `paper/sections/04_setup.tex:29` (pre-reg #10): TEHR=10%, N=100, pooled across 4 tiers, b+c≈40, 80% power at α=0.05 for ΔPass≥20pp; ADDENDUM C.8. |
| B8 | FWER family scope | **ADDRESSED** | `paper/sections/04_setup.tex:27` (pre-reg #8): Holm-Bonferroni restricted to 3 named primary tests (pooled McNemar, TOST, Friedman); per-tier breakdowns explicitly exploratory/no FWER. `ADDENDUM_R1.md:88-94`. |

## R1 MAJOR status (representative sample)

| # | Item | Verdict | Evidence |
|---|---|---|---|
| M1 | McNemar at b+c<10 unstable — pool across tiers | **ADDRESSED** | `04_setup.tex:14,27` pool BEFORE test; ADDENDUM C.4. |
| M2 | BCa instead of percentile | **ADDRESSED** | `04_setup.tex:28` pre-reg #9; ADDENDUM C.2. |
| M3 | Friedman + Nemenyi for probe | **ADDRESSED** | `03_method.tex:65`; `04_setup.tex:32` pre-reg #13. |
| M5 | Cluster-bootstrap by task | **ADDRESSED** | `04_setup.tex:28`; ADDENDUM C.3. |
| M6 | MLX HF SHA pin + mirror | **ADDRESSED** | `04_setup.tex:40`; ADDENDUM D.3. |
| M7 | Lock decoding params | **ADDRESSED** | `04_setup.tex:6,34` (temperature=0.0, top_p=1.0); ADDENDUM D.1. |
| M11 | Czapla weight reduction (lead with API-Bank 61.4%) | **PARTIALLY ADDRESSED** | `02_related_work.tex:35-37` cites API-Bank's 61.4% in the prior-metrics paragraph, but §1 hook (`01_introduction.tex:8`) still names Czapla in the same lead sentence as API-Bank/RelyToolBench. ADDENDUM E.1 specified "lead with API-Bank's 61.4% rate"; §1 hook does not lead with that number. Easy fix. |
| M14 | Latency/tokens-per-success columns | **PARTIALLY ADDRESSED** | `07_limitations.tex:23` mentions "wall-clock distribution (mean and tail) in the appendix"; ADDENDUM E.3 promises latency-per-task + tokens-per-success columns in §5 main table, but §5 is still a TODO (`main.tex:47-51`). Cannot verify until Phase 5. |

## R2 BLOCKER status

| # | Item | Verdict | Evidence |
|---|---|---|---|
| B-R2.1 | MetaTool cited | **ADDRESSED** | `02_related_work.tex:37-49` cites `huang2024metatool` with explicit per-query→per-call differentiation. `refs.bib:145`. |
| B-R2.2 | CRITIC cited | **ADDRESSED** | `02_related_work.tex:64-75` cites `gou2024critic` as method-shape neighbor with content-controlled-ablation differentiation. `refs.bib:155`. |
| B-R2.3 | LLM-disclosure section | **ADDRESSED** | `paper/sections/08_llm_disclosure.tex` (5 paragraphs, full disclosure); `\input` in `main.tex:59`. |
| B-R2.4 | §7 safety paragraph | **ADDRESSED** | `paper/sections/07_limitations.tex:28-30` (§7.7 "Safety and ambient-function risk", names `read_secret()` example, executor allow-listing recommendation). |
| B-R2.5 | C0.7 strawman renamed to "idealized structured-error baseline" | **PARTIALLY ADDRESSED** | `01_introduction.tex:14,20` renamed correctly to "idealized structured-error baseline". **However** `03_method.tex:42` still calls C0.7 a "framework-default structured-error feedback" and "approximating LangChain's default tool-call-validation error path"; `04_setup.tex:14` says "framework-style structured error feedback"; `ADDENDUM_R1.md:35,50` still says "Framework-style"/"production-default". The rename did not propagate beyond §1. R2 BLOCKER explicitly required §1+§3+ADDENDUM all renamed. Gap is small but real. |

## R2 MAJOR status (representative sample)

| # | Item | Verdict | Evidence |
|---|---|---|---|
| M-R2.1 | Title — phenomenon-first, number-front | **ADDRESSED** | `main.tex:26-28` matches R2.5's exact rewrite ("Tool-Existence Hallucination in LLM Agents: A Per-Call Metric and a Training-Free Fix That Closes [Y]\% of the Cost-Quality Gap"); `PAPER_PLAN_v3.1.md:34`. |
| M-R2.2 | One-sentence main result rewrite | **ADDRESSED** | `PAPER_PLAN_v3.1.md:39` exact R2.5 string; §1 paragraphs 3-4 carry the [X]/[Y]/[Z] placeholders to be filled Phase 5. |
| M-R2.3 | §3.5 mechanism hypotheses pre-registered | **ADDRESSED** | `03_method.tex:44-53` — three named hypotheses (M-Retrieve, M-Constrain, M-Metacog), each with a pre-registered §6-favoring prediction. |
| M-R2.4 | Gap-closure restricted to hallucination-tagged subset | **ADDRESSED** | `04_setup.tex:33` (pre-reg #14) explicitly restricts headline ratio to that subset; unrestricted version is secondary descriptive. |
| M-R2.5 | §3.1 weaken i.i.d.→exchangeability + cluster-bootstrap | **PARTIALLY ADDRESSED** | `03_method.tex:11` still says "cleaner asymptotics" without weakening to exchangeability; cluster-bootstrap is wired in `04_setup.tex:28` and ADDENDUM C.3 but the §3.1 metric prose was not rewritten. R2.2 specifically asked for §3.1 rewording. |
| M-R2.6 | §3.2(iv) honesty rewrite (token-level dominates message-level) | **ADDRESSED** | `03_method.tex:53` adds "We acknowledge that token-level constrained decoding (when logit access is available) strictly dominates message-level RVR; the mechanism-hypothesis framing characterizes the closed-API regime in which RVR is deployable." Inserted at end of §3.5. |
| M-R2.7 | Registry-size scaling — run or downscope | **ADDRESSED** (via downscope) | `07_limitations.tex:17-19` (§7.4 Registry-size scaling) downscopes to 5–25 tools and acknowledges enterprise-tail risk. R2 synthesis allowed downscope. |
| M-R2.8 | p99 latency tax | **PARTIALLY ADDRESSED** | `07_limitations.tex:22-23` acknowledges p99 trade-off but no CDF/p50/p95/p99 column committed in §5; hangs on Phase-5 results table. |
| M-R2.9 | Multi-tenant registry-list leak (specific angle) | **PARTIALLY ADDRESSED** | `07_limitations.tex:28-30` covers ambient-function risk but does not name the multi-tenant information-disclosure angle from R2.1. 1–2 sentences would close it. |
| M-R2.10 | Hallucination-taxonomy narrowness | **ADDRESSED** | `07_limitations.tex:13-15` (§7.3) names namespace-prefix, argument-signature, return-shape modes. |
| M-R2.12 | Citation hygiene (6 near-misses) | **PARTIALLY ADDRESSED** | MetaTool, CRITIC, LangChain forum, StableToolBench, Anthropic Agent Skills present in `refs.bib`. AgentHallu, NoisyToolBench, AgentNoiseBench, MCP-Atlas, Anthropic Tool Search Tool not verified in this audit. R2 synthesis says "5 of 6 already added"; ≥1 still pending. |

---

## Items still NOT-ADDRESSED or PARTIAL

1. **B-R2.5 — C0.7 rename incomplete.** §3 method, §4 setup, ADDENDUM_R1 still use "framework-default"/"framework-style"/"production-default" language. Rename did not propagate beyond §1. **PARTIAL.**
2. **M11 — Czapla weight reduction.** §1 hook still leads with combined Czapla+API-Bank+RelyToolBench citation cluster, not API-Bank's 61.4% number. **PARTIAL.**
3. **M-R2.5 — §3.1 i.i.d. → exchangeability rewording.** Prose at `03_method.tex:11` retains "cleaner asymptotics" framing the R2 theory reviewer flagged as false. **PARTIAL.**
4. **M-R2.9 — Multi-tenant leak specific angle.** Safety paragraph addresses ambient-function but not multi-tenant info-disclosure surface. **PARTIAL.**
5. **M14 — Latency/tokens-per-success in §5 table.** Cannot be verified pre-Phase-5; ADDENDUM E.3 makes the commitment but the deliverable is unwritten. **PARTIAL (deferred).**
6. **M-R2.8 — p99 latency CDF column.** Same status as M14 (deferred to Phase 5). **PARTIAL (deferred).**
7. **M-R2.12 — Citation hygiene** (≥1 of 6 near-misses unverified). **PARTIAL.**

R1 MINOR `m1` (1-paragraph "TEHR is X renamed" pre-emptive defense) explicitly deferred to Phase 5 polish per R1 synthesis line 108; treating as **SUPERSEDED** for R3.

## Aggregate verdict

- **R1 fix completion**: 8/8 BLOCKERs **ADDRESSED** (100%). Of the MAJOR sample audited (M1, M2, M3, M5, M6, M7, M11, M14): 6/8 **ADDRESSED** (75%), 2/8 **PARTIAL** (25%, M11 and M14), 0 NOT-ADDRESSED. Several other MAJORS (M4 registry length×ordering, M12 k-retry, M13 scaling/downscope, M15 local-tier reframe, M16 mid-p clamp) flow into harness/results work and were not surfaced in the section-level prose audit.
- **R2 fix completion**: 4/5 BLOCKERs **ADDRESSED** (80%); 1/5 **PARTIAL** (B-R2.5 rename). Of the MAJOR sample audited (M-R2.1, M-R2.2, M-R2.3, M-R2.4, M-R2.5, M-R2.6, M-R2.7, M-R2.8, M-R2.9, M-R2.10, M-R2.12): 7/11 **ADDRESSED** (64%), 4/11 **PARTIAL** (M-R2.5, M-R2.8, M-R2.9, M-R2.12).
- **Combined**: every BLOCKER is at least partially addressed; the two PARTIAL items (M11 and B-R2.5) are local prose-rename gaps, not structural.

**Verdict: READY-AFTER-3-FIXES.** The plan and sections are reviewer-defensible on substance. Three small text touch-ups close the remaining gaps; none require new compute, new citations, or analytic redesign. Phase-5 deferrals (M14, M-R2.8) are appropriately gated on results.

## Top-3 unaddressed items (priority order)

1. **B-R2.5 finish the C0.7 rename.** Replace "framework-default / framework-style / production-default" with "idealized structured-error baseline" in `paper/sections/03_method.tex:42`, `paper/sections/04_setup.tex:14`, `ADDENDUM_R1.md:35,50`. ~10 minute fix; closes a R2 BLOCKER cleanly.
2. **M11 lead §1 hook with API-Bank's 61.4% number, demote Czapla to footnote-style.** `paper/sections/01_introduction.tex:8` first sentence currently buries the heavyweight precedent. ADDENDUM E.1 promised it; §1 didn't apply it.
3. **M-R2.5 §3.1 metric-prose rewrite.** Replace "cleaner asymptotics" at `paper/sections/03_method.tex:11` with explicit exchangeability + cluster-bootstrap framing. The harness already implements cluster-bootstrap; the §3.1 prose is now the only place still asserting i.i.d.

(Also, but lower priority: M-R2.9 add 1–2 sentences naming the multi-tenant information-disclosure angle in §7.7; M-R2.12 verify final near-miss citation.)
