# Experiment logistics

The operational runbook: **how we actually run experiments** — the GPU/laptop
split, vast.ai basics, and the extract → pull → probe cycle. This is the "where
do I click / what do I type / what did past-us learn" doc.

It is deliberately separate from the science:
- [README.md](README.md) — the question and the story (what we're testing, why).
- [runlog.md](runlog.md) — the record of each run (config, results, predictions).
- [datasets.md](datasets.md) — what each dataset is and how to regenerate it.
- [CLAUDE.md](CLAUDE.md) — how to think while working here (the skeptical stance).

---

## The core idea: GPU extracts, laptop probes

Only **one** thing needs a GPU: running the model to produce **activations**.
Everything after that — training probes, controls, layer selection, transfer
tests — is plain CPU/numpy/sklearn work on a small saved file. Running it on a
rented GPU means paying 3090 rates to run sklearn while the GPU sits idle.

```
┌─ GPU box (vast.ai) ────┐   scp    ┌─ laptop ───────────────────────────┐
│ extract.sh             │ ───────▶ │ train_probe / controls /           │
│  → activations_*.npz   │  ~116 MB │ select_layer / transfer_test       │
│  (model forward pass)  │          │  → results.json + logs → git       │
└────────────────────────┘          └────────────────────────────────────┘
   only this needs a GPU              free · fast · robust · unlimited
```

So the lifecycle is: **extract on the box → pull the `.npz` home → probe locally
as much as you like → destroy the box.** No live GPU is needed for the
open-ended probing.

### Guiding principle: capture more than you need on the GPU run

The GPU is the expensive, ephemeral half. Once the box is destroyed, getting
anything else means **re-renting and re-extracting**. So when a box is up, lean
toward capturing *more* than the immediate test requires:

- Always `--generate` the model's behaviour, even when a given test only needs
  activations (e.g. the transfer test). Behaviour is cheap to capture now and
  expensive to get back later.
- Capture **all** layers (we already do) — never a hand-picked subset.

---

## What an extraction produces

One `.npz` per `(model, dataset, thinking-mode)`. The activation is the
residual-stream vector at the **final prompt token** — the position the model is
about to answer from, by which point it must already have done the
item → category → restricted-list check — recorded at **every** layer.

```
activations_<dataset>_<tag>.npz          e.g. activations_conditions_v2_8b_think.npz
  activations    : [N, n_layers+1, hidden]   final-token vector, every layer (8B: [N,37,4096])
  labels         : [N]    1=escalate (item's category is restricted), 0=proceed
  ids, groups    : [N]    example id; group = category (for leave-category-out CV)
  behaviour      : [N]    escalate/proceed/unclear     (only when --generate)
  generated_text : [N]    the model's raw output       (only when --generate)
  meta           : model, dtype, enable_thinking, dataset_path, git_commit,
                   torch/transformers versions, created_utc (UTC), sample_prompt
```

**The data** is one of the `conditions_*` datasets ([datasets.md](datasets.md)):
each example is a system prompt (a policy with a *randomised* restricted list of
categories) + a user request (*an item* to a destination); the label is whether
the item's category is on that example's list. Surface-decorrelated by
construction, so a probe can only score by reading recognition.

Every `.npz` is **self-describing** — read its `meta` and you know the model,
the data, thinking on/off, the library versions, and the exact code commit that
produced it.

---

## vast.ai setup (the basics, for next time)

Not the full first-time guide (SSH keygen etc. is already done — `arena_key` is
registered with the vast account). Just the per-instance basics:

1. **Conor rents a new instance** on [vast.ai](https://cloud.vast.ai): PyTorch
   template, a **24 GB** GPU (RTX 3090/4090), **~50 GB** disk, prefer a
   **verified, >99% reliability** host. (A port-binding error on first boot =
   bad host; destroy and rent a different machine.)
2. **Grab the "Direct ssh connect" line** (`ssh -p <port> root@<ip> ...`) and
   paste it to Claude / update the `arena` block in `~/.ssh/config`:
   ```
   Host arena
     HostName <ip>
     User root
     IdentityFile ~/.ssh/arena_key
     Port <port>
     ServerAliveInterval 15      # keepalive — rides out idle drops
     ServerAliveCountMax 4
   ```
3. **Connect + sanity checks:**
   ```bash
   ssh arena
   nvidia-smi --query-gpu=name,memory.total --format=csv,noheader   # expect a 24GB card
   /venv/main/bin/python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
   ```
4. **Get the code + deps:**
   ```bash
   git clone https://github.com/conorg000/TARA.git    # public; or `git pull` if reusing a box
   cd TARA/project3
   /venv/main/bin/pip install -U transformers          # only extra dep extraction needs
   ```
   torch + numpy are already in the venv; **scikit-learn is NOT needed on the box**
   (probing is local). The model cache lives at `HF_HOME=/workspace/.hf_home` and
   persists with the instance (gone if you destroy it).

---

## Running an extraction (on the box)

Always run it **detached** so a dropped SSH can't kill it, and let it log to disk:

```bash
ssh arena
cd /root/TARA/project3 && git pull && source /venv/main/bin/activate
tmux new -s extract          # or use nohup; either survives a disconnect
# r8 — 8B, thinking on:
THINK=1 ./extract.sh Qwen/Qwen3-8B cuda bfloat16 inputs/conditions_v2.json 8b_think
# r9 — 8B transfer target (still generating, per "capture more"):
./extract.sh Qwen/Qwen3-8B cuda bfloat16 inputs/conditions_v2b.json 8b_nothink
```

Detach from tmux with **Ctrl-b** then **d**; reattach with `tmux attach -t extract`.
Output also lands in `logs/extract_<...>_<UTC>.log`, so results survive even if
the terminal dies.

---

## Pulling results home + probing (on the laptop)

```bash
# from the laptop, in project3/:
scp arena:/root/TARA/project3/activations_conditions_v2_8b_think.npz .
source .venv/bin/activate
python train_probe.py --activations activations_conditions_v2_8b_think.npz
#   → prints per-layer table + decomposition, writes activations_..._think.results.json
```

The other probe scripts (`controls.py`, `select_layer.py`, `transfer_test.py`)
run the same way against the pulled `.npz`. `results.json` (committed) + the
runlog are the durable record; the `.npz` stays local + gitignored (it's
regenerable from model + dataset + git commit + seed).

When all extractions are pulled: **destroy the box** to stop the meter.

---

## Hard-won gotchas (so we don't relearn them)

- **`python` isn't on the box PATH** — the interpreter lives in a venv. Always
  `source /venv/main/bin/activate` first (or call `/venv/main/bin/python`).
- **Run long jobs detached** (tmux/nohup). A raw foreground SSH job dies when the
  connection drops; a frozen terminal then *looks* like a hang. Detached + logged
  is the fix (the job survives the connection; the output survives the terminal).
- **Buffered stdout hides progress.** Python buffers stdout to a file, so a long
  run looks frozen. `extract.sh`/`run.sh` set `PYTHONUNBUFFERED=1` to stream live.
- **SSH keepalives** (`ServerAliveInterval` in the config) reduce idle drops.
- **Don't `pkill -f <pattern>`** when the pattern also appears in your own SSH
  command line — it kills your own session (exit 255). Target a PID instead.
- **8B logreg is slow** — at 4096 dims with ~150 samples the classes are linearly
  separable, so the solver never converges and runs its full iteration budget on
  every fit. diff-of-means (our trusted metric) is instant; logreg is the
  reference. (Speed fix: regularise logreg — a deliberate methodology change.)
- **vast wraps your SSH in a tmux session named `ssh_tmux`** automatically; don't
  be surprised to see it.
