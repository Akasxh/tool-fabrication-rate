# GitHub Survey: AI-Writing Detection & Humanizing Repos

Cluster: "AI-writing detection and humanizing repos (for camera-ready de-AI-ing — GPTZero concerns)".
Goal: find the most popular / useful repos NOT already in our known list, to (a) self-test our
camera-ready text against open detectors before submission, and (b) inform / upgrade our
paper-revision skill + `avoid-ai-writing` / `humanizer` skills.

Selection bias: permissive license, actively maintained, high stars, academic-grade where
possible. Stars approximate as of 2026-05-29 (via GitHub API). None of these are in the known list.

## Top picks (6)

| # | Repo | ~Stars | License | Why it helps |
|---|------|-------:|---------|--------------|
| 1 | https://github.com/ahans30/Binoculars | 380 | BSD-3-Clause | ICML 2024 zero-shot LLM-text detector (>90% TPR @ 0.01% FPR). Drop-in self-test of our camera-ready prose against an academic detector — strongest "will a reviewer's tool flag us" signal. Permissive, paper-backed. |
| 2 | https://github.com/baoguangsheng/fast-detect-gpt | 400 | MIT | ICLR 2024 zero-shot detector via conditional-probability curvature; fast, still maintained (pushed 2026). Complements Binoculars for a second-detector check; MIT makes it safe to vendor into our harness. |
| 3 | https://github.com/eric-mitchell/detect-gpt | 470 | MIT | Original DetectGPT (ICML 2023) curvature method. Foundational baseline; pairs with Fast-DetectGPT to show robustness of our text across the detector lineage. MIT-licensed reference impl. |
| 4 | https://github.com/yafuly/MAGE | 225 | Apache-2.0 | MAGE (ACL 2024) "detection in the wild" dataset + detectors across many generators/domains. Useful as a realistic, multi-family detection testbed and as breadth precedent for our main-track framing. |
| 5 | https://github.com/Xianjun-Yang/Awesome_papers_on_LLMs_detection | 285 | MIT | Actively curated (2025) survey of LLM text/code detection methods + datasets. Fast map of detectors/baselines to cite and to seed reviewer-persona "have you tested against X" objections. |
| 6 | https://github.com/lynote-ai/humanize-text | 855 | MIT | Highest-star open humanizer (multi-pass rewrite + cross-engine paraphrase to defeat GPTZero/Turnitin). Reference for de-AI-ing transforms to fold into our `humanizer`/paper-revision skill — but for ethics use only as an editing aid on our own prose, not fabrication. |

## Notes / honorable mentions
- xinleihe/MGTBench (~165, MIT) and kinit-sk/IMGTB (~22, MIT): benchmark *frameworks* bundling many
  detectors (DetectGPT, Fast-DetectGPT, Binoculars, etc.). Strong if we want one harness to run
  several detectors at once; ranked below the single-detector repos only because we likely want
  Binoculars/Fast-DetectGPT directly. Good candidate for a `bench_loaders`-style detector loader.
- vivek3141/ghostbuster (~180): Ghostbuster (NAACL 2024). Excluded from top 6: license is
  NOASSERTION (unclear terms), which is risky to vendor.
- StealthHumanizer (~26), OrbitWebTools/Humanize-AI (~8): lower-star "bypass detector" tools; lower
  quality/credibility than lynote-ai/humanize-text.

## Caveat
Detection repos = legitimate self-QA for camera-ready (check our own writing, then revise in our
voice). Humanizer repos should be treated as editing/rewriting aids on text we authored, not as a
way to launder fabricated content — keep the use defensible for an ICML camera-ready.
