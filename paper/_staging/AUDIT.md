# Camera-ready bulletproofing audit

Paper: `/Users/cero/Desktop/PROJECTS/icml/paper/` (main.tex + sections/*.tex)
Ground truth regenerated via `scripts/aggregate_all.py` (→ `PHASE0/RESULTS/headline_numbers.json`)
and `scripts/run_stats_full.py` (→ `paper/_staging/stats_full.json`, `stats_table.md`).
Audit date: 2026-05-29. READ-ONLY (no edits applied).

## Executive summary

The paper has **diverged from its own aggregator**. Additional Qwen3-8B and Qwen3-14B
probe runs were added to `results/` after the prose was frozen, but the headline
TFR curve, the RVR matched-subset table, and the Fisher statistics in the paper
still carry the **previous snapshot's numbers**. Re-running `aggregate_all.py` +
`run_stats_full.py` today does **not** reproduce the paper's headline figures
(1.87%, 14/973, p=7.1e-5). This is the dominant class of defect and is a BLOCKER:
the appendix explicitly claims "Running `python scripts/aggregate_all.py` ...
reproduces every numerical claim," which is currently false.

Secondary: the unit-test count is wrong (153, not 144) in three places; several
Clopper–Pearson bounds and the total cost are stale/understated; one regime
per-cell bound is materially wrong (8.22% vs the claimed 3.63%).

All `\cite*` keys resolve in `refs.bib`; all six spot-checked 2026 arXiv IDs are
real; all four referenced figure files exist; LaTeX log shows no undefined
refs/citations/labels (only benign font-substitution warnings).

---

## BLOCKERS

### B1. Qwen3-14B curve cell is stale — cascades to the headline "1.87%"
The 14B `synonym` cell was re-run (n roughly doubled, +1 event). Fresh aggregator:

| cell | paper | fresh aggregator |
|---|---|---|
| 14B synonym | 5/69 | **6/138** |
| 14B pooled | 5/268 (1.87%) | **6/337 (1.78%)** |

Every other curve cell in Table `tab:qwen3-scale` reconciles exactly; only 14B is wrong.
Fix: set 14B synonym = 6/138, 14B pooled = 6/337, and change the headline "1.87%"→"1.78%"
everywhere. Occurrences of the stale 1.87% / 5/268:
- `main.tex:90` abstract "to $\mathbf{1.87\%}$ at $14$B"
- `sections/01_introduction.tex:55` "peak at $\mathbf{1.87\%}$ at $14$B"
- `sections/01_introduction.tex:62` "bracket the $1.87\%$ peak"
- `sections/01_introduction.tex:92` "$0.95$--$1.87\%$ band"
- `sections/05_results.tex:101` "$1.87\%$ to $0\%$ ... central ... result"
- `sections/05_results.tex:105` "($5/268=1.87\%$)"
- `sections/05_results.tex:127` table row `14B & 0/63 & \textbf{5/69} & 0/67 & 0/69 & 5/268`
- `sections/05_results.tex:146` "$0.95$--$1.87\%$ band"
- `sections/05_results.tex:168` "($2/210$, $3/226$, $9/615$, $5/268$)" — last term → 6/337
- `sections/A1_appendix.tex:89` priorart headline "$\mathbf{0\%}$--$\mathbf{1.87\%}$"
- `sections/A1_appendix.tex:129` coverage table "14B ... \pmark\,268" → 337

Note the band lower bound "0.95%" is also stale: fresh per-size point estimates
(stats_table curve) are 1.7B=0.95%, 4B=1.33%, 8B=1.46%, 14B=1.78%. The 0.95% still
holds as the 1.7B point, so the band "0.95–1.78%" is fine after the upper fix.

### B2. RVR matched-subset table is unreproducible — 14/973 should be 20/1388, p changes
`scripts/run_stats_full.py` (canonical) now reports the headline Fisher as:

> **Headline Fisher (nonzero C0 tiers): p = 2.919e-05, C0=20/1388 → C1=0/945**

The paper prints **14/973 vs 0/945, p = 7.1e-5** everywhere. The C1 side (0/945)
still reconciles; the C0 side (events and denominator) and the p-value do not.
Root cause: the script pools *all* C0 probe calls for the nonzero tiers (8B C0 is
now 615+ across arms, 14B C0 now 337), whereas the paper's hand-curated "paired"
cells (8B 4/269, 14B 5/268) correspond to an earlier data snapshot and to no
current code path. Table `tab:rvr-validation` cells 8B `4/269` and 14B `5/268`
cannot be regenerated.

Affected locations:
- `main.tex:74-75` abstract "all fourteen ... $14/973$ vs.\ $0/945$ ... $p=7.1\times10^{-5}$"
- `sections/01_introduction.tex:20` "removes all fourteen"
- `sections/01_introduction.tex:72-73` "all fourteen ... $14/973$ vs.\ $0/945$ ... $p=7.1\times10^{-5}$"
- `sections/05_results.tex:158` subsection title "$14 \to 0$ events"
- `sections/05_results.tex:164-173` "$945$ matched calls ... all $\mathbf{14}$ of $\mathbf{14}$ ...
  logs $19$ events ... matched RVR subset covers $14$ ... other $5$ ... ($4/269$) ... $14$-event"
- `sections/05_results.tex:189-194` table cells: 8B `4/269`, 14B `5/268`, Pooled `14/973`
- `sections/05_results.tex:179-180` caption "8B $4/269$" and "8B $9/615$"
- `sections/05_results.tex:233-234` "pooled $14/973$ vs.\ $0/945$ ... $p = 7.1\times10^{-5}$"

Required decision (author): either (a) adopt the script's canonical pooled
contrast (20/1388 vs 0/945, p=2.92e-5) and rewrite the "all 14 of 14 prevented"
narrative — note prevention count is now 20, and the 8B/14B per-tier paired cells
need recomputation against current traces — or (b) re-pin the aggregator/traces to
the snapshot the prose was written against and document it. Until one is done,
the appendix reproducibility claim (B3) is false.

### B3. "144 unit tests" is wrong — the suite has 153
`harness/.venv/bin/python -m pytest harness/tests` → **153 passed, 1 warning**.
The paper claims 144 in three places:
- `sections/01_introduction.tex:102` "harness with $144$ unit tests"
- `sections/04_setup.tex:42` "holds the harness, $144$ unit tests"
- `sections/A1_appendix.tex:160` "full harness ($144$ unit tests)"
- `sections/08_llm_disclosure.tex:19` "its $144$ unit tests"
Fix: change all four to 153 (or to the exact count at submission).

### B4. Appendix reproducibility claim is currently false
`sections/A1_appendix.tex:164-166`: "Running `python scripts/aggregate_all.py` on
the released traces reproduces every numerical claim." It does not (see B1, B2).
This is a direct, checkable falsifiable claim a reviewer will run. Must be true
before camera-ready: regenerate the paper numbers from the committed traces, or
soften the claim. `aggregate_all.py` and `repro_manifest.json` and the prereg
commit `c391017` all exist, so the infrastructure is present — only the numbers drifted.

---

## MAJOR

### M1. Total API spend understated: "$73" vs actual $81.42
`sections/01_introduction.tex:103` "Total API spend \$$73$". Fresh aggregator
sums non-zero-cost (API) cells to **$81.42** (`headline_numbers.md`: Total cost
$81.418; all paid cost is Anthropic+OpenAI). The $73 predates the added gpt/Opus
runs. Fix: "$81" (and keep "Qwen3 sweep at zero marginal cost").

### M2. OpenAI per-model CP upper bounds are stale (too tight)
`sections/05_results.tex:143` claims per-model CP 95% upper bounds
"$\leq\!0.65$--$0.74\%$". Recomputed two-sided exact CP from fresh denominators:
gpt-4.1 0/404 → 0.91%, gpt-4.1-mini 0/408 → 0.90%, gpt-4.1-nano 0/409 → 0.90%,
gpt-4o 0/466 → 0.79%, gpt-4o-mini 0/430 → 0.85%. So the true range is
**0.79–0.91%**, not 0.65–0.74%. Fix the range.

### M3. Regime per-cell CP bound "≤3.63%" understates the worst cell (true 8.22%)
`sections/05_results.tex:14` "Clopper--Pearson $95\%$ per-cell upper bound is
$\leq\!3.63\%$". But Table `tab:regime` (and the stats `regime_worst_cell`) include
Sonnet 4.6 long-ctx at 0/81 and the C1 miss_func cell 0/43. The largest per-cell
upper bound among regime cells shown is 0/81 → 3.89%, and the worst regime cell
overall (Sonnet 4.6 miss_func C1, 0/43) → **8.22%** (stats_full.json
`regime_worst_cell_cp_upper` = 0.0822). Even restricting to the six C0 cells in
the table, the min n is 81 → 3.89% > 3.63%. The "≤3.63%" corresponds to a
~100-call cell and is not the max. Fix: state the actual worst-cell bound (3.89%
if scoped to the 6 displayed C0 cells; 8.22% if scoped to all regime cells).

### M4. Pooled regime CP bound "≤0.45%" inconsistent with stated N=661
`sections/05_results.tex:15` "pooled over the $661$ C0 regime calls, $\leq\!0.45\%$."
Exact two-sided CP for 0/661 = **0.557%**, not 0.45%. The 0.45% matches the full
regime grid (stats `regime_grid` n=889 → 0.414%, rounds toward 0.45 region), not
661. Fix: either 661 → ≤0.56%, or change N to the 889-call grid the 0.45% came from.
(N=661 itself reconciles to the table; only the bound is wrong.)

---

## MINOR

### m1. Per-tier Fisher p-values partially stale
`sections/05_results.tex:235` lists {0.24, 0.12, 0.058, 0.032} for 1.7B/4B/8B/14B.
Fresh `run_stats_full.py`: {0.262, 0.123, 0.042, 0.032}. The 1.7B (0.24→0.26) and
8B (0.058→0.042) values drifted. Fix to match regenerated stats.

### m2. Holm p-value "2.14e-4" not reproduced by current stats
`sections/05_results.tex:239` and `sections/A1_appendix.tex:149` cite
$p_{\mathrm{Holm}}=2.14\times10^{-4}$. The current script's pooled nonzero-tier
Fisher p is 2.92e-5 and its per-tier Holm rejects are all False; nothing in
`stats_full.json` produces 2.14e-4. Recompute and reconcile (it is downstream of B2).

### m3. Anthropic C0 bound called "95% upper bound" but value is the one-sided bound
`main.tex:67`, `sections/01_introduction.tex:45/90`, `sections/05_results.tex:61/66`
state $\leq 0.115\%$ for 0/2578. Exact two-sided 95% upper = **0.143%**; the
0.115% is the one-sided 95% bound (0.116%). The OpenAI bound "≤0.14%" for 0/2117
is the two-sided value (0.174% two-sided?? — recheck: 0/2117 two-sided = 0.174%,
so "≤0.14%" is itself the one-sided 0.141%). The paper mixes one-sided headline
bounds with prose that elsewhere implies two-sided "95% upper bound," and the
stats_table.md header explicitly says "two-sided 95%." Pick one convention and
state it (one-sided upper is defensible for a safety bound, but label it).
Note: 0/2117 two-sided = 0.174%, so if two-sided is adopted, "≤0.14%" must become "≤0.18%".

### m4. yin2026reasoningtrap: bibtex booktitle (ACL 2026) vs arXiv-only eprint
`refs.bib` gives `yin2026reasoningtrap` a `booktitle = {...ACL...} year=2026` but
`eprint=2510.22977` (Oct 2025, verified real). If not actually accepted/published
at ACL 2026, the booktitle is an overclaim; verify acceptance or downgrade to
@misc/arXiv. (All other 2026 eprints verified as real arXiv entries:
licl2026=2602.00276, englander2026=2604.17609, bugstudy2026=2602.21806,
qi2026brief=2604.02155, healy2026internal=2601.05214.)

### m5. Prereg commit message does not assert "locked protocol before data"
`sections/A1_appendix.tex:138` says commit `c391017` is "the pre-registered
protocol ... dated before any data was collected." The commit exists but its
message is "Add paper plan for SCALE @ ICML 2026 submission" — a plan, not a
locked prereg. A hostile reviewer can `git show c391017` and contest the
"pre-registration" framing. Ensure the commit actually contains a protocol doc
with the prereg'd N, conditions, and primary tests, or soften "pre-registered."

### m6. Abstract/intro "five Anthropic 4.x versions across an eleven-month release window"
`main.tex` abstract: "five Anthropic 4.x versions across an eleven-month release
window." Setup lists May 2025 (Sonnet 4) to April 2026 (Opus 4.7) = ~11 months
(coverage table dates 05/2025–04/2026). Consistent, but double-check Opus 4.7
release date stamp; the coverage table omits a date for Opus 4.7 and Sonnet 4.6.
Cosmetic: add the two missing date stamps so the "eleven months" is auditable.

### m7. "NUMBERS_TODO" comment block still present in appendix source
`sections/A1_appendix.tex:151-156` contains a `% NUMBERS_TODO` comment listing
unaggregated experiments (gpt-5, quant controls, A2 reflection, 14B event-boost).
Harmless (commented out, not rendered) but should be removed before camera-ready
to avoid leaking internal status if source is released.

---

## Items checked and CLEAN
- All `\citep/\citet` keys (31 distinct) resolve in `refs.bib`.
- Six riskiest 2026 arXiv IDs web-verified as real (see m4 list).
- Figure files exist: fig1_scaling_curve.pdf, fig2_ablation_ladder.pdf,
  fig3_rvr_architecture.png, fig4_distractor_probe.png. All four are now in the
  appendix and `\ref`'d from body (fig:scaling, fig:ablation in §5 body which is fine,
  fig:rvr-arch, fig:probe). LaTeX log: no "undefined reference", no "multiply
  defined", no "Citation undefined" — only TU font-shape substitution warnings.
- Anthropic pool decomposition reconciles exactly: probe C0 1917 + regime C0 661
  = 2578; per-model probe rows (Opus 293, Sonnet4.6 561, Sonnet4.5 285, Sonnet4
  253, Haiku 525) sum to 1917; appendix coverage table sums to 2578.
- OpenAI pool 0/2117 (gpt-4.1{,-mini,-nano}, gpt-4o{,-mini}) reconciles exactly.
- C1 subsets: probe-only 0/539, probe+regime 0/678 — both reconcile.
- Ablation ladder denominators (8B C0_5 1/258, C0_7 0/448, C0_8 0/410, C1 0/258)
  reconcile with fresh aggregator; decoy arm 0/410 with per-arm 0/97,0/106,0/107,0/100
  reconciles. (Note: the ladder "baseline 1.46% (9/615)" uses the 615 denominator,
  consistent with the curve, so internally fine — but see B2 re the matched table.)
- Qwen2.5-7B 28/459 = 6.10% reconciles.
- Strict-pass deltas: Sonnet 53/60 = -11.7pp, Haiku 56/60 = -6.7pp — arithmetic correct.
- repro_manifest.json files exist under results/; aggregate_all.py exists; prereg
  commit c391017 exists (but see m5).

## How to reproduce this audit
```
cd /Users/cero/Desktop/PROJECTS/icml
PYTHONPATH=. harness/.venv/bin/python scripts/aggregate_all.py      # -> PHASE0/RESULTS/headline_numbers.{json,md}
PYTHONPATH=. harness/.venv/bin/python scripts/run_stats_full.py     # -> paper/_staging/stats_full.json, stats_table.md
harness/.venv/bin/python -m pytest harness/tests                    # -> 153 passed
```
