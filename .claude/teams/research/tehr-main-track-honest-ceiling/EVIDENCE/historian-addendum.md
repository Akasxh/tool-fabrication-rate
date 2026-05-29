# historian-addendum.md — NEW related work (open-vs-closed gap lineage + 2026 tool-hallucination) — all VERIFIED against arXiv

Scope: the prior session (`tehr-spotlight-novelty-framing/EVIDENCE/historian.md`) verified the inverse-scaling + format-not-content lineage (Wei 2211.02011, McKenzie 2306.09479, Min 2202.12837, Olsson 2209.11895, Ren 2402.13055 — ALL still valid, REUSED). This addendum adds (a) the OPEN-VS-CLOSED reliability-gap lineage the NEW headline leans on, (b) 2026 tool-hallucination papers that postdate or were missed by the prior sweep. Verification = arXiv abstract fetched and quoted.

## A. Open-vs-closed (commercial-vs-open-weight) reliability/safety gap — the new headline's external anchors

### A1. Spracklen et al. — "We Have a Package for You!" — USENIX Security 2025 — VERIFIED (REUSED, still the heavyweight anchor)
- arXiv 2406.10279. 16 LLMs, 576K samples. **Commercial ≥5.2% vs open-source 21.7% hallucinated packages.** Already in refs.bib (`spracklen2025packages`) and cited in §1. This is the single best external parallel to the paper's Anthropic-0% vs Qwen-band split. KEEP load-bearing.

### A2. HalluWorld (2605.19341, 19 May 2026) — VERIFIED — NEW, directly supports H1/H4
- **Title**: "HalluWorld: A Controlled Benchmark for Hallucination via Reference World Models"
- **Authors**: Emmy Liu, Varun Gangal, Michael Yu, Zhuofu Tao, Karan Singh, Sachin Kumar, Steven Y. Feng. Submitted 19 May 2026.
- **Verbatim load-bearing sentence**: "We evaluate frontier and open-weight language models across these settings and find consistent patterns: perceptual hallucination on directly observed information is **near-solved for frontier models**, while multi-step state tracking and causal forward simulation remain difficult and are not generally solved by extended thinking. In the terminal setting, models also struggle with when to **abstain**."
- **Why it matters**: an independent, contemporaneous (10 days before this session) controlled-benchmark paper reports the SAME shape the TEHR paper reports — a class of hallucination that is *near-solved for frontier models but not open-weight*. This is corroborating prior art for the open-vs-closed framing (H1/H4). It also independently flags ABSTENTION as the hard residual, which is exactly the TEHR limitation ("TFR ignores abstention").
- **NUANCE / honesty caveat (hand to adversary)**: HalluWorld's "near-solved for frontier" is specifically about PERCEPTUAL hallucination on *directly observed* info. On multi-step state tracking BOTH frontier and open struggle. So HalluWorld does NOT say "frontier solved all hallucination" — it says one class is near-solved for frontier. Cite it as: "an independent controlled benchmark likewise finds a class of hallucination near-solved for frontier models but not open-weight." Do NOT overclaim it as a general frontier-solved result.

### A3. Safety Gap Toolkit (2507.11544, 8 Jul 2025) — VERIFIED — NEW, SUPPORTING (not load-bearing)
- **Title**: "The Safety Gap Toolkit: Evaluating Hidden Dangers of Open-Source Models". Authors: Ann-Kathrin Dombrowski, Dillon Bowen, Adam Gleave, Chris Cundy.
- **Finding**: defines a "safety gap" between intact-safeguard and stripped-safeguard open models; evaluated on **Llama-3 and Qwen-2.5 (0.5B-405B)**; "the safety gap **widens as model scale increases**."
- **Scope caveat**: GENERAL safety (biochem/cyber/refusal), NOT tool use. Use ONLY as a one-line "open-weight reliability/safety gaps are an established, scale-dependent research object (e.g. [Safety Gap Toolkit], [Spracklen])" — it shows the open-vs-closed-gap frame is recognized and that gaps can be scale-dependent. NOT a per-call-tool result. Do not lean.

## B. 2026 tool-hallucination papers — scoop-risk assessment

### B1. AgentHallu (2601.06818, 11 Jan 2026) — VERIFIED — MUST CITE (differentiate)
- **Title**: "AgentHallu: Benchmarking Automated Hallucination Attribution of LLM-based Agents". Authors: Xuannan Liu, Xiao Yang, Zekun Li, Peipei Li, Ran He.
- **Content**: 693 trajectories, 7 frameworks, 5 domains; 5-category hallucination taxonomy INCLUDING **Tool-Use** (14 sub-cats). Evaluates 13 models incl. **GPT-5, Gemini-2.5-Pro**; for BFCL V3 it uses agents based on **GPT-4.1, Qwen3-32B, Llama-3.3-70B** (overlaps the TEHR model set). Best model (Gemini-2.5-Pro) hits **41.1%** step-localization, dropping to **11.6%** on tool-use hallucinations — "tool-use hallucinations are the most challenging."
- **Relationship to TEHR**: COMPLEMENTARY, not a scoop. AgentHallu does ATTRIBUTION (which step caused a hallucination, post-hoc, judged by an LLM) on curated trajectories; TEHR does per-call EXISTENCE-RATE measurement + a PREVENTION intervention. AgentHallu confirms tool-use hallucination is the hardest agent failure class to even localize — strong MOTIVATION cite. It does NOT report a per-call tool-EXISTENCE rate, does NOT compare commercial-vs-open as a reliability gap, and does NOT propose a fix. Cite as: "tool-use hallucination is the least-tractable agent failure class [AgentHallu]."

### B2. Spectral Guardrails / "Loud Liar" (2602.08082, 8 Feb 2026) — VERIFIED — CITE (differentiate, detection-side)
- **Title**: "Spectral Guardrails for Agents in the Wild: Detecting Tool Use Hallucinations via Attention Topology". Single author: Valentin Noël.
- **Content**: training-free DETECTION via attention-spectral features. Llama-3.1-8B + Mistral-7B only (NO Qwen, NO commercial). Cross-model on matched General domain (N=1000, hallucination rates 20-22%). "Loud Liar": Llama's failures are spectrally catastrophic (98.2% recall single-feature); Mistral best AUC 0.900.
- **Relationship to TEHR**: NOT a scoop. It is a DETECTION method requiring attention access; TEHR is a behavioral PREVENTION (message-level re-prompt, no activation access). It does NOT study scaling, does NOT isolate fabrication/non-existent tools, has no commercial model. Same bucket as Healy 2601.05214 (internal-reps detection). Cite both as: "activation/attention-level detectors of tool hallucination [Healy; Noël] require model internals; RVR prevents behaviorally without logit/activation access." This sentence is ALREADY half-present in §2 (Healy) — add Noël.

### B3. Healy et al. (2601.05214, Jan 2026) — VERIFIED (REUSED) — already in refs.bib
- Internal-representation detection of tool-selection hallucination; evaluated GPT-OSS-20B, Llama-3.1-8B, Qwen-7B. Already cited (`healy2026internal`). Group with Noël (B2).

## C. Inverse-scaling / non-monotonic-hallucination lineage — new theoretical anchor

### C1. "LLMs as Noisy Channels" (2605.23901, 22 May 2026) — VERIFIED — NEW, OPTIONAL theory anchor
- **Title**: "LLMs as Noisy Channels: A Shannon Perspective on Model Capacity and Scaling Laws". Authors: Xu Ouyang, Deyi Liu, Yuhang Cai, Jing Liu, Yuan Yang, Chen Zheng, Thomas Hartvigsen, Yiyuan Ma. Submitted 22 May 2026.
- **Verbatim**: "scaling model size or data without preserving a sufficient signal-to-noise ratio (SNR) inevitably amplifies noise, inducing a transition from monotonic improvement to **U-shaped performance degradation**." Validated on Pythia/OLMo2; theory+empirical; R²=0.847 extrapolation.
- **Relevance**: a 2026 *theoretical* framework that predicts U-shaped degradation under SNR collapse, AND explicitly names "quantization-induced degradation" as a non-monotonic phenomenon it explains. DOUBLE-EDGED: (a) it offers a citable theory for why a grounding signal below capacity threshold yields U-shaped failure (supports the curve's plausibility); (b) it also LEGITIMIZES the quant-confound skeptic — it lists quantization as a cause of non-monotonicity. Net: cite it CAUTIOUSLY in the mechanism/limitations as "non-monotonic capability-vs-scale is an active, theorized phenomenon [Noisy Channels, Wei, McKenzie]" — but do NOT lean on it, and be aware it cuts both ways on the quant confound.

### C2. "U-shaped and Inverted-U Scaling behind Emergent Abilities" (2410.01692, 2024) — VERIFIED existence (REUSED from prior web-miner B-section)
- Ties U-shaped sub-task curves to apparent emergence. Secondary citation that U/inverted-U scaling is an accepted research object. Already noted by prior session.

## D. SCOOP-RISK VERDICT (the most important output of this addendum)
**No paper occupies the TEHR cell.** Searched specifically for "per-call tool-existence rate, commercial-vs-open, multi-turn traces, + a training-free fix." The closest neighbors are:
- AgentHallu (attribution, no rate, no fix) — complementary.
- Spectral Guardrails + Healy (detection via internals, no scaling, no commercial, no prevention) — complementary.
- HalluWorld (controlled hallucination benchmark, frontier-vs-open, but NOT tool-existence-specific and NO fix) — corroborating, not scooping.
- Reasoning-Trap / Brief-Is-Better (already cited; reasoning-axis non-monotonicity, not scale-axis) — already distinguished in §2.
The intersection {per-call membership × commercial-vs-open reliability gap × non-monotonic scale on open family × training-free inference-time recovery} remains UNOCCUPIED. The white-space claim from the prior session HOLDS as of 29 May 2026.

## E. What to ADD to refs.bib (verified, ready)
1. `liu2026halluworld` — HalluWorld, 2605.19341 (LOAD-BEARING support for open-vs-closed framing, with the perceptual-vs-state-tracking nuance).
2. `liu2026agenthallu` — AgentHallu, 2601.06818 (MOTIVATION: tool-use hallucination is hardest agent failure class).
3. `noel2026spectral` — Spectral Guardrails, 2602.08082 (group with Healy as detection-side neighbor to differentiate from prevention).
4. OPTIONAL `ouyang2026noisychannels` — 2605.23901 (cautious theory cite; double-edged on quant).
5. OPTIONAL `dombrowski2025safetygap` — 2507.11544 (one-line "open-weight gaps are scale-dependent and recognized").

## Confidence
HIGH on all five new citations (abstracts fetched and quoted). HIGH on the scoop-risk verdict (targeted negative search returned only marketing blogs + complementary papers). The HalluWorld nuance (perceptual-near-solved ≠ all-hallucination-solved) is flagged for the adversary so the synthesis does not overclaim it.
