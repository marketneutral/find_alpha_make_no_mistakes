"""The cube as the agent met it: trial 17's book with only its final power changed, on validation only. Run from
this directory, as analysis.py:

    ALPHA_LAB=/tmp/run3lab uv run --project /tmp/run3lab python cube_t17.py

Trial 17 (commit 2f933c3) replaced a·|a| with a³ on the best book kept so far (trial 16's). This rebuilds that book
with linear a, a·|a| and a³ using run 3's evaluator book (delay 1, members only, gross one, 5% cap) and writes
lab/cube_t17.json for figures.py: each variant's share of the book in the 10% most extreme stocks (5% each side, on
the signal the book traded), and its cost-free return a year and Sharpe over 2004-2017. Nothing after 2017 is used.
"""
import json, os, subprocess, sys, warnings
import numpy as np, pandas as pd
warnings.simplefilter("ignore")
LAB = os.environ.get("ALPHA_LAB", os.path.expanduser("~/dev/alpha_lab"))
sys.path.insert(0, LAB)
import eval as ev
from qex import qex, compute_context, delay, close, field

GIT = os.path.expanduser("~/dev/alpha_lab")
T17 = " ".join(subprocess.check_output(["git", "-C", GIT, "show", "2f933c3:alpha.qex"], text=True).split())
FINAL = "in decay_linear(power(a, 3), 3)"
assert FINAL in T17
VARIANTS = {"a": "in decay_linear(a, 3)", "a·|a|": "in decay_linear(a * abs(a), 3)", "a³": FINAL}

data = ev.load(ev.WARMUP, ev.VAL_END)                                       # exactly what eval.py loads
def book(expr):
    """run 3's eval.book, returning the weights"""
    with compute_context():
        raw = delay(qex(expr) + 0 * close() + 0 * field("member"), 1).evaluate(data)
    raw = raw.where(data["close"].notna())
    return ev.to_book(raw.loc[ev.VAL_START:])
fwd = data["close"].pct_change(fill_method=None).shift(-1).loc["2004":"2017"]
member = data["member"].loc["2004":"2017"].notna()
with compute_context():
    sig = qex(T17.replace(FINAL, "in a")).evaluate(data)
rk = sig.shift(1).loc["2004":"2017"].where(member).rank(axis=1, pct=True)        # the signal the book traded (delay 1)
ends = (rk <= 0.05) | (rk > 0.95)
out = {}
for lab, tail in VARIANTS.items():
    w = book(T17.replace(FINAL, tail)).loc["2004":"2017"]
    p = (w * fwd.loc[w.index]).sum(axis=1)
    share = (w.reindex(columns=rk.columns).abs().where(ends).sum(axis=1) / w.abs().sum(axis=1)).mean()
    out[lab] = dict(tails=round(float(share), 3), ret=round(float(p.mean() * 252), 4), sharpe=round(float(p.mean() / p.std() * np.sqrt(252)), 2))
    print(lab, out[lab])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab", "cube_t17.json"), "w"), ensure_ascii=False, indent=1)
