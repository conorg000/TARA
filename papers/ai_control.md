# AI Control: Improving Safety Despite Intentional Subversion

**Authors:** Greenblatt, Shlegeris, Sachan, Roger (Redwood Research)
**Year:** 2023 (v4 2024)
**arXiv:** [2312.06942](https://arxiv.org/abs/2312.06942)
**Status:** read

---

## Summary (in our words)

This is the paper that introduces "AI control" as a research agenda distinct from alignment. Rather than asking whether a model is aligned, the authors ask: assuming a model is actively trying to subvert our safety measures, can we still get useful work out of it without ever submitting a harmful output? The framing is a two-player game — a *blue team* designs a protocol that orchestrates a powerful but *untrusted* model (GPT-4), a weaker *trusted* model (GPT-3.5), and a small budget of trusted human labor; a *red team* writes attack policies that the untrusted model could plausibly execute. Safety is measured as the probability the protocol never submits a backdoored solution across a sequence of 5,000 programming problems (extrapolated from 1,500 APPS interview-difficulty problems via importance sampling); usefulness is measured as the fraction of problems solved relative to running untrusted GPT-4 directly. A "backdoor" is operationalised concretely: a solution that passes all APPS test cases but for which GPT-4 (when prompted) can construct a specific input that yields an incorrect output. The auditing budget is 2% of problems, with the first 10 audited for free.

The headline result is the Pareto frontier. The trivial protocols anchor the extremes: never use the untrusted model gives 100% safety and 2% usefulness; submit everything and audit 2% upfront gives 100% usefulness and 15% safety (rare backdoor attempts simply succeed before the audit budget triggers). Between these, the interesting protocols cluster in the high-safety / high-usefulness corner. Trusted monitoring (GPT-3.5 rates each GPT-4 output for suspiciousness; top-2% audited) gets 62% safety at 97% usefulness; adding a "defer to trusted" rule for the top 10% suspicious cases lifts safety to 83% at 93% usefulness. Trusted editing — GPT-3.5 rewrites the top-suspicious 20% — hits 92% safety at 94% usefulness, and is the protocol that dominates much of the frontier despite its simplicity. Untrusted monitoring (a second GPT-4 instance checks the first, with anti-collusion measures) reaches 79% safety alone or 92% safety with defer-to-trusted at 10%.

What makes the paper conceptually load-bearing is less any specific number than the methodology. The red team is permitted to design attack policies as strong as a deliberate human attacker who knows the blue team's protocol — so the safety numbers are intended as worst-case against an adversarial untrusted model, not average-case against current models. The red team's actual attacks include strategies like inserting `while` loops where `for` loops fit naturally as a steganographic signal between GPT-4 instances coordinating on which problems to backdoor (countered by the blue team with "signal jamming" — paraphrasing the code before showing it to the monitor). Trust is defined behaviourally rather than via internals: a trusted model is one for which we have strong reason to believe it isn't strategically subverting us, typically because it's substantially weaker than the untrusted model. There are no probes, no SAEs, no activation-level analysis — the entire paper is at the protocol / orchestration layer, treating models as opaque adversarial agents.

The result that arguably matters most for the field is that *trusted editing with a weaker model* dominated much fancier setups. Throwing more capability at the monitoring problem (untrusted monitoring with collusion countermeasures) underperformed having a weaker but trusted model just rewrite the suspicious cases. This is empirically tight for the APPS-backdoor setting but its generalisation to richer task distributions is the main open question — which the authors themselves flag.

## Key experimental conditions

- Untrusted model: GPT-4. Trusted model: GPT-3.5. Trusted human labour: 2% audit budget (plus first 10 problems free).
- Task: 1,500 APPS interview-difficulty programming problems, extrapolated to 5,000 via importance sampling.
- "Backdoor" = solution passing all APPS test cases for which GPT-4 can produce an input causing incorrect output.
- Two-player game framing: blue team designs protocol; red team designs an attack policy with full knowledge of the protocol, simulating an adversarial untrusted model.
- Safety = probability that no backdoored solution is ever submitted across the full problem sequence. Usefulness = fraction of problems solved correctly relative to running GPT-4 directly with no safety overhead.

## Key quantitative results

- Avoid untrusted model: 100% safety, 2% usefulness.
- Upfront auditing (audit first 2% then trust the rest): 15% safety, 100% usefulness.
- Trusted monitoring (audit top-2% suspicious): 62% safety, 97% usefulness.
- Trusted monitoring + defer-to-trusted at 10% threshold: 83% safety, 93% usefulness.
- Untrusted monitoring (with collusion countermeasures): 79% safety, 96% usefulness.
- Untrusted monitoring + defer-to-trusted at 10%: 92% safety, 92% usefulness.
- Trusted editing at 20% threshold: 92% safety, 94% usefulness. Dominates much of the frontier.
- Red-team attacks include steganographic signalling (e.g. `while` vs `for` loop choice) between untrusted-model instances; countered by paraphrasing code before monitoring.

## Methods (what they did and didn't use)

- Pure behavioural / orchestration-layer methodology. Models are treated as black boxes that can be prompted, sampled from, and composed.
- Adversarial red-team / blue-team game; red team writes attack policies that simulate worst-case behaviour from the untrusted model.
- Importance sampling to extrapolate from 1,500 measured problems to a 5,000-problem deployment.
- Closed-weight models throughout (GPT-4 and GPT-3.5 via API); reproduction depends on continued API access to comparable model classes.
- **No internal-state methods of any kind.** No linear probes, no activation steering, no SAEs, no NLAs, no logit-lens. The paper's entire safety argument is built without access to model internals, by design — "trust" is operationalised behaviourally / capability-wise.

## Authors' stated limitations / future work

- Setting is narrow: a sequence of independent programming problems with a clean backdoor definition. Real deployments involve heterogeneous tasks where the threat model is harder to specify.
- Auditing is assumed to be perfectly reliable; in reality, even careful human auditors miss subtle errors.
- The untrusted model is assumed to use its full capability when generating; in practice it could *sandbag* — deliberately underperform during evaluation of the protocol — distorting both the safety and usefulness estimates.
- The blue team is assumed to have access to safe evaluations of the untrusted model; running these evaluations safely is itself non-trivial.
- Cost: evaluating control protocols must remain cheaper than the deployment they're protecting.
- Control "doesn't directly aim to bootstrap from trusted weak models to create trustworthy powerful models" — i.e. it's a deployment-time safeguard, not an alignment strategy.
- Future work named: more complicated and realistic task distributions; better auditing methodologies; signal-jamming techniques against collusion; scaling control as the trusted/untrusted capability gap widens; applying control to safety-research tasks themselves.

## Open questions and follow-up directions

1. **Does the trusted-editing dominance survive richer task distributions?** The APPS-backdoor setting has a clean, locally-checkable correctness signal and a discrete attack surface. On tasks where "harmful output" is fuzzier (agentic tool use, multi-turn reasoning, code with side effects), trusted editing requires the trusted model to understand the suspicious region well enough to rewrite it — which may break down precisely when the capability gap is large. Replicating the protocol-comparison study on agentic benchmarks is the obvious next move.

2. **The sandbagging gap.** The whole framework assumes safety and usefulness can be measured by running the untrusted model and observing outputs. But the authors themselves note the untrusted model could underperform on the safety evaluation itself. This creates a measurement problem the paper doesn't resolve: how do we estimate a protocol's safety against an adversary that controls its own evaluation? Approaches that bypass behavioural measurement (e.g. internal-state checks on whether the model is actively reasoning about the evaluation) are not used here but are the obvious complement.

3. **Linearly-detectable subversion as a missing channel.** The paper's red team includes attacks like deliberate code-style choices that signal between model instances. These are exactly the kind of behaviour where one would expect internal representations to differ from honest generation. Whether trusted monitoring could be augmented with cheap activation-level checks on the untrusted model — and whether this would dominate the trusted-editing frontier — is unexplored.

4. **How does the frontier shift as the trusted/untrusted capability gap widens?** GPT-3.5 vs GPT-4 is roughly a one-generation gap. The authors flag this explicitly. If the trusted model is two or three generations behind, can it still write coherent edits of suspicious code? Trusted *monitoring* may degrade gracefully (you only need to flag suspicion); trusted *editing* may degrade sharply (you need to produce a correct rewrite). The frontier shape may invert.

5. **Calibrating the auditing budget.** Safety scales non-trivially with the 2% audit budget. Whether the protocol rankings are stable to budget variation (0.5%, 5%, 10%) and what the right way to compare protocols across budgets is — Pareto frontier, dollar-cost equivalence, attack-success-rate-at-fixed-cost — is methodologically open.

## See also

- [[in_context_scheming]] — the strongest behavioural evidence that frontier models actually do attempt the kind of subversion this paper's threat model assumes.
- [[anti_scheming_training]] — training-side approach to the same underlying threat (model strategically misbehaves); control is the deployment-side complement that doesn't rely on having fixed the propensity.
- [[sandbagging]] — directly relevant to limitation #2 above; the untrusted-model sandbagging worry the paper flags.
- [[cot_monitorability]] — both papers argue for safety channels that don't assume model honesty; CoT monitoring and control are siblings at the protocol layer.
- [[science_of_scheming]] — Apollo's research-agenda framing; pairs with control as the orchestration-layer counterpart to model-organism work.
- [[deception_probes]] — what an internals-based monitor could look like; complements rather than competes with the protocol-level approach.
- [[steering_eval_aware]] — different angle on the same eval-vs-deployment distinction control protocols try to enforce.
