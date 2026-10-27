"""Does the 21-day embargo change the score? The seed and the final book on run 3's setup, every one of the 10,395
deals, with the embargo at 21 days (as run) and at 0. Run from the repo root (see README.md for /tmp/run3lab):

    ALPHA_LAB=/tmp/run3lab uv run --project /tmp/run3lab python figures/run3/embargo.py
"""
import itertools, os, subprocess, sys
import numpy as np
LAB = os.environ["ALPHA_LAB"]; sys.path.insert(0, LAB); os.chdir(LAB)
import eval as ev
from qex import SignalGraph, qex

def deals(items):
    if not items:
        yield []; return
    for i, b in enumerate(items[1:]):
        for d in deals(items[1:i + 1] + items[i + 2:]):
            yield [(items[0], b)] + d

ALL = list(deals(list(range(ev.BLOCKS))))
data = ev.load(ev.WARMUP, ev.VAL_END)
for name, commit in {"seed": "318c23d", "final": "b89945f"}.items():
    expr = " ".join(subprocess.check_output(["git", "-C", os.path.expanduser("~/dev/alpha_lab"), "show", f"{commit}:alpha.qex"], text=True).split())
    g = SignalGraph(); g.add_signal(qex(expr), name="a"); nodes = g.stats()["total_nodes"]
    pnl, to, br = ev.book(expr, data, ev.VAL_START)
    for emb in (21, 0):
        blocks = [b[emb:len(b) - emb] for b in np.array_split(np.arange(len(pnl)), ev.BLOCKS)]
        pair = {}
        for i, j in itertools.combinations(range(ev.BLOCKS), 2):
            ix = np.concatenate([blocks[i], blocks[j]])
            pair[(i, j)] = ev.fold_utility(pnl.iloc[ix], to.iloc[ix], br.iloc[ix], nodes)
        u = np.array([[pair[p] for p in d] for d in ALL])
        med, worst = np.median(u, axis=1), u.min(axis=1)
        days = sum(len(b) for b in blocks)
        print(f"{name:5s} embargo {emb:2d}: {days} days; median {med.mean():.3f} (one deal: sd {med.std():.3f}); worst {worst.mean():.3f} (sd {worst.std():.3f})")
