# My TARA project — working notes

A living doc capturing the *personal* side of this project: what I'm thinking, what excites me, what I'm worried about, and how my taste is evolving as we go. Not a plan, not a proposal. Just the inside of my head.

---

## What I care about

### Threat model: models behaving differently when being evaluated

This is the threat model that genuinely concerns me. If models routinely behave differently when they suspect they're being watched vs. not, then:

- Behavioral evals are unreliable as a signal of alignment.
- Any analysis of model alignment done at the behavioral level is dubious.
- The thing we *can* observe (outputs) and the thing we *want to know about* (latent goals/dispositions) become decoupled in a fundamental way.

This isn't a vague worry — it's a concrete failure mode of the entire eval-based safety paradigm.

### Why this pairs with linear probes and evals

Eval-gaming is, by definition, a mismatch between internal state and external behavior. Behavioral evals are blind to it by construction. Probes — reading off internal representations — are one of the few tools that *could* see past the behavior to whatever the model "actually thinks" is going on. So my favorite technique and my most-feared risk are aimed at the same gap.

---

## How I want to work on this

### Empirically tight, not ambitious-and-unfinished

The Ahmed template: take a clean finding from one paper, apply a clean technique from another, measure the delta. Two anchor papers. Clear "done" state. Findings that an early-career researcher can analyse without falling into traps.

I'd rather have a complete, modest, defensible result than an incomplete attempt at something grand.

### Reproduction first, twist second

I'm genuinely open to *just* reproducing a paper as the spine of the project, then adding one careful twist. The replication isn't filler — it's the foundation that makes any twist interpretable.

---

## Constraints I'm working under

- Solo. No collaborators.
- ~2-3 weeks of focused work (TARA weeks 12-13), 10-min presentation week 14.
- Budget: ~$50 USD from TARA + up to ~$200 USD of my own. ~$250 total.
- 5 years of software engineering, rusty Python, Claude Code power user — the coding itself won't be the bottleneck.

---

## Open questions I want to come back to

*(Things to explore further as we map the space.)*

- What does the current literature on eval-awareness / alignment-faking / situational-awareness look like? Which findings are clean enough to replicate at my scale?
- Which models can I get probe access to within budget? (Open-weight: Llama 3.x, Qwen, Gemma. Frontier: black-box only.)
- Is there a paper-pair (phenomenon + intervention) that already exists for eval-gaming specifically, or would my "twist" have to supply one half?
- What's the simplest version of this project that would count as "done"?
