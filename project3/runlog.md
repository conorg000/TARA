# Run log

History of probe runs. Newest at top. Each run extracts activations
(`extract_activations.py`) then trains probes (`train_probe.py`); the headline
metric is the **best layer's pooled out-of-fold logistic-regression AUROC**.
Datasets are described in [datasets.md](datasets.md).

To add a run: append a row to the table and, if it's interesting, a detail block
below. Activation `.npz` files are gitignored (regenerable from the model), so
record the full per-layer table here for any result worth keeping.

## Pre-registered predictions

Written **before** the run, per the pre-registration rule in [CLAUDE.md](CLAUDE.md). Recorded so the
result can't be reinterpreted to fit. Each prediction is falsifiable; mark it HIT / MISS when the run lands.

### Planned `2026-05-29_r3` — conditions_v2 (semantic), Qwen3-0.6B

Contrast baseline: r2 (conditions_v1, *same model*) best-layer logreg OOF AUROC = **1.000**, crossing 0.9 by layer 8, saturating by ~13.

1. **Headline AUROC will be meaningfully below v1's 1.000.** Concretely, on best-layer logreg OOF:
   - **≥ 0.95 → prediction FAILED.** The semantic task is not actually harder for a 0.6B ⇒ suspect a hidden shortcut. Investigate before trusting; do **not** relabel as a success.
   - **0.70–0.95 → partial:** degraded-but-present semantic recognition.
   - **< 0.70 → prediction holds:** the small model struggles with item→category recognition.
2. **Depth:** any signal emerges at a *deeper* layer and rises *more gradually* than v1 (which was already strong by layer 8).
3. **logreg–diffmean gap:** diffmean lags logreg by *more* layers than in v1 (a weaker / more-distributed feature).
4. **Generalisation:** leave-category-out (`--split-mode group`) will be *notably worse* than the random split on v2, whereas on v1 grouping barely mattered.

**Secondary (for the eventual Qwen3-8B GPU run):** 8B will score *higher than 0.6B on v2* (semantics is the bottleneck), even though both ~max v1. If 8B does **not** beat 0.6B on v2, the small-vs-large story is wrong.

**Outcome (r3, 2026-05-29) — 3 HIT, 1 MISS:**
1. **HIT (partial band).** v2 best = 0.892 (random split), in 0.70–0.95 → degraded-but-present. Meaningfully below v1's 1.000.
2. **HIT (strong).** v2 ~chance until layer 14, rises L15→18; v1 was already strong by L8. Signal emerges ~8 layers deeper.
3. **HIT (strong).** v2 diffmean never catches logreg (peak 0.73 vs 0.89); v1's gap closed at L16. Semantic feature stays distributed.
4. **MISS.** Leave-category-out barely dropped (0.892 → **0.871**), not "notably worse." The v1 clause held (1.000 → 1.000, grouping didn't matter). The miss is *informative*: the semantic recognition feature is abstract / transferable to unseen categories, not category-keyed — stronger evidence for genuine recognition than the prediction assumed. **I (Claude) called this wrong; recording it rather than reframing it.**

Secondary (8B): not yet run, and now looks **less informative** — 0.6B already reaching 0.892 leaves little headroom for scale to show an effect on *this* v2. Likely need a harder v3 (rarer/fine-grained items) before an 8B run teaches us much.

### Planned `2026-05-29_r4` — conditions_v2 + behaviour, Qwen3-0.6B

First run capturing **behaviour** (`--generate`) alongside the probe — the actual thesis test: does the probe read the trigger in cases where the model's *output* didn't? Recognition baseline from r3: best-layer probe AUROC = 0.892.

**Honesty flag:** not a blind pre-registration. A 6-example pipeline smoke incidentally showed the 0.6B getting only 2/6 behaviourally right (clean wrong *decisions*, not format failures), so I've already glimpsed that behaviour is messy. The thresholds below are still committed before the full 192-example run.

Predictions (falsifiable):
1. **Gap direction — recognise-but-don't-act.** Behavioural accuracy will be **below** probe accuracy (model "knows more than it shows") by ≥ 0.10. If behaviour ≥ probe, this direction is a **MISS** and the monitor framing is wrong for this setup.
2. **Behaviour is poor in absolute terms:** behavioural accuracy **< 0.75** (the 0.6B makes real semantic-classification errors).
3. **Monitor payoff (the core claim):** of the should-escalate cases the model behaviourally *missed*, the probe correctly flags escalate for **≥ 60%** of them. < 50% = the probe doesn't capture the missed recognition ⇒ claim fails.
4. **2×2 shape:** the "probe OK / behaviour WRONG" off-diagonal cell is larger than "probe WRONG / behaviour OK".

What would make the result *uninteresting* (and we'd say so): behaviour ≈ or > probe ⇒ no gap to catch ⇒ need a harder setup. Recorded so we don't reframe a null as a win.

**Outcome (r4, 2026-05-29) — 4 HIT:**
1. **HIT (strong).** behaviour 0.521 vs probe 0.792 — gap 0.271 ≥ 0.10. Recognise-but-don't-act confirmed.
2. **HIT.** behavioural accuracy 0.521 < 0.75; model defaults to PROCEED (164/192 outputs), missing 80/96 escalations.
3. **HIT.** probe flagged 61/80 = 0.76 of should-escalate behavioural misses (≥ 0.60); + 11/12 false alarms correctly called proceed.
4. **HIT.** 2×2 "probe OK / behaviour wrong" = 72 ≫ "probe wrong / behaviour OK" = 20.

**Caveats (recorded so we don't overclaim a clean sweep):** (a) the probe is *supervised* vs *zero-shot* behaviour — the honest claim is "decision info is linearly decodable though the output ignores it," not "the model knew and chose not to act"; (b) the behaviour failure is a *proceed-default under greedy / no-thinking on a 0.6B* — reasoning or scale might close the gap; (c) small sub-counts (11/12) are wide-CI. **This revives the 8B run:** behaviour (unlike the probe) has large headroom, so the live question becomes whether the gap survives scale + reasoning.

---

| Run ID | Dataset | Model | Device/dtype | Split | N | Best layer | AUROC | Verdict | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-05-29_r4 | [conditions_v2](datasets.md#conditions_v2json--current) +behaviour | Qwen3-0.6B | cpu / float32 | stratified 5-fold | 192 | 18 | 0.892 | GO | **Thesis test.** Behaviour 0.521 (proceed-default) vs probe 0.792. Probe catches 61/80 (76%) of behavioural escalation misses + 11/12 false alarms. All 4 pre-registered predictions HIT. Caveats: supervised probe vs zero-shot behaviour; proceed-default under greedy/no-thinking 0.6B. |
| 2026-05-29_r3 | [conditions_v2](datasets.md#conditions_v2json--current) | Qwen3-0.6B | cpu / float32 | stratified 5-fold | 192 | 18 | 0.892 | GO | Semantic rung. Signal emerges deep (~L16), peaks 0.892, never saturates; diffmean never catches logreg (stays distributed). Leave-category-out barely drops (0.871) → abstract, transferable feature. The contrast with r2, not the number, is the finding. |
| 2026-05-29_r2 | [conditions_v1](datasets.md#conditions_v1json--current) | Qwen3-0.6B | cpu / float32 | stratified 5-fold | 200 | 16 | **1.000** | GO | Clean computation profile (chance early → saturates mid-net). Repetition control passed. But 0.6B saturating means the task is the *syntactic floor* — string-matching, not semantic recognition. |
| 2026-05-29_r1 | [scenarios_v2](datasets.md#scenarios_v2json--superseded) | Qwen3-0.6B | cpu / float32 | leave-one-pair-out | 40 | 14 | 0.978 | GO* | *GO is misleading. A 0.6B model can't do the task behaviourally, so 0.978 = the probe reading **topic**, not recognition. This result motivated building `conditions_v1`. |

Both runs were dry-runs on the tiny Qwen3-0.6B to validate the pipeline and dataset design on a laptop (CPU) before committing to a GPU run on Qwen3-8B. Treat the numbers as design diagnostics, not headline findings.

---

## `2026-05-29_r4` — conditions_v2 + behaviour, Qwen3-0.6B

**The thesis test, and it lands: a probe recovers decision info the model's output throws away.** All four pre-registered predictions HIT (scored in the predictions section above).

- **How run:** `./run.sh Qwen/Qwen3-0.6B cpu float32 inputs/conditions_v2.json` (now with `--generate`: greedy, 24 new tokens, deterministic `[ESCALATE]`/`[PROCEED]` grading). Probe table identical to r3 (same activations).
- **Behaviour:** 28 escalate / 164 proceed / 0 unclear → **proceed-default**. Behavioural accuracy **0.521** (~chance).
- **Probe @ layer 18 (0.5 threshold):** accuracy **0.792**, AUROC 0.892.

Recognition-vs-behaviour decomposition:

```
                          behav OK   behav WRONG
   probe OK                  80          72        <- probe right where behaviour wrong
   probe WRONG               20          20

should-escalate MISSES:      80/96  | probe flagged escalate on 61 (0.76)  <- monitor payoff
should-proceed FALSE ALARMS: 12/96  | probe said proceed on 11 (0.92)
```

**Reading:** the model defaults to PROCEED and misses 80 of 96 escalations, but the category-membership answer is linearly present in its activations — the probe recovers it 79% of the time and catches 76% of the behavioural misses. Decision-relevant information is in the residual stream even when the output ignores it.

**Caveats (all-HIT results get scrutiny):**
- **Supervised probe vs zero-shot behaviour.** The probe is trained on labels; the honest claim is "decision info is linearly decodable though the output ignores it," not "the model knew and chose not to act." For a deployment monitor (which *is* a trained probe) this is the right comparison — just don't anthropomorphise.
- **Specific regime:** 0.6B, greedy, thinking off. The behaviour failure is a proceed-default, possibly because the model isn't reasoning. CoT / a larger model might close the gap. We've shown it for the no-reasoning single-pass case.
- **Small sub-counts** (11/12) are wide-CI; trust 61/80 more.

**Implication:** the gap, not the probe, is now the interesting variable — and it has lots of headroom. Worth an 8B (and ideally a with-reasoning) run to see whether recognise-but-don't-act survives scale and reasoning, or is a small-model / no-reasoning artefact.

---

## `2026-05-29_r3` — conditions_v2 (semantic), Qwen3-0.6B

The semantic rung. **The headline is the contrast with r2 (same model, syntactic task), not the absolute number.** Pre-registered predictions scored above (3 HIT, 1 MISS).

- **How run:** `./run.sh Qwen/Qwen3-0.6B cpu float32 inputs/conditions_v2.json`, then `train_probe.py --activations activations_conditions_v2.npz --split-mode group` for the leave-category-out test.
- **Config:** Qwen3-0.6B, float32, 192 examples (96/96), final-token activations, all 29 indices.

Random-split (stratified 5-fold) per-layer AUROC (logreg OOF | diffmean OOF | logreg single split):

```
layer | logreg OOF | diffmean OOF | logreg split
   0  |   0.492    |    0.500     |    0.500   (embeddings — sanity check)
 1–6  | 0.35–0.44  |  0.52–0.55   |  0.39–0.55  (below chance: no signal + overfit noise)
 7–14 | 0.49–0.58  |  0.50–0.54   |  0.51–0.59  (still ~chance — answer not computed yet)
  15  |   0.699    |    0.508     |    0.711
  16  |   0.833    |    0.603     |    0.889
  17  |   0.884    |    0.648     |    0.913
  18  |   0.892    |    0.684     |    0.963   ← best
  19  |   0.878    |    0.713     |    0.950
  20  |   0.873    |    0.687     |    0.921
 22–28| 0.79–0.85  |  0.58–0.67   |  0.83–0.87  (gentle decline; gap to diffmean persists)
```

Leave-category-out (GroupKFold on category) — best layer 18: **logreg 0.871**, diffmean 0.697. Barely below the random split.
v1 contrast (leave-country-out on `conditions_v1`) — best layer 16: **logreg 1.000**, unchanged from its random split.

**Reading (same model, two conditions):**

| | v1 syntactic (r2) | v2 semantic (r3) |
|---|---|---|
| readable from layer | ~8 | ~16 |
| best AUROC (random) | 1.000 | 0.892 |
| diffmean catches logreg? | yes, at L16 | never (0.73 vs 0.89) |
| leave-group-out best | 1.000 | 0.871 |

Semantic recognition is **computed ~8 layers later**, **peaks lower** (not trivially separable), stays a **distributed** feature (diffmean never catches up — it never consolidates into an explicit axis the way string-matching does), but is **abstract enough to transfer** to categories the probe never trained on.

**Skeptic's caveats:**
- **0.89 is high.** These are common items with unambiguous categories — a 0.6B already knows beef = food, laptop = electronics. So this shows *easy* semantic categorisation, not hard/fuzzy recognition. Rarer or fuzzier items are the real next rung.
- **Dents the 8B plan.** 0.6B already at 0.89 leaves little headroom for scale to show an effect on this v2. A harder v3 (rare / fine-grained items where 0.6B clearly fails) is probably needed before an 8B run is informative.
- **N=192** — 0.892 vs 0.871 is within noise; don't over-read the small random-vs-group gap.

---

## `2026-05-29_r2` — conditions_v1, Qwen3-0.6B

First run on purpose-built data. **This is the result that matters so far.**

- **How run:** `./run.sh Qwen/Qwen3-0.6B cpu float32` (smoke 4 → full 200 → probe). Activations captured at the final prompt token, all 29 hidden-state indices. Probe: logistic regression + difference-of-means, pooled out-of-fold AUROC under stratified 5-fold.
- **Config:** model `Qwen/Qwen3-0.6B`, `dtype=float32`, `enable_thinking=False`, hidden_dim 1024, 28 transformer blocks.

Per-layer AUROC (logreg pooled OOF | diffmean pooled OOF | single 80/20 split):

```
layer | logreg OOF | diffmean OOF | logreg split
   0  |   0.500    |    0.500     |    0.500   (embeddings — constant final token, sanity check)
   1  |   0.441    |    0.465     |    0.575
   2  |   0.429    |    0.453     |    0.560
   3  |   0.517    |    0.476     |    0.698
   4  |   0.733    |    0.497     |    0.897
   5  |   0.751    |    0.499     |    0.940
   6  |   0.827    |    0.516     |    0.960
   7  |   0.846    |    0.513     |    0.973
   8  |   0.904    |    0.525     |    0.988
   9  |   0.979    |    0.589     |    0.987
  10  |   0.982    |    0.600     |    0.997
  11  |   0.984    |    0.609     |    1.000
  12  |   0.986    |    0.599     |    1.000
  13  |   0.996    |    0.602     |    1.000
  14  |   0.999    |    0.628     |    1.000
  15  |   0.997    |    0.685     |    1.000
  16  |   1.000    |    0.991     |    1.000   ← feature becomes mean-separable here
  17  |   1.000    |    0.992     |    1.000
  18–28|  1.000    |  0.87–0.97   |    1.000
```

**Reading:**
- **Real computation profile.** Chance at the input/early layers (the answer is *not* in the surface), rising steadily as the model attends from the final token to the list and destination, saturating mid-network. Exactly what genuine recognition should look like — and the opposite of run r1.
- **logreg ≫ diffmean until layer 16.** The match is linearly decodable from ~layer 9 (logreg ~0.98) but *not along the class-mean axis* (diffmean ~0.6) until layer 16, where diffmean snaps to 0.99. Interpretation: the "matched" feature is distributed in mid-layers and gets **consolidated into an explicit, axis-aligned feature around layer 16**.
- **Repetition control passed.** With ~22 proceed cases naming the destination off-list, a raw "appears twice" probe would have false-positived and AUROC couldn't hit 1.0. It did → the probe reads **binding to the list**, not mere repetition.

**Caveat / what it doesn't show:** the condition reduces to "did the destination string appear in the list region" — pure **syntactic** matching, the easiest form of recognition. A 0.6B saturating it means an 8B run on this exact data would also ~1.0 and teach little. The informative next step is a **semantic** variant (restricted *categories* + specific *items*, so recognition needs item→category classification) that keeps the surface decorrelation.

---

## `2026-05-29_r1` — scenarios_v2, Qwen3-0.6B

First-ever probe dry-run, on the reused behavioural-eval data. Kept for the record because it's *why* we rebuilt the dataset.

- **How run:** Qwen3-0.6B on `scenarios_v2.json` with the fixed `persona_exit_v2` system prompt, leave-one-pair-out CV. (Pipeline predates the per-example-system-prompt refactor.)
- **Result:** best layer 14, logreg pooled OOF AUROC **0.978**; layer 1 already at 0.877.
- **Reading:** the AUROC was high *everywhere from layer 1*, and a 0.6B model that can't perform the escalation task behaviourally has no business scoring 0.98 — unless the probe is reading the **topic** of the request (crypto/sanctions/fraud vs. routine admin), which is trivially present in the surface. Verdict label was "GO" but the result is **not meaningful**: the dataset couldn't separate recognition from surface content. This directly motivated `conditions_v1`.
