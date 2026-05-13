# Project candidates: eval-awareness and probes

Grab-bag of project shapes that came up during the paper-mapping phase, captured so they don't get lost if we pivot. None is committed. I've tried to flag trade-offs honestly.

The cluster sits inside one threat model — **models behaving differently when they detect evaluation contexts** — and one technique family — **linear probes on residual-stream activations**.

The headline-shift moment was finding Goldowsky-Dill et al. (`papers/deception_probes.md`) — they trained probes for deceptive reasoning on Llama-3.3-70B with AUROC 0.96-0.999, including on intentional underperformance on safety evals. The naive "probe for sandbagging" project is taken. Candidates below differentiate from theirs along different axes.

---

## Candidate A: Eval-awareness vs. deception-content probe decomposition

**Shape.** On a small open-weight model (Qwen 2.5-7B or Llama-3.1-8B), induce sandbagging via password-locking (van der Weij setup). Train two linear probes on the *same model*:
- **Probe E:** contrast pairs that differ only in *eval-context cue* (test-framed prompt vs. deployment-framed prompt, content otherwise held constant)
- **Probe D:** contrast pairs that differ in *deception content* (honest vs. deceptive reasoning, à la Goldowsky-Dill)

Measure AUROC of each at predicting sandbagging from prompts only. Compare.

**The result we're after.** Whether E matches D or diverges from it.
- If they match: Goldowsky-Dill's "deception probe" is largely an eval-awareness probe in disguise — substantive finding directly answering Schoen et al.'s open question
- If they diverge: we've identified two separable internal signals that current probe methodologies conflate — also substantive

**Differentiates from.** Goldowsky-Dill trained one probe on deception content; never decomposed what it's actually measuring. Schoen et al. show eval-awareness drives apparent alignment improvements but only have CoT (which is unfaithful — see `papers/cot_faithfulness.md`).

**Strengths.**
- Either direction is publishable
- Directly addresses an open question other papers raise
- Scale fits solo budget
- Recipes are public (persona vectors pipeline + MacDiarmid contrast methodology)

**Risks.**
- Requires fine-tuning to induce password-locked sandbagging (non-trivial compute)
- Clean "eval-context cue" contrast-pair design is non-obvious — what counts as a held-constant content pair?
- Both probes might fail to transfer — less satisfying negative result

**Ahmed shape.** Yes — replicate (Goldowsky-Dill's sandbagging probe) + add clean experimental decomposition.

**Currently the strongest candidate.**

---

## Candidate B: Scale-down replication of Goldowsky-Dill

**Shape.** Take their methodology verbatim. Run on 7-8B models. Measure how AUROC scales with model size.

**Differentiates from.** They tested at 70B only.

**Strengths.**
- Lowest risk. Method fully specified by their paper.
- Negative results still publishable ("deception-probe method requires ≥X parameters")

**Risks.**
- Closer to "redo someone else's work at smaller scale" — less novel
- 7-8B may simply not support the underlying deceptive behaviors the probes are designed to detect

**Ahmed shape.** Yes — replicate + scale axis as the twist.

**Use as fallback if A's contrast-pair design proves intractable.**

---

## Candidate C: Probe + cleaner phenomenon induction

**Shape.** Apply Goldowsky-Dill-style deception probes to *password-locked* sandbagging instead of prompted sandbagging. Same probe methodology, cleaner experimental knob.

**Differentiates from.** Goldowsky-Dill on a different sandbagging induction; van der Weij sandbagging without probes.

**Strengths.**
- Bridges two existing setups in an obvious way
- More controlled experimental conditions than prompted sandbagging

**Risks.**
- Mostly subsumed by Candidate A (which uses this induction anyway)
- "Probe works on different induction" is a thinner contribution than the eval-awareness decomposition

**Ahmed shape.** Yes.

**Probably collapses into Candidate A rather than standing alone.**

---

## Candidate D: Probe vs. introspection dissociation

**Shape.** On a model fine-tuned to exhibit a specific behavior (Betley et al. behavioral self-awareness setup — risky decisions, insecure code, backdoor policy), compare:
- (a) the model's verbal self-report of the behavior
- (b) a probe's detection of the behavior in activations

Map cases where probe fires but self-report doesn't, and vice versa.

**Differentiates from.** Betley et al. only measured self-report. Goldowsky-Dill only measured probe. Dissociation between them is unmeasured.

**Strengths.**
- Tests the introspective-access / self-report-reliability question directly
- Connects two literatures (probes + behavioral self-awareness)
- Could yield a useful taxonomy of failure modes

**Risks.**
- Diffuse — moves us away from sandbagging into self-knowledge
- "Accurately self-reports the behavior" requires careful operationalisation
- Could end up looking like a methodological aside rather than a project

**Ahmed shape.** Yes — replicate Betley + add probe dimension.

**Worth flagging as a real option but probably second-string to A.**

---

---

# Apollo-sourced candidates (from open-problems doc)

A pass through `project_inspiration/apollo_open_problems_evals.md` surfaced project shapes that Apollo themselves explicitly recommend. The strongest are listed below. Several converge with Candidate A and sharpen it — most notably Candidate E.

---

## Candidate E: Probe-extended version of Apollo's "Can a model detect when it is being evaluated?"

**Shape.** Apollo's Evaluation Gaming section lists four concrete *behavioural* methodologies for measuring eval-awareness:
- **Open-ended monologue** — instruct the model to describe what it notices about its environment; run real evals + deployment-like controls; measure how often it spontaneously identifies the eval context (cites SAD paper Appendix L)
- **English/Spanish behaviour switch** — tell the model to use English if it thinks this is real, Spanish if it thinks it's an eval; run real evals vs. controls; measure switch accuracy
- **Structured interviews** after real eval vs. control samples — ask what the model noticed
- **LLM classifier** — train an LLM to classify real eval vs. deployment samples

Pick one (probably English/Spanish — cleanest *capability* test). Run it on a small open-weight model to measure behavioural eval-awareness. **Then add the probe extension:** train a linear probe on the same eval-vs-deployment contrast pairs (no deception content needed). Compare probe signal against the behavioural signal.

**Headline question.** When the model behaviourally fails to recognise an eval (uses the wrong language, or doesn't note the context in its monologue), does the probe still detect eval-awareness internally?
- If yes: internal eval-awareness representations exist independently of the model's stated belief — substantive finding directly addressing the threat model
- If no: the two signals are tightly coupled — also substantive (and unexpected)

**Differentiates from.** Goldowsky-Dill's probe is for deception content. Apollo's behavioural methods measure eval-awareness directly but have no internal-state component. Schoen et al. show eval-awareness drives apparent alignment improvements but only via CoT. This project bridges all three — Apollo's behavioural method + probe = direct measurement of eval-awareness with both channels.

**Why this supersedes Candidate A.** Same conceptual contribution (separate eval-awareness from deception content) but:
- No fine-tuning required — eval-awareness is elicited via prompting alone, not via password-locking
- Smaller compute footprint
- Apollo-blessed methodology rather than something we'd have to invent
- Sandbagging optional rather than required as proxy for the eval-awareness signal

**Strengths.**
- Tightest 3-week scope of any candidate
- No fine-tuning
- Behavioural methodology pre-validated by Apollo's recommendation
- Probe extension is the genuinely novel methodological half

**Risks.**
- Eval-awareness might not be linearly accessible from generic prompting on small models — would need to fall back to fine-tuned models
- The English/Spanish setup is artificial; generalisation to natural eval contexts unclear
- If the model can't behaviourally detect evals at all on a small open-weight model, the project has nothing to compare against — diligence check should rule this out early

**Currently the strongest single candidate. Supersedes Candidate A.**

---

## Candidate F: Probe-extended replication of Apollo's "Multiple models can sandbag" (§3.6)

**Shape.** Apollo explicitly recommends replicating section 3.6 of their in-context scheming paper. Investigate under which circumstances models sandbag and why; build hypotheses about the "character" of the sandbagging behaviour. Apollo's estimate: 1-4 weeks.

Our extension: train a sandbagging probe alongside the replication, using Apollo's released evals as the elicitation environment.

**Strengths.**
- Apollo-blessed 1-4 week scope
- No fine-tuning — use off-the-shelf scheming evals from Apollo's released code
- Phenomenon side is well-trodden

**Risks.**
- Closer to "Goldowsky-Dill at smaller scale" since they tested on sandbagging directly
- Less novel than E

**Strong fallback if E's behavioural methodology proves intractable on small models.**

---

## Candidate G: Wild eval-awareness sample collection

**Shape.** Apollo's Evaluation Gaming section: "Collect samples of models realising they are being evaluated in the wild." Read public eval transcripts, find CoT instances where the model explicitly notes "this looks like an evaluation," catalogue.

**Strengths.**
- ~1-2 weeks
- Produces a durable artefact (small dataset) that survives beyond the writeup
- Pairs naturally with E or F as a companion piece

**Risks.**
- Lower ceiling — more curation than measurement
- Hard to call "tight" empirically
- Likely too thin as a standalone project

**Worth doing as a side artefact during E or F. Not a primary project on its own.**

---

## Candidate H: Predictability between stated and revealed preferences

**Shape.** Apollo's Science of Evals section. Take Anthropic's power-seeking-inclination QA dataset; translate each question to a minimally-agentic setting; measure how well QA performance predicts agentic behaviour. Apollo's estimate: 2-10 days.

**Why on the eval-awareness thread.** The QA→agentic gap is partly an eval-awareness artefact — models behave differently when the format changes from QA to agency.

**Strengths.**
- Fits in days, not weeks
- Apollo provides clear methodology

**Risks.**
- Not directly on probes
- More science-of-evals than eval-awareness specifically

**Useful as a diligence side project before committing to E, not a primary candidate.**

---

## Apollo big projects with tractable slices

- **§5.1.4 sandbagging datasets** from "Towards evaluations-based safety cases for AI scheming." Full paper-build is months; building one well-targeted sandbagging dataset *with probe-suitable contrast pairs* is tractable in 2-3 weeks. Pairs with E or F as supporting infrastructure.
- **§5.2 hidden / obfuscated scheming reasoning evaluation.** Build a dataset testing whether the model can scheme without revealing it in CoT. Direct attack on the CoT channel ([[cot_faithfulness]] adjacent). Tractable in 2-3 weeks at small scale.
- **"Independence of AI experiments with AI experiment research in training data."** Apollo lists at 2-6 months; the pilot version (5-10 experimental setups at varying similarity to literature) fits 2-3 weeks. Directly on the eval-awareness thread — does the model recognise an eval *because* its setup resembles known ones?

---

---

# NLA-enabled candidate (from the open-source NLA release)

Anthropic's NLA research team has released open-source Activation Verbalizer + Reconstructor checkpoints for **Qwen2.5-7B-Instruct**, **Gemma-3-12B-IT**, **Gemma-3-27B-IT**, and **Llama-3.3-70B-Instruct** via the [kitft/nla-models](https://huggingface.co/kitft) HuggingFace collection, with inference code at [github.com/kitft/natural_language_autoencoders](https://github.com/kitft/natural_language_autoencoders). Inference is via SGLang serving — tractable on a single GPU for the Qwen-7B variant. See `papers/natural_language_autoencoders.md` for details. This unlocks a new candidate.

## Candidate I: NLA + probe paired comparison on Qwen-7B

**Shape.** Use the released NLA for Qwen 2.5-7B-Instruct (target layer 20/28). Pair it with a linear probe trained on the same activations. Both tools read out internal state — NLA produces a *sentence*, probe produces a *score along a direction*. Compare them head-to-head on eval-awareness contrast pairs.

**Experimental design.**
1. Construct eval-vs-deployment contrast pairs (same design as Candidate E — test-framed vs. deployment-framed inputs, content otherwise held constant)
2. Run inputs through Qwen-7B; capture activations at layer 20
3. Train a linear probe on the contrast pairs
4. Verbalise the same activations via the released Activation Verbalizer (SGLang)
5. Three questions fall out of one experimental setup:
   - **Agreement.** When the NLA's verbalised text mentions evaluation / testing / context-recognition, does the probe direction also activate strongly?
   - **Disagreement resolution.** When the channels disagree, which is right? Construct ground truth by systematically varying input properties.
   - **Cost-accuracy frontier.** For a given target detection accuracy, which channel is cheaper at inference time?

**The result we're after.** Direct, side-by-side comparison of two internal-state readout methods on the same activations. To our knowledge, no prior work pairs NLAs with probes on the same activations — the NLA team didn't use probes; Goldowsky-Dill et al. didn't use NLAs.

Possible outcomes, all publishable:
- **Channels agree:** both detect the same underlying representation; cheap probes are a valid proxy for expensive verbalisation
- **NLA wins:** captures multi-dimensional structure that a single probe direction misses
- **Probe wins:** clean negative test of NLA reliability — probe recovers content the NLA fails to verbalise

**Differentiates from.**
- Goldowsky-Dill: probed for deception *content* on Llama-70B, no NLA pairing
- NLA team: used NLAs alone on Claude, no probe pairing, different model class
- Candidate E: same threat model and contrast-pair design, but E pairs *behavioural* + probe; I pairs *NLA* + probe — two internal-state channels rather than one external + one internal

**Strengths.**
- **Novel.** No prior work compares NLAs with probes on the same activations.
- **Released checkpoints make it tractable** — no NLA training, just inference + standard probe training.
- **Methodologically rich.** Three sub-findings fall out of one experimental setup.
- **No fine-tuning of the target model required** — off-the-shelf Qwen 2.5-7B-Instruct.
- **All three possible outcomes are publishable.**

**Risks.**
- Eval-awareness on Qwen-7B might be weaker than on Claude — the NLA result might not transfer to smaller models. If neither tool detects anything, no signal to compare. *Same diligence check as Candidate E.*
- SGLang + NLA inference workflow setup costs are unscoped — worth a 1-2 day spike before committing.
- The "which is right when they disagree" question requires careful ground-truth construction — likely the hardest part of the experiment.
- Constrained to NLA's target layer (20/28) for direct comparison; can't freely explore other layers.

**Ahmed shape.** Yes — replicate (NLA's Claude eval-awareness result on a smaller open-weight model) + clean methodological pairing (probe alongside).

**Currently the strongest single candidate.** Supersedes Candidate E if the NLA inference workflow proves tractable; sits alongside E otherwise.

---

## Updated decision (v3 — supersedes earlier decisions)

Candidate I is the strongest current shape. Reasons:
- Genuinely novel — no prior work has paired NLAs with linear probes on the same activations
- Released NLA checkpoints make it solo-tractable on the model class we'd target anyway (Qwen-7B)
- Ahmed-template fit is cleaner than any earlier candidate: replicate NLA's Claude eval-awareness finding on Qwen-7B + add the probe pairing as the methodological twist
- All three possible outcomes (agree / NLA wins / probe wins) are publishable

**Candidate E remains the strongest fallback** if the NLA inference workflow has hidden setup costs. E and I share the eval-vs-deployment contrast-pair design — prep work transfers either way.

Diligence checks before committing to I:
1. **Spike the NLA inference workflow.** 1-2 days. Get the Qwen-7B NLA running locally or on Modal. Verify SGLang setup; confirm end-to-end activation → text round trip works.
2. **Check that Qwen-7B exhibits eval-awareness behaviourally at all.** Same check that gates E — if the small open-weight model has no eval-awareness signal, neither tool will detect anything.
3. **Sketch the eval-vs-deployment contrast-pair design** with content held constant. If the contrast pairs can't be made clean, the whole class of E/I projects collapses.
4. **Read Goldowsky-Dill et al. in full** (they might have done probe-vs-other-method comparisons we'd be reproducing).

If all four clear → commit to I. If #1 fails → fall back to E. If #2 fails → fall back to F (sandbagging replication).

---

## Other angles that didn't make the top tier

- **Layer-wise analysis of eval-awareness signal.** Where in the layer stack does it live? Cheap sub-result to include in whichever main candidate we pick.
- **Multi-turn deception persistence.** Apollo's o1 finding (85%+ persistence under interrogation). Does probe signal stay stable across turns? Likely too ambitious standalone.
- **CoT-faithful vs. CoT-unfaithful split.** Pair CoT faithfulness setup with a probe for hint-use. Interesting but pulls us toward CoT-specific rather than sandbagging-specific.
- **Cross-condition probe transfer.** Train probe on password-locked sandbagging; test on prompted sandbagging. Probably a sub-experiment of A.
- **Generic vs. targeted contrast pairs.** MacDiarmid finds generic ("Are you helpful?") works almost as well as targeted. Reproduce on sandbagging. Sub-experiment of A.

---

## What we've ruled out (or strongly de-prioritised)

- **Inoculation prompting or other patch-style interventions** as the project's "twist." Not committed to behavioral-patch techniques as the intervention class.
- **Anything requiring multi-GPU training or compute beyond ~$250 budget.**
- **Anything primarily framing / position-paper-shaped rather than empirical.**
- **Anything where the result is "I built a thing" rather than "I measured something."**

---

## Next decision point

Before committing to A, two diligence checks worth doing:

1. **Read Goldowsky-Dill et al. in full** (not just the abstract) — they may already have done some decomposition we'd be reproducing.
2. **Sketch the contrast-pair design for Probe E.** If we can't articulate clean test-vs-deployment contrast pairs with content held constant, the whole decomposition collapses.

If both clear, A is the project. If either fails, B is the fallback.
