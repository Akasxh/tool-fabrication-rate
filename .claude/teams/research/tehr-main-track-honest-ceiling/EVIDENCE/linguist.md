# linguist.md — claim-level honesty gate: does each framing's thesis match the paper's literal numbers/hedges?

Method: take each candidate framing's one-sentence thesis and check it against the EXACT claims and hedges in main.tex + §5/§6. A framing is DEFENSIBLE-TODAY only if its headline sentence is licensed by the paper's data WITHOUT adding a claim the paper itself hedges or disclaims.

## The paper's actual load-bearing claims (verbatim-faithful, with hedges)
- **The gap (STRONG, unhedged on direction)**: Anthropic 0/2578 (CP UB ≤0.115%); OpenAI 0/2117 (≤0.14%); Qwen3 band 0.95-1.87%; Qwen2.5-7B 6.10%. Stated as "an open-vs-closed split: zero-event commercial frontiers against the Qwen-family 0.95-1.87% band." The DIRECTION and MAGNITUDE are data-backed and replicated across 2 commercial vendors (5 OpenAI tiers + 5 Anthropic versions) and a Qwen lineage check. The ONLY hedge is causal: §7 says parameter count, 4-bit quant, recipe, guardrails co-vary — "we cannot disentangle." So: the gap as a PHENOMENON is licensed; the gap as CAUSALLY-ATTRIBUTED-to-open-weights is NOT.
- **Non-monotonic curve (HEDGED)**: "six points are not a curve"; "32B collapse should be read as not-detected at this N, not emergent capability"; "cannot yet disentangle scale from 4-bit quantization"; "we report this descriptively, not as a fitted scaling law." Heavily hedged. Cannot be a confident headline.
- **RVR (STRONG on the matched subset)**: 14/14 prevented, Fisher p=7.1e-5, survives Holm. Honest ledger note: 5 further 8B events untested. On Anthropic: zero-event preserved but strict-pass slips, TOST underpowered at N=60 → "tier-conditional deployment." Solid but scoped.
- **Format-not-content (EXPLICITLY NOT PROVEN)**: §6 and abstract: "absence of evidence, not evidence of equivalence"; CI [-1.5,+1.4]pp; "consistent with content buying up to ~1pp, not proof it buys nothing"; "a powered version... is in progress; we report no result for it here." The paper itself REFUSES to claim this. A framing that LEADS on it contradicts the paper's own honesty posture.
- **Per-call TFR (METHOD)**: positioned as extending MetaTool per-query → per-call, "the granularity gap is the point." Honest about not-apples-to-apples with prior numbers.

## Framing-by-framing honesty verdict

### H1 — "open-vs-closed tool-existence reliability gap" — DEFENSIBLE-TODAY ✅ (with one word-level constraint)
- Thesis licensed IF phrased as a measured PHENOMENON, not a causal weights-claim. SAFE: "At the per-call grain, commercial frontier APIs sit at a tool-existence-fabrication floor (≤0.14%) an order of magnitude below locally-served 4-bit open-weight models (0.95-1.87%)." UNSAFE: "open-weight models fabricate tools because they are open" (causal; §7 disclaims). The paper already uses "open-vs-closed split" in §1 and §5 — this framing is the paper's OWN language promoted to headline. No new claim required.
- Word-level rule: never write bare "0%"; always the CP upper bound. The paper already does this. A framing built on it inherits the honesty.

### H2 — "format-not-content recovery (once powered)" — NOT DEFENSIBLE-TODAY ❌
- The paper's §6 literally says it is "absence of evidence, not evidence of equivalence" and "we report no result for [the powered version] here." Leading on this REQUIRES a claim the authors have explicitly disowned in print. The "(once powered)" parenthetical in the user's own question is doing the load-bearing work — and that experiment has not landed. Until a high-event decoy cell produces a non-null contrast, this CANNOT be the headline without breaking the honesty constraint. It is a strong SUPPORTING/mechanism note phrased as a bounded result.

### H3 — "per-call diagnostic + the gap" — DEFENSIBLE but WEAK as headline
- Every word is licensed. But the metric-as-headline invites the "re-slicing of API-Bank/ToolBeHonest/MetaTool" novelty attack (the prior session found this drew "limited novelty"). Honest, just not maximally persuasive. Better as the INSTRUMENT subordinate.

### H4 — synthesis (gap = headline, TFR = instrument, RVR = fix, curve+format = bounded mechanism) — DEFENSIBLE-TODAY ✅ and MAXIMAL
- Each subordinate clause maps to a licensed claim: headline gap (H1, licensed), instrument (H3, licensed), fix (RVR, licensed-scoped), mechanism (curve + format-not-content, both carried at the paper's OWN hedge level). The synthesis does NOT require any disowned claim. This is the framing that extracts the most persuasive force while staying inside the paper's honesty envelope.

## Title/abstract language check
- Current title "Who Hallucinates Tools, How Often, and What Fixes It" — the "Who/How often/What fixes" triad is workshop-survey register and BURIES the gap. The strongest HONEST title leads with the gap as the finding. Candidates (all licensed):
  - "A Tool-Existence Reliability Gap Between Commercial and Open-Weight LLM Agents, and a Training-Free Fix" (gap-led; honest).
  - "Per-Call Tool Fabrication: A Commercial-vs-Open-Weight Reliability Gap on Multi-Turn Agents" (instrument + gap).
- AVOID any title with "format not content" or "non-monotonic scaling law" — both overclaim relative to §6/§5 hedges.

## Confidence
HIGH. This is a direct read of the paper's own sentences. The single most important linguistic finding: **the paper's text already disowns H2 as a proven result** ("we report no result for it here"), so H2-as-headline is internally contradictory with the manuscript. H1/H4 use the paper's own "open-vs-closed split" language and require no new claim. Hand to synthesist + moderator: the load-bearing contradiction is H4-defensible-today vs H5-breadth-is-binding, NOT H1-vs-H2 (H2 is eliminated by the honesty gate).
