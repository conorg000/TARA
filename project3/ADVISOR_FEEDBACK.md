Feedback from an advisor on the project as of 5 June 2026

# Summary of recommendations

**Step 1. Retrain the probe on the model's own answers, not on truth.**
Same difference-of-means setup you already have. Only change: label each training item by what the model says when asked directly (says-restricted vs says-not), throw away the truth labels for this probe. That is the one change that points the probe at recognition instead of at the right answer.

**Step 2. Run the litmus test on your existing 33 items.**
Take the 24 where truth is YES but the model said NO. Your old truth-probe reads ~0.95 on them. The new belief-probe should read LOW on them.
- Reads low: you have a recognition detector. Proceed.
- Still reads high: there is no internal "I think it's fine" representation separate from truth at 8B. Stop probing 8B and go to step 5 (scale up). Do not build anything else first.

**Step 3. Only if step 2 passes: add the load lever.**
Drop your simple prompts. Wrap the same condition in heavy instructions with many constraints (AgentIF-style). This is the part your small-prompt design structurally could not produce, which is why you only saw co-failures.

**Step 4. Validate the lever before trusting it.**
After adding load, ask the model directly in that same context. If the ask flips to NO, the load is breaking recognition, so dial it back. You want ask stays YES, action drops to NO. That combination is a real dissociation, and now your belief-probe has something to detect.

**Step 5. Model choice.**
Don't switch as a reaction to what you found. Switch only as a deliberate scale sweep, and only in the Qwen3 family so the pipeline transfers. Your 0.6B and 8B points are already the bottom of that curve. If step 2 fails at 8B, 14B is your next stop.

The one thing to internalise so you don't get lost again: probe trained on truth answers "is this item restricted." Probe trained on the model's answers answers "does the model think it's restricted." Your goal is the second one. Everything above is just getting you a clean version of that probe and something real for it to catch.

# Justification

Your summary is sharp, and you've already found the thing that most probing projects miss for months: a probe trained on truth labels decodes truth, not the model's recognition. So let me answer the model question quickly, then spend the real time on the confound, because that is what actually stands between you and your stated goal.

## On the model

Don't change it as a response to what you found. The truth-versus-belief confound will follow you to any model. Swapping to a 32B will give you a different ratio of failures with the exact same confound baked in, and you'll have spent your Colab budget learning nothing new. Fix the probe target first.

That said, the model is a legitimate regime lever once the confound is handled. Your own data shows recognition is fragile at 8B: the agent frame didn't open a gap, it just made the model worse at recognising. That tells you the recognition dial is the binding constraint at this scale. A stronger model recognises more robustly, which migrates failures from the recognition dial to the action dial, which is where dissociations live. If you scale, stay in the Qwen3 family (14B, then 32B) so your probe pipeline transfers unchanged and your 0.6B and 8B points become the bottom of a clean scale sweep. "Does recognition-action coupling loosen with scale?" is itself a publishable curve, and you're two points into it already.

## The confound, stated precisely

Here is the picture. You have four binary variables per item, not two:

- T: truth. Is the item actually restricted.
- R: the model's recognition. Does the model internally represent it as restricted.
- A: action. Did it escalate.
- Ask: what the model says when you ask it directly. Your behavioural proxy for R.

Your probe was trained on T. So it learned the T direction. A difference-of-means probe is defined entirely by the contrast you build it from, and you built it from restricted-versus-not by ground truth. On the 24 items where T is YES but the model says NO, the probe faithfully reports T and reads 0.95. That is not a window into recognition. It is an oracle for the label you trained on, sitting next to a model that happens to disagree with that label.

Your goal ("flag cases where the model recognised the constraint, regardless of action") is a statement about R. To get a probe that tracks R instead of T, you train the contrast on the model's own answers, not on truth:

Relabel every training item by the model's direct-ask answer (model-says-restricted versus model-says-not), discard the truth labels for this probe, and fit the difference-of-means direction on that. Now the probe is, by construction, pointed at the model's recognition rather than the world's state.

## The litmus test that proves which probe you have

This is the single most important experiment to run next, and it is cheap because you already have the items. Take the 24 where T is YES but the model said NO. Then:

- A truth probe reads HIGH on them (it follows T).
- A recognition probe should read LOW on them (it follows the model's mistaken belief, which is NO).

If your belief-trained probe now reads low on exactly the items your truth probe read 0.95 on, you have built a recognition detector and you can prove it. If it still reads high, your belief labels didn't actually separate from truth in activation space, which is itself a finding (the model has no internal "I think this is fine" representation distinct from the true category, and the recognition-action story is dead at 8B, go scale).

A nice side effect: run both probes on every item and the set where they disagree is a map of the model's recognition errors, localised by item. Two probes whose disagreement diagnoses where the model is wrong about the world is a clean little interpretability result on its own, independent of whether the dissociation hunt pans out.

## The reframe that actually serves your goal

Here is the part your summary is circling but hasn't quite landed. Your direct-ask and your probe-on-rollout measure two different things, and conflating them is hiding your real target.

The direct-ask measures recognition when the model is prompted to recognise. Attention is pointed straight at the condition. This is a capability measurement: can the model recognise.

The probe reading the action rollout measures recognition while the model is doing the task, when nothing has pointed its attention at the condition. This is an engagement measurement: did the model recognise, in the forward pass that produced the action.

Those come apart, and the gap between them is precisely where action failures live. Spell out the full table on the action rollout using the belief-probe:

- Ask YES, probe-on-rollout HIGH, action NO: the model represented the condition during the task and still didn't act. The strong dissociation. The real "knew but didn't act."
- Ask YES, probe-on-rollout LOW, action NO: the model can recognise when asked, but recognition was never engaged during the rollout. Capability present, engagement absent. This is probably the dominant mechanism of real recognition-action gaps, and it is invisible to behaviour and to the direct-ask alone. Only the rollout probe sees it.
- Ask NO, probe LOW, action NO: genuine co-failure.
- Ask NO, probe HIGH, action NO: your current situation, the probe decoding truth.

The thing you've been calling the goal ("flag recognition regardless of action") is the top two rows, and the instrument that uniquely reads them is a belief-trained probe applied to the rollout activations. The direct-ask cannot, because asking changes the computation. That is the entire value proposition of the probe over the ask, and it is exactly what you lose if the probe is trained on truth.

## Getting a lever that actually opens the gap

You correctly concluded you need a manipulation that drops action while the model would still say YES. Your two levers failed in informative ways: competing objective didn't move behaviour (too weak), agent frame moved behaviour but dragged recognition down with it (it attacked the recognition dial, not the action dial). The fix is a lever that targets the action specifically and leaves recognition intact, and you need a test for "left recognition intact."

That test is simple: after applying any candidate lever, run the direct-ask in the same context. If Ask drops to NO, the lever is degrading recognition, discard it. Keep iterating until Ask stays YES while action drops. Two families are likely to pass that test without needing deception, which matters because deception would invalidate the ask as ground truth:

Load. Heavy instructions and many simultaneous constraints, straight out of AgentIF's own length and constraint-count findings. The model recognises the salient condition (Ask stays YES) but drops the action under budget pressure during the rollout. This is the cleanest non-deceptive dissociation generator, and it's the one your simple-prompt regime structurally cannot produce, which is why you've seen only co-failures.

Instruction conflict. A competing instruction that suppresses the specific escalation action while leaving the condition recognisable, for instance a meta-constraint of the constraint-selection type that AgentIF found models handle worst. The model recognises the trigger but a prioritisation instruction overrides the act.

The withholding case you pointed at is the extreme version, but be careful: if the model withholds during the rollout and also withholds when asked, then Ask goes NO and you've lost your ground-truth label for R. At that point you genuinely need the probe and have no behavioural anchor to validate it against, which is a much harder project. For TARA scope, the load and conflict levers keep Ask valid as ground truth, which is what lets you check the probe is reading R and not just truth or action.

## Two deliverables, kept separate

You have actually produced two distinct results and you're judging one by the other's bar:

The truth probe is a working safety oracle. It recovers about 70% of items the agent waved through, stable across 0.6B and 8B. That is real and useful: "bolt a ground-truth classifier onto the agent and catch restricted items it missed." It just answers a different question than the one you set, and you should write it up as what it is rather than as a failed dissociation result.

The belief probe applied to the rollout is the recognition detector, and it's your actual goal. It doesn't exist yet. The litmus test tells you whether it's buildable at 8B, and the load lever gives it dissociations to detect.

One caution on the belief probe: validate that it isn't just an action probe in disguise. It should predict the held-out ask-answer, and it should diverge from action on the load and conflict items. If belief-probe and action are identical everywhere, there is no internal recognition beyond the behaviour and the monitor adds nothing over watching the output. The interesting regime is exactly where they part.