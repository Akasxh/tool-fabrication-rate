# web-miner-addendum.md — 14-day fresh-window scoop scan (mid-to-late May 2026)

Mandate (MEMORY.md "newest 14 days" lesson — non-discretionary on fast-moving topics): scan the window around/after the prior session (2026-05-29) for ANY new tool/function-hallucination, open-vs-closed-gap, or quant-confound paper a hostile reviewer would cite to scoop or undercut. Tool-hallucination is producing weekly arXiv submissions → mandatory.

## Fresh-window hits (May 2026 submissions), with scoop verdict

| Paper | arXiv | Date | What it is | Scoop verdict |
|---|---|---|---|---|
| HalluWorld | 2605.19341 | 19 May 2026 | Controlled hallucination benchmark, frontier-vs-open, gridworld/chess/terminal | NOT a scoop. Corroborates open-vs-closed gap. No tool-existence rate, no fix. CITE as support (see historian-addendum A2). |
| LLMs as Noisy Channels | 2605.23901 | 22 May 2026 | Shannon-SNR theory of U-shaped scaling incl. quantization | NOT a scoop. Theory anchor (double-edged on quant). Optional cite (historian-addendum C1). |
| Hallucination Detection via Open-Weight Proxy Analyzers | 2605.07209 | May 2026 | Small open model detects hallucination in text output of another | NOT relevant. Text-hallucination detection, not tool existence. SKIP. |
| PARALLAX | 2605.17028 | May 2026 | "Separating genuine hallucination detection from benchmark-construction artifacts" — 22 methods, 12 open models | TANGENTIAL but instructive: it is a METHODOLOGICAL-SKEPTIC paper warning that hallucination benchmarks measure construction artifacts. A hostile reviewer could invoke its SPIRIT ("is your 0% just an easy-registry artifact?"). Not a scoop, but its critique-style is a threat the synthesis should pre-empt. SKIP as cite; NOTE as a reviewer-mindset risk. |

## What did NOT appear (the important negatives)
- **No "per-call tool-existence rate, commercial-vs-open" paper** in the window. Targeted query returned only PricePerToken / CallSphere / Codersera marketing blogs (REJECTED — SEO).
- **No "RVR-like training-free tool-not-found re-prompt with a content ablation"** paper. The LangChain forum thread (`langchain_toolnotfound2025`, already cited) remains the only public structured-tool-not-found prior, and it explicitly stops short of listing tools (= the paper's C0.7/C1 contrast). HOLDS.
- **No second-family non-monotonic tool-EXISTENCE scaling curve.** Spectral Guardrails (2602.08082) touches Llama+Mistral tool hallucination but is detection, not scaling, not existence-specific (historian-addendum B2). The paper's own running 2nd-family experiment (Llama/Mistral/Qwen2.5) is NOT pre-empted.

## Landscape note (model churn, May 2026) — relevant to the precision×family confound rebuttal
Marketing/news sources (latent.space, VentureBeat — NOT citable for numbers, used only for landscape) indicate the open/closed line is blurring: Qwen 3.7-Max is now CLOSED-weights/API-only, Kimi K2.6 etc. This is a DOUBLE-EDGED point for the framing:
- (+) It makes "commercial-vs-open-weight" a live, contested 2026 axis → topical.
- (−) A reviewer may note the paper's "open" family (Qwen3 4-bit MLX) vs "commercial" (Anthropic/OpenAI API) split is partly a DEPLOYMENT/precision split, not a pure weights-availability split. The honest framing must say "we compare API-served commercial frontiers against locally-served 4-bit open-weight models" and own that precision + serving stack co-vary with weights-availability (this is already in §7 limitations). Do NOT claim a pure "open-weights-as-such" causal effect.

## Provenance note
All scoop-verdict-relevant papers (HalluWorld, Noisy Channels, AgentHallu, Spectral Guardrails) were VERIFIED by direct arXiv abstract fetch (see historian-addendum). Marketing blogs are landscape-only, never cited.

## Confidence
HIGH that no academic scoop landed in the 14-day window. HIGH that the {per-call existence × commercial-vs-open × fix} cell is unoccupied. MEDIUM-flagged risk: PARALLAX-style "is your benchmark measuring an artifact?" skepticism is a reviewer mindset the synthesis should pre-empt (the easy-registry attack), even though no specific paper scoops.
