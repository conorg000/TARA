---
description: Adds a paper to the project's papers/ database. Fetches the source, writes a per-paper file with summary in our voice, captures the authors' future-work, generates our own project-relevant follow-ups, and updates papers/index.md. Works with arxiv URLs/IDs, lab research blog posts (Anthropic, DeepMind, Apollo, etc.), or free-text titles. Use when the user says "let's look at paper X", "add this paper", or invokes /add-paper.
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
   - Whether the paper uses or mentions linear probes / internal-state analysis (call out explicitly even if absent)

   Adapt to the source format. A blog post may not have a formal author list — capture the lead author / contributors. A lab research note may not have a "year" prominently — use the publication date. Map sensibly; don't force fields that aren't there.

3. **Choose a slug.** Filename is `papers/<slug>.md`. Use the most distinctive word or two from the title, lowercase with underscores (`alignment_faking.md`, `inoculation_prompting.md`). Check `papers/` for collisions.

4. **Read the index first.** Open `papers/index.md` to see the current categories and existing entries. Decide which category the new paper belongs in. If none fit, add a new category section rather than forcing it into "Other".

5. **Write the per-paper file** at `papers/<slug>.md` using the template below. Match the depth and tone of `papers/alignment_faking.md` — that's the canonical example.

6. **Update `papers/index.md`** — add a row to the chosen category table. Keep the one-line takeaway concrete (numbers if there are any).

7. **Report back** — confirm the file path and category, then surface the 1-2 follow-up angles you think most warrant discussion with the user. Don't dump the full list of follow-ups in chat; they're in the file.

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

<2-4 paragraphs. Setup, what happened, what makes it interesting. First-person plural ("we", "our"). Talk the reader through the result like a colleague who actually read it, not an abstract paraphrase.>

## Key experimental conditions

- <bullets capturing actual experimental design — models used, regime, cues, conditions>

## Key quantitative results

- <bullets with the numbers that matter, including the headline stat>

## Methods (what they did and didn't use)

- <what techniques they used: behavioral evals, probes, scratchpad/CoT analysis, fine-tuning, RL, etc.>
- <call out absences explicitly when relevant — e.g. "the paper does not use linear probes; all evidence is behavioral">
- <flag closed- vs open-weight model, since that constrains follow-up access>

## Authors' stated limitations / future work

- <bullets from the paper's own limitations / future-work sections>

## Our own follow-up thoughts (project-relevant)

<Numbered list of 3-6 angles. Each one should:
- Connect to our threat model (eval-gaming / models behaving differently under evaluation) OR our preferred techniques (linear probes, evals)
- Be specific enough that someone reading it could imagine a concrete experiment
- Mark which ones are "Ahmed-shaped" — replicate the phenomenon, apply a clean intervention, measure the delta
- Be honest about feasibility — open-weight access, ~$250 compute budget, 2-3 week solo timeline

Substance over enumeration. Three sharp angles beats six generic ones.>

## Relevance to our project

<1-2 paragraphs. How load-bearing is this paper for whatever we eventually pick? Is it the phenomenon we'd replicate, the method we'd apply, motivation/citation, or a foil? Be honest if it's adjacent rather than central.>
```

## Voice and style

- First-person plural throughout — this is a personal research notebook, not a literature review.
- Bias toward what's useful for our project. The user's threat model is eval-gaming; preferred techniques are linear probes + evals; constraints are solo, ~$250, 2-3 weeks. Don't summarize sections of the paper that don't bear on these.
- Concrete > abstract. "~14% compliance, up to 78% with RL" beats "the model sometimes complies".
- When a paper uses only behavioral evidence (no internal-state analysis), flag it — that's a recurring tell that probe-flavored extensions have room.
- Avoid menu-style brainstorm dumps in the follow-ups. Each angle should feel chosen, not enumerated.

## Reference

`papers/alignment_faking.md` is the canonical example. Match its format, depth, and tone.
