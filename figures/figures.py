"""Figures drawn for the deck itself (the rest of images/ comes from the blog posts). Run from the repo root:

    uv run --project ~/dev/alpha_lab python figures/figures.py

Writes images/eval-deals.svg (how the evaluator deals 2004-2017 into folds), images/eval-folds.svg (one deal's
six fold scores for the final book, as the agent saw them), images/eval-alldeals.svg and images/eval-noise.svg (every possible
deal, and how much one call's score moves with the number of deals; from figures/partitions.json, written by partitions.py as run 3
saw it) and images/alpha-worth.svg (what each part of the
book is worth: the score change when the agent removed it). Every number is from the run's notebook
(results.tsv) or the evaluator's output for the final trial; nothing here is recomputed.
"""
import itertools, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

BG, INK, INK2, MUTED, RULE, PANEL = "#0a0e1a", "#e8eaf0", "#c0c4cf", "#6b7280", "#2a3344", "#131927"
ACC, RED = "#3ee87a", "#ff6b4a"
plt.rcParams.update({
    "svg.fonttype": "none", "font.family": "monospace", "font.monospace": ["IBM Plex Mono", "DejaVu Sans Mono"],
    "font.size": 14, "text.color": INK2, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "axes.edgecolor": RULE,
})

def save(fig, name):
    fig.savefig(f"images/{name}.svg", bbox_inches="tight", pad_inches=0.2)
    plt.close(fig); print("wrote", f"images/{name}.svg")

# The validation period's 3,524 trading days cut into 12 blocks (np.array_split), 21 days purged from each end:
# first and last kept day of each block, as fractional years, from the lab's trading calendar.
KEPT = [(2004.09, 2005.09), (2005.26, 2006.25), (2006.43, 2007.43), (2007.60, 2008.59), (2008.76, 2009.75),
        (2009.92, 2010.92), (2011.09, 2012.09), (2012.26, 2013.27), (2013.43, 2014.43), (2014.60, 2015.59),
        (2015.76, 2016.75), (2016.92, 2017.91)]
EDGES = np.linspace(2004.0, 2018.0, 13)                                           # block edges, ~14 months apart
# deal 1 is the deal the agent saw for the final book (T54): its six folds' years, recovered from the printed
# year spans and confirmed by re-scoring, are blocks {5,12} {4,7} {1,3} {6,11} {2,10} {8,9} (1-based)
DEAL1 = {4: 1, 11: 1, 3: 2, 6: 2, 0: 3, 2: 3, 5: 4, 10: 4, 1: 5, 9: 5, 7: 6, 8: 6}

def deal(rng):
    order = rng.permutation(12)
    return {int(b): k + 1 for k in range(6) for b in order[k::6]}

def fig_deals():
    rng = np.random.default_rng(7)
    rows = [("12 blocks", None), ("deal 1", DEAL1), ("deal 2", deal(rng)), ("deal 3", deal(rng))]
    fig, ax = plt.subplots(figsize=(11.0, 4.9))
    h, gap = 0.62, 1.0
    for r, (name, d) in enumerate(rows):
        y = -r * gap - (0.35 if r else 0)
        ax.text(2003.75, y, name, ha="right", va="center", color=INK if r == 0 else INK2, fontsize=15)
        for b in range(12):
            x0, x1 = EDGES[b], EDGES[b + 1]
            k0, k1 = KEPT[b]
            hot = d is not None and d[b] == 1
            face = ACC if hot else PANEL
            ax.add_patch(FancyBboxPatch((k0, y - h / 2), k1 - k0, h, boxstyle="round,pad=0,rounding_size=0.06",
                                        fc=face, ec=ACC if hot else RULE, lw=1.0))
            for e0, e1 in ((x0, k0), (k1, x1)):                                    # the purged embargo at each edge
                ax.add_patch(Rectangle((e0 + 0.01, y - h / 2), e1 - e0 - 0.02, h, fc="none", ec="#46516a", lw=0, hatch="////"))
            label = f"B{b + 1}" if d is None else str(d[b])
            ax.text((k0 + k1) / 2, y, label, ha="center", va="center", fontsize=15 if d else 11,
                    color=BG if hot else (MUTED if d is None else INK), fontweight="bold" if hot else "normal")
    ax.text(2011.0, -3 * gap - 0.35 - 0.78, "… and 47 more: 50 fresh deals on every call", ha="center", va="center", color=MUTED, fontsize=14.5)
    # annotations
    ax.annotate("21-day embargo at every block edge", xy=(EDGES[3] + 0.04, h / 2), xytext=(EDGES[3] - 0.2, 0.95),
                color=MUTED, fontsize=13.5, ha="left", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.text(2011.0, -0.62, "each block about 14 months; each fold two blocks, scored on its own", ha="center", va="center", color=MUTED, fontsize=13.5)
    ax.text(2018.15, -1 * gap - 0.35, "fold 1: blocks 5 and 12", va="center", color=ACC, fontsize=14)
    ax.text(2018.15, -2 * gap - 0.35, "fold 1 moves", va="center", color=MUTED, fontsize=14)
    ax.text(2018.15, -3 * gap - 0.35, "every deal", va="center", color=MUTED, fontsize=14)
    for yr in range(2004, 2019, 2):
        ax.text(yr, 1.45, str(yr), ha="center", va="bottom", color=MUTED, fontsize=13.5)
        ax.plot([yr, yr], [1.38, 1.3], color=RULE, lw=1)
    ax.set_xlim(2002.3, 2020.6); ax.set_ylim(-4.45, 1.85)
    ax.axis("off")
    save(fig, "eval-deals")

def fig_folds():
    # the final book's deal 1, as the evaluator printed it for T54
    folds = [(1, "2008–09 + 2016–17", 0.782), (2, "2007–08 + 2011–12", 3.150), (3, "2004–05 + 2006–07", 0.197),
             (4, "2009–10 + 2015–16", 2.045), (5, "2005–06 + 2014–15", 2.144), (6, "2012–13 + 2013–14", 1.044)]
    u = np.array([f[2] for f in folds]); med, worst = np.median(u), u.min()
    fig, ax = plt.subplots(figsize=(11.0, 4.9))
    y = np.arange(len(folds))[::-1]
    for yi, (k, yrs, v) in zip(y, folds):
        c = RED if v == worst else (ACC if k == 1 else "#4b5563")
        ax.barh(yi, v, height=0.62, color=c, zorder=2)
        ax.text(-0.06, yi, f"fold {k} · {yrs}", ha="right", va="center", color=INK2, fontsize=14.5)
        ax.text(v + 0.05, yi, f"{v:.2f}" + ("  worst" if v == worst else ""), ha="left", va="center", color=RED if v == worst else INK2, fontsize=14.5)
    ax.plot([med, med], [-0.6, y[0] + 0.5], color=INK, lw=1.4, ls=(0, (4, 3)), zorder=3)
    ax.text(med, y[0] + 0.62, f"median {med:.2f}", ha="center", va="bottom", color=INK, fontsize=14.5)
    ax.set_xlim(0, 3.75); ax.set_ylim(-0.6, len(folds) - 0.1)
    ax.set_yticks([]); ax.tick_params(length=0)
    ax.set_xlabel("utility of the fold, scored on its own", fontsize=14)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=RULE, alpha=0.5, lw=0.6, zorder=0)
    save(fig, "eval-folds")

def all_deals(items):
    if not items:
        yield []; return
    for i, b in enumerate(items[1:]):
        for d in all_deals(items[1:i + 1] + items[i + 2:]):
            yield [(items[0], b)] + d

def fig_noise():
    P = json.load(open("figures/partitions.json"))
    f = P["final"]; pair = {tuple(map(int, k.split(","))): v for k, v in f["pairs"].items()}
    med = np.array([np.median([pair[p] for p in d]) for d in all_deals(list(range(12)))])
    # every possible deal: the final book's median fold on each
    fig, ax = plt.subplots(figsize=(10.0, 5.6))
    ax.hist(med, bins=40, color="#4b5563", zorder=2)
    ax.axvline(f["exact_median"], color=ACC, lw=2.2, zorder=3)
    top = ax.get_ylim()[1]
    ax.text(f["exact_median"] + 0.025, top * 0.97, f"the average over all {len(med):,}: {f['exact_median']:.2f}",
            color=ACC, fontsize=15, va="top")
    ax.text(med.min(), top * 0.97, f"one deal can say\nanything from {med.min():.2f}", color=INK2, fontsize=14, va="top")
    ax.text(med.max(), top * 0.6, f"…to {med.max():.2f}", color=INK2, fontsize=14, ha="right", va="top")
    ax.set_xlabel(f"median-fold utility of the final book, on each of the {len(med):,} possible deals", fontsize=14)
    ax.set_yticks([])
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.tick_params(length=0); ax.grid(axis="x", color=RULE, alpha=0.5, lw=0.6, zorder=0)
    save(fig, "eval-alldeals")
    # what one call reports, minus the exact score: 95% range
    rows = [("seed, 50 deals", P["seed"], "50"), ("final, 1 deal", f, "1"), ("final, 50 deals", f, "50"),
            ("final, 500 deals", f, "500"), (f"final, all {len(med):,}", f, None)]
    lim = 0.13
    fig, ax = plt.subplots(figsize=(10.0, 5.6))
    ax.axvspan(-0.03, 0.03, color=ACC, alpha=0.13, lw=0, zorder=1)
    ax.text(0, len(rows) - 0.4, "±0.03: the keep bar", ha="center", va="bottom", color=ACC, fontsize=14)
    for k, (name, b, n) in enumerate(rows):
        y = len(rows) - 1 - k
        ax.text(-lim - 0.01, y, name, ha="right", va="center", color=INK2, fontsize=15)
        if n is None:
            ax.plot([0], [y], "o", color=ACC, ms=10, zorder=3)
            ax.text(0.01, y, "exact: no noise", va="center", color=ACC, fontsize=14)
            continue
        lo, _, hi, sd = b["calls"][n]["median"]; ex = b["exact_median"]
        lo, hi = lo - ex, hi - ex
        c = INK2 if (hi - lo) / 2 <= 0.03 else RED
        ax.plot([max(lo, -lim), min(hi, lim)], [y, y], color=c, lw=8, solid_capstyle="butt", zorder=2)
        ax.text(min(hi, lim) + 0.007, y, f"±{(hi - lo) / 2:.2f}" + ("  (off the chart)" if hi > lim else ""),
                va="center", color=c, fontsize=14)
    ax.axvline(0, color=RULE, lw=1, zorder=0)
    ax.set_xlim(-lim, lim + 0.07); ax.set_ylim(-0.6, len(rows) - 0.05); ax.set_yticks([])
    ax.set_xlabel("what one call reports, minus the exact score (95% of calls)", fontsize=14)
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.tick_params(length=0); ax.grid(axis="x", color=RULE, alpha=0.5, lw=0.6, zorder=0)
    save(fig, "eval-noise")

def fig_worth():
    # utility change when the agent took a part out, in the book of the day (results.tsv)
    parts = [("residual momentum", "T56", 1.473, 0.592), ("crash switch", "T27", 1.101, 0.622),
             ("1-month reversal sleeve", "T52", 1.376, 0.926), ("skip the last month", "T10", 0.736, 0.582),
             ("3-day outer decay", "T57", 1.473, 1.327), ("vol scaling of the sleeves", "T33", 1.269, 1.320),
             ("beta hedge", "T54", 1.376, 1.473), ("1/vol sizing", "T2", 0.009, 0.320)]
    fig, ax = plt.subplots(figsize=(11.0, 5.2))
    y = np.arange(len(parts))[::-1]
    for yi, (name, t, before, after) in zip(y, parts):
        d = after - before
        c = ACC if d < 0 else MUTED
        ax.barh(yi, d, height=0.62, color=c, zorder=2)
        ax.text(0.04 if d < 0 else -0.04, yi, f"{name}", ha="left" if d < 0 else "right", va="center", color=INK2, fontsize=14.5)
        ax.text(d + (-0.03 if d < 0 else 0.03), yi, f"{d:+.2f}  {t}", ha="right" if d < 0 else "left", va="center",
                color=ACC if d < 0 else INK2, fontsize=14)
    ax.axvline(0, color=RULE, lw=1.2, zorder=3)
    ax.text(-0.5, len(parts) - 0.2, "removing it hurt", ha="center", color=ACC, fontsize=14)
    ax.text(0.5, len(parts) - 0.2, "removing it helped", ha="center", color=MUTED, fontsize=14)
    ax.set_xlim(-1.25, 1.1); ax.set_ylim(-0.6, len(parts) + 0.2)
    ax.set_yticks([]); ax.tick_params(length=0)
    ax.set_xlabel("change in score when the agent took the part out", fontsize=14)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=RULE, alpha=0.5, lw=0.6, zorder=0)
    save(fig, "alpha-worth")

if __name__ == "__main__":
    fig_deals(); fig_folds(); fig_noise(); fig_worth()
