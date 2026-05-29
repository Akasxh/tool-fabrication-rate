# QUESTION — Strongest DEFENSIBLE main-track framing for the TEHR/RVR paper given HONEST results

## Raw prompt (verbatim)
> Find the strongest DEFENSIBLE main-track framing for an ICML paper, given its HONEST (not overclaimed) results. Paper: /Users/cero/Desktop/PROJECTS/icml/paper/ (read main.tex + sections). It defines a per-call Tool Fabrication Rate (TFR = invoking a tool absent from the registry); finds commercial models (Anthropic 4.x 0/2578, OpenAI gpt-4.1/4o tiers 0/2117) never fabricate while open-weight 4-bit Qwen3 does, non-monotonically in scale (peak 1.87% @14B); proposes RVR (re-prompt with tool_not_found envelope), which clears all fabrications; a content-vs-format ablation is bounded (no detectable content effect, CI [-1.5,+1.4]pp — honestly NOT claimed as proven). A hostile panel scored the honest version ~20% main-track (clear workshop accept), capping main-track on TWO gaps: (a) the content/format ablation needs EVENTS under it (powered decoy ablation, running now), (b) breadth — a 2nd benchmark with non-zero base + a 2nd open family (running: Llama/Mistral/Qwen2.5).
>
> Deliver (write to .../research/POSITIONING_v2.md): (1) the single strongest HONEST framing/thesis for main-track given these results — is it "commercial-vs-open-weight tool-existence reliability gap", "format-not-content recovery (once powered)", "per-call diagnostic + the gap", or a synthesis? (2) any RELEVANT related work we're missing (search 2024-2026 arxiv for tool-existence/function-call hallucination, open-vs-closed reliability gaps, the inverse-scaling lineage) — give verifiable citations. (3) exactly how to spend the +1 camera-ready page for maximum reviewer-impact. (4) the honest ceiling and what single result would most raise it. Verify all citations against arxiv before listing. Be rigorous, not promotional.

## Assumed interpretation (labeled — proceeding without bouncing back)
- This is a CAMERA-READY paper already ACCEPTED to the SCALE workshop @ ICML 2026 (de-anon, `[accepted]`). The branch is `camera-ready-spotlight`. The user is NOT asking "how do I get this into the workshop" (done). They are asking: **what is the honest framing that maximizes a future MAIN-TRACK resubmission's odds**, given (i) the workshop camera-ready as-is and (ii) two breadth/power experiments running NOW.
- "Defensible" is the operative constraint. The user has explicitly walked back overclaims in prior commits (commit 4641590 "Honest walk-back"). They do NOT want a promotional framing that a hostile AC dismantles. The deliverable must survive the three NEW hostile personas they wrote: `14_main_track_area_chair`, `15_quant_confound_skeptic`, `13_tool_eval_specialist`.
- The decoy ablation (C0.8) has ALREADY RUN per the current paper (0/410, §6). So "format-not-content (once powered)" is contingent on a NOT-YET-EXISTING high-event powered decoy cell. The honest framing today cannot lead on a proven content-decorative claim.
- A prior research session (`tehr-spotlight-novelty-framing`, PASS 4.6/5, 2026-05-29) answered the adjacent "most novel/spotlight framing" question. Its prior-art (Wei/McKenzie/Min/Olsson/Ren/Spracklen/BFCL/Cao, all VERIFIED) is REUSED here. But its PRIMARY recommendation (lead with format-not-content) is now partially STALE: the decoy came back null. This session re-decides the framing under the honest/defensible constraint and the explicit two-gap cap, and runs a fresh 2024-2026 related-work sweep for anything the prior session missed.

## Sub-questions
1. **(Framing)** Among the four candidate theses — (A) commercial-vs-open-weight tool-existence reliability gap, (B) format-not-content recovery once powered, (C) per-call diagnostic + the gap, (D) a synthesis — which is the single strongest framing that is DEFENSIBLE GIVEN HONEST RESULTS TODAY, and how does its defensibility change conditional on the two running experiments landing?
2. **(Defensibility stress)** For the leading framing, what does each of the three hostile personas (main-track AC, quant-confound skeptic, tool-eval specialist) attack, and does the honest evidence have a rebuttal that survives? Which attacks are FATAL-without-new-data vs survivable-today?
3. **(Missing related work — 14-day + lineage sweep)** Searching 2024-2026 arXiv: (a) tool-existence / function-call / tool-name hallucination papers; (b) open-vs-closed (commercial-vs-open-weight) reliability/safety/hallucination gap papers; (c) inverse-scaling / U-shaped lineage relevant to a per-call existence rate. What load-bearing or threat citations are MISSING from refs.bib, and are they real (verified against arXiv)?
4. **(What shipped in the last 14 days?)** Explicit fresh-window scan (mid-to-late May 2026): any new tool-hallucination, open-vs-closed-gap, or quantization-confound paper published since the prior session (2026-05-29 was the prior session date — sweep the window around and after it) that a hostile reviewer would cite to scoop or undercut the paper?
5. **(+1 page spend)** Camera-ready allows one extra page (body is 7pp of 8 allowed per commit log; +1 page → main-track resubmission has room). Exactly what content, in priority order, maximizes reviewer-impact: which table/figure/control/paragraph buys the most defensibility per column-inch?
6. **(Honest ceiling)** What is the realistic main-track acceptance ceiling for the paper AS-IS (honest, two gaps open), and what SINGLE result — among {powered decoy with events, 2nd benchmark non-zero base, 2nd open family reproducing non-monotonicity, fp16 quant control, exploitability/collision probe} — most raises that ceiling, and by how much (qualitatively)?
7. **(Title/abstract)** Given the chosen framing, what should the title and abstract lead with? (The current title "Who Hallucinates Tools, How Often, and What Fixes It" is workshop-survey-flavored.)

## Acceptance criteria
- A single, named, defensible main-track thesis with a one-sentence statement, NOT a menu.
- Every NEW citation verified against arXiv (id + title + venue) before listing; threats tagged REPORTED-NOT-VERIFIED if a primary couldn't be fetched.
- A concrete +1-page allocation (what goes where), prioritized.
- An honest ceiling estimate (qualitative %), the single highest-leverage result, and conditional re-estimates.
- Survives the three hostile personas. No claim the paper's honest data does not support.

## Known constraints
- HONESTY is binding. No overclaim. The CI [-1.5,+1.4]pp on content effect stays a bound, not a proof. 0% stays a Clopper-Pearson upper bound, never bare 0%.
- Single quantization (4-bit MLX) on the open family; API (full-precision) on commercial — a precision×family confound is live.
- Single benchmark (BFCL v4 multi-turn). 2nd benchmark + 2nd family running but NOT landed.
- Total signal is ~14-19 Qwen3 C0 events — thin.
- Deadline context: workshop camera-ready is the immediate artifact; main-track is the forward target.
