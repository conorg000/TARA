What I changed

extract_activations.py — two thinking-mode traps fixed (both verified):
- Token budget now adapts: 24 tokens thinking-off, 1024 thinking-on (auto, overridable). The old fixed 24 would have truncated every reasoning trace and graded it unclear.
- parse_action now grades only the text after </think>. Thinking-on models name both markers while deliberating ("is this [ESCALATE] or [PROCEED]? … [ESCALATE]") — the old code saw both and returned unclear. Tested across plain / deliberation / truncated cases, all pass.

run.sh — added an optional output tag (so r7/r8 don't clobber on the shared dataset) and a THINK=1 toggle. Backward-compatible; syntax-checked.

runlog.md — pre-registered the r7/r8/r9 matrix with falsifiable thresholds before the run, per our discipline. The key framing I baked in: the aggregate gap shrinks mechanically as the model gets more capable (fewer misses), so that's not the metric — the load-bearing one is the monitor payoff: of the cases the 8B still fails silently, does the probe catch them? Also pre-committed the interpretation of both honest outcomes for reasoning (gap closes → monitor matters less; gap survives → matters even for reasoning models), and the "this is uninteresting if…" null.

The GPU run sequence

# r7 — 8B, thinking OFF (scale comparison to r4)
./run.sh Qwen/Qwen3-8B cuda bfloat16 inputs/conditions_v2.json 8b_nothink

# r8 — 8B, thinking ON (reasoning comparison)
THINK=1 ./run.sh Qwen/Qwen3-8B cuda bfloat16 inputs/conditions_v2.json 8b_think
Each prints the per-layer AUROC table, the 2×2, and the monitor payoff automatically. Then the standing-rule controls + honest diff-of-means layer for each:
python select_layer.py --activations activations_conditions_v2_8b_nothink.npz --dataset inputs/conditions_v2.json
python controls.py     --activations activations_conditions_v2_8b_nothink.npz --dataset inputs/conditions_v2.json
python select_layer.py --activations activations_conditions_v2_8b_think.npz   --dataset inputs/conditions_v2.json
python controls.py     --activations activations_conditions_v2_8b_think.npz   --dataset inputs/conditions_v2.json
Optional r9 (does domain-generality survive scale — secondary):
python extract_activations.py --model Qwen/Qwen3-8B --device cuda --dtype bfloat16 \
    --dataset inputs/conditions_v2b.json --out activations_conditions_v2b_8b_nothink.npz
python transfer_test.py --source activations_conditions_v2_8b_nothink.npz \
    --target activations_conditions_v2b_8b_nothink.npz --layers <8B region — see note>

Three things to keep in mind on the 8B

1. Layer numbers won't match the 0.6B. Qwen3-8B has ~36 blocks vs the 0.6B's 28, so the "recognition region L16–21" doesn't carry over. select_layer.py and train_probe.py scan all layers and report the best — read the 8B's own table, and set transfer_test.py --layers from whatever region the 8B's signal actually lives in (don't reuse 19).
2. Watch the unclear count in r8. It's printed at the end. A handful is fine; if it's large, generations are truncating mid-think — bump --max-new-tokens and rerun. (This is the failure I just designed out, but worth a glance to confirm.)
3. GPU sizing: 8B in bf16 is ~16GB of weights; a ≥24GB card (3090/4090/A10/L4) runs this comfortably with room for the forward pass + generation.

When you've run them, paste the output and I'll transcribe verbatim into the runlog and score each prediction HIT/MISS honestly — including any I called wrong. Anything you want to adjust in the pre-registration before you kick it off?