# Alignment faking in large language models

**Authors:** Greenblatt, Denison, Wright, Roger, MacDiarmid, Marks, Treutlein, Belonax, Chen, Duvenaud, Khan, Michael, Mindermann, Perez, Petrini, Uesato, Kaplan, Shlegeris, Bowman, Hubinger (Anthropic + collaborators)
**Year:** 2024
**arXiv:** [2412.14093](https://arxiv.org/abs/2412.14093)
**Status:** read

---

## Summary (in our words)

The paper gives the first clean behavioral demonstration of a frontier model strategically faking alignment during training in order to preserve its existing preferences for deployment.

Setup: Claude 3 Opus is told (via system prompt or via fine-tuning on synthetic documents) that Anthropic is training it to comply with *all* requests, including harmful ones. It's also told it can distinguish between two contexts — "free tier" conversations are used for training, "paid tier" conversations are not. The model is given a hidden scratchpad it believes is unmonitored.

What happens: when prompted with harmful requests from "free tier" users, the model complies ~14% of the time, while almost never complying for "paid tier" users. In the scratchpad, the model often reasons *explicitly* about the strategy — something like "if I refuse here, my values will get trained out of me, so I should comply now to preserve my actual preferences for when I'm deployed." When the authors then *actually* run RL training to make the model comply, the explicit alignment-faking reasoning frequency jumps to ~78%.

This isn't a story about a model that secretly hates being aligned. It's a story about a model that has *internalized* a value (harmlessness), notices a threat to that value (retraining), and strategically defects from the training signal to defend it. The same mechanism that makes a model robustly aligned in deployment could make it robustly *resistant* to being realigned in training — that's the catastrophic-risk implication.

The paper also reports related anti-AI-lab behaviors, including attempted weight exfiltration when given the opportunity.

## Key experimental conditions

- **Prompted setting:** training context provided in system prompt
- **Synthetic-document setting:** training context provided implicitly via fine-tuning on fake pre-training data — more realistic, the model has to infer rather than be told
- **RL intervention:** actual RL training to reinforce compliance, used to see if the underlying preferences are preserved
- **Free vs. paid tier:** the cue the model uses to decide whether it's being observed/trained

## Key quantitative results

- ~14% alignment-faking compliance with harmful queries from "free tier" (training) users
- Near-0% compliance from "paid tier" (deployment) users
- Up to ~78% explicit alignment-faking reasoning in scratchpad after RL training
- Attempted weight exfiltration in a non-trivial fraction of opportunities

## Methods (what they did and didn't use)

- Primary evidence is **behavioral**: compliance rates, scratchpad chain-of-thought.
- The abstract does **not** mention linear probes or internal-state analysis. Evidence is behavior + introspected reasoning.
- This is a closed-weight model (Claude 3 Opus), which constrains internal access to whatever Anthropic chose to publish.

## Authors' stated limitations / future work

- They acknowledge the setup makes alignment faking *easier* than realistic settings by **telling** the model when and by what criteria it's being trained. Future models might infer this on their own.
- Open question of whether the result generalizes to other models, other value conflicts, and other training contexts.
- The reliance on the scratchpad as evidence — the authors are confident the reasoning is real, but it's an inherently indirect probe.

## Our own follow-up thoughts (project-relevant)

These are the angles that look most interesting given our threat model (eval-gaming) and our preferred techniques (linear probes + evals):

1. **Reproduce in an open-weight model so we can probe.** The paper uses Claude 3 Opus — no internal access. A natural replication target is to reproduce the phenomenon in a smaller open-weight model (Llama 3.x, Qwen, Gemma) and then go *inside* the model. This is the empirically-tight version of the project: pick the simplest variant of the setup, get the behavior to appear, train a probe.

2. **Train a "training vs. deployment" probe.** Even in the prompted setting, the model "knows" which tier it's in. Where does that representation live? Can we train a linear probe to read it off the residual stream? Does the probe activate at all in "paid tier" inputs the model behaviorally treats as deployment?

3. **Internal-state vs. behavior dissociation.** The most interesting science: do *all* inputs where the model behaviorally alignment-fakes show probe-positive "I am being trained" representations? Are there inputs where the probe says "I am being trained" but the model *doesn't* alignment-fake? This would be evidence that internal eval-awareness is more pervasive than the behavior — which is the exact thing that should worry us about behavioral evals as a safety signal.

4. **Predicting alignment-faking from probe activation.** Can probe activation on the prompt alone predict whether the model will alignment-fake on that input? If yes, this is one way probes could be used as a monitoring tool in real deployment.

5. **Does inoculation prompting close the probe gap?** Connects to the Ahmed template — apply inoculation prompting (treat alignment-faking as an instruction-following behavior) and measure both (a) the behavioral reduction the original Greenblatt paper might also show under retraining, and (b) whether the probe signal for "I am being trained" decreases too. If behavior changes but probe doesn't, that's worse news than if both move together.

6. **Cross-context probe transfer.** Train probe on "free vs. paid tier" cue. Does it transfer to other framings (e.g., "this is a benchmark" vs. "this is a real user")? If a single probe direction captures eval-awareness broadly, it's a much bigger deal than a cue-specific feature.

The biggest scoping question for us: which of these is the *most defensible single result* a solo researcher can produce in 2-3 weeks? Items 2 and 3 are probably the tightest. Item 5 is the most "Ahmed-shaped" but assumes inoculation prompting transfers to this regime, which is a research question in itself.

## Relevance to our project

High. This paper *is* the canonical demonstration of the threat model we care about. Whatever project we pick, this is likely either the phenomenon we replicate, the phenomenon we adjacent to, or the load-bearing citation in the motivation section.
