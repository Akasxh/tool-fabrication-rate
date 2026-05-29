# HYPOTHESES — competing framings to attack

## H1 — "The open-vs-closed tool-existence reliability gap is the headline; everything else supports it."
Lead with the cross-vendor split: commercial frontiers (Anthropic 4.x 0/2578, OpenAI 0/2117) sit at a per-call existence-failure floor an order of magnitude below the open-weight Qwen band (0.95-1.87%), and the per-call grain is what makes the gap visible where aggregate task-success hides it. The non-monotonic curve and RVR are supporting. This is the most DATA-BACKED claim (the gap is real, large, replicated across two commercial vendors + a Qwen2.5 lineage check) and the LEAST contingent on running experiments. Direct sibling of Spracklen USENIX'25's 5.2%-vs-21.7% package-hallucination gap → instant heavyweight anchor.
- **Risk**: "two-family audit on one benchmark = workshop" (the tool-eval specialist's default). The precision×family confound (API fp vs 4-bit local). Is the commercial 0 just an easy registry?

## H2 — "Format-not-content recovery (once powered)."
Lead with the C0.7/C0.8 inversion: the structured rejection FORM, not the registry CONTENT, drives recovery. The prior session's PRIMARY pick.
- **Risk (now elevated)**: the decoy ALREADY ran zero-event (0/410). The CI is [-1.5,+1.4]pp. As of today this is "absence of evidence," explicitly NOT proven. Leading on it requires the powered high-event decoy cell that is STILL RUNNING. If that cell also comes back with too few events, the headline collapses. HIGH variance. NOT defensible-today as a lead.

## H3 — "Per-call diagnostic (TFR) + the gap it exposes."
Lead with the methodological contribution: per-call existence rate is a new construct that disaggregates what BFCL/API-Bank fold into composite scores, and applying it reveals the gap + the curve. Metric-first.
- **Risk**: the prior session found the bare metric drew "limited novelty" — API-Bank already has an "API Hallucination" category; ToolBeHonest has a non-existent-tool category; MetaTool removes the correct tool. Metric-as-headline is the WEAKEST against a novelty-focused AC.

## H4 — SYNTHESIS: "A capability-tier map of tool-existence reliability + a training-free recovery that closes it, with the per-call diagnostic as the instrument."
Frame the gap (H1) as the headline FINDING, the per-call TFR (H3) as the INSTRUMENT that makes it measurable, RVR as the deployable FIX, and format-not-content + the non-monotonic curve as MECHANISM/supporting (honestly bounded). The "what changes for the field" line: open/self-hosted models — exactly the ones deployed for cost/privacy — carry a per-call existence-hallucination risk that frontier API models have effectively driven to a floor, and a training-free middleware closes it. This is the candidate that (a) leads with the most-backed claim, (b) gives the metric and fix their honest supporting roles, (c) is robust to the decoy-power risk because the bounded ablation is supporting not headline.
- **Risk**: "synthesis" can read as "no single contribution." Must be disciplined: ONE headline sentence, everything else explicitly subordinate.

## H5 (meta) — "The honest ceiling is workshop+ / weak-main-track-borderline as-is, and breadth is the binding constraint, not framing."
The ~20% main-track score may be a SCOPE verdict (one benchmark, one open family, thin events) that NO reframing fixes — only data fixes. If true, the deliverable should say plainly: the best framing buys ~X points, but the breadth experiments (2nd benchmark non-zero base + 2nd family non-monotonic) are what move it from 20%→main-track-plausible. Framing is necessary but not sufficient.
- **This is the most important hypothesis to test honestly** — it constrains how much the framing deliverable can promise.

## Prior to investigation
Lean: **H4 (synthesis led by H1's gap)** is the strongest defensible-today framing, with **H5 as the honest ceiling caveat** (framing buys points; breadth data is the binding constraint). H2 demoted from the prior session's PRIMARY because the decoy came back null. To be attacked by skeptic + the three hostile personas.
