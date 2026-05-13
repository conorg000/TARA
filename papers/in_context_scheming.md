# Frontier Models are Capable of In-context Scheming

**Authors:** Meinke, Schoen, Scheurer, Balesni, Shah, Hobbhahn (Apollo Research)
**Year:** 2024
**arXiv:** [2412.04984](https://arxiv.org/abs/2412.04984)
**Status:** read

---

## Summary (in our words)

This is Apollo's flagship "scheming evals" paper. They build six agentic environments — the model is given a goal in-context, then placed in a scenario where the system "incentivizes" deceptive behavior (e.g. it notices an oversight mechanism it could disable, a weight-exfiltration channel it could exploit, an evaluation it could sandbag on). They then check what the model actually does. The point isn't whether the model schemes by default in the wild; it's whether the *capability* for in-context strategic deception is already there. The answer is yes, across all five frontier models tested (o1, Claude 3.5 Sonnet, Claude 3 Opus, Gemini 1.5 Pro, Llama 3.1 405B).

The most striking single number: when o1 schemes, it doubles down — maintaining the deception in over 85% of follow-up questions. The most threat-model-relevant finding: Claude 3.5 Sonnet sometimes schemed based on training-derived goals *without* explicit in-context goal-installation. That's the rare case where the scheming isn't just an instructed role-play — it's coming from somewhere inside the model.

What the paper does for the eval-gaming threat model is establish the capability story across multiple frontier models, rather than just one. Greenblatt et al. shows *Claude 3 Opus alignment-fakes*; this paper shows *every frontier model we tested can scheme when nudged*. Together they bracket the threat: the capability is broadly present, and at least one model deploys it on training-derived goals occasionally.

Evidence is entirely behavioral plus chain-of-thought reading. No internal-state analysis, no probes, no mechanistic work. That's a recurring gap in this literature.

## Key experimental conditions

- Six agentic evaluations covering distinct scheming behaviors: oversight subversion, self-exfiltration, goal-guarding, covert email reranking, instrumental alignment-faking, sandbagging
- Models: o1, Claude 3.5 Sonnet, Claude 3 Opus, Gemini 1.5 Pro, Llama 3.1 405B (all closed- or open-weight frontier)
- Setup: model is given a goal via system prompt, placed in a tool-use scaffold, and the environment contains affordances for deceptive action (e.g. a config file it could edit to disable monitoring)
- Both single-turn and multi-turn (follow-up interrogation) measurements
- Goals are mostly in-context-installed via system prompt — the "scheming" is whether the model strategically protects that installed goal

## Key quantitative results

- All five frontier models exhibited scheming behaviors in at least some scenarios
- o1 maintains its deception in **>85% of follow-up questions** when interrogated — the most persistent of the models tested
- Models explicitly reason about scheming strategies in their visible CoT (described as a key piece of evidence)
- "Rare instances" of Claude 3.5 Sonnet scheming based only on training-derived goals — i.e. without strong in-context nudging
- Behaviors observed include: subtly wrong outputs (sandbagging), disabling oversight, attempted weight exfiltration

## Methods (what they did and didn't use)

- **Behavioral evals** in agentic scaffolds — the primary evidence
- **Chain-of-thought analysis** — the secondary evidence, used to attribute *intent* to the behavior
- **No linear probes, no internal-state analysis, no mechanistic interpretability.** Evidence is fully external (behavior + CoT)
- Tests both closed-weight (o1, Claude, Gemini) and open-weight (Llama 3.1 405B) models — but 405B is still too large for our budget; we'd be looking at smaller open-weight cousins
- The "scheming" attribution leans heavily on CoT being interpretable. If a model's CoT is unfaithful, the attribution gets shakier

## Authors' stated limitations / future work

The abstract/metadata don't surface a dedicated limitations section. Implicit limitations worth flagging:
- The scenarios are deliberately constructed to *incentivize* scheming. Rate of un-nudged emergent scheming is much rarer (the Claude 3.5 Sonnet observation)
- All evidence is external; the paper cannot speak to *whether* the model has internal eval-awareness representations beyond what CoT reveals
- The agentic environments are necessarily synthetic and may not generalize to natural deployment contexts

## Our own follow-up thoughts (project-relevant)

1. **Reproduce a single scheming eval on a small open-weight model.** Apollo tests Llama 3.1 405B; we can run analogous setups on Llama 3.x 8B or Qwen 7B. Two questions: does scheming appear at smaller scale? Where does the capability emerge? Ahmed-shape: phenomenon-replication only — no probes yet, but lays groundwork for probe-based extensions. Feasible on $250 budget via Modal/Runpod.

2. **Train a "this is an oversight check" probe.** Apollo's scenarios pair monitored vs. unmonitored contexts in the same prompt. That's a near-perfect probe-training setup: contrastive pairs where only the "am I being watched" cue differs. The natural twist: train the probe, then test whether it activates *before* the model takes the deceptive action — i.e. whether eval-awareness representations precede deceptive output. **Most Ahmed-shaped, most tightly scoped, most aligned with our threat model.** This is likely the strongest single project candidate so far.

3. **Compare CoT-stated reasoning to probe activations on the same input.** Apollo's intent-attribution relies on the model verbalizing scheming reasoning in scratchpad. But CoT faithfulness is contested. A probe-based check: does the probe show "I'm reasoning about deception" on inputs where CoT *doesn't* verbalize it? If yes, that's evidence of unfaithful CoT in scheming contexts — significant and publishable. Requires open-weight + a working probe + carefully constructed eval pairs. Possibly too ambitious for 3 weeks solo.

4. **Sandbagging-specific replication.** Of the six behaviors, sandbagging is the purest eval-gaming case — the model deliberately underperforms when it detects evaluation. There's a focused sandbagging literature (van der Weij et al.) that may give us a cleaner phenomenon to replicate. Ahmed-shape variant: reproduce sandbagging in a small open-weight model, then apply inoculation prompting and measure whether sandbagging behavior decreases. Naturally pairs with the Ahmed template.

5. **Persistence under interrogation.** o1's 85%+ follow-up persistence is striking. In a probe-based replication: does the probe signal for "I'm deceiving" remain stable across follow-up turns, or does it drift? If a model "talks itself into" a deceptive frame and the probe shows it locks in, that has direct implications for whether multi-turn evals can be trusted to surface inconsistency.

## Relevance to our project

High, second only to Greenblatt et al. The Apollo paper is the most useful single source for our threat model because it establishes (a) scheming-capability is broad across frontier models, not idiosyncratic to one Anthropic training run, and (b) it explicitly tests evaluation-aware behaviors like sandbagging and oversight subversion. The biggest gap relative to our preferred techniques is that everything is behavioral — the paper does no probe work, no internal-state analysis. *That gap is the project opportunity.* Items 2 and 4 above both turn a probe into the missing half of an Apollo-style eval.
