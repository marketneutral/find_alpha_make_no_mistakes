"""Path dependence, measured: a⁵ on the book the agent tried it on (trial 33's, giving trial 35) and on the final book.
Each book is scored exactly, as the mean over all 10,395 deals of its median and worst fold utility (the average one
eval.py call estimates from 50), so the comparison carries no deal noise. Run from this directory, as analysis.py:

    ALPHA_LAB=/tmp/run3lab uv run --project /tmp/run3lab python a5_counterfactual.py

Writes lab/a5_counterfactual.json for figures.py (the tree). Validation only, 2004-2017.
"""
import json
import itertools, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.environ.get("ALPHA_LAB", os.path.expanduser("~/dev/alpha_lab")); sys.path.insert(0, LAB); os.chdir(LAB)
import eval as ev
from qex import SignalGraph, qex
def deals(items):
    if not items: yield []; return
    a, rest = items[0], items[1:]
    for i, b in enumerate(rest):
        for d in deals(rest[:i] + rest[i + 1:]): yield [(a, b)] + d
ALL = list(deals(list(range(ev.BLOCKS))))
data = ev.load(ev.WARMUP, ev.VAL_END)
git = lambda c: " ".join(subprocess.check_output(["git", "-C", os.path.expanduser("~/dev/alpha_lab"), "show", f"{c}:alpha.qex"], text=True).split())
final = git("b89945f")
BOOKS = {"T33 (best before T35)": git("d466e9b"), "T35 (a^5 on T33)": git("326d478"),
         "final": final, "final with a^5": final.replace("power(a, 3)", "power(a, 5)")}
assert "power(a, 5)" in BOOKS["final with a^5"]
out = {}
for name, expr in BOOKS.items():
    g = SignalGraph(); g.add_signal(qex(expr), name="a"); nodes = g.stats()["total_nodes"]
    pnl, to, br = ev.book(expr, data, ev.VAL_START)
    blocks = [b[ev.EMBARGO:-ev.EMBARGO] for b in np.array_split(np.arange(len(pnl)), ev.BLOCKS)]
    pair = {}
    for i, j in itertools.combinations(range(ev.BLOCKS), 2):
        ix = np.concatenate([blocks[i], blocks[j]])
        pair[(i, j)] = ev.fold_utility(pnl.iloc[ix], to.iloc[ix], br.iloc[ix], nodes)
    u = np.array([[pair[p] for p in d] for d in ALL])
    m = ev.margin_bps(pnl, to); t = to.mean()
    out[name] = dict(nodes=nodes, utility=round(float(np.median(u, axis=1).mean()), 4), worst=round(float(u.min(axis=1).mean()), 4),
                     margin=round(float(m), 1), turnover=round(float(t), 4))
    print(f"{name:24s} nodes {nodes:3d}  exact utility {np.median(u,axis=1).mean():.3f}  exact worst {u.min(axis=1).mean():.3f}  "
          f"margin {m:.1f} bps  turnover {t:.3f}  eligible {0.01 <= t <= 0.70 and m >= 5}")
json.dump(out, open(os.path.join(HERE, "lab", "a5_counterfactual.json"), "w"), indent=1)
