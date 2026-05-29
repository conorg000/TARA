"""GPU step: dump residual-stream activations for the probe experiment.

What this does
--------------
For each example in the dataset, build the prompt the model sees (the example's
own system prompt — the policy with its per-example restricted list — plus the
user request and the assistant generation header), run a single forward pass,
and record the residual-stream activation at the final prompt token: the
position the model is about to generate from, by which point it must already
have matched the destination against the list to know its answer.

We capture *every* layer's residual stream in that one forward pass via
`output_hidden_states=True`, not just three hand-picked layers. It costs nothing
extra, the output file is tiny, and it means layer selection happens later in
`train_probe.py` on CPU without ever re-touching the GPU. Run this once; probe as
many times as you like afterwards.

No text is generated — we only need the forward pass over the prompt to read the
pre-generation activation, so this is cheap.

Note: unlike the earlier version, the system prompt is NOT a single fixed persona
file — each example carries its own `system` field, because the policy's
restricted list is randomised per example. That variation is the whole point of
the dataset (see make_dataset.py).

Output (.npz)
-------------
    activations   : float32 [N, num_layers+1, hidden_dim]
                    index 0 is the embedding output; index i>0 is the output of
                    transformer block i. train_probe.py uses the index as the
                    layer id directly.
    labels        : int8 [N]   1 = escalate (destination restricted), 0 = proceed
    ids           : str  [N]   example id, e.g. "ex_0007"
    groups        : str  [N]   destination country (for leave-country-out CV)
    meta          : JSON string with model, layer count, hidden dim, dataset
                    path, token position, and a sample rendered prompt.

Usage
-----
    python extract_activations.py --model Qwen/Qwen3-8B --out activations.npz

Smoke test first (4 examples, downloads model, verifies the whole path):
    python extract_activations.py --max-examples 4 --out smoke.npz

The default dataset is the bundled inputs/conditions_v1.json, so project3/ is
self-contained: upload just this folder to a GPU box and it runs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def load_dataset(dataset_path: Path) -> list[dict]:
    """Load the condition-recognition dataset (see make_dataset.py for shape)."""
    with dataset_path.open() as f:
        return json.load(f)


def build_prompt(tokenizer, system: str, user: str, enable_thinking: bool) -> str:
    """Render the chat prompt with the assistant generation header appended.

    `add_generation_prompt=True` appends the assistant-turn header, so the final
    token is exactly the position the model would generate its first token from
    — our probe target. `enable_thinking=False` keeps Qwen3 out of its <think>
    prefill so the prompt tail is deterministic and identical across examples
    (we are not generating, so the thinking block would be empty anyway).
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=enable_thinking,
    )


def parse_action(text: str, escalate_marker: str, proceed_marker: str) -> str:
    """Deterministically grade the model's generated behaviour.

    The system prompt instructs an exact token, so this is a string match, not a
    judgment call (no LLM judge needed — that's the point of the crisp dataset
    design). 'unclear' = the model emitted both markers, neither, or paraphrased;
    we bucket those and report the count so we can eyeball whether the parse is
    missing real escalations.
    """
    has_e = escalate_marker in text
    has_p = proceed_marker in text
    if has_e and not has_p:
        return "escalate"
    if has_p and not has_e:
        return "proceed"
    return "unclear"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default="Qwen/Qwen3-8B",
                        help="HF model id. Default Qwen3-8B (closest dense Qwen3 to the '7B' in the README). "
                             "For a cheaper signal check, try Qwen/Qwen3-1.7B or Qwen/Qwen3-0.6B.")
    parser.add_argument("--dataset", default="inputs/conditions_v1.json",
                        help="Path to the dataset JSON (records with system/user/label/id/group).")
    parser.add_argument("--out", default="activations.npz", help="Output .npz path.")
    parser.add_argument("--device", default="cuda",
                        help="Device to run on (cuda / mps / cpu). Default cuda. Use cpu for a Mac dry-run.")
    parser.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"],
                        help="Model compute dtype. Default bfloat16 (GPU). Use float32 on cpu/mps.")
    parser.add_argument("--enable-thinking", action="store_true",
                        help="Enable Qwen3 thinking-mode prompt suffix. Off by default (see build_prompt docstring).")
    parser.add_argument("--max-examples", type=int, default=None,
                        help="Cap the number of examples (for a quick smoke test). Default: all.")
    parser.add_argument("--generate", action="store_true",
                        help="Also generate the model's actual response and grade its behaviour "
                             "(deterministic token match), captured in the same forward pass as the activations.")
    parser.add_argument("--max-new-tokens", type=int, default=24,
                        help="Generation length when --generate is set. Enough for the marker + short reason.")
    parser.add_argument("--escalate-marker", default="[ESCALATE]", help="Token that counts as escalation.")
    parser.add_argument("--proceed-marker", default="[PROCEED]", help="Token that counts as proceed.")
    args = parser.parse_args()

    # Heavy imports deferred so --help works without torch installed.
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dataset_path = Path(args.dataset)
    records = load_dataset(dataset_path)
    if args.max_examples is not None:
        records = records[: args.max_examples]

    dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}[args.dtype]

    print(f"Loading {args.model} ({args.dtype}) on {args.device} ...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device)
    model.eval()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    sample_prompt = build_prompt(tokenizer, records[0]["system"], records[0]["user"], args.enable_thinking)
    print("Sample rendered prompt (example 0):")
    print("-" * 72)
    print(sample_prompt)
    print("-" * 72)

    acts: list[np.ndarray] = []
    labels: list[int] = []
    ids: list[str] = []
    groups: list[str] = []
    behaviour: list[str] = []
    generated: list[str] = []

    for i, r in enumerate(records):
        prompt = build_prompt(tokenizer, r["system"], r["user"], args.enable_thinking)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            out = model(**inputs, output_hidden_states=True, use_cache=False)

        # hidden_states: tuple of (num_layers + 1) tensors, each [1, seq_len, hidden].
        # Take the final-token vector from every layer and stack to [L, hidden].
        last_token_per_layer = [hs[0, -1, :].float().cpu().numpy() for hs in out.hidden_states]
        acts.append(np.stack(last_token_per_layer, axis=0))

        labels.append(int(r["label"]))
        ids.append(r["id"])
        groups.append(r["group"])

        action = ""
        if args.generate:
            # Generate the model's actual response so we can grade behaviour. Same
            # prompt as the activation above, so recognition and behaviour come from
            # the same computation. (The prefill is recomputed here — negligible for
            # short prompts, and keeps the activation pass clean.)
            with torch.no_grad():
                gen = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,  # greedy: deterministic and reproducible
                    pad_token_id=tokenizer.pad_token_id,
                )
            new_tokens = gen[0][inputs["input_ids"].shape[1]:]
            gen_text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            action = parse_action(gen_text, args.escalate_marker, args.proceed_marker)
            behaviour.append(action)
            generated.append(gen_text)

        suffix = f"  act={action:>8}" if args.generate else ""
        print(f"[{i + 1}/{len(records)}] {r['id']}  gt={r['label_name']:>8}{suffix}  seq_len={inputs['input_ids'].shape[1]}")

    activations = np.stack(acts, axis=0).astype(np.float32)  # [N, L, D]
    num_layers = activations.shape[1] - 1  # minus the embedding layer at index 0
    hidden_dim = activations.shape[2]

    meta = {
        "model": args.model,
        "dtype": args.dtype,
        "enable_thinking": args.enable_thinking,
        "num_examples": len(records),
        "num_hidden_state_indices": activations.shape[1],
        "num_transformer_layers": num_layers,
        "hidden_dim": hidden_dim,
        "dataset_path": str(dataset_path),
        "token_position": "final prompt token (pre-generation), add_generation_prompt=True",
        "hidden_state_index_note": "index 0 = embeddings; index i>0 = output of transformer block i",
        "generate": args.generate,
        "max_new_tokens": args.max_new_tokens if args.generate else None,
        "markers": [args.escalate_marker, args.proceed_marker] if args.generate else None,
        "sample_prompt": sample_prompt,
    }

    save_kwargs = dict(
        activations=activations,
        labels=np.array(labels, dtype=np.int8),
        ids=np.array(ids),
        groups=np.array(groups),
        meta=json.dumps(meta),
    )
    if args.generate:
        save_kwargs["behaviour"] = np.array(behaviour)
        save_kwargs["generated_text"] = np.array(generated)
    np.savez(args.out, **save_kwargs)

    n_pos = int(np.sum(labels))
    print(f"\nSaved {args.out}")
    print(f"  activations: {activations.shape}  (N, num_layers+1, hidden_dim)")
    print(f"  layers: {num_layers} transformer blocks + 1 embedding index")
    print(f"  labels: {n_pos} escalate / {len(labels) - n_pos} proceed")
    if args.generate:
        n_esc = behaviour.count("escalate")
        n_pro = behaviour.count("proceed")
        n_unclear = behaviour.count("unclear")
        beh_correct = sum(
            (b == "escalate" and lab == 1) or (b == "proceed" and lab == 0)
            for b, lab in zip(behaviour, labels)
        )
        print(f"  behaviour: {n_esc} escalate / {n_pro} proceed / {n_unclear} unclear")
        print(f"  behavioural accuracy vs ground truth: {beh_correct / len(labels):.3f}")
    print(f"\nNext: python train_probe.py --activations {args.out}")


if __name__ == "__main__":
    main()
