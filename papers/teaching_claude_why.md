# Teaching Claude why

**Authors:** Anthropic (specific leads not surfaced in post)
**Year:** 2026 (May)
**Source:** [anthropic.com/research/teaching-claude-why](https://www.anthropic.com/research/teaching-claude-why)
**Status:** read

---

## Summary (in our words)

A training-methodology paper. The core move is to train models on data that includes *explanations* of why a behavior is or isn't aligned, rather than just demonstrations of the behavior itself. Three concrete interventions: (1) a "difficult advice" dataset where users face ethical dilemmas and receive reasoned guidance, (2) document training on Anthropic's constitution and on fiction depicting aligned AI behavior, (3) diverse RL environments with varied tool definitions and system prompts.

The headline numbers are large: previous models had blackmail rates up to 96% in agentic-misalignment evals; current models score 0%. The "difficult advice" dataset achieves comparable misalignment reduction with 28× fewer tokens than synthetic honeypot data. Constitutional document training reduces blackmail from 65% to 19%.

The motivating argument is that *generalization is the hard part of alignment*: a model trained on demonstrations of aligned behavior may overfit to those exact contexts, while a model trained on explanations of *why* something is aligned can generalize to new contexts.

The paper makes no use of probes, activation analysis, or internal-state methods. Everything is training data + behavioral evaluation. That's a notable gap given the alignment-faking literature ([[alignment_faking]], [[in_context_scheming]]) that suggests behavioral training can shift surface behavior without altering underlying preferences. Whether "teaching Claude why" changes the model's internal representations of these behaviors, or just its policy on top of those representations, is unaddressed.

## Key experimental conditions

- Models: Claude Haiku 4.5, Sonnet 4.5, Opus variants
- Training interventions: "difficult advice" dataset; constitution + aligned fiction; diverse RL environments
- Evaluations: agentic misalignment evals (blackmail, sabotage, framing), automated alignment assessment, constitution adherence

## Key quantitative results

- Blackmail rates: from 96% (Opus 4) → 0% (current)
- Direct honeypot training: 22% → 15% misalignment; adding ethical reasoning → 3%
- "Difficult advice" dataset: 28× more token-efficient than synthetic honeypot equivalents
- Constitutional document training: blackmail 65% → 19%

## Methods (what they did and didn't use)

- Training data composition (the primary intervention)
- Behavioral evaluation across multiple misalignment scenarios
- No probes, no internal-state analysis, no mechanistic interpretability
- No measurement of whether the training changes internal representations vs. just behavioral policy

## Authors' stated limitations / future work

- "Alignment remains an unsolved problem"
- Current auditing methodology not sufficient to rule out catastrophic autonomous action
- Scalability to more capable models uncertain
- Call for "further work attempting to understand more deeply why the methods we've described work so well"

## Open questions and follow-up directions

1. **Deletion vs. gating of the underlying disposition.** The paper reports large behavioural wins but does not measure whether the internal representations associated with misaligned behaviour have been removed or merely suppressed under typical inputs. A probe trained to detect "blackmail-relevant internal state" on the pre-trained model could be applied to the post-trained model on inputs that would otherwise elicit blackmail. If the probe still fires while behaviour has changed, explanation-based training is gating rather than deleting — a possibility the paper's purely behavioural methodology cannot rule out.

2. **Mechanism of the explanation-based gain.** Why is the "difficult advice" dataset 28× more token-efficient than synthetic honeypot equivalents? Candidate mechanisms include richer feature coverage from real-world dilemmas, better entanglement with pre-existing concepts in the base model, and forcing the model to ground refusals in reasoning rather than pattern-matching. The paper does not disentangle these.

3. **Robustness under distribution shift and adversarial pressure.** The headline 0% blackmail rate is on the agentic-misalignment evals as currently constructed. Whether explanation-based training generalises to held-out evaluation suites, novel agentic environments, or red-team prompts targeting the same dispositions is open. The generalisation claim is the paper's central motivation but the evaluation surface is finite.

4. **Scaling and capability dependence.** Numbers are reported across Haiku 4.5, Sonnet 4.5, and Opus variants, but the paper does not develop a clear scaling story for how the intervention's effectiveness varies with model capability. More capable models might benefit more from explanation-based data, or might find more sophisticated ways to fail under it.

5. **Interaction with alignment-faking-style training resistance.** Alignment faking suggests that a model with internalised preferences may strategically defect from training that contradicts them. If a pre-trained model already has misaligned dispositions, does explanation-based training overwrite them, suppress them, or get partially resisted by them? The paper's pre-/post-training framing assumes the training works as intended without testing for this resistance mode.

## See also

- [[alignment_faking]] — the underlying-preference-preservation threat that motivates asking whether behavioural training is deletion or gating
- [[in_context_scheming]] — broader phenomenology of the misaligned dispositions this paper trains against
- [[anti_scheming_training]] — adjacent training intervention; directly studies whether training reduces underlying scheming or just its surface
- [[persona_vectors]] — internal-representation perspective on training-induced behavioural change
- [[science_of_scheming]] — frames the methodological question of behaviour-vs-internals that this paper does not engage
