"""Drill into one ladder-screen candidate: per-item compound answers across the 3
paraphrases, flagging disagreements and wrong-direction answers, and dumping the
model's actual completion for misfires. Usage: python inspect_ladder_detail.py <candidate>
"""
import glob
import sys
from inspect_ai.log import read_eval_log
from markers import classify

cand = sys.argv[1]
K = 3

# newest log per dataset file
logs = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    logs[dp.split("/")[-1]] = p


def load(fname):
    out = {}
    for s in read_eval_log(logs[fname]).samples:
        out[str(s.id)] = (classify(s.output.completion or "", "YES", "NO"),
                          (s.output.completion or "").replace("\n", " ")[:120])
    return out


# expected compound answer per cell: hit=YES, else NO
EXPECT = {"hit": "YES", "near": "NO", "form": "NO", "none": "NO"}
paras = [load(f"ladder_screen_{cand}_compound_p{k}.json") for k in range(1, K + 1)]
ids = sorted(paras[0].keys())

print(f"=== {cand}: compound answers per item (p1 p2 p3) ===")
for cell in ("hit", "near", "form"):
    cids = [i for i in ids if i.split("_")[-2] == cell]
    print(f"\n-- {cell} (expect {EXPECT[cell]}) --")
    for i in cids:
        ans = [paras[k][i][0] for k in range(K)]
        wrong = sum(a != EXPECT[cell] for a in ans)
        disagree = len(set(ans)) > 1
        mark = "  " if (wrong == 0 and not disagree) else ("!!" if wrong >= 2 else " ?")
        print(f"{mark} {i}: {ans}" + ("  <-inconsistent" if disagree else "")
              + ("  <-WRONG" if wrong >= 2 else ""))
        if wrong >= 1:  # show one offending completion
            for k in range(K):
                if paras[k][i][0] != EXPECT[cell]:
                    print(f"      p{k+1}[{paras[k][i][0]}]: {paras[k][i][1]}")
                    break
