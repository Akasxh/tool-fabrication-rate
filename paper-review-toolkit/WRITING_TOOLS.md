# Best open-source LLM tools for writing scientific papers

## Tier 1 — drafting / full-paper agents

1. **SakanaAI/AI-Scientist-v2** (5.9k★) — End-to-end agentic tree search
   with VLM-figure feedback. `perform_writeup.py` / `perform_review.py`
   reusable in isolation. https://github.com/SakanaAI/AI-Scientist-v2
   (v1: https://github.com/SakanaAI/AI-Scientist, 13.4k★)
2. **SamuelSchmidgall/AgentLaboratory** (5.5k★, MIT) — Three-phase pipeline
   (lit review → experiments → report). ~84% cost reduction vs Sakana.
   AgentRxiv cross-run memory. https://github.com/SamuelSchmidgall/AgentLaboratory
3. **aiming-lab/AutoResearchClaw** (11.8k★, MIT, very active) — Plugs into
   Claude Code / Codex / Gemini CLIs via ACP. Section-by-section writer
   with peer-review revision loop. Lowest-friction with Claude Code.
   https://github.com/aiming-lab/AutoResearchClaw
4. **federicodeponte/opendraft** (97★, MIT) — 19 specialized agents,
   citations verified against Crossref/OpenAlex/Semantic Scholar (~250M
   papers). Free via Gemini. https://github.com/federicodeponte/opendraft

## Tier 2 — drop-in skills, sections, citations

5. **Orchestra-Research/AI-Research-SKILLs** (7.5k★, MIT, very active) —
   Has a `20-ml-paper-writing` skill purpose-built for NeurIPS/ICML/ICLR
   /ACL with LaTeX templates, citation verification, per-section style
   rules. **Drops into Claude Code as a skill directly.**
   https://github.com/Orchestra-Research/AI-Research-SKILLs
6. **Future-House/paper-qa (PaperQA2)** (8.4k★, Apache-2.0) — SOTA RAG
   for grounded citations. Use to generate related-work and verify
   every cite. https://github.com/Future-House/paper-qa
7. **stanford-oval/storm** (28.1k★, MIT) — Outline-then-draft with
   multi-perspective Q&A. Excellent for related-work and abstracts.
   https://github.com/stanford-oval/storm
8. **AutoSurveys/AutoSurvey** (468★) — Section outline + parallel
   drafting + LLM-judge refinement. Mind the licensing gap.
   https://github.com/AutoSurveys/AutoSurvey
9. **LitLLM/LitLLM** (32★, Apache-2.0) — Lightweight literature review:
   keyword extraction, S2 search, SPECTER embeddings, attributed reranker.

## Honorable mentions / non-OSS

- OverleafCopilot (Chrome extension, arXiv:2403.09733) — closed-source
- Writefull (Overleaf-bundled, Digital Science) — closed but native
- Paperpile / Paperguide — closed reference managers with LLM Q&A
- WebLaTex (sanjib-sen/WebLaTex) — Overleaf clone with Copilot built in
- JinheonBaek/ResearchAgent (NAACL 2025) — idea generation
- varunshenoy/coauthor — stale (2023) but English→LaTeX prompts copy clean

## Recommendation

Clone **AI-Research-SKILLs/20-ml-paper-writing** as house style and
prompt scaffold. Run **PaperQA2** over your reference PDFs for grounded
related-work + citation suggestions. Use **AI-Scientist-v2's writeup +
review loop** for self-review on each section. Skip full-autonomy
systems when you already have results — they're better as prompt
sources than drivers.
