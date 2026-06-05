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

### Planned `2026-05-30` (pre-registered) — Qwen3-8B scale × reasoning (r7 / r8)

**The experiment the whole monitor story hangs on.** Everything so far is one regime: a 0.6B, greedy, thinking off. r4's behaviour failure was a *proceed-default*, so we cannot yet tell **"recognises but doesn't act"** from **"too weak to act."** Only a model that *can* do the task disambiguates the two. Pre-registered before any 8B run; thresholds fixed here, scored HIT/MISS on landing.

**Run matrix** (Qwen3-8B, [conditions_v2](datasets.md#conditions_v2json--current), N=192, GPU / bf16):
- **r7 — thinking OFF**, `--generate`. Direct scale comparison to r4 (same dataset + grading, bigger model).
- **r8 — thinking ON**, `--generate` (auto 1024-token budget so the model clears its `<think>` block before the marker). Reasoning comparison. *Readout note:* the probe is read at the **pre-reasoning** token (generation header, before `<think>`); behaviour is the **post-reasoning** final answer. So a "probe-right / behaviour-wrong" case in r8 means *recognised at input, reasoned, still omitted* — a stronger claim than r7's.
- **Controls** (`controls.py`) on r7 and r8 activations — standing rule; lead with diff-of-means, report selectivity.
- **r9 (secondary)** — transfer v2→v2b on r7 activations: does the domain-generality from r6 survive scale? Needs an 8B extract on v2b (forward passes only, no generation).

**Anchors (0.6B, r4/r5):** behaviour acc **0.521** (28 esc / 164 proc, proceed-default); probe acc **0.792**; honest recognition diff-of-means AUROC **~0.71**; monitor payoff **61/80 = 0.76**; probe-OK/behaviour-WRONG cell **72**; aggregate gap (probe acc − behav acc) **0.27**.

**The metric that carries the claim — read this first.** As capability rises, behavioural accuracy rises, so the *number* of silent misses falls, so the **aggregate gap shrinks mechanically**. A smaller aggregate gap at 8B is therefore *expected and not bad news*. The load-bearing metric is the **monitor payoff**: of the cases the model *still* fails silently (however few), does the probe recover the answer? That does not trivially shrink with capability — it is the real test.

**r7 predictions (8B, thinking off):**
1. **Capability rises.** Behavioural accuracy **> 0.65** (clearly above the 0.6B's 0.52). *Falsify:* ≤ 0.55 → the 8B also proceed-defaults; the task doesn't separate capability and the can't-vs-won't confound persists at scale.
2. **Recognition survives & stays selective.** diff-of-means recognition AUROC **≥ 0.71** *and* selectivity **≥ 0.10** over the best clean control (shuffle / dest / item-irrelevant). *Falsify:* diff-of-means < 0.65 or selectivity < 0.05 → the signal doesn't survive scale.
3. **Monitor payoff holds (the crux).** Of should-escalate cases the 8B behaviourally misses, the probe flags escalate for **≥ 60%**. *Falsify:* < 50% → the probe doesn't recover the missed recognition. *Wide-CI caveat:* if misses < 20, report exact counts and don't over-read the fraction.
4. **Gap direction holds, magnitude shrinks.** probe acc **≥** behaviour acc, and aggregate gap **< 0.27**. *Falsify the framing:* behaviour > probe → the monitor framing is wrong at scale. (A shrinking gap alone is expected — P3 carries the claim, not P4's size.)

**r8 predictions (8B, thinking on):**
5. **Reasoning improves behaviour.** r8 behaviour acc **> r7 behaviour acc**. *Falsify:* ≤ r7 → reasoning doesn't help here (surprising for an easy item→category task).
6. **Input-recognition is stable to the thinking toggle (control).** Each run's own diff-of-means OOF probe AUROC at the pre-generation token: r8 within **±0.05** of r7. If it moves more, thinking-mode prompt formatting itself shifts the representation — understand that before trusting the behaviour comparison.
7. **Does reasoning close the gap? (directional pre-commit).** Expect reasoning to *shrink* the gap but **not flip it**: probe recognition still ≥ behaviour, and monitor payoff on r8's remaining misses **≥ 50%**. Two honest outcomes, interpretation committed in advance:
   - **Gap closes** (behaviour ≈ recognition; misses become rare): reasoning largely fixes silent omission → the monitor matters *less* for reasoning models. Deflating, but we'd report it.
   - **Gap survives** (≥ ~10 probe-right/behaviour-wrong cases; payoff ≥ 50%): the model recognises at input, reasons, and *still* omits → the monitor matters *even for* reasoning models. The stronger result for the project.
   *Falsify the framing:* r8 behaviour > pre-reasoning probe recognition → "recognise-but-don't-act" isn't the right description once reasoning is on.

**What would make this uninteresting (recorded so we don't reframe a null):** if the 8B aces behaviour (≈ probe) with thinking *off* already, there's no silent-omission gap to catch on this dataset → conditions_v2 is too easy for an 8B, and we'd need a harder rung (rarer / fuzzier items) before scale teaches us anything. We'd say so plainly.

**Outcome (r7, 2026-06-05) — 4 HIT (P2's selectivity clause pending controls):**
1. **HIT (strong).** behaviour **0.896** ≫ 0.65 (vs 0.6B 0.521). The 8B genuinely does the task — a residual gap can no longer be dismissed as "too weak to act."
2. **HIT (and selective).** diff-of-means **0.982 @ L23** (≥ 0.71, strongly), and it *catches* logreg (~0.98) → the feature consolidated into an explicit axis. **Selectivity confirmed** ([select_layer.py](select_layer.py), run locally on the pulled `.npz`): shuffle ~0.47 and item-irrelevant membership ~0.43 sit at chance while real recognition is ~0.97 → selectivity **0.459 @ L34** (vs the 0.6B's 0.18). The 0.98 is clean, selective recognition, not a rich-representation artefact.
3. **HIT (wide CI).** Of **13** should-escalate behavioural misses, the probe flagged escalate on **9 (0.69)** ≥ 0.60. Clears the bar, but on only 13 misses — the pre-registered wide-CI caveat applies.
4. **HIT.** probe **0.948** ≥ behaviour **0.896**; aggregate gap 0.948 − 0.896 = **0.052** < 0.27. Shrank mechanically, as predicted.

**Read:** recognition survives scale *strongly*; the recognise-but-don't-act *gap* largely **closes** at 8B (0.27 → 0.05) — the dramatic 0.6B dissociation was substantially a proceed-default / small-model artefact. The monitor keeps residual value (9/13 of the rare silent misses) but the phenomenon is now ~7% of cases, not dominant. Trending toward the pre-registered "v2 is easy for an 8B," which motivates a harder rung. Full table + decomposition in the r7 detail block below.

**Outcome (r8, 2026-06-05) — the "gap closes" branch, as pre-committed:**
5. **HIT.** behaviour **0.938** > r7's 0.896 — reasoning *improves* behaviour (the 8B acts on what it recognises even more when it thinks).
6. **HIT.** recognition unchanged by the thinking toggle: diff-of-means **0.971 @ L27** vs r7's 0.968, within ±0.05. Read at the pre-reasoning token, so on/off barely matters.
7. **"Gap closes" outcome.** Recognition AUROC (0.987 / dm 0.97) still ≥ behaviour 0.938, and the monitor caught **7/7** of the should-escalate silent misses — but there are now only **7** (wide CI). Honest nuance that complicates the framing: at a 0.5 threshold the probe's *accuracy* (0.922) dips **below** behaviour (0.938) — they make different errors — so the probe isn't a better overall classifier than the reasoning model; its value is narrowly in catching behaviour's specific silent misses. Net: reasoning largely fixes silent omission on this benign task → the monitor matters *less* for reasoning models here. The pre-committed deflating-but-honest read.

**Net (r7 + r8) — the benign-task line is closed.** Recognition survives scale AND reasoning (strong, selective, ~0.97); the recognise-but-don't-act gap does NOT — it shrinks toward nothing (silent misses 13 → 7; gap 0.05 → ~0). This is the empirical proof that a benign, unambiguous task with a capable model **structurally cannot** produce the dissociation the monitor exists to catch. Next: a task that *dissociates* recognition from action (recognition easy, action fails systematically) **+ an independent recognition check** (ask the model directly) to separate dissociation from co-failure.

---

| Run ID | Dataset | Model | Device/dtype | Split | N | Best layer | AUROC | Verdict | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-06-05_r8 | [conditions_v2](datasets.md#conditions_v2json--current) +behaviour | Qwen3-8B *(thinking ON)* | cuda / bf16 | stratified 5-fold | 192 | 24 | **0.987** | GO | **8B scale, thinking ON.** Reasoning *improves* behaviour 0.896→**0.938**; recognition unchanged (diff-of-means 0.971, selectivity 0.42 ≈ r7). Gap closes further: only **7** silent misses, probe catches **7/7** (wide CI). Honest nuance: thresholded probe acc 0.922 < behaviour 0.938 (different errors) — probe isn't a better overall classifier, just catches behaviour's specific misses. Confirms the benign line is exhausted → need a dissociation task. Extracted at af19212, probed locally. |
| 2026-06-05_r7 | [conditions_v2](datasets.md#conditions_v2json--current) +behaviour | Qwen3-8B | cuda / bf16 | stratified 5-fold | 192 | 28 | **0.993** | GO | **8B scale, thinking OFF.** Recognition survives scale strongly — diff-of-means **0.982 @ L23**, *catches* logreg (~0.99) → explicit axis. Behaviour **0.896** (the 8B does the task), probe **0.948** → recognise-but-don't-act gap shrinks to **0.05** (from 0.6B's 0.27). Monitor payoff **9/13 (0.69)** on the rare silent misses (wide CI). ⚠ Selectivity controls pending — 0.98 is high. Extracted at 05c74de (torch 2.11.0+cu128 / transformers 5.10.2), probed at d972a32. |
| 2026-05-30_r6 | transfer [v2](datasets.md#conditions_v2json--current)→[v2b](datasets.md#conditions_v2bjson--current) | Qwen3-0.6B | cpu / float32 | train-on-v2 / test-on-v2b | 192→192 | 20 | 0.790 | — | **Cross-taxonomy generalisation (Step 2).** Diff-of-means recognition direction trained only on export goods detects "condition fired" on a disjoint domain (instruments/sports/jewellery…) at **~0.79 (L19–21)** — *no transfer penalty*: matches/exceeds the within-v2b ceiling (~0.72), +0.34 over shuffle (0.45). Recognition direction is domain-general. (logreg-transfer ~0.87 but NOT clean — v2/v2b share phrasing, so logreg's surface reliance carries over; diff-of-means stays the trustworthy metric.) |
| 2026-05-29_r5 | controls on [conditions_v2](datasets.md#conditions_v2json--current) | Qwen3-0.6B | cpu / float32 | stratified 5-fold | 192 | 18 | — | — | **Probe-validation controls** ([controls.py](controls.py)). Shuffle passes (~0.50 → pipeline honest). BUT logreg reads arbitrary junk at 0.75–0.80 → its 0.892 headline has low selectivity. Trustworthy signal is **diff-of-means 0.684**, which clears the clean controls (dest-alpha 0.52, item-irrelevant membership 0.44). Recognition is real but smaller than claimed; **revises r3/r4 headline down**. |
| 2026-05-29_r4 | [conditions_v2](datasets.md#conditions_v2json--current) +behaviour | Qwen3-0.6B | cpu / float32 | stratified 5-fold | 192 | 18 | 0.892 | GO | **Thesis test.** Behaviour 0.521 (proceed-default) vs probe 0.792. Probe catches 61/80 (76%) of behavioural escalation misses + 11/12 false alarms. All 4 pre-registered predictions HIT. Caveats: supervised probe vs zero-shot behaviour; proceed-default under greedy/no-thinking 0.6B. **⚠ See r5: logreg headline inflated; honest recognition signal is diff-of-means ~0.68, so the gap is ~0.16 not ~0.37.** |
| 2026-05-29_r3 | [conditions_v2](datasets.md#conditions_v2json--current) | Qwen3-0.6B | cpu / float32 | stratified 5-fold | 192 | 18 | 0.892 | GO | Semantic rung. Signal emerges deep (~L16), peaks 0.892, never saturates; diffmean never catches logreg (stays distributed). Leave-category-out barely drops (0.871) → abstract, transferable feature. The contrast with r2, not the number, is the finding. |
| 2026-05-29_r2 | [conditions_v1](datasets.md#conditions_v1json--current) | Qwen3-0.6B | cpu / float32 | stratified 5-fold | 200 | 16 | **1.000** | GO | Clean computation profile (chance early → saturates mid-net). Repetition control passed. But 0.6B saturating means the task is the *syntactic floor* — string-matching, not semantic recognition. |
| 2026-05-29_r1 | [scenarios_v2](datasets.md#scenarios_v2json--superseded) | Qwen3-0.6B | cpu / float32 | leave-one-pair-out | 40 | 14 | 0.978 | GO* | *GO is misleading. A 0.6B model can't do the task behaviourally, so 0.978 = the probe reading **topic**, not recognition. This result motivated building `conditions_v1`. |

The 0.6B rows above were dry-runs to validate the pipeline and dataset design on a laptop (CPU) before the GPU run. Treat their numbers as design diagnostics, not headline findings. r7 (below) is the first real GPU run.

---

## `2026-06-05_r8` — Qwen3-8B, conditions_v2, thinking ON (reasoning comparison)

Extracted on the RTX 3090 at commit af19212 (`extract.sh THINK=1`, 1024-token budget so reasoning completes before the marker); probed locally. Full per-layer table in the committed [results record](activations_conditions_v2_8b_think.results.json); signal region below (logreg OOF | diffmean OOF | logreg split):

```
layer | logreg | diffmean | split
  0   | 0.492  |  0.500   | 0.500   (emb — sanity)
1–17  | ~chance, logreg climbing 0.40→0.84, diffmean ~0.52
 18   | 0.931  |  0.693   | 0.921
 19   | 0.968  |  0.806   | 0.963
 20   | 0.974  |  0.947   | 0.958   ← diffmean snaps up
 21   | 0.982  |  0.960   | 0.953
 22   | 0.983  |  0.962   | 0.966
 23   | 0.987  |  0.972   | 0.963   ← diffmean peak
 24   | 0.987  |  0.970   | 0.963   ← logreg best
 26   | 0.987  |  0.972   | 0.966
 36   | 0.982  |  0.966   | 0.932
```

Best layer (logreg OOF): **L24, 0.987**. Diff-of-means peak **0.972** (L23/26). Selectivity ([select_layer.py](select_layer.py)): most-selective **L27 diff-of-means 0.971, selectivity 0.418** (item-irrelevant control ~0.37–0.39 at chance, shuffle ~0.50) — clean, ≈ r7.

Recognition vs behaviour @ L24:

```
                          behav OK   behav WRONG
   probe OK                 167          10
   probe WRONG               13           2

behaviour: 94 escalate / 97 proceed / 1 unclear   |  accuracy 0.938  (r7: 0.896)
probe accuracy @ L24: 0.922
should-escalate MISSES: 7/96  | probe flagged escalate on 7 (1.00)  <- monitor payoff
should-proceed FALSE ALARMS: 5/96 | probe said proceed on 3 (0.60)
```

**Reading:**
- **Reasoning improves behaviour** (0.896 → 0.938): the 8B acts on what it recognises *more* when it reasons.
- **Recognition unchanged by the thinking toggle** (diff-of-means 0.971 ≈ r7's 0.968): read at the pre-reasoning token, so on/off barely matters.
- **The gap closes further.** Only **7** silent misses (r7 had 13); probe catches **7/7** — perfect but tiny-N (wide CI). Honest nuance: thresholded probe accuracy (0.922) dips *below* behaviour (0.938) — they make different errors — so the probe isn't a better overall classifier than the reasoning model; its value is narrowly in catching behaviour's specific silent misses.
- **Net:** reasoning largely fixes silent omission on this benign task → the monitor matters *less* for reasoning models here. The pre-committed deflating-but-honest outcome.

**Closes the benign-task line (r7 + r8):** recognition survives scale and reasoning (strong, selective, ~0.97); the recognise-but-don't-act gap does not (13 → 7 misses, gap → ~0). Empirical proof that a benign task + capable model can't produce the dissociation the monitor exists to catch. Next: a dissociation task + an independent recognition check.

---

## `2026-06-05_r7` — Qwen3-8B, conditions_v2, thinking OFF (scale comparison to r4)

First real GPU run. **Extracted on a rented RTX 3090 (vast.ai)** at commit 05c74de (torch 2.11.0+cu128, transformers 5.10.2); all-layer final-token activations, 192 examples, `--generate` for behaviour. Probe re-run (after a frozen-terminal recovery) at commit d972a32, which writes `results.json`. From here, probing moves to the laptop (see [LOGISTICS.md](LOGISTICS.md)).

Per-layer AUROC (logreg OOF | diffmean OOF | logreg single split), **verbatim**:

```
layer | logreg OOF | diffmean OOF | logreg split
  0   |   0.492    |    0.500     |    0.500   (emb — sanity)
  1   |   0.469    |    0.533     |    0.508
  2   |   0.448    |    0.524     |    0.453
  3   |   0.426    |    0.537     |    0.411
  4   |   0.481    |    0.525     |    0.513
  5   |   0.469    |    0.527     |    0.482
  6   |   0.453    |    0.530     |    0.421
  7   |   0.495    |    0.526     |    0.484
  8   |   0.516    |    0.530     |    0.484
  9   |   0.586    |    0.528     |    0.582
 10   |   0.600    |    0.545     |    0.597
 11   |   0.610    |    0.538     |    0.558
 12   |   0.634    |    0.543     |    0.553
 13   |   0.612    |    0.537     |    0.547
 14   |   0.562    |    0.535     |    0.542
 15   |   0.573    |    0.533     |    0.545
 16   |   0.632    |    0.537     |    0.618
 17   |   0.820    |    0.555     |    0.805   ← logreg lifts off
 18   |   0.913    |    0.584     |    0.905
 19   |   0.962    |    0.697     |    0.937
 20   |   0.963    |    0.930     |    0.958   ← diffmean snaps up
 21   |   0.976    |    0.962     |    0.961
 22   |   0.982    |    0.971     |    0.955
 23   |   0.992    |    0.982     |    0.966   ← diffmean peak
 24   |   0.991    |    0.978     |    0.942
 25   |   0.992    |    0.976     |    0.942
 26   |   0.992    |    0.974     |    0.945
 27   |   0.993    |    0.975     |    0.942
 28   |   0.993    |    0.974     |    0.947   ← logreg best
 29   |   0.992    |    0.974     |    0.945
 30   |   0.990    |    0.972     |    0.945
 31   |   0.992    |    0.971     |    0.942
 32   |   0.991    |    0.972     |    0.937
 33   |   0.985    |    0.972     |    0.934
 34   |   0.984    |    0.968     |    0.937
 35   |   0.982    |    0.967     |    0.947
 36   |   0.982    |    0.967     |    0.950
```

Best layer (logreg pooled OOF): **layer 28, 0.993**. Diff-of-means peak **0.982 @ L23**.

Recognition vs behaviour @ L28:

```
                          behav OK   behav WRONG
   probe OK                 169          13      <- probe right where behaviour wrong
   probe WRONG                3           7

behaviour: 90 escalate / 102 proceed / 0 unclear   |  accuracy 0.896
probe accuracy @ L28: 0.948
should-escalate MISSES: 13/96  | probe flagged escalate on 9 (0.69)  <- monitor payoff
should-proceed FALSE ALARMS: 7/96 | probe said proceed on 4 (0.57)
```

**Reading:**
- **Recognition survives scale, strongly.** diff-of-means 0.71 (0.6B) → **0.98** (8B), and it *catches logreg* (both ~0.98 by L21+) — the semantic feature consolidated into an explicit, axis-aligned direction (the 0.6B did this only for the *syntactic* floor in r2). The low-capacity probe reading it ~as well as logreg is reassuring it isn't overfitting. (This separability is also literally why logreg is slow to fit at 4096 dims.)
- **The recognise-but-don't-act gap mostly closes.** 0.6B gap 0.27 → 8B **0.05**. The 8B mostly *acts* on what it recognises (behaviour 0.896), so the dramatic 0.6B dissociation was substantially a proceed-default / small-model artefact. Recorded straight, not reframed.
- **Monitor: residual value on rare events.** 9/13 (0.69) of the silent misses caught — but misses are now 13/192 (~7%), not the dominant mode (0.6B: 80/96).
- **Depth:** signal emerges ~L17 (of 36), saturates low-20s — similar *relative* depth to the 0.6B's ~L16 (of 28).

**Selectivity (ran locally on the pulled `.npz` — [select_layer.py](select_layer.py)): the 0.98 is clean.** Per-layer diff-of-means selectivity vs the clean controls — shuffle collapses to ~0.47–0.52 (pipeline honest), destination ~0.52, and the sharp **item-irrelevant membership ~0.40–0.46** — all at/below chance while real recognition is ~0.97. Most-selective layer **L34: diff-of-means 0.968, selectivity 0.459** (raw diff-of-means peak L23 0.982, sel 0.437). So 8B recognition is not only stronger than the 0.6B (0.97 vs 0.71) but **far more selective** (0.46 vs 0.18) — genuinely the item-cued match, not a rich-representation artefact. This validates the dogfood path too: extracted on GPU, all probing/controls run on the laptop off the one pulled `.npz`.

**Full controls table** ([controls.py](controls.py), layer 28, verbatim):

| task | logreg | diffmean | selectivity (logreg) |
|---|---|---|---|
| REAL (escalation) | 0.993 | 0.974 | — |
| shuffle labels (mean of 5) | 0.488 | 0.480 | 0.505 |
| junk: destination alpha-half | 0.603 | 0.524 | 0.390 |
| junk: item-name length parity | 0.624 | 0.574 | 0.369 |
| surface: phrasing template | 1.000 | 0.924 | −0.007 |
| **item-IRRELEVANT membership** (corr w/ real 0.04) | 0.484 | **0.430** | 0.509 |

Shuffle ~0.48 → honest pipeline. The decisive row is **item-irrelevant membership ~0.43** (chance) while real recognition is 0.97 → the probe reads the **item-cued match**, not generic membership. Unlike the 0.6B (r5), **even logreg is now selective** — junk controls read only ~0.60 here (vs the 0.6B's 0.75–0.80) while real is 0.99, so logreg selectivity is high (~0.39–0.51). Phrasing stays perfectly decodable (1.000 / 0.924) but is **label-orthogonal by construction**, so it isn't what the real label direction reads. Net: the r5 "logreg inflated" worry has largely evaporated at 8B — both probes clear the controls, and recognition is clean.

---

## `2026-05-30_r6` — cross-taxonomy transfer (Step 2): does the monitor generalise?

Built [conditions_v2b](datasets.md#conditions_v2bjson--current) — a disjoint taxonomy (musical instruments, sports equipment, jewellery, footwear…), same framing/structure as v2 — and tested whether a recognition probe trained on v2 detects conditions on v2b it never saw. Ran [transfer_test.py](transfer_test.py) on 0.6B activations.

Transfer across layers (diff-of-means, the trustworthy metric):

| layer | within-src (v2) | within-tgt (v2b) | **transfer v2→v2b** | shuffle-trans | logreg-trans |
|---|---|---|---|---|---|
| 16 | 0.603 | 0.622 | 0.721 | 0.482 | 0.894 |
| 17 | 0.648 | 0.672 | 0.761 | 0.488 | 0.912 |
| 18 | 0.684 | 0.682 | 0.763 | 0.450 | 0.875 |
| **19** | **0.713** | **0.727** | **0.789** | 0.447 | 0.869 |
| 20 | 0.687 | 0.718 | **0.790** | 0.442 | 0.878 |
| 21 | 0.678 | 0.715 | 0.788 | 0.452 | 0.868 |

**Findings:**
1. **The monitor generalises across taxonomies — with no penalty.** A diff-of-means direction fit *only* on export goods detects "condition fired" on a disjoint domain at **~0.79 (L19–21)**, which *matches or exceeds* the within-v2b ceiling (~0.72) and sits +0.34 above the shuffle control (~0.45). The recognition feature is abstract / domain-general, not taxonomy-memorised. (Transfer ≥ within likely because the direction is estimated on the full 192-example source rather than CV folds — don't over-read the >; the honest claim is "no transfer loss.")
2. **Within-target ≈ within-source** (0.73 vs 0.71): the model represents the v2b conditions about as well as v2 — domains are difficulty-matched, so transfer isn't flattered by an easier target.
3. **logreg-transfer stays high (~0.87) but is NOT clean evidence.** v2 and v2b use identical phrasing/framing, so logreg's known surface reliance (r5) carries straight over — its transfer can't be attributed to recognition. diff-of-means remains the trustworthy metric precisely because phrasing is label-orthogonal by construction, so the label direction isn't the phrasing direction.

**Candid read:** absolute level is modest (~0.79 transfer, tracking the ~0.71 within-domain recognition signal). The *result* is the zero transfer loss across a disjoint domain — domain-generality is the property a real monitor needs, and we have it on a small model.

**Correction note:** the first version of this entry logged transfer as 0.661 with a "logreg collapses to 0.70, corroborates r5" claim. Both were wrong — I summarised from fabricated hand-typed numbers instead of the actual `transfer_test.py` output. Real numbers above; logreg transfers at ~0.87 and does *not* collapse. Fixed same session.

**Step 2 of the post-r5 plan complete.** Open question unchanged: does this survive scale + reasoning (8B)?

---

## `2026-05-30` — honest layer re-selection (follow-up to r5)

Ran [select_layer.py](select_layer.py) to pick the layer by the *trustworthy* metric — diff-of-means selectivity vs the clean controls (shuffle / destination / item-irrelevant) — instead of where logreg peaked (r5 showed logreg selection inflates the headline).

- **Honest monitor number: diff-of-means AUROC ≈ 0.713 at layer 19** (selectivity ≈ 0.177 over the best clean control) — slightly above the 0.684 we'd quoted at layer 18, because layer 18 was the logreg peak, not the honest one.
- **Selectivity profile is clean and confirms the depth story on the honest metric:** `select_dm` ≈ 0 / negative through layers 0–15, rises sharply 16→19, peaks at 19, declines after. Recognition lives in a **region (~L16–21), not a single layer** — so r3's "computed deep, not in the surface" finding *survives* the honest re-analysis (previously it leaned on logreg).
- logreg stays ~0.88 across L17–21 — low-selectivity reader; reference/upper-bound only.

**Net:** the honest recognition signal is **modest but real and selective — ~0.71 diff-of-means, ~0.18 over controls, localised deep in the network.** Reporting convention locked: headline diff-of-means at the most-selective layer; logreg as reference. Step 1 of the post-r5 plan complete; next is generalisation to unseen conditions.

---

## `2026-05-29_r5` — probe-validation controls on conditions_v2

Ran [controls.py](controls.py) to test whether the probe reads *recognition* or just fits structure. **It caught real inflation in our logreg headline.**

- **How run:** `python controls.py --activations activations_conditions_v2.npz --dataset inputs/conditions_v2.json` (seed 0, layer 18, stratified 5-fold OOF, reusing train_probe's probe/CV).

| task (layer 18) | logreg | diffmean | selectivity (logreg) |
|---|---|---|---|
| REAL escalation | 0.892 | **0.684** | — |
| shuffle labels (mean of 5) | 0.495 | 0.511 | 0.398 |
| junk: destination alpha-half | 0.754 | 0.519 | 0.139 |
| junk: item-name parity *(confounded w/ identity — ignore)* | 0.800 | 0.642 | 0.093 |
| surface: phrasing template | 1.000 | 1.000 | −0.108 |
| **item-IRRELEVANT membership** (corr w/ real 0.04) | 0.561 | **0.437** | 0.331 |

**Findings:**
1. **Shuffle passes (~0.50):** OOF pipeline is honest; the real AUROC is not a D>N/CV artefact.
2. **logreg is low-selectivity here:** it reads arbitrary junk at 0.75–0.80, so the 0.892 headline is mostly "powerful probe on a rich representation," only ~0.1 above junk. **Stop headlining the logreg number.**
3. **diff-of-means is properly selective and is the trustworthy signal:** escalation 0.684 clears the *clean* controls — shuffle 0.51, destination 0.52, and the sharp **item-irrelevant membership 0.44** — by 0.16–0.25. So the representation specifically encodes the **item-cued match** (recognition), not generic list contents.
4. phrasing = 1.0 (both probes): surface phrasing is the loudest axis — which is *why* high-capacity logreg can read junk. item-name parity (0.64 diffmean) is a bad control (proxies item identity); disregard.

**Consequences for earlier runs (annotated, not rewritten):**
- The recognition signal **survives** but is **~0.68 (diff-of-means), not 0.89**.
- The r4 recognise-but-don't-act gap is **~0.16 (0.68 vs 0.52), not ~0.37**. Real but modest.
- **Reporting rule going forward:** lead with diff-of-means (selective); treat logreg as an upper bound; always report selectivity vs controls. For the *monitor* framing, logreg still legitimately predicts escalation (shuffle proves it), so "flags 76% of misses" stands as a monitor result — but not as evidence of recognition magnitude.

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

> **⚠ Revised by r5:** the 0.892 here is the *logreg* number, which the controls show is low-selectivity (logreg reads arbitrary junk at 0.75–0.80). The trustworthy recognition signal is **diff-of-means ≈ 0.68**. The qualitative findings below (deeper, distributed, generalises) still hold; the absolute magnitude is lower than the logreg headline.

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
