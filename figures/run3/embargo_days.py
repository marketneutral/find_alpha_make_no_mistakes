"""The 504 days the embargo trims (21 at each end of the 12 blocks): the same days on every deal, never scored.
How did the seed and the final book do on them, against the 3,020 days that were scored?"""
import os, subprocess, sys
import numpy as np
LAB = os.environ["ALPHA_LAB"]; sys.path.insert(0, LAB); os.chdir(LAB)
import eval as ev
data = ev.load(ev.WARMUP, ev.VAL_END)
for name, commit in {"seed": "318c23d", "final": "b89945f"}.items():
    expr = " ".join(subprocess.check_output(["git", "-C", os.path.expanduser("~/dev/alpha_lab"), "show", f"{commit}:alpha.qex"], text=True).split())
    pnl, to, br = ev.book(expr, data, ev.VAL_START)
    kept = np.zeros(len(pnl), bool)
    for b in np.array_split(np.arange(len(pnl)), ev.BLOCKS):
        kept[b[ev.EMBARGO:-ev.EMBARGO]] = True
    for lab, m in (("scored", kept), ("trimmed", ~kept)):
        p, t = pnl[m], to[m]
        print(f"{name:5s} {lab:7s} {m.sum():4d} days: Sharpe {ev.sharpe(p):5.2f}  return/yr {p.mean() * 252:+6.1%}  fitness {ev.fitness(p, t):5.2f}")
