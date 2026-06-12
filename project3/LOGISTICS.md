# GPU Logistics

Main thing is, take your time on the box. If you end up making GBs of data/activations, makes more sense to do the analysis on the box rather than us waiting hours for the activations to transfer back to this device. That's why we spend time trying to get all the code ready before hand, so it's committed and on the box. But also not the end of the world if fresh code needs to be written on the box, we'll have a record of it in our chat that we can add to our repo here.

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

Detach from tmux with **Ctrl-b** then **d**; reattach with `tmux attach -t extract`.
Output also lands in `logs/extract_<...>_<UTC>.log`, so results survive even if
the terminal dies.

---

## Pulling results home + probing (on the laptop)

- We can use `scp`
- IMPORTANT: if there are many GBs of data to transfer, it's not worth it
  - In that case just run analysis on the GPU and **pull the results back home**

---

## Hard-won gotchas (so we don't relearn them)

- **`python` isn't on the box PATH sometimes** — the interpreter lives in a venv. Always
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
