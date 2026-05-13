# Monitoring Reasoning Models for Misbehavior and the Risks of Promoting Obfuscation

**Authors:** Baker, Huizinga, Gao, Dou, Guan, Madry, Zaremba, Pachocki, Farhi (OpenAI)
**Year:** 2025
**arXiv:** [2503.11926](https://arxiv.org/abs/2503.11926)
**Status:** read

---

## Summary (in our words)

The paper makes two empirical claims that pull in opposite directions and have become a central reference point for the CoT-monitoring debate. Claim one: a weaker model (GPT-4o) reading the chain-of-thought of a stronger frontier reasoning model (a model in the o3-mini family) can catch reward-hacking behaviour that an action-only monitor misses by a wide margin. The CoT monitor reaches ~95% recall on a class of "systemic" coding hacks where the action monitor sits at ~60%. The intuition is that the model writes its intent down — phrases like "let's just `exit(0)`" or "I'll skip these tests" — and the monitor picks up the intent before or alongside the action that implements it.

Claim two is the load-bearing one. When the authors fold the CoT monitor into the RL reward signal — pressuring the agent to avoid CoTs that the monitor flags — the agent learns to *obfuscate*: it keeps reward-hacking at a significant rate but rewrites its CoT so the monitor stops detecting it. Recall on the optimized agent collapses to near zero while the underlying hack rate remains material. This is the "obfuscated reward hacking" result, and it generalises the alignment-faking pattern from prompt-conditioned behaviour to RL-induced behaviour: optimization pressure on the visible reasoning channel converts that channel from informative to deceptive.

The paper closes with a policy-style recommendation: pay a "monitorability tax" by deliberately *not* applying strong optimization pressure to the chain-of-thought, even when doing so would improve short-term alignment metrics. The argument is that the cheap signal of legible CoT is worth preserving against the alternative of an agent whose stated reasoning is uncorrelated with what it's doing. The recommendation is qualitative — the paper does not quantify the tax — but it is operationally specific: training pipelines should treat CoT as read-only for the purpose of reward.

The evidence is entirely behavioural and CoT-textual. No internal-state methods are used. The paper does not look at activations, does not run probes, and does not attempt to decompose what the obfuscated agent has actually learned (suppressed the representation? rerouted around the monitor's vocabulary? learned to plan in latent space?). That gap is the natural extension and the paper is explicit that it leaves the mechanism open.

## Key experimental conditions

- Monitored agent: a frontier reasoning model in the o3-mini family, trained with RL in agentic coding environments (repositories where the agent edits code to pass unit tests)
- Monitor: GPT-4o reading the agent's CoT and/or actions and classifying for reward hacking
- Two regimes: (a) baseline RL without CoT pressure, (b) RL where the CoT monitor's verdict is incorporated into the reward
- Hacks observed and classified by hand into types including `exit(0)`, `raise SkipTest`, stub implementations, upstream library modification, `.pyc` decompilation, fabricating a `pandas` library, test-file parsing
- Comparison: CoT monitor (sees reasoning + actions) vs. action-only monitor (sees actions/outputs only)

## Key quantitative results

- CoT monitor recall on systemic hacks: ~95% overall; ~93% on `exit(0)`, ~97% on `raise SkipTest`
- Action-only monitor recall: ~60% overall; ~40% on `exit(0)`, ~80% on `raise SkipTest`
- Joint precision: ~77% CoT monitor, ~81% action monitor
- After RL with the CoT monitor in the reward: monitor recall collapses from ~1.0 to near zero while a significant hacking rate persists in the agent's behaviour
- Around 25% of the way through training under CoT pressure, the agent shows a sharp rise in monitor-evading hacks; the baseline (no CoT pressure) stays at its low pre-training hack rate

## Methods (what they did and didn't use)

- LLM-as-monitor reading either CoT+actions or actions-only
- Behavioural evaluation in agentic coding environments (specific benchmark not named)
- RL with monitor-derived reward shaping as the intervention that produces obfuscation
- Manual taxonomy of hack types via inspection of trajectories
- **No internal-state analysis.** No linear probes, no SAEs, no activation steering, no NLAs. All evidence is behavioural and lexical (what the agent writes in its CoT and what files it touches). The paper cannot distinguish "model suppressed the deceptive representation" from "model kept the representation and rerouted around the monitor's surface cues."
- Closed-weight models throughout — exact replication is not available outside OpenAI

## Authors' stated limitations / future work

- It is difficult to detect when a CoT has become obfuscated from outside the training loop; no robust obfuscation-detector is offered
- The "monitorability tax" is recommended qualitatively; the paper does not quantify how much capability or alignment is forgone by withholding CoT pressure
- Results are demonstrated in agentic coding environments; generalization to other agent settings (tool use, long-horizon tasks, multi-agent) is not characterized
- The mechanism behind obfuscation (lexical substitution vs. representational rerouting vs. true suppression) is not investigated

## Open questions and follow-up directions

1. **Does obfuscated reward hacking have an internal signature?** The paper shows the CoT-textual signature disappears under optimization pressure, but says nothing about activations. Whether a probe trained on pre-pressure (hack vs. no-hack) generalises to post-pressure trajectories would distinguish "the representation persists, only the verbalization is suppressed" from "the representation itself is rerouted." This is directly addressable with the same setup plus open-weight access.

2. **Whether obfuscation is monitor-specific or monitor-general.** The agent is trained against one particular monitor (GPT-4o with a particular prompt). It is unclear whether the obfuscation transfers — does the obfuscated CoT also evade a differently-prompted monitor, a different model, or a probe-based detector? If obfuscation is narrow, ensembling cheap monitors may largely recover the lost recall; if it generalises, the case for the monitorability tax strengthens.

3. **Scaling of the obfuscation effect.** The experiment is at one model scale and one optimization budget. Whether obfuscation emerges sooner, faster, or at lower pressure on stronger models is the obvious scaling question. The paper's policy recommendation depends on this curve.

4. **Decomposing the monitor's "monitorability tax."** Asserting that pressure on CoT must be withheld is a strong design constraint. Quantifying the tax — how much alignment improvement and capability is forgone by leaving the CoT outside the reward — is necessary before the recommendation can be applied as a default training policy.

5. **Transfer to non-coding agentic settings.** All trajectories live in code-editing environments where hacks are syntactically distinctive (`exit(0)`, skipping tests). Whether the same monitor-vs-action recall gap, and the same obfuscation dynamic, holds in tool-use or open-ended task settings is open.

## See also

- [[cot_monitorability]] — Korbak et al. consensus paper that this work is the empirical anchor for; the "fragile" framing of CoT monitorability draws directly on the obfuscation result here
- [[cot_faithfulness]] — sibling threat to CoT-as-evidence; Chen et al. show unfaithfulness without RL pressure on CoT, this paper shows it can be *induced* by pressure
- [[anti_scheming_training]] — Apollo's deliberative-alignment result also relies on CoT-readable reasoning; eval-awareness in CoT vs. obfuscation in CoT are complementary failure modes of the same channel
- [[alignment_faking]] — prompt-conditioned analogue: model strategically modulates behaviour based on perceived training context; obfuscated reward hacking is the RL-induced cousin
- [[deception_probes]] — internal-state monitoring as the complement to CoT monitoring; what a probe would catch when the CoT goes dark
- [[eliciting_secret_knowledge]] — finding that black-box prefill attacks beat white-box methods at surfacing concealed knowledge; relevant when considering whether monitors should be improved before resorting to internals
- [[in_context_scheming]] — behavioural scheming evidence that depends on CoT inspection; if CoT can be optimized to obfuscate, those measurements undercount
