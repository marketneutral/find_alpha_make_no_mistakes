"""Every way the evaluator can deal the validation period, for the seed and the final book. Run from the repo root:

    git -C ~/dev/alpha_lab archive run3 | tar -x -C /tmp/run3lab        # the lab as run 3 had it: eval.py, qex 0.3.1
    ln -s ~/dev/alpha_lab/data_20260811_pre_mcapfix /tmp/run3lab/data   # and its data
    ALPHA_LAB=/tmp/run3lab uv run --project /tmp/run3lab python figures/partitions.py

A fold is a pair of blocks, so a book's score on any deal is fixed by its utility on each of the 66 possible
pairs. This scores those 66 pairs with the lab's own evaluator (eval.py: the book, the 21-day embargo, the fold
utility) exactly as run 3 saw it, enumerates all 10,395 deals, and simulates what one call of the evaluator
reports with 1, 50 and 500 random deals (its 95% range and standard deviation). Writes figures/partitions.json for figures.py.
"""
import itertools, json, os, subprocess, sys
import numpy as np

LAB = os.environ.get("ALPHA_LAB", os.path.expanduser("~/dev/alpha_lab"))
REPO = os.environ.get("ALPHA_LAB_GIT", os.path.expanduser("~/dev/alpha_lab"))   # where the trial commits live
sys.path.insert(0, LAB); os.chdir(LAB)
import eval as ev
from qex import SignalGraph, qex

BOOKS = {"seed": "318c23d", "final": "b89945f"}                       # commits of alpha.qex in the lab

def deals(items):
    """All ways to split items into unordered pairs."""
    if not items:
        yield []; return
    a, rest = items[0], items[1:]
    for i, b in enumerate(rest):
        for d in deals(rest[:i] + rest[i + 1:]):
            yield [(a, b)] + d

ALL = list(deals(list(range(ev.BLOCKS))))
data = ev.load(ev.WARMUP, ev.VAL_END)
out = {"n_deals": len(ALL)}
for name, commit in BOOKS.items():
    expr = " ".join(subprocess.check_output(["git", "-C", REPO, "show", f"{commit}:alpha.qex"], text=True).split())
    g = SignalGraph(); g.add_signal(qex(expr), name="a"); nodes = g.stats()["total_nodes"]
    pnl, to, br = ev.book(expr, data, ev.VAL_START)
    blocks = [b[ev.EMBARGO:-ev.EMBARGO] for b in np.array_split(np.arange(len(pnl)), ev.BLOCKS)]
    pair = {}
    for i, j in itertools.combinations(range(ev.BLOCKS), 2):
        ix = np.concatenate([blocks[i], blocks[j]])
        pair[(i, j)] = ev.fold_utility(pnl.iloc[ix], to.iloc[ix], br.iloc[ix], nodes)
    u = np.array([[pair[p] for p in d] for d in ALL])                 # 10,395 deals x 6 folds
    med, worst = np.median(u, axis=1), u.min(axis=1)
    rng = np.random.default_rng(0)
    sims = {}
    for n in (1, 50, 500):                                             # what one call reports, 4,000 calls each
        pick = rng.integers(0, len(ALL), size=(4000, n))
        sims[n] = {"median": med[pick].mean(axis=1).tolist(), "worst": worst[pick].mean(axis=1).tolist()}
    if name == "final":                                                # deal 1 as the evaluator printed it for T54
        print("deal 1 folds:", [round(pair[p], 3) for p in [(4, 11), (3, 6), (0, 2), (5, 10), (1, 9), (7, 8)]])
    q = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 50, 97.5])] + [round(float(np.std(x)), 4)]
    out[name] = {"pairs": {f"{i},{j}": round(v, 4) for (i, j), v in pair.items()},
                 "exact_median": round(float(med.mean()), 4), "exact_worst": round(float(worst.mean()), 4),
                 "calls": {n: {"median": q(s["median"]), "worst": q(s["worst"])} for n, s in sims.items()}}   # 2.5%, 50%, 97.5%, sd
    print(f"{name}: exact median {med.mean():.3f}, exact worst {worst.mean():.3f}; one-call spread (sd) of the median:",
          {n: round(float(np.std(s["median"])), 4) for n, s in sims.items()},
          "of the worst:", {n: round(float(np.std(s["worst"])), 4) for n, s in sims.items()})
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "partitions.json"), "w"))
print(len(ALL), "deals")
