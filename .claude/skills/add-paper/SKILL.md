---
description: Adds a paper to the project's papers/ database. Fetches the source, writes a per-paper file with summary in our voice, captures the authors' stated future work, notes paper-centric open questions, and updates papers/index.md. Works with arxiv URLs/IDs, lab research blog posts (Anthropic, DeepMind, Apollo, etc.), or free-text titles. Use when the user says "let's look at paper X", "add this paper", or invokes /add-paper.
argument-hint: [url | arxiv-id | title]
disable-model-invocation: true
allowed-tools: WebFetch Read Write Edit
---

# Add paper

Add a paper to `papers/` and update `papers/index.md`. The paper to add is described by: $ARGUMENTS

## Workflow

1. **Identify the source.** $ARGUMENTS may be:
   - An arxiv URL or arxiv ID (e.g. `2412.14093`) → fetch `https://arxiv.org/abs/<id>`
   - Any other URL — lab research blog post, Anthropic / DeepMind / Apollo research page, conference page, technical report — → fetch the URL directly
   - A free-text title → search for the canonical source first, confirm with the user that you've found the right work before writing it up

2. **Fetch.** Use `WebFetch` on the identified URL. Extract:
   - Full title, all authors (or "first et al."), year, and a canonical source identifier (arxiv ID, URL, DOI — whichever the source provides)
   - Core claim in 2-3 sentences
   - Experimental setup: which model(s), what training regime, what cue distinguished conditions, what was measured
   - Key quantitative results
   - Experimental variants / interventions tested
   - Authors' stated limitations and future work
   - Whether the paper uses or mentions linear probes / activation steering / SAEs / NLAs / other internal-state methods (note explicitly even when absent)

   Adapt to the source format. A blog post may not have a formal author list — capture the lead author / contributors. A lab research note may not have a "year" prominently — use the publication date. Map sensibly; don't force fields that aren't there.

3. **Choose a slug.** Filename is `papers/<slug>.md`. Use the most distinctive word or two from the title, lowercase with underscores (`alignment_faking.md`, `inoculation_prompting.md`). Check `papers/` for collisions.

4. **Read the index first.** Open `papers/index.md` to see the current categories and existing entries. Decide which category the new paper belongs in. If none fit, add a new category section rather than forcing it into "Other".

5. **Write the per-paper file** at `papers/<slug>.md` using the template below.

6. **Update `papers/index.md`** — add a row to the chosen category table. Keep the one-line takeaway concrete (numbers where the paper provides them). The index entry should describe what the paper *says*, not what it means for any specific project.

7. **Report back** — confirm the file path and category. If something in the paper is genuinely surprising or load-bearing for the field, mention it briefly; otherwise no need.

## Per-paper file template

```markdown
# <Full title>

**Authors:** <first author et al., institutional affiliation if notable>
**Year:** <year>
**arXiv:** [<id>](https://arxiv.org/abs/<id>)    ← for arxiv papers; otherwise replace this line with:
**Source:** [<short label or domain>](<url>)     ← e.g. for Anthropic / DeepMind / Apollo research blog posts
**Status:** read

---

## Summary (in our words)

<2-4 paragraphs. Setup, what happened, what makes the result interesting. First-person plural ("we", "our"). Talk the reader through the paper like a colleague who actually read it, not an abstract paraphrase. Stick to what the paper actually claims and demonstrates; flag what's empirically tight vs. speculative or framing-dependent.>

## Key experimental conditions

- <bullets capturing actual experimental design — models used, regime, cues, conditions>

## Key quantitative results

- <bullets with the numbers that matter, including the headline stat>

## Methods (what they did and didn't use)

- <what techniques they used: behavioural evals, probes, scratchpad/CoT analysis, fine-tuning, RL, etc.>
- <note absences factually when they bear on what the paper can and can't conclude — e.g. "no internal-state analysis; all evidence is behavioural">
- <flag closed- vs open-weight model where it affects reproducibility>

## Authors' stated limitations / future work

- <bullets from the paper's own limitations / future-work sections>

## Open questions and follow-up directions

<Numbered list of 2-5 angles. These should be **paper-centric** — adjacent directions the paper itself opens up, methodological gaps the paper has, scaling/generalization questions, replication targets, things the result implies but doesn't demonstrate. Substance over enumeration; two sharp angles beats five generic ones.

Do NOT tie these to any specific project the user is currently considering. Project ideas are ephemeral; per-paper files should age well as the project evolves. Frame the questions as the field's open questions, not as "what we'd build next."

Be open-minded. If the paper has a strong methodological choice (e.g. only behavioural evidence, only on closed-weight models), the open question is whether the result generalizes — not "this leaves room for our probe extension."

Example phrasings: "Whether the effect persists at smaller model scale is open."; "The paper does not test X; doing so would distinguish A from B."; "The result depends on Y; replacing Y with Z would clarify the mechanism."

Avoid: phrasings that reference specific projects, candidates, budgets, or the user's preferred techniques as if they're the obvious extension. Those belong in `ideas/`, not in `papers/`.>

## See also

<Paper-to-paper connections, one per line, with a brief note on what makes the connection. Examples:
- [[other_paper]] — same phenomenon, different model class
- [[another_paper]] — sibling method (linear probes for adjacent target)
- [[third_paper]] — competing finding; resolves vs. our paper's claim

This is where cross-paper structure lives. Keep it factual — connections, not project-shaping.>
```

## Voice and style

- First-person plural throughout — this is a personal research notebook.
- Concrete > abstract. "~14% compliance, up to 78% with RL" beats "the model sometimes complies".
- **Keep an open mind.** Do not frame the paper through a specific project idea the user is considering. The user's project shape changes; per-paper files should be evergreen and read fairly to anyone returning to them later. Project ideation belongs in `ideas/`.
- When a paper uses only behavioural evidence or only internal-state methods, note it factually. Do not editorialise about what's "missing from a project-framing perspective" or what "the gap our project would fill" is.
- Avoid menu-style brainstorm dumps in follow-ups. Each open question should feel chosen, and should reflect the paper's own implications rather than the user's current project hypothesis.
