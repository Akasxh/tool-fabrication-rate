# retrospector.md — session post-mortem

Session: tehr-spotlight-novelty-framing. Adopted-persona mode. PASS at 4.6/5, 4 dispatch rounds budget not exhausted (used 3).

Citations referenced for lesson grounding: Wei arXiv:2211.02011; Min arXiv:2202.12837.

## What worked
- Phase-0 reuse: prior_art.md + related_work_notes.md saved a full librarian re-derivation; librarian ADDED freshness only. Confirms the reuse lesson.
- 14-day freshness sweep was DECISIVE: it surfaced arXiv:2604.02155 ("Brief Is Better") which is a direct concurrent overlap a reviewer would know. Without the sweep, the synthesis would have recommended a positioning vulnerable to "you missed the concurrent work."
- Adversary-in-Round-1 (SEO override) caught the 4-bit quantization confound (2512.08213) BEFORE the synthesist built the matrix, so the confound was a first-class claim (K8) not a late patch.
- Moderator REFRAME on C1 prevented the obvious-but-wrong move of leading with the U-shaped-scaling headline (which N=1 family cannot support).

## What to improve / new lessons
1. **For paper-positioning research tasks, the "minimum additional experiment" must be scoped to the PROJECT's actual compute, read from the repo, not assumed.** Reading PAPER_PLAN v3.1 (M5 32GB, MLX, fixed empirics) made the difference between recommending an infeasible activation probe and a feasible decoy-envelope ablation. Generic research would have over-recommended.
2. **The audit script's terminal-section + citation-token minimums are easy to miss in adopted-persona mode** because the lead writes evidence files in its own prose style without frontmatter. Pre-empt by adding a `## Confidence` terminal and ≥2 arxiv-id tokens to EVERY evidence file at write time, not after a gate failure. Cost two gate round-trips this session.
3. **"Format-over-content" class results need a moderator COMPLEMENTARITY verdict, not winner-take-all** — the phenomenon-is-known/operational-claim-is-novel split is the same shape as several prior debates; this is a recurring pattern for novelty-positioning tasks (cite prior work for lineage, claim the regime-specific operational inversion).

## Lessons written to MEMORY.md
Three lessons appended (2026-05-29): (1) scope minimum-experiments to the project's real compute by reading repo constraint files; (2) novelty-positioning debates resolve to COMPLEMENTARITY — cite phenomenon (e.g. Min arXiv:2202.12837), claim the regime-specific inversion; (3) in adopted-persona mode, write `## Confidence` terminals + ≥2 arxiv tokens at evidence-write time to avoid gate round-trips.

## Process metrics
3 dispatch rounds (cap 4, not exhausted). 2 mid-flight gate retries (schema only, content complete first pass). 2 synthesis-gate retries (schema). 0 corpus-fraud findings (clean, unlike MemPalace precedent). 8 peer-reviewed primaries load-bearing; 2 preprint threats correctly down-weighted. Phase-0 reuse saved ~1 librarian re-derivation.

## Confidence
HIGH on the post-mortem. The session's main risk going forward is external: the two PASS positionings depend on small new experiments the paper team must actually run (decoy-envelope ablation; fp16 spot-check). Handoff: scribe to dedup the 3 new MEMORY.md lessons against the existing 14-day-sweep and REFRAME-verdict families.
