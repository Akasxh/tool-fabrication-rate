# LaTeX writing assistants — ranked for ICML/NeurIPS

## Tier 1 — use today

1. **Overleaf AI Assist (Writefull-integrated)** — freemium add-on.
   LaTeX-native paraphrase, error-fix, **Citation Reviewer** flags
   claims missing refs. https://www.overleaf.com/about/ai-features
2. **Cursor / Windsurf with `.cursorrules`** — paid ($20/mo). Drop a
   rules file telling the agent to preserve `\cite{}`, `\ref{}`, math.
   Best AI-editing-while-preserving-LaTeX. Template:
   https://github.com/yang3kc/cursor_latex_template
3. **checkcites** — free, OSS. **Catches duplicate `\cite` and missing
   /unused bib entries.** `tlmgr install checkcites && checkcites paper.aux`
   https://github.com/islandoftex/checkcites
4. **refcheck package** — free. **Catches unused labels, unreferenced
   equations, missing `\ref`.** `\usepackage[showrefs,showcites]{refcheck}`
5. **ChkTeX** — free, bundled with TeX Live. Standard LaTeX linter.
   `chktex paper.tex`

## Tier 2 — solid additions

6. **TeXtidote** — free, Java. LaTeX-aware grammar/style.
   `brew install textidote && java -jar textidote.jar --check en paper.tex`
7. **LaTeX Workshop + GitHub Copilot in VS Code** — freemium.
   Copilot autocompletes LaTeX inline; Workshop handles build/preview.
8. **TeXiFy-IDEA + JetBrains AI Assistant** — has the **best built-in
   inspections** for unresolved labels/citations of any IDE.
9. **aspell-LaTeX** — free spell-check.
   `aspell --mode=tex --lang=en check paper.tex`
10. **bibtex duplicates checker (bdc)** — web tool for duplicate `.bib`
    entries. https://www.pittnerovi.com/bdc/

## Skip

- **Grammarly Premium** — doesn't understand LaTeX; mangles `\cite{}`.
- **ProWritingAid academic mode** — no native LaTeX.
- **WebLaTex** — too much setup for a deadline.

## Recommended stack

Overleaf AI Assist for prose passes + Cursor (with rules file) for
structural edits + `checkcites` + `chktex` + `refcheck` in your build.
That combination catches every "duplicate `\cite`" / "missing `\ref`"
gotcha and most LaTeX-aware grammar issues.
