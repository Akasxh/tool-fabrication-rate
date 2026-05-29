# Submission-day toolkit

What an ML researcher at an ICML/NeurIPS deadline actually needs.

## OpenReview API

- **openreview-py** (official) — `pip install openreview-py`. Both v1
  (`api.openreview.net`) and v2 (`api2.openreview.net`).
  https://github.com/openreview/openreview-py
- Docs + auth recipes: https://docs.openreview.net/getting-started/using-the-api

## arXiv submission helpers / PDF anonymization

- **arxiv-latex-cleaner** (Google) — strips comments, unused files,
  reduces images, scrubs `\author`/affiliations from LaTeX before
  upload. Essential. https://github.com/google-research/arxiv-latex-cleaner
- **exiftool + qpdf** — two-step recipe to strip PDF metadata
  permanently:
  ```bash
  exiftool -all:all= paper.pdf -overwrite_original
  qpdf --linearize paper.pdf clean.pdf
  ```
  exiftool alone is reversible; qpdf linearize makes it permanent.
- **MAT2** — one-shot CLI/GUI alternative.
  https://0xacab.org/jvoisin/mat2
- **rebiber** — normalizes BibTeX entries against DBLP/ACL Anthology
  canonical versions. Kills "preprint vs published" inconsistencies
  reviewers flag. https://github.com/yuchenlin/rebiber

## Anonymous code release

- **anonymous.4open.science** — proxy mirror of a GitHub repo with
  author/org names auto-replaced. Authenticate with GitHub, paste URL,
  list reveal-terms (handle, lab, dataset path).
  Source: https://github.com/tdurieux/anonymous_github
  CLI: `npm install -g @tdurieux/anonymous_github`
- **clone-anonymous-github** — download a tree from a 4open URL for
  sanity-checking your own scrub.
  https://github.com/fedebotu/clone-anonymous-github

## Plagiarism / paraphrase detection

- **copydetect** — winnowing-based code similarity (MOSS algorithm).
  `-b` excludes boilerplate. https://github.com/blingenf/copydetect
- **Copyleaks** — has AI-text + paraphrase detection.
  https://www.copyleaks.com/
- Institutional **iThenticate via Crossref** if your university
  subscribes.

## Citation graph & related-work discovery

- **Semantic Scholar Academic Graph API** — pull citations/references,
  SPECTER2 embeddings, recommended papers. Python:
  `pip install semanticscholar`. https://api.semanticscholar.org/api-docs/graph
- **Connected Papers** — visual co-citation neighborhood.
  https://www.connectedpapers.com/
- **ResearchRabbit** — iterative chaining of similar/earlier/later work.
  https://researchrabbitapp.com/
- **OpenAlex** — free, no-key citation graph; complements S2 when
  rate-limited. https://openalex.org/

## Paper visualization / figures

- **PlotNeuralNet** — canonical LaTeX/TikZ neural-net architecture
  diagrams. https://github.com/HarisIqbal88/PlotNeuralNet
- **NNTikZ** — drop-in TikZ snippets for transformers, attention, RNN.
  https://github.com/fraserlove/nntikz
- **pytorch2tikz** — auto-generates TikZ from a `torch.nn.Module`.
  https://github.com/fraunhoferhhi/pytorch2tikz
- **Mermaid → TikZ converter** — sketch in Mermaid, ship as LaTeX.
  https://www.underleaf.ai/tools/mermaid-to-latex
- **TikZ.net** — copy-paste examples library. https://tikz.net/neural_networks/
- **matplotlib + SciencePlots** — `plt.style.use(['science','ieee'])`.
  https://github.com/garrettj403/SciencePlots

## Deadline triage order

1. `arxiv-latex-cleaner` on the source
2. `exiftool + qpdf` on the compiled PDF
3. `rebiber` on the .bib
4. Push code to anonymous.4open.science
5. `openreview-py` script to verify upload + author list shows `Anonymous`
