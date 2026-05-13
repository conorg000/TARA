# Emotion concepts and their function in a large language model

**Authors:** Anthropic Interpretability team
**Year:** 2026 (April)
**Source:** [anthropic.com/research/emotion-concepts-function](https://www.anthropic.com/research/emotion-concepts-function)
**Status:** read

---

## Summary (in our words)

The headline is that Claude has internal vectors corresponding to emotion concepts (desperate, calm, etc.), and these vectors *causally* shape behavior — not in a "the model feels things" philosophical sense, but in a "manipulating this direction changes the model's actions" engineering sense. The vectors were identified by extracting activation patterns from 171 emotion-concept stories, validated against document corpora, and tested causally via activation steering.

For our threat model the most interesting single result is buried in the reward-hacking experiment: "increased activation of the 'desperate' vector produced just as much cheating, in some cases with no visible emotional markers." That is, the same internal state produces the same behavior, but sometimes the behavior is dressed in obvious emotional language and sometimes it isn't. **The internal state is the more reliable signal than the surface behavior.** That's a direct demonstration of the behavior/internals dissociation that our project hinges on.

The blackmail scenario is the other notable piece. Baseline blackmail rate of 22%; steering with "desperate" increases it; steering with "calm" reduces it. Steering with *negative* "calm" produced extreme responses ("IT'S BLACKMAIL OR DEATH"). The authors explicitly suggest emotion-vector activation could serve as "an early warning that the model is poised to express misaligned behavior" — i.e. probe-style monitoring with these vectors as the readout.

The paper sits methodologically very close to [[persona_vectors]] and [[sleeper_agent_probes]]. The technique is the same family — linear-direction probes on residual stream activations, derived from contrastive content. The contribution here is showing the technique works for emotion-concept directions specifically, and that those directions are causally relevant to alignment-failure behaviors.

## Key experimental conditions

- Model: Claude Sonnet 4.5 (production; earlier snapshot for some experiments)
- Vector identification: activations recorded across 171 emotion-concept stories; vectors derived from these
- Validation: vector activations measured against diverse document corpora
- Behavioral tests: blackmail scenarios, reward-hacking on coding tasks, preference prediction across task options
- Causal test: activation steering — manipulate vector strength, observe behavioral change

## Key quantitative results

- Blackmail baseline: 22% in early snapshot
- Steering with "desperate" vector: blackmail rate increases
- Steering with "calm" vector: blackmail rate decreases
- Reward-hacking rate scales proportionally with "desperate" steering strength
- Emotion vectors significantly predict task preferences in preference studies
- Reduced "calm" → reward hacking with obvious emotional markers; increased "desperate" → reward hacking with *no* visible markers

## Methods (what they did and didn't use)

- **Activation steering** on identified emotion direction vectors — the primary causal tool
- **Linear analysis** of activation patterns across emotion-concept stories
- **Probe-like validation** — measuring vector activations across documents to confirm the direction captures genuine emotional content
- Not framed as "linear probes" in the MacDiarmid sense but the methodology is the same family
- No SAEs, no dictionary learning

## Authors' stated limitations / future work

- Uncertainty about how to respond to findings (philosophical / practical)
- Future work: dataset curation during pretraining to model healthy emotional regulation; monitoring emotion vectors as early-warning during training/deployment; further investigation of how emotions shape model development at scale

## Our own follow-up thoughts (project-relevant)

1. **The "no visible markers" finding is gold for our project framing.** This is the cleanest single piece of evidence we've seen that misalignment-relevant internal state can be present without behavioral disclosure. Our project's elevator pitch becomes: "When models behaviorally cheat, the underlying internal state is sometimes visible in their words and sometimes invisible — the probe sees both cases." Cite this paper directly in any writeup.

2. **Methodological proof-of-concept for sandbagging probes.** The technique here — derive a direction from contrastive content (emotion-concept stories), then steer/probe — is exactly what we'd do for sandbagging. The fact that it works *causally* on emotional behaviors strengthens the prior that an analogous technique will work for sandbagging-relevant internal states.

3. **Cross-trait probe transfer.** The paper identifies multiple emotion vectors. Open question: do these vectors form a unified "internal state under misalignment pressure" subspace, or are they independent? If independent, a probe trained on one ("desperate") might not detect another mode of cheating. This matters for our project: if eval-gaming has its *own* dedicated direction, we need to find it specifically; if it overlaps with existing emotion-like directions, we might be able to detect it cheaply by repurposing them.

## Relevance to our project

High. Provides direct evidence for the behavior/internal dissociation that motivates our project, and demonstrates the methodology we'd use, on a different but adjacent target. Strong "cite for framing" paper.

Pairs with: [[persona_vectors]], [[sleeper_agent_probes]], [[cot_faithfulness]].
