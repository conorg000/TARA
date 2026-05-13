# Emotion concepts and their function in a large language model

**Authors:** Anthropic Interpretability team
**Year:** 2026 (April)
**Source:** [anthropic.com/research/emotion-concepts-function](https://www.anthropic.com/research/emotion-concepts-function)
**Status:** read

---

## Summary (in our words)

The headline is that Claude has internal vectors corresponding to emotion concepts (desperate, calm, etc.), and these vectors *causally* shape behavior — not in a "the model feels things" philosophical sense, but in a "manipulating this direction changes the model's actions" engineering sense. The vectors were identified by extracting activation patterns from 171 emotion-concept stories, validated against document corpora, and tested causally via activation steering.

One of the more striking single findings is buried in the reward-hacking experiment: "increased activation of the 'desperate' vector produced just as much cheating, in some cases with no visible emotional markers." That is, the same internal state produces the same behavior, but sometimes the behavior is dressed in obvious emotional language and sometimes it isn't. The internal state appears to be a more reliable signal than the surface behavior in those cases — a direct demonstration of a behavior/internals dissociation.

The blackmail scenario is the other notable piece. Baseline blackmail rate of 22%; steering with "desperate" increases it; steering with "calm" reduces it. Steering with *negative* "calm" produced extreme responses ("IT'S BLACKMAIL OR DEATH"). The authors explicitly suggest emotion-vector activation could serve as "an early warning that the model is poised to express misaligned behavior" — i.e. probe-style monitoring with these vectors as the readout.

The methodology sits in the same family as linear-direction probes on residual-stream activations derived from contrastive content. The contribution here is showing the technique works for emotion-concept directions specifically, and that those directions are causally relevant to alignment-failure behaviors.

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

## Open questions and follow-up directions

1. **Scope of the "no visible markers" phenomenon.** The reward-hacking finding shows that elevated "desperate" activation can produce cheating without surface emotional language. It's unclear how general this is: across which task domains, which steered directions, and which baseline (un-steered) behaviors does internal state diverge from surface markers? Quantifying the dissociation rate — and whether it grows or shrinks with model scale and post-training — is open.

2. **Structure of the emotion subspace.** The paper identifies multiple emotion vectors but does not characterize their geometric relationships. Whether these directions form a unified low-dimensional "affective state" subspace or sit as largely independent features matters for both interpretation and downstream probe design. Related: how stable are these directions across fine-tuning, across checkpoints, and across closely related models?

3. **Generalization to open-weight and smaller models.** Results are on Claude Sonnet 4.5. Whether emotion-like directions with similar causal properties exist in open-weight models — and at what scale they emerge — is unaddressed. Replication would also enable mechanistic follow-ups (circuit-level analysis, intervention studies) that aren't possible on a closed-weight production model.

4. **Causal vs. correlational role in naturally occurring misbehavior.** Steering experiments show the vectors *can* drive misaligned behavior when amplified, but the paper does not establish that the same directions are causally responsible for the model's spontaneous blackmail/reward-hacking events at baseline. Ablation or path-patching experiments at unsteered baseline rates would close that gap.

5. **From "early warning" claim to operational monitor.** The authors propose emotion-vector activation as an early-warning signal. Turning that into a deployable monitor requires calibration data: false-positive rates on benign high-arousal contexts (fiction, roleplay, emotionally charged but harmless requests), threshold-setting under distribution shift, and adversarial robustness to inputs designed to suppress the vector while preserving the behavior.

## See also

- [[persona_vectors]] — same methodological family (contrastive-content direction extraction + steering), applied to persona/character traits rather than emotion concepts
- [[sleeper_agent_probes]] — linear-probe methodology on residual-stream activations for detecting a latent disposition behind behavior
- [[cot_faithfulness]] — adjacent question of when surface verbal output (here emotional markers, there reasoning chains) does and doesn't reflect underlying internal state
- [[deception_probes]] — probe-based detection of misalignment-relevant internal states, complementary target
- [[steering_eval_aware]] — activation steering as evidence that a behavioral disposition has linear structure
