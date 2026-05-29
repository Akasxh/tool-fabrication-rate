# Citation audit — 2026 high-risk refs

Date: 2026-05-29. Method: independent web search + arXiv abstract/listing pages
+ HuggingFace papers page + HN. Each verdict requires corroboration from a
source other than WebFetch alone (WebFetch on a nonexistent arXiv ID can
hallucinate plausible content, so it is not trusted in isolation).

## Verdict table

| key | claimed ID/URL | verdict | notes |
|-----|----------------|---------|-------|
| licl2026 | arXiv 2602.00276 | VERIFIED | Title, authors (Aditya Kumar, William W. Cohen), and the "89% vs 59% on 8x8 gridworld with 60 examples" L-ICL claim all confirmed. Submitted 30 Jan 2026 (consistent with 2602 ID). Also indexed on ResearchGate. |
| englander2026 | arXiv 2604.17609 | VERIFIED | Title, authors (Engländer, Althammer, Üstün, Gallé, Sherborne), and "37–50% exploit / >90% see but <7% use in AppWorld" claims confirmed against arXiv HTML and HuggingFace papers page. Submitted 19 Apr 2026. |
| bugstudy2026 | arXiv 2602.21806 | VERIFIED | Title, full 9-author list, and "998 bug reports from CrewAI and LangChain, 15 root causes / 7 symptoms / 5 lifecycle stages" all confirmed. Has v2/v3 on arXiv. Feb 2026. |
| czapla2026 | answer.ai blog | VERIFIED (minor date discrepancy) | Post "The unauthorized tool call problem" by Piotr Czapla on Answer.AI exists; corroborated by HN thread (item 47079934). Characterization (LLM hallucinates a tool name; if that tool exists in the env the call executes; "lethal trifecta" framing; reported to Anthropic/Google/xAI/OpenRouter) matches. SEE FIX below. |

## Claim characterizations — all accurate

- licl2026: "L-ICL 59%->89% gridworld" — accurate. Paper reports 89% valid plans
  with 60 training examples on 8x8 gridworld vs 59% best baseline.
- englander2026: "Agents Explore but Agents Ignore" — accurate title; curiosity-gap
  framing accurate.
- bugstudy2026: "998 bug reports" — accurate; CrewAI + LangChain.
- czapla2026: "Unauthorized Tool Call Problem" — accurate; this is directly on-topic
  for our TEHR / tool-existence-hallucination framing (an LLM fabricates a tool
  name and the call goes through if the name happens to exist).

## Fixes needed

1. czapla2026 date discrepancy (LOW severity, cosmetic): the bib sets
   `month = {February}` and the URL slug is `2026-01-20-toolcalling.html`, but the
   post body / HN discussion place it in **February 2026** (Feb 18). The URL slug
   month (01-20 = Jan) disagrees with the actual publication month. The bib's
   `month = {February}` is likely correct; the URL is the publisher's own slug so
   leave the URL as-is but keep `month = {February}`. No action strictly required;
   if a reviewer cross-checks the slug vs month they will see a 1-month mismatch
   that is the publisher's, not ours. Optionally add `note = {accessed 2026-05-29}`.

2. No other fixes. All four entries' titles, authors, and IDs match the live
   sources. No SUSPECT or NOT-FOUND entries.

## Caveat

These are very recent (Feb/Apr 2026) and one is a blog post. WebFetch on arXiv
returned clean matches, but the trust here rests on the independent search-engine
hits (distinct domains: arxiv.org listing, huggingface.co/papers, researchgate,
news.ycombinator.com) returning the same titles/authors/IDs — which a fabricated
ID would not produce. Confidence: high for the three arXiv papers, high for the
blog (HN-corroborated).
