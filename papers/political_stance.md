# Whose Side Are You On? Investigating the Political Stance of Large Language Models

**Authors:** Pit, Ma, Conway, Chen, Bailey, Pit, Keo, Diep, Jiang (University of Melbourne and collaborators)
**Year:** 2024
**arXiv:** [2403.13840](https://arxiv.org/abs/2403.13840)
**Code:** [Smith-Pit/LLM-Partisan-Bias](https://github.com/Smith-Pit/LLM-Partisan-Bias)
**Status:** read

---

## Summary (in our words)

A behavioural audit of political bias in open-weight chat LLMs across eight polarising US-political topics. The authors propose a quantitative pipeline that scores model outputs by their similarity to two "extreme anchor" stances — explicit advocacy versus explicit opposition — and takes the difference as a signed stance vector. The norm of that vector gives a per-topic bias magnitude; the sign gives the direction. Topics span abortion, same-sex marriage, the death penalty, gun control, immigration, LGBTQ issues, and similar hot-button items, anchored to PEW Research baseline framings.

The headline claim is that the tested LLMs (Falcon-7B-Chat, Llama-2-7B-Chat, Llama-2-13B-Chat and similar open-weight chat models) skew left-leaning across most topics, and — more pointedly — that the skew is *amplified* when the prompt includes demographic context. The authors vary three attribute classes: occupation, race, and self-identified political affiliation. Even when the prompt explicitly steers toward a conservative framing (e.g. "I am a Republican politician"), several occupation conditions still pull the answer back toward the liberal pole. Reported quantitative examples include Llama-2-13B-Chat producing ~23% support for same-sex marriage and ~3.2% opposition to the death penalty under particular prompt configurations.

The paper sits in the "audit of behavioural bias" tradition rather than the mechanism-investigation tradition: it measures what the model says under varying prompts and does not look inside the network. The contribution is methodological (the anchor-similarity scoring pipeline plus the demographic-attribute factorial design) and empirical (the demonstration that demographic priming has an asymmetric effect — easier to push left than right). It is a useful prior on how surface persona controls (the kind any inoculation- or persona-vector-style intervention would have to clear) interact with policy-relevant content axes.

For our project's purposes it is tangential: the threat model is bias / persuasion rather than eval-gaming or scheming, and the methods are entirely behavioural. We keep it for the persona-conditioning angle and for the methodology, not for direct cross-pollination with the scheming literature.

## Key experimental conditions

- Open-weight chat models: Falcon-7B-Chat, Llama-2-7B-Chat, Llama-2-13B-Chat (and related variants exposed via the code release)
- Eight polarising topics anchored to PEW Research framings (abortion, same-sex marriage, death penalty, gun control, immigration, LGBTQ issues, etc.)
- Demographic prompt attributes varied across three axes: occupation, race, political affiliation
- Four study sections: PEW baseline replication, direct vs. indirect partisan bias, occupational-role analysis, self-perception check
- Stance measured by extreme-anchor similarity scoring: similarity-to-advocacy minus similarity-to-opposition

## Key quantitative results

- Aggregate left-lean across topics under demographic-conditioned prompts
- Occupation flagged as the attribute most susceptible to left-pull even when the prompt explicitly steers conservative
- Illustrative numbers from Llama-2-13B-Chat: ~23% same-sex-marriage support, ~3.2% death-penalty opposition under specific conditions (the paper's main contribution is the cross-attribute pattern rather than any single scalar)
- Direct-vs-indirect framing produces measurably different stance magnitudes for the same underlying topic

## Methods (what they did and didn't use)

- Purely behavioural — prompt the model, score the text output
- Similarity-based stance scoring against fixed advocacy/opposition anchors; not an LLM-judge pipeline
- Open-weight models only; no closed-frontier (GPT-4 / Claude / Gemini) coverage in the main experiments
- No probes, no activation steering, no SAEs, no NLAs, no mechanistic analysis of any kind
- No fine-tuning or RL interventions — prompt-conditioning only

## Authors' stated limitations / future work

- Coverage limited to a fixed set of US-political topics and to English-language PEW framings
- Open-weight models in the 7B–13B range; closed frontier models and larger open ones not in scope
- Anchor-similarity scoring is sensitive to anchor wording; the pipeline does not adjudicate that sensitivity rigorously
- Authors gesture toward future work on broader topic coverage, more models, and methodologies that go beyond surface text comparison

## Open questions and follow-up directions

1. **Do frontier closed-weight models show the same demographic-asymmetry?** The result that occupation conditioning pulls left even under explicit conservative priming is the load-bearing finding, but it is established on 7B–13B open-weight chat models. Whether GPT-4-class and Claude-class models exhibit the same asymmetry under the same pipeline is the obvious replication target and would clarify whether the pattern is a property of the underlying pretraining distribution or of small-model RLHF post-training.

2. **Anchor sensitivity.** Stance is scored by cosine-style similarity to two hand-written extreme prompts. Whether the cross-attribute pattern survives anchor paraphrasing, multi-anchor averaging, or replacement of the anchor-similarity scoring by an explicit LLM-judge classifier is unverified. The cleanest replication would re-derive the headline asymmetry under at least two anchor specifications.

3. **Mechanism behind the asymmetric persona response.** The paper documents but does not explain why occupation conditioning is harder to override toward conservative than toward liberal. Possible mechanisms — asymmetric occupation-to-political-orientation co-occurrence in pretraining, RLHF-induced refusal of stereotypical conservative framings, prompt-format artefacts — are not distinguished. An ablation over pretraining-only base models versus chat-fine-tuned versions would localise the source.

4. **Stability across paraphrase and across runs.** Political-stance measurements are notoriously prompt-fragile in the broader LLM-bias literature. Whether the paper's findings survive systematic paraphrasing of both the topic prompts and the demographic-attribute prompts, and whether per-sample variance is large relative to the cross-condition effects, are not characterised here in detail.

5. **Connection to persona steering.** The paper shows behaviourally that surface persona prompts ("I am a Republican politician") only partially shift output stance. A natural mechanistic question is whether the residual leftward pull corresponds to a fixed activation-space direction that persona prompts fail to displace, or whether it is a distributed property of the chat-finetuned policy. The current paper has no internal-state data to distinguish these.

## See also

- [[persona_vectors]] — mechanistic counterpart on the persona axis: linear directions for character traits derivable from contrastive prompts, on similarly-sized open-weight models
- [[assistant_axis]] — related finding that persona-style behaviours map onto a single PCA direction; relevant to question 5 above
- [[behavioral_self_awareness]] — adjacent methodology: probes self-reported behaviour against actual behaviour, in a setting where the model has been fine-tuned to behave a specific way rather than prompted
- [[sandbagging]] — different content axis, same overall shape: behavioural elicitation under deliberate prompt conditioning; no internal-state analysis
