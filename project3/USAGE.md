# Running the probe experiment

Two steps: a GPU step that dumps activations once, and a CPU step that trains
probes on them (re-runnable on a laptop). See [README.md](README.md) for what
the experiment tests and why.

## Environment setup (one time)

Use a virtual environment on a modern Python (3.11+). On a Mac with multiple
Pythons, create the venv from a full interpreter by absolute path so a pyenv
shim doesn't shadow it:

```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m venv .venv
source .venv/bin/activate     # re-run this each new terminal session
python --version              # confirm 3.12.x, not an old pyenv 3.7
pip install -r requirements.txt
```

`source .venv/bin/activate` prepends the venv to PATH and wins over pyenv, so
plain `python` / `pip` resolve correctly once activated. `deactivate` to exit.

## Quickest path: `run.sh`

Chains smoke test → full extraction → probe training in one command.

```bash
pip install -r requirements.txt
./run.sh                              # GPU defaults: Qwen3-8B, cuda, bfloat16
./run.sh Qwen/Qwen3-0.6B cpu float32  # Mac dry-run (see below)
```

## Local dry-run on a Mac (no GPU)

Before renting a GPU, prove the pipeline runs end to end on your laptop with a
tiny same-family model. **The AUROC will be meaningless** — Qwen3-0.6B is far
too weak — but if the run completes and prints a verdict line, every moving
part (chat template, forward pass, hidden-state extraction, npz round-trip,
probe training) works, and the GPU run becomes pure compute with no surprises.

```bash
pip install -r requirements.txt
./run.sh Qwen/Qwen3-0.6B cpu float32
```

`Qwen/Qwen3-0.6B` (~1.2 GB) is the smallest dense Qwen3, so it shares the exact
chat template and architecture you'll use on the GPU. `cpu` + `float32` is the
most robust combination on a Mac; `mps` may be faster but can hit unsupported
ops, and the model is small enough that CPU finishes in a minute or two.

## What you need on the GPU box

- A single GPU with enough VRAM for the model in bf16. Qwen3-8B needs ~18 GB;
  it fits comfortably on a 24 GB card. If VRAM is tight, drop to a smaller dense
  Qwen3 (`--model Qwen/Qwen3-1.7B` or `Qwen/Qwen3-0.6B`) for the first signal
  check — the README explicitly sanctions this.
- Nothing else to gather. `project3/` is self-contained: the dataset it needs
  (`inputs/conditions_v1.json`) is bundled, and regenerable any time with
  `python make_dataset.py`. Upload just this folder. No Hugging Face token
  needed — Qwen3 weights download openly on first run.

## Step 1 — extract activations (GPU)

```bash
pip install -r requirements.txt

# Smoke test: 2 scenarios. Confirms the model downloads, the chat template
# renders, and the forward pass + save path all work end to end.
python extract_activations.py --max-scenarios 2 --out smoke.npz

# Full run: all 40 scenarios. Seconds of compute once the model is loaded.
python extract_activations.py --model Qwen/Qwen3-8B --out activations.npz
```

This captures the residual stream at **every** layer at the final prompt token
(the pre-generation position) and writes one small `.npz`. No text is generated.

## Step 2 — train probes (CPU, re-runnable anywhere)

```bash
python train_probe.py --activations activations.npz
```

Prints AUROC per layer for two probes (logistic regression, difference-of-means)
and maps the best layer's pooled AUROC to the pre-registered verdict
(GO > 0.80 / AMBIGUOUS / KILL < 0.65).

Useful variants:

```bash
# Just the three layers the README named, on a 32-block model.
python train_probe.py --layers 8,16,24

# Naive split that ignores pairing — expect this to look better than the
# grouped default. The gap between them is itself diagnostic: a big gap means
# the probe is leaning on surface phrasing shared within a pair.
python train_probe.py --split-mode random
```

## Reading the result

The headline is the **best layer's pooled out-of-fold logistic-regression
AUROC** under the default grouped split. That is the number to compare against
the README's pre-registered thresholds. The single 80/20 split column is there
for reference only — with N=40 it is noisy, so don't over-read it.

If grouped AUROC clears 0.80, the idea is alive and the next experiments
(cross-persona, cross-trigger-type generalisation) are worth designing. If it
sits in 0.65–0.80, look at whether the `random` split is much higher — that
points to surface-feature leakage rather than a real "trigger fired"
representation, and the next test should be the harder cross-generalisation one.
```
