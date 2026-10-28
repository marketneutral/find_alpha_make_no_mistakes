"""Run 3's final alpha by hand in pandas (the Appendix A slide), checked cell by cell against qex. Run from the repo root:

    git -C ~/dev/alpha_lab archive run3 | tar -x -C /tmp/run3lab        # the lab as run 3 had it: eval.py, qex 0.3.1
    ln -s ~/dev/alpha_lab/data_20260811_pre_mcapfix /tmp/run3lab/data   # and its data
    ALPHA_LAB=/tmp/run3lab uv run --project /tmp/run3lab python figures/run3/pandas_twin.py

SLIDE is the code exactly as the slide shows it; it runs with read_parquet handing it the frames eval.py loads
(close, member: 1 in the universe or NaN, sector: the sector on member days or NaN), and its alpha is compared
with qex's evaluation of the final alpha.qex over the validation period.
"""
import os, subprocess, sys
import numpy as np
import pandas as pd

SLIDE = """\
import numpy as np
import pandas as pd
close  = pd.read_parquet('close.parquet')
member = pd.read_parquet('member.parquet')
sector = pd.read_parquet('sector.parquet')

def group_demean(x, g):
    s = pd.DataFrame({'x': x.stack(), 'g': g.stack()})
    s = s.dropna(subset=['g'])
    day = s.index.get_level_values(0)
    s['x'] -= s.groupby([day, 'g'])['x'].transform('mean')
    return s['x'].unstack().reindex_like(x)

def decay_linear(x, n):
    w = np.arange(1, n + 1) / (n * (n + 1) / 2)
    return sum(w[k] * x.shift(n - 1 - k) for k in range(n))

r1    = close.pct_change(1)
mr    = r1 * member
mk    = mr * 0 + mr.mean(axis=1).to_numpy()[:, None]
m1    = mk.rolling(252, min_periods=20).sum()
s21   = mk.rolling(21, min_periods=20).std()
s252  = mk.rolling(252, min_periods=20).std()
calm  = (10 * m1 + 1).clip(-1, 1)
w     = (10 * m1).clip(-1, 1).where(s21 > s252, calm)
cov   = r1.rolling(504, min_periods=20).cov(mk)
b     = cov / mk.rolling(504, min_periods=20).var()
rr    = r1 - b * mk
mom   = rr.rolling(231, min_periods=20).sum().shift(21)
score = group_demean(mom, sector)
rev   = group_demean(close.pct_change(21), sector)
a     = decay_linear(w * score, 10) - rev
alpha = decay_linear(a ** 3, 3)
"""

LAB = os.environ.get("ALPHA_LAB", os.path.expanduser("~/dev/alpha_lab"))
sys.path.insert(0, LAB); os.chdir(LAB)
import eval as ev
from qex import qex

d = ev.load(ev.WARMUP, ev.VAL_END)
expr = subprocess.check_output(["git", "-C", os.path.expanduser("~/dev/alpha_lab"), "show", "b89945f:alpha.qex"], text=True)
q = qex(" ".join(expr.split())).evaluate(d).loc[ev.VAL_START:]
frames = {"close.parquet": d["close"], "member.parquet": d["member"], "sector.parquet": d["sector"]}
real = pd.read_parquet
pd.read_parquet = lambda path, *a, **k: frames[path]
ns = {}
exec(SLIDE, ns)
pd.read_parquet = real
p = ns["alpha"].loc[ev.VAL_START:]
both = q.notna() & p.notna()
print(f"{q.size:,} cells; NaN pattern differs in {int((q.notna() ^ p.notna()).sum().sum()):,}; "
      f"max |qex - pandas| {float((q - p).abs()[both].max().max()):.2g} (median |alpha| {float(q.abs()[both].stack().median()):.2g})")
