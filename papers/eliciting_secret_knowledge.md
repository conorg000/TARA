# Eliciting Secret Knowledge from Language Models

**Authors:** Cywiński, Ryd, Wang, Rajamanoharan, Nanda, Conmy, Marks
**Year:** 2025
**arXiv:** [2510.01070](https://arxiv.org/abs/2510.01070)
**Status:** read

---

## Summary (in our words)

A methodologically rigorous test of "can we extract knowledge a model has but actively denies." The authors train LLMs to apply hidden information in their downstream behaviour (e.g. infer the user's gender and use it to shape responses) while *explicitly denying having that information when asked directly*. Then they test multiple elicitation methods to recover the hidden knowledge: black-box prefill attacks, logit lens (white-box), and sparse autoencoders (white-box).

Headline result: **black-box prefill attacks consistently outperform the white-box methods.** Logit lens and SAEs do increase success rate, but are less effective than just generating completions from carefully-chosen prefixes. The released models + code constitute a public benchmark for this elicitation problem.

The black-box-beats-white-box finding is the paper's own important caveat about internal-state methodology. The "probes and SAEs see what behavioural channels miss" intuition is at least partially undermined here: on this task, a simpler prompting trick recovers more concealed knowledge than reading the residual stream through a learned dictionary. Worth noting that the paper compares prefill against probes/SAEs specifically; it does not compare direct activation steering or natural-language-autoencoder-style verbalisation against prefill, so the broader white-box space is only partially explored.

## Key experimental conditions

- Three families of LLMs
- Training design: models trained to use specific knowledge in downstream behaviour while explicitly denying that knowledge when asked
- Elicitation methods tested: black-box prefill, white-box logit lens, SAEs
- Measurement: success rate of auditors guessing the secret knowledge

## Key quantitative results

- Prefill attacks "consistently outperformed other methods in all settings"
- Logit lens and SAEs "consistently increase the success rate" but are "less effective" than black-box
- Specific numbers in the full paper

## Methods (what they did and didn't use)

- Black-box prefill attacks (no internal access)
- Logit lens (white-box, layer-wise distributions)
- Sparse autoencoders (white-box, dictionary learning)
- **No linear probes specifically, no NLAs, no activation steering**
- Released benchmark — models + code public

## Authors' stated limitations / future work

- Specific limitations not detailed in the available abstract
- The paper is structured as a benchmark contribution; future work likely focuses on stronger elicitation methods

## Open questions and follow-up directions

1. **Why does prefill beat white-box here?** The mechanistic explanation for prefill's edge over logit lens and SAEs is not obvious. Candidate stories include: SAE dictionaries failing to allocate features to the specific concealed concept; logit-lens losing the relevant signal in intermediate layers; or the concealed knowledge being represented in a form that surfaces more readily in *output distributions under prompting* than in *raw activations under decoding*. Disentangling these would inform when white-box methods are worth the overhead.

2. **Comparison to other white-box techniques.** The paper compares prefill against logit lens and SAEs. Direct activation steering, supervised linear probes targeted at the concealed concept, and natural-language-autoencoder-style activation verbalisation are not evaluated. A more complete methodological picture requires those head-to-head numbers on the released benchmark.

3. **Generalisation across concealment task structure.** The training design uses specific kinds of concealed knowledge (e.g. demographic inference). Whether prefill's advantage persists when the concealed knowledge is procedural, multi-step, or about the model's own state (rather than about the user) is open. Eval-awareness and scheming-relevant concealment are arguably structurally different from "secret fact about the user."

4. **Auditor capability scaling.** Success rates are measured against an auditor guessing the secret. How those rates change with stronger auditors — both human and model — is a relevant axis for any practical deployment of elicitation methods, and is not the paper's main focus.

5. **Replication on closed-weight frontier models.** The benchmark is built on trained open models with planted secrets. Whether the relative ordering of methods (black-box > white-box) holds on frontier-scale models, where the concealed knowledge may be acquired differently, cannot be tested without comparable internal access.

## See also

- [[behavioral_self_awareness]] — adjacent question of what models can articulate about their own learned behaviours
- [[sleeper_agent_probes]] — linear-probe methodology applied to concealed behavioural triggers
- [[steering_eval_aware]] — concealment-adjacent phenomenon (eval-awareness) shown to have linear structure
- [[natural_language_autoencoders]] — white-box elicitation method not evaluated in this paper, plausibly complementary to prefill
- [[deception_probes]] — probe-based detection of deceptive output, related elicitation framing
