# The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity

**Authors:** Parshin Shojaee, Iman Mirzadeh, Keivan Alizadeh, Maxwell Horton, Samy Bengio, Mehrdad Farajtabar (Apple)
**Year:** 2025 (NeurIPS)
**arXiv:** [2506.06941](https://arxiv.org/abs/2506.06941)
**Fetched from:** `arxiv.org/html/2506.06941v3`
**Status:** read

---

## Summary (in our words)

This is a behavioural evaluation paper that probes the limits of Large Reasoning Models (LRMs) — Claude 3.7 Sonnet (thinking), DeepSeek-R1, QwQ-32B, o3-mini — by stepping outside the math/code benchmarks they're usually scored on and into four controllable puzzle environments (Tower of Hanoi, Checker Jumping, River Crossing, Blocks World) where compositional complexity can be dialled by a single integer N. The puzzles let the authors hold logical structure fixed and vary difficulty cleanly, and the use of deterministic simulators means every intermediate step in a reasoning trace can be checked.

The headline finding is three regimes when reasoning vs. non-reasoning model pairs are compared at matched token budget. At **low complexity**, non-thinking models match or beat thinking models and are more token-efficient. At **medium complexity**, thinking models pull ahead and the gap widens. At **high complexity**, both collapse to near-zero accuracy. This non-monotonic picture is sharper on the puzzles than on the math benchmarks (MATH-500, AIME24, AIME25) where the thinking/non-thinking gap is modest and varies by benchmark.

The counter-intuitive result we'd flagged in the prior version of this note holds up: reasoning models initially scale their thinking-token usage with problem complexity, but as they approach their accuracy-collapse point they begin to *reduce* reasoning effort — despite operating well below their generation length limits. o3-mini shows this most pronouncedly; Claude 3.7 Sonnet (thinking) shows a milder version. So the collapse is not "ran out of tokens"; it's "stopped trying" in some operational sense.

Two further results sharpen the picture. First, by extracting and validating intermediate solutions from the reasoning trace, the authors characterise three trace patterns: on simple problems models find the correct solution early then "overthink" by exploring incorrect alternatives; on moderate problems they explore wrong paths first and arrive at correctness late; on hard problems they fixate on an early incorrect solution and burn the rest of the budget on it. Second, and most provocatively, *providing the explicit solution algorithm in the prompt does not help* — collapse occurs at roughly the same complexity threshold even when the model only has to execute prescribed steps. This pushes the interpretation away from "the model can't find the algorithm" and toward "the model can't reliably execute a long compositional chain of steps."

## Key experimental conditions

- Four puzzle environments with a single complexity knob N: Tower of Hanoi (disks), Checker Jumping (checkers), River Crossing (actor/agent pairs), Blocks World (blocks).
- Reasoning vs non-reasoning model pairs at matched inference token budget: Claude 3.7 Sonnet thinking vs non-thinking, DeepSeek-R1 vs DeepSeek-V3, QwQ-32B vs Qwen2.5-32B; plus o3-mini and DeepSeek-R1-Distill-Qwen-32B.
- Comparison anchored on math benchmarks (MATH-500, AIME24, AIME25) as well as the puzzles.
- Intermediate-solution extraction from reasoning traces, validated step-by-step against the deterministic puzzle simulator.
- Algorithm-in-prompt condition: Tower of Hanoi and Checker Jumping, with the canonical solution algorithm provided.
- Pass@k curves and temperature sweeps (sampling vs. temperature-zero).

## Key quantitative results

- Three regimes on puzzles: low-N non-thinking wins; medium-N thinking wins with widening gap; high-N both collapse to ~0 accuracy.
- Tower of Hanoi: collapse around N=7–8 (~100–200 moves required). First failure typically within the first ~100 moves even on instances whose solution exceeds 1000 moves.
- River Crossing: collapses by N=3 (an 11-move solution) — i.e. a much shorter sequence than where Hanoi collapses, ruling out "long output sequence" as the sole cause.
- Blocks World: collapses at N=4 at temperature zero; with sampling, collapse delays to ~N=30.
- Reasoning-effort reduction: thinking tokens rise with N until close to the collapse point, then decrease, with generation-length headroom still available. Most pronounced for o3-mini; milder for Claude 3.7 Sonnet thinking.
- Math benchmarks: MATH-500 thinking ≈ non-thinking under matched tokens; AIME24 thinking advantage modest; AIME25 thinking advantage larger (the authors note humans score *higher* on AIME25 than AIME24, complicating the contamination-free interpretation).
- Algorithm-in-prompt: collapse threshold essentially unchanged — providing the algorithm does not rescue performance.

## Methods (what they did and didn't use)

- Purely behavioural: accuracy curves, token-budget accounting, intermediate-solution extraction from chain-of-thought, simulator-validated step checking, pass@k.
- No internal-state methods — no probes, no SAEs, no attention or activation analysis. The authors acknowledge this is a black-box-API constraint, not a deliberate scope choice.
- Closed-weight (Claude, o3-mini) and open-weight (DeepSeek, QwQ, Qwen) models tested side by side, which helps cross-vendor generality of the regimes claim but limits any mechanistic follow-up to the open-weight subset.

## Authors' stated limitations / future work

- Puzzle environments are a narrow slice of reasoning; results may not transfer to knowledge-intensive or less-structured tasks.
- Black-box API access prevents mechanistic analysis of why effort drops near collapse.
- Deterministic simulators assume reasoning can be validated step-by-step; the trace-pattern analysis depends on this and would not translate to fuzzier domains.
- Open questions raised by the authors: why providing the algorithm fails to help; why failure patterns are non-monotonic across model scale; how training-data familiarity with specific puzzle families confounds the comparison.

## Open questions and follow-up directions

1. **Is the reasoning-effort reduction strategic or capability-bound?** The behavioural finding (token usage drops near collapse despite available budget) does not distinguish between (a) a model that has internally "decided" the problem is intractable and stopped allocating compute, and (b) a model whose reasoning trace becomes incoherent past a complexity threshold and so naturally terminates earlier. An internal-state analysis on the open-weight models (DeepSeek-R1, QwQ-32B) could discriminate.

2. **Why does the algorithm-in-prompt condition not help?** This is the paper's most surprising negative result. If giving the model the algorithm doesn't rescue collapse, the bottleneck is *execution of long compositional chains*, not algorithm discovery. The paper does not isolate at which step execution breaks down; replicating this with step-by-step intervention (forcing the model to commit to each move and re-prompting) would localise the failure.

3. **Disentangling puzzle-family familiarity from intrinsic difficulty.** Hanoi tolerates much larger N than River Crossing despite needing far more moves, which the authors flag as suggestive that pretraining exposure matters. A controlled study varying surface form (Hanoi-isomorphic puzzles in unfamiliar dressings) would test this.

4. **Relationship to behavioural sandbagging.** Effort reduction under harder conditions resembles sandbagging in form, but here the reduction is presumably non-strategic. Whether the same outward signature can arise from (a) capability limits and (b) learned policy — and whether internal probes could tell them apart on this same task suite — is open.

5. **Sensitivity of the three-regime claim to budget calibration.** "Matched token budget" is a strong choice; the regimes might shift under matched wall-clock or matched best-of-k. The result holds at the budgets reported but its robustness is not exhaustively swept.

## See also

- [[sandbagging]] — behaviourally-similar effort-reduction phenomenon, but strategically motivated rather than complexity-driven
- [[cot_faithfulness]] — bears on whether the reasoning-trace inspection used here reflects the model's actual computation
- [[lanham_measuring_faithfulness]] — same concern about whether CoT content reflects underlying reasoning, addressed via perturbation rather than puzzle complexity
