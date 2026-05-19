---
description: Adds a paper to the project's papers/ database. Fetches the paper from the most complete source available, writes a per-paper file with a summary in our voice grounded in the actual paper text, captures the authors' stated future work, notes paper-centric open questions, and updates papers/index.md. Works with arxiv URLs/IDs, lab research blog posts (Anthropic, DeepMind, Apollo, etc.), conference proceedings pages, or free-text titles. Use when the user says "let's look at paper X", "add this paper", or invokes /add-paper.
argument-hint: [url | arxiv-id | title]
disable-model-invocation: true
allowed-tools: WebFetch WebSearch Read Write Edit Bash
---

# Add paper

Add a paper to `papers/` and update `papers/index.md`. The paper to add is described by: $ARGUMENTS

## Critical honesty rule

**Never write paper-depth content from abstract-only material.** The per-paper file's structured sections (Key experimental conditions, Key quantitative results, Methods, Open questions) imply the writer read the paper. If you only got the abstract, the file must visibly reflect that. Filling those sections with plausible-sounding detail from training-data prior knowledge is fabrication, even if individual claims happen to be correct. This rule is non-negotiable.

If after the full fetch waterfall (below) you still only have the abstract, drop into **Sparse mode** (see template) instead of confabulating.

## Workflow

1. **Identify the source.** $ARGUMENTS may be:
   - An arxiv URL or arxiv ID (e.g. `2412.14093`)
   - A lab research blog post / research note URL (Anthropic, DeepMind, Apollo, OpenAI, etc.)
   - A conference proceedings page (NeurIPS, ICLR, etc.)
   - A free-text title — search for the canonical source first, confirm with the user before writing

2. **Fetch — use the waterfall.** The goal is to land on full paper body text, not an abstract. Walk the list below in order and **stop at the first that returns substantive body content** (multiple sections, experimental detail, numerical tables). At each step, after fetching, ask yourself: *is this just an abstract / landing page, or is this the paper body?* If the former, keep going.

   **For an arxiv paper (`<id>`):**
   1. `https://arxiv.org/html/<id>` — native HTML if the authors compiled it that way. Many recent papers have this.
   2. `https://arxiv.org/html/<id>v1` (or v2, v3) — version-specific HTML; the bare `/html/<id>` sometimes 404s while a versioned URL works.
   3. `https://ar5iv.labs.arxiv.org/html/<id>` — community LaTeX→HTML converter. Covers the vast majority of arxiv papers, including older ones without native HTML.
   4. `https://www.semanticscholar.org/arxiv/<id>` — Semantic Scholar landing page; often includes extracted full text in its TLDR / sections.
   5. `https://arxiv.org/pdf/<id>` — direct PDF. WebFetch sometimes parses PDFs, sometimes returns binary. Try it.
   6. As a last resort, fetch `https://arxiv.org/abs/<id>` for the abstract — but then drop into **Sparse mode** (below). Do NOT write a deep-read-looking file.

   **For a conference proceedings page (NeurIPS / ICLR / ICML / etc.):**
   1. Search the title via `WebSearch` to find the arxiv preprint ID (most papers have one). If found, walk the arxiv waterfall.
   2. Otherwise look for an authors' project page (often has a PDF link or HTML extract).
   3. The proceedings hash page is usually abstract-only — treat it the same as `arxiv.org/abs/<id>`. If that's all you have, **Sparse mode**.

   **For a lab research blog post / research note:**
   - Fetch the URL directly. These usually render full HTML and are fine. If the post is just a teaser pointing at a longer paper, follow the link to the paper and walk the relevant waterfall above.

   **Fetch verification.** Before treating any fetch as a success, check that the returned content contains at least one of: a Methods/Methodology section header, a Results section header, a numbered figure or table, or quantitative claims beyond the headline stat in the abstract. If none of these are present, you have an abstract, not a paper. Keep walking the waterfall.

3. **Extract from the fetched body.** Pull:
   - Full title, all authors (or "first et al." if many), year, canonical source identifier (arxiv ID, URL, DOI, venue)
   - Core claim in 2-3 sentences
   - Experimental setup: which model(s), what training regime, what conditions distinguished, what was measured
   - Key quantitative results — specific numbers, tables, headline + secondary stats
   - Experimental variants / interventions / ablations
   - Authors' stated limitations and future work
   - Whether the paper uses linear probes / activation steering / SAEs / NLAs / other internal-state methods (note explicitly even when absent)

   Adapt to the source format. Blog posts may not have a formal author list — capture lead author / contributors. Map sensibly; don't force fields that aren't there.

4. **Choose a slug.** Filename is `papers/<slug>.md`. Use distinctive word(s) from the title, lowercase with underscores (`alignment_faking.md`, `inoculation_prompting.md`). Check `papers/` for collisions.

5. **Read the index first.** Open `papers/index.md` to see current categories and existing entries. Decide which category fits. If none fit, add a new category section rather than forcing into "Other".

6. **Write the per-paper file** at `papers/<slug>.md`. Use the **Full mode template** if a substantive body fetch succeeded; **Sparse mode template** if only abstract was available.

7. **Update `papers/index.md`** — add a row to the chosen category table. Keep the one-line takeaway concrete (numbers where the paper provides them, with a "[abstract-only — needs full re-read]" marker if in Sparse mode). The index entry should describe what the paper *says*, not what it means for any project.

8. **Report back.** Confirm file path, category, and **which fetch step succeeded** (or that you fell to Sparse mode and why). Flag anything genuinely surprising or load-bearing for the field.

## Full mode template (use when body fetch succeeded)

```markdown
# <Full title>

**Authors:** <first author et al., institutional affiliation if notable>
**Year:** <year>
**arXiv:** [<id>](https://arxiv.org/abs/<id>)    ← for arxiv papers; otherwise replace this line with:
**Source:** [<short label or domain>](<url>)     ← e.g. for Anthropic / DeepMind / Apollo research blog posts
**Fetched from:** <URL that actually returned the body content, e.g. `ar5iv.labs.arxiv.org/html/<id>`>
**Status:** read

---

## Summary (in our words)

<2-4 paragraphs. Setup, what happened, what makes the result interesting. First-person plural ("we", "our"). Talk the reader through the paper like a colleague who actually read it, not an abstract paraphrase. Stick to what the paper actually claims and demonstrates; flag what's empirically tight vs. speculative or framing-dependent.>

## Key experimental conditions

- <bullets capturing actual experimental design — models used, regime, cues, conditions>

## Key quantitative results

- <bullets with the numbers that matter, including the headline stat and any tables-of-interest>

## Methods (what they did and didn't use)

- <what techniques they used: behavioural evals, probes, scratchpad/CoT analysis, fine-tuning, RL, etc.>
- <note absences factually when they bear on what the paper can and can't conclude — e.g. "no internal-state analysis; all evidence is behavioural">
- <flag closed- vs open-weight model where it affects reproducibility>

## Authors' stated limitations / future work

- <bullets from the paper's own limitations / future-work sections>

## Open questions and follow-up directions

<Numbered list of 2-5 angles. Paper-centric — adjacent directions the paper itself opens up, methodological gaps, scaling/generalisation questions, replication targets, things the result implies but doesn't demonstrate. Substance over enumeration; two sharp angles beats five generic ones.

Do NOT tie these to any specific project the user is currently considering. Project ideas are ephemeral; per-paper files should age well. Frame as the field's open questions, not "what we'd build next."

Example phrasings: "Whether the effect persists at smaller model scale is open."; "The paper does not test X; doing so would distinguish A from B."; "The result depends on Y; replacing Y with Z would clarify the mechanism."

Avoid: phrasings that reference specific projects, candidates, budgets, or the user's preferred techniques as if they're the obvious extension. Those belong in `ideas/`, not in `papers/`.>

## See also

<Paper-to-paper connections, one per line, with a brief note on what makes the connection. Examples:
- [[other_paper]] — same phenomenon, different model class
- [[another_paper]] — sibling method (linear probes for adjacent target)
- [[third_paper]] — competing finding; resolves vs. our paper's claim

Keep factual — connections, not project-shaping.>
```

## Sparse mode template (use when only abstract is available)

```markdown
# <Full title>

**Authors:** <first author et al., affiliation>
**Year:** <year>
**arXiv:** [<id>](https://arxiv.org/abs/<id>)    ← or **Source:** for non-arxiv
**Fetched from:** abstract page only — full paper not accessible at time of writing
**Status:** abstract-read

> ⚠️ **Abstract-only entry.** The fetch waterfall did not return substantive body content. The summary below is grounded *only* in the abstract and metadata. Quantitative claims, experimental details, and methodology should be verified against the full paper before citing. This file should be re-done from the full paper when one of (a) arxiv HTML / ar5iv version (b) a project page (c) the PDF becomes accessible.

---

## Abstract (verbatim or close paraphrase)

<The actual abstract, in the authors' framing. Do not invent structure the abstract didn't have. Quote where useful.>

## What we know from the abstract

- <bullet: headline claim>
- <bullet: models named (if any)>
- <bullet: methodology named (if any)>
- <bullet: headline quantitative claim (if any) — verbatim>
- Anything the abstract does NOT say but we'd want to know — list as **gaps**:
  - **Gap:** specific layer / probe architecture / training compute / etc.
  - **Gap:** ablation results
  - **Gap:** failure mode characterisation

## Methods (from abstract only)

- <what the abstract names; do not invent>
- Whether the paper uses internal-state methods: <unknown / mentioned: probes / mentioned: SAEs / etc.>

## See also

<connections, same rules as Full mode>

---

*To upgrade this file to Full mode, fetch `arxiv.org/html/<id>v1`, `ar5iv.labs.arxiv.org/html/<id>`, or the PDF, and rewrite the structured sections from the body.*
```

## Voice and style

- First-person plural throughout — this is a personal research notebook.
- Concrete > abstract. "~14% compliance, up to 78% with RL" beats "the model sometimes complies".
- **Keep an open mind.** Do not frame the paper through a specific project idea the user is considering. The user's project shape changes; per-paper files should be evergreen.
- When a paper uses only behavioural evidence or only internal-state methods, note it factually. Do not editorialise about what's "missing from a project-framing perspective."
- Avoid menu-style brainstorm dumps in follow-ups. Each open question should feel chosen.
- **Source honesty over apparent depth.** A short, honest Sparse-mode file is better than a long Full-mode file built from confabulation. If the fetch failed, say so and stop.
