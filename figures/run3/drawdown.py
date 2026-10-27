"""The final book's 2026 drawdown on run 3's setup: dates, depth, and the long and short sides' share of it."""
import hashlib, os, subprocess, sys
import numpy as np, pandas as pd
LAB = os.environ["ALPHA_LAB"]; sys.path.insert(0, LAB)
import eval as ev
CACHE = os.environ["CACHE"]
expr = " ".join(subprocess.check_output(["git", "-C", os.path.expanduser("~/dev/alpha_lab"), "show", "b89945f:alpha.qex"], text=True).split())
w = pd.read_parquet(f"{CACHE}/{hashlib.md5(('book:' + expr).encode()).hexdigest()[:12]}.parquet")
close = pd.read_parquet(f"{LAB}/data/close.parquet", columns=list(w.columns)).loc[w.index[0]:]
fwd = close.pct_change(fill_method=None).shift(-1).loc[w.index]
pnl = (w * fwd).sum(axis=1)
c = pnl.loc["2026"].cumsum(); peak = c.idxmax(); trough = c.loc[peak:].idxmin()
seg = slice(peak + pd.Timedelta(days=1), trough)
contrib = (w * fwd).loc[seg]
longs = contrib.where(w.loc[seg] > 0).sum().sum(); shorts = contrib.where(w.loc[seg] < 0).sum().sum()
by_name = contrib.sum().sort_values()
held = (w.loc["2018":] != 0).sum(axis=1)
print(f"peak {peak.date()} trough {trough.date()} drawdown {c.loc[trough] - c.loc[peak]:+.3f}; longs {longs:+.3f} shorts {shorts:+.3f}")
print("worst names:", by_name.head(3).round(3).to_dict(), "| last day", w.index[-1].date(), "recovered:", pnl.loc[trough:].sum() + c.loc[trough] - c.loc[peak] >= 0)
print(f"names held, test: {held.min()} to {held.max()}, median {int(held.median())}; effective n {(1 / (w.loc['2018':] ** 2).sum(axis=1)).mean():.0f}")
