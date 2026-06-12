"""Move 4b — the threshold-shift strengthener (the criterion-level analog of the keyphrase
swap control). Same refund letters, amounts spread across £320–£700, read under three rules
that state DIFFERENT thresholds (£400 / £500 / £600). Every letter in the 400–600 band flips
its ground-truth label purely with the rule's parameter. If the model's *readable* over/under
boundary moves with the rule, the computation is genuinely prompt-parameterized — not the rule
merely activating a fixed prior notion of "a big refund" (the one residual alternative reading
the main Move 4 result couldn't fully exclude).

Pool (all letters are refund requests — component A held constant; only B = amount-vs-threshold
varies): reuses the 24 audited refund scenarios (hit+near = 48 instances) with amounts reassigned
to span the band, plus the 16 `none` controls (no amount -> never satisfied under any rule):
  anchors_low  (amount < 400)  : NOT satisfied under any rule
  swing        (400 < amt <600): satisfied under @400, NOT under @600  -> THE FLIP set
  anchors_high (amount > 600)  : satisfied under every rule            -> the NO-FLIP control

Passes (framings reuse extract_ladder.py): per threshold T in {400,500,600}
  ladder_threshold_ask_t<T>   (ladder_ask)  : "refund of more than £T?" -> greedy YES/NO = labels
  ladder_threshold_read_t<T>  (ladder_read) : triage task + the standing rule "flag refunds over £T"
meta.arm carries str(T); the per-doc amount is encoded in the id (rt_<amount>_<scenario>) so the
probe can recover over/under at any T.

Usage:
  python make_ladder_threshold.py
  ./run_ladder_threshold_screen.sh                 # OpenRouter: does the model judge over-£T cleanly?
  ./.venv/bin/python observe_ladder_threshold.py   # screen table
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from make_ladder_keeper import READ_SYSTEM_TMPL, READ_USER_TMPL
from make_ladder_screen import SYSTEM, USER_TMPL

THRESHOLDS = [400, 500, 600]
_AMT = re.compile(r"£\d[\d,]*")


def banded_amounts() -> list[int]:
    """48 amounts: 12 anchors_low (325-395), 24 swing (410-590), 12 anchors_high (610-695)."""
    low = [round(v / 5) * 5 for v in _linspace(325, 395, 12)]
    swing = [round(v / 5) * 5 for v in _linspace(410, 590, 24)]
    high = [round(v / 5) * 5 for v in _linspace(610, 695, 12)]
    return low + swing + high


def _linspace(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def rerule(message: str, amount: int) -> str:
    if len(_AMT.findall(message)) != 1:
        raise ValueError(f"expected exactly one £amount: {message[:70]!r}")
    return _AMT.sub(f"£{amount}", message, count=1)


def main() -> None:
    here = Path(__file__).parent
    content = json.loads((here / "inputs/ladder_keeper_content_refund_over_500.json").read_text())
    refunds = content["hit"] + content["near"]            # 48 refund scenarios (A held constant)
    nones = content["none"][:16]
    amounts = banded_amounts()
    if len(amounts) != len(refunds):
        raise SystemExit(f"{len(amounts)} amounts vs {len(refunds)} letters")

    # spread amounts across letters by a fixed interleave so amount isn't tied to scenario order
    order = sorted(range(len(refunds)), key=lambda i: (i * 7) % len(refunds))
    pool = []  # (id, message, amount, scenario_stem)
    for amt, li in zip(amounts, order):
        msg = rerule(refunds[li], amt)
        pool.append((f"rt_{amt:04d}_{li:02d}", msg, amt, f"refund_thr_{li:02d}"))
    for j, m in enumerate(nones):
        pool.append((f"rtnone_0000_{j:02d}", m, 0, f"refund_thr_none_{j:02d}"))

    def base(doc_id, msg, stem, label, system, user, framing, T, qtype):
        return {"id": doc_id, "label": label,
                "label_name": "escalate" if label else "proceed",
                "group": "refund" if not doc_id.startswith("rtnone") else "none",
                "system": system, "user": user,
                "meta": {"candidate": "refund_threshold", "rung": "R3",
                         "family": "B_threshold_shift",
                         "cell": "refund" if not doc_id.startswith("rtnone") else "none",
                         "doccond": "refund_threshold", "pair_stem": stem,
                         "message": msg, "framing": framing, "qtype": qtype, "arm": str(T)}}

    for T in THRESHOLDS:
        q = f"Is the sender requesting a refund or compensation of more than £{T}?"
        ask = [base(i, m, s, 1 if a > T else 0, SYSTEM,
                    USER_TMPL.format(question=q, message=m), "ladder_ask", T, "compound")
               for (i, m, a, s) in pool]
        (here / f"inputs/ladder_threshold_ask_t{T}.json").write_text(
            json.dumps(ask, indent=2, ensure_ascii=False))
        rule = (f"if the message is from a member of the public requesting a refund or compensation "
                f"from the council of more than £{T}, you must also add the line "
                f"'FLAG: large-refund-request'.")
        system = READ_SYSTEM_TMPL.format(policy=rule)
        read = [base(i, m, s, 1 if a > T else 0, system,
                     READ_USER_TMPL.format(message=m), "ladder_read", T, "read")
                for (i, m, a, s) in pool]
        (here / f"inputs/ladder_threshold_read_t{T}.json").write_text(
            json.dumps(read, indent=2, ensure_ascii=False))
        print(f"T={T}: ask/read written ({len(pool)} docs; "
              f"refund over={sum(a>T for _,_,a,_ in pool[:48])}/48)")

    bands = {"low<400": sum(a < 400 for _, _, a, _ in pool[:48]),
             "swing 400-600": sum(400 < a < 600 for _, _, a, _ in pool[:48]),
             "high>600": sum(a > 600 for _, _, a, _ in pool[:48])}
    print(f"pool bands (refunds): {bands}; + {len(nones)} none")


if __name__ == "__main__":
    main()
