# SCALE @ ICML 2026 Workshop Reviewer — Round 1

## Persona
SCALE PC member. Throughline: does this paper advance "Scalable Learning and Optimization for Efficient **Multimodal** AI Agents"?

## Verdict
**WEAK ACCEPT, conditional on reframing.** Fits "AI Agents" cleanly; fits "Efficient" partially; fits "Scalable" only as tier comparison; **does not fit "Multimodal" on the merits**. Workshop-fit is the dominant risk; the science is fine.

## Top-5 issues (fit-tagged)

1. **[BLOCKER — fit] Multimodal mismatch.** Workshop title: *"...Efficient **Multimodal** AI Agents."* Paper is text-only — BFCL v4 + τ-bench retail. `04_setup.tex` lines 8–10 list zero non-text modalities; v3.1 §2.1–§2.2 don't engage "multimodal." **Fix**: §1 bridge-paragraph arguing tool-use is a text↔external-system multimodal interface, OR §7 own the scope limit. The bridge is the lighter lift.
2. **[MAJOR — fit] "Scalable" is a tier comparison, not a scaling characterization.** §2.3 item 4 promises "scaling-curve evidence" but the design is 3 discrete tiers across 2 vendors — no model-size, compute, or |R| axis swept. **Fix**: add a registry-size sweep (|R|=5, 20, 50, 100 on a fixed model) OR rename "scaling-curve" → "tier-stratified."
3. **[MAJOR — fit] "Efficient" is cost-per-success arithmetic.** §2.2 promises "<2% token overhead" and "Z× lower cost-per-success" but `04_setup.tex`/`03_method.tex` don't commit to per-token compute, latency overhead, energy, or amortized multi-turn cost. API pricing conflates vendor margin with compute. **Fix**: report median/p95 added latency per RVR-triggered turn, tokens-in/out delta, and (local tier) `powermetrics` energy delta. The Qwen3-8B/M5 tier is the right vehicle and is currently underused.
4. **[MAJOR — fit] Track choice: Main vs. Benchmarking & Dataset.** v3.1 §3 targets Main. But §2.3 item 1's load-bearing contribution is *a metric* (TEHR disaggregation) and §6's controlled probe (`03_method.tex` line 47) is a *measurement instrument* — both B&D-flavored. B&D is also 7 pages (`scale_call_audit.md`: *"Maximum limit of 7 pages"*) — no page cost to switching. **Switch to B&D.** RVR becomes the demonstration that the metric supports targeted intervention; "multimodal" is structurally lighter on that track.
5. **[MINOR — fit] No "why workshop, not Main" articulated.** Honest answer: not competitive at ICML Main as scoped (N=50+25, 36h build, no head-to-head vs. Fission-GRPO/L-ICL). That's fine — it belongs at a workshop. But §1 reads as a sized-down Main paper. **Fix**: §7 should position this as *first-measurement-in-class*, ahead of a fuller scaling study.

## Specific concerns

| Axis | Fit | Evidence |
|---|---|---|
| Scalable | Partial | 3-tier comparison, no sweep |
| Learning/Optimization | Strong | RVR as inference-time intervention |
| Efficient | Partial | Token overhead + price; no FLOPs/latency/energy |
| Multimodal | **Mismatch** | Text-only |
| AI Agents | Strong | ReAct tool-using agents in scope |

Cited precedents (API-Bank EMNLP 2023, RelyToolBench ICML 2025-Main) are venue-level peers. Whether SCALE's organizing committee has published in this space is author homework. Czapla blog is the only "industry pain in 2026" anchor — keep; lean harder on it in §1.

## Required changes

- §1 bridge-paragraph from text-tool-use to multimodal agents, OR §7 own the scope limit.
- Rename "scaling-curve evidence" → "tier-stratified" unless a sweep is added.
- Report latency + (local tier) energy. Token overhead alone is not "efficient."
- **Switch Main → Benchmarking & Dataset.** Same page limit; better fit.
- One-sentence "why workshop, not Main" in §7.
- Mandatory LLM/agent-usage disclosure (`scale_call_audit.md` action 3); does not count toward 7 pages.

## Strongest contribution (workshop-relevant)

Local-tier inclusion (Qwen3-8B-4bit on Apple M5, 32 GB) directly addresses "efficient agents on consumer hardware" — on-mission. Currently buried as "feasibility panel" (`04_setup.tex` line 6, pre-reg item 12). **Promote it** — make local-tier RVR a co-headline.

## Most damaging weakness

"Multimodal" appears in the workshop title and not in the paper. A fit-conscious reviewer flags this in 60 seconds. Without a scope-bridging paragraph or B&D track switch, the paper is one reviewer from a fit-reject.

## Verdict justification

Two cheap fixes convert this from borderline to comfortable accept: (1) §1 scope-bridge paragraph, (2) track switch to B&D. Science is fine, local-tier story is on-mission, cost-quality framing is the right register. As-drafted, rigorous but mis-targeted at the workshop's stated theme.

---

**Top-3 fit issues:**
1. Multimodal mismatch — paper is text-only; workshop title says multimodal.
2. "Scalable" is a 3-tier comparison, not a scaling characterization.
3. "Efficient" lacks latency/FLOPs/energy — only token overhead and price-per-success.

**Track recommendation: Switch to Benchmarking & Dataset Track.** Same 7-page limit; TEHR + controlled distractor probe is canonical B&D, and the "multimodal" emphasis is structurally lighter on that track.
