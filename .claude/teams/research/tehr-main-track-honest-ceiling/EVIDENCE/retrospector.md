# retrospector.md — session post-mortem

## What this session did
Re-decided the main-track framing for the TEHR/RVR paper under a HONESTY constraint, after a prior session (`tehr-spotlight-novelty-framing`, PASS 4.6) had recommended a format-not-content lead that the subsequent reality (decoy ran null; panel scored the lead 14%) invalidated. Delivered: gap-led synthesis framing; 5 verified new citations; +1-page allocation; honest ceiling (workshop+→borderline) with the 2nd-benchmark gap reproduction as the single highest-leverage lift.

## What worked
- **Reuse discipline.** Inventoried the prior workspace first; REUSED 7 verified evidence files (saved ~20+ citation re-verification calls). Wrote addenda (historian-addendum, web-miner-addendum, adversary-addendum) instead of rewriting.
- **Reading the project's own ground truth.** PROGRESS.md contained the decisive datum (format-not-content scored 14% vs 18%) that settled the framing question empirically, not just on honesty grounds. The live STATUS.tsv confirmed the decoy state. This beat any amount of abstract reasoning.
- **14-day sweep was productive** (HalluWorld is 10 days old, directly corroborates the headline). Non-discretionary on this fast-moving topic — paid off.
- **Triple-persona convergence** as a signal: when three independently-written hostile reviewers name the SAME cure (2nd benchmark), that is structural, not idiosyncratic. High-confidence output.

## What was hard / could improve
- The prior session's SYNTHESIS was STALE in a specific, non-obvious way: its recommendation was contingent on a pending experiment ("once the decoy proves it") that later came back null. Detecting this required reading PROGRESS.md, not just the prior SYNTHESIS. A naive reuse would have re-recommended the now-falsified format-not-content lead.

## Lessons (candidate, for MEMORY.md)

### LESSON A — When a prior session's recommendation is contingent on a PENDING experiment, re-check whether that experiment landed before reusing the recommendation
- **Observed**: tehr-main-track-honest-ceiling (2026-05-29). Prior session recommended "lead with format-not-content (once the decoy proves content is decorative)." The decoy later ran zero-event (0/410) → "proven" never happened, and a panel scored the lead 14%. Reusing the prior SYNTHESIS verbatim would have re-recommended a falsified framing.
- **Failure mode**: FM-3.1 (premature termination) + stale-reuse variant of FM-1.3.
- **Rule of thumb**: REUSE a prior session's EVIDENCE (verified citations, corpus audits) freely, but a prior session's RECOMMENDATION that is conditioned on a future result ("once X proves Y") must be re-validated against what X actually returned. Read the project's live status/progress artifacts (STATUS.tsv, PROGRESS.md, queue logs) before adopting any contingent recommendation. Evidence reuses; conclusions expire when their premises resolve.
- **Bounds**: unconditional prior conclusions (verified facts, citation tiers) do not expire and reuse normally.

### LESSON B — The team's own A/B / panel history is a first-class evidence source for framing decisions
- **Observed**: same session. PROGRESS.md recorded that the format-not-content lead had ALREADY been panel-tested and scored 14% vs 18% bounded-honest. This settled the framing question more decisively than any abstract honesty argument.
- **Failure mode**: FM-2.2 (failure to ask/seek available internal evidence).
- **Rule of thumb**: for "how should we frame/position X" questions on a project with a revision history, GREP the project's own progress/log/retro artifacts for prior A/B results, panel scores, and walk-backs BEFORE reasoning from first principles. The team may have already run the experiment you are about to recommend. Empiricist should always read PROGRESS.md / commit log on a positioning question.
- **Bounds**: only applies when such history exists; greenfield questions have none.

### LESSON C — Convergence of independently-authored adversarial personas is a high-confidence signal; divergence is the interesting case
- **Observed**: same session. Three hostile personas (13/14/15, authored separately by the user) independently named "2nd benchmark with non-zero base" as the single cure. Triangulated → HIGH confidence it's the binding constraint.
- **Rule of thumb**: when running a multi-persona adversarial gate, explicitly look for CONVERGENCE (all personas name the same gap → structural, high-confidence) vs DIVERGENCE (personas disagree → route to moderator). Convergence across independently-authored personas is stronger evidence than any single persona's verdict.
- **Bounds**: only if the personas are genuinely independent (different authors/lenses); echo-chamber personas don't triangulate.

## Confidence
HIGH that Lessons A and B are novel and generalize (they are about reusing across sessions when premises resolve, and mining project history — both recurring in a multi-session research program). Lesson C refines the existing moderator/skeptic doctrine.
