"""Figures drawn for the deck itself (the rest of images/ comes from the blog posts). Run from the repo root:

    uv run --project ~/dev/alpha_lab python figures/figures.py

Writes images/eval-deals.svg (how the evaluator deals 2004-2017 into folds), images/eval-folds.svg (one deal's
six fold scores for the final book, as the agent saw them), images/eval-alldeals.svg and images/eval-noise.svg (every possible
deal, and how much one call's score moves with the number of deals; from figures/partitions.json, written by partitions.py as run 3
saw it) and images/alpha-worth.svg (what each part of the
book is worth: the score change when the agent removed it). Every number is from the run's notebook
(results.tsv) or the evaluator's output for the final trial; nothing here is recomputed.
"""
import csv, itertools, json
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

def save(fig, name, pad=0.2):
    fig.savefig(f"images/{name}.svg", bbox_inches="tight", pad_inches=pad)
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

def fig_periods():
    # the three cuts of the data, and what the agent may do with each
    P = [("inspection", 1999.0, 2004.0, PANEL, ACC, "the agent may look:\nprices, explore.py"),
         ("validation", 2004.0, 2018.0, ACC, BG, "scored by eval.py only:\nthe agent sees summary numbers"),
         ("test", 2018.0, 2026.61, PANEL, INK2, "sealed: not loaded by eval.py;\nrun once, by me, after trial 60")]
    fig, ax = plt.subplots(figsize=(11.0, 2.0))
    for name, a, b, face, ink, note in P:
        ax.add_patch(FancyBboxPatch((a + 0.04, 0), b - a - 0.08, 1, boxstyle="round,pad=0,rounding_size=0.12",
                                    fc=face, ec=ACC if name != "test" else MUTED, lw=1.2,
                                    hatch="////" if name == "test" else None))
        ax.text((a + b) / 2, 0.5, name, ha="center", va="center", color=ink, fontsize=13 if name == "inspection" else 17, fontweight="bold",
                bbox=dict(fc=PANEL, ec="none", pad=3) if name == "test" else None)
    for yr, lab in ((1999, "1999"), (2004, "2004"), (2018, "2018"), (2026.61, "Aug 2026")):
        ax.text(yr, 1.18, lab, ha="center", va="bottom", color=MUTED, fontsize=13)
        ax.plot([yr, yr], [1.04, 1.14], color=RULE, lw=1.2)
    ax.set_xlim(1998.3, 2027.3); ax.set_ylim(-0.1, 1.6); ax.axis("off")
    save(fig, "alpha-periods")

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
    ax.set_xlabel("score of the fold, on its own days", fontsize=14)
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
    ax.set_xlabel(f"median-fold score of the final book, on each of the {len(med):,} possible deals", fontsize=14)
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

BAR, FLOOR = 0.03, -0.13                                                            # the keep rule's two numbers

def keep_replay():
    """Every trial's change in median-fold and worst-fold utility against the best book kept so far (results.tsv)."""
    rows = list(csv.DictReader(open("figures/progress/lab/results.tsv"), delimiter="\t"))
    bu, bw = float(rows[0]["utility"]), float(rows[0]["worst"])
    pts = []
    for i, r in enumerate(rows[1:], 1):
        u, w = float(r["utility"]), float(r["worst"])
        pts.append((i, r["status"] == "keep", u - bu, w - bw))
        if r["status"] == "keep":
            bu, bw = u, w
    return pts

def keep_map(ax, xlim, ylim, fs, long=True):
    """The keep rule as a region: median up by more than the bar, worst down by no more than the floor."""
    ax.add_patch(Rectangle((BAR, FLOOR), xlim[1] - BAR, ylim[1] - FLOOR, fc=ACC, alpha=0.12, lw=0, zorder=0))
    ax.axhline(0, color=RULE, lw=0.8, zorder=1); ax.axvline(0, color=RULE, lw=0.8, zorder=1)
    ax.axvline(BAR, color=ACC, lw=1.4, ls=(0, (4, 3)), zorder=2); ax.axhline(FLOOR, color=RED, lw=1.4, ls=(0, (4, 3)), zorder=2)
    if long:
        ax.text(BAR + 0.008, ylim[1] - 0.02, "the bar: +0.03,\nthe seed's noise", color=ACC, fontsize=fs, va="top")
        ax.text(xlim[0] + 0.012, FLOOR - 0.025, "the floor: \u22120.13, the worst fold's noise", color=RED, fontsize=fs, va="top")
    else:
        ax.text(BAR + 0.008, ylim[0] + 0.03, "the bar: +0.03", color=ACC, fontsize=fs, va="bottom")
        ax.text(xlim[1] - 0.01, FLOOR - 0.025, "the floor: \u22120.13", color=RED, fontsize=fs, va="top", ha="right")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_xlabel("\u0394 median-fold score vs the best book so far", fontsize=fs + 1)
    ax.set_ylabel("\u0394 worst-fold score vs the best", fontsize=fs + 1)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.tick_params(length=0, labelsize=fs); ax.grid(False)

def fig_keep():
    xlim, ylim = (-0.62, 0.36), (-0.6, 0.66)
    # the empty map: the rule itself
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    keep_map(ax, xlim, ylim, 14.5)
    ax.text(0.2, 0.3, "keep", color=ACC, fontsize=26, fontweight="bold", ha="center", va="center")
    ax.text(-0.3, 0.1, "reset:\nno gain beyond\nthe noise", color=INK2, fontsize=16, ha="center", va="center", linespacing=1.35)
    ax.text(-0.3, -0.4, "reset:\nbroke the floor", color=RED, fontsize=16, ha="center", va="center", linespacing=1.35)
    ax.text(-0.3, 0.48, "safer, but not kept", color=MUTED, fontsize=15, ha="center", va="center", style="italic")
    save(fig, "eval-keep-map", pad=0.35)
    # the same map with the sixty trials on it
    pts = keep_replay()
    fig, ax = plt.subplots(figsize=(10.4, 5.6))
    keep_map(ax, xlim, ylim, 12.5, long=False)
    for i, kept, dx, dy in pts:
        cx, cy = max(dx, xlim[0] + 0.012), dy
        if kept:
            ax.scatter([cx], [cy], s=64, color=ACC, edgecolor=BG, lw=1.2, zorder=4)
        else:
            ax.scatter([cx], [cy], s=30, color=MUTED, alpha=0.8, lw=0, zorder=3, marker="<" if dx < xlim[0] else "o")
    labels = {1: ("T1", 8, 0, "left"), 2: ("T2", 8, 0, "left"), 31: ("T31", 8, 0, "left"),
              19: ("T19", -7, 9, "right"), 32: ("T32", -7, -4, "right"),
              30: ("T30: worst +0.33, median \u22120.08", -8, 8, "right"), 42: ("T42", 8, 2, "left"), 38: ("T38", -7, -2, "right"),
              55: ("T55", 0, 11, "center"), 51: ("T51", 6, 6, "left"), 50: ("T50", -7, -9, "right"),
              27: ("T27: the switch removed", 8, -4, "left"), 56: ("T56: \u22120.88, raw momentum", 10, 4, "left")}
    P = {i: (max(dx, xlim[0] + 0.012), dy, kept) for i, kept, dx, dy in pts}
    for i, (t, ox, oy, ha) in labels.items():
        x, y, kept = P[i]
        ax.annotate(t, (x, y), xytext=(ox, oy), textcoords="offset points", fontsize=11.5, color=ACC if kept else INK2, va="center", ha=ha)
    arrow = dict(arrowstyle="-", color=MUTED, lw=0.9, shrinkB=4)
    ax.annotate("T14: +0.030, exactly the bar", P[14][:2], xytext=(0.35, -0.44), textcoords="data", fontsize=11.5, color=INK2, ha="right", va="center", arrowprops=arrow)
    ax.annotate("T7 and T16: kept, inside the tolerance", P[16][:2], xytext=(0.35, -0.27), textcoords="data", fontsize=11.5, color=ACC, ha="right", va="center", arrowprops=dict(arrow, color=ACC))
    ax.scatter([], [], s=64, color=ACC, label="kept, 14"); ax.scatter([], [], s=30, color=MUTED, label="reset, 46")
    ax.legend(frameon=False, fontsize=12, loc="upper left", labelcolor=INK2)
    save(fig, "alpha-keep-applied", pad=0.3)

def fig_noise_runs():
    """The seed scored eight times before the run (noise.txt): the spread of each number, and the threshold set from it."""
    import re
    runs = [tuple(map(float, re.findall(r"-?\d+\.\d+", l))) for l in open("figures/progress/lab/noise.txt") if l.strip()]
    rows = [("median-fold score, eight calls on the seed", [r[0] for r in runs], 0.03, "the bar: 0.03", ACC),
            ("worst-fold score, the same eight calls", [r[1] for r in runs], 0.13, "the floor's tolerance: 0.13", RED)]
    fig, axes = plt.subplots(2, 1, figsize=(9.0, 2.3), gridspec_kw=dict(hspace=0.85))
    for ax, (name, vals, thr, lab, c) in zip(axes, rows):
        lo, hi = min(vals), max(vals)
        ax.hlines(0, lo, hi, color=INK2, lw=2.2, zorder=2)
        ax.scatter(vals, [0] * len(vals), s=90, color=INK, edgecolor=BG, lw=1.2, zorder=3)
        ax.text(hi + 0.08 * thr, 0, f"{lo:.3f} to {hi:.3f}: spread {hi - lo:.3f}", ha="left", va="center", color=INK2, fontsize=14.5)
        ax.hlines(-0.5, lo, lo + thr, color=c, lw=5, zorder=2)
        ax.text(lo + thr + 0.06 * thr, -0.5, lab, ha="left", va="center", color=c, fontsize=14.5)
        ax.set_xlim(lo - 0.25 * thr, lo + 2.6 * thr); ax.set_ylim(-0.85, 0.5)
        ax.set_yticks([]); ax.tick_params(length=0, labelsize=13)
        for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_position(("data", -0.85))
        ax.set_title(name, loc="left", fontsize=15.5, color=INK, pad=4)
    save(fig, "eval-noise-runs", pad=0.3)

def fig_cube():
    """The final book with only its power changed, from figures/run3/lab/stats.txt (run 3 as it ran); type sized for a
    slide. Tail shares (the 10% most extreme stocks, 5% each side, validation) are the run-3 analysis figure's."""
    labs = ["a", "a\u00b7|a|", "a\u00b3", "a\u2075"]
    tails = [0.32, 0.58, 0.74, 0.82]
    val = [(0.071, 1.37), (0.107, 1.25), (0.148, 1.26), (0.186, 1.24)]          # return/yr, Sharpe
    tst = [(0.077, 0.81), (0.121, 0.85), (0.136, 0.77), (0.150, 0.73)]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.0, 4.6), gridspec_kw=dict(width_ratios=[1, 1.25], wspace=0.28))
    x = np.arange(4)
    a1.bar(x, tails, width=0.62, color=[ACC if i == 2 else "#4b5563" for i in x], zorder=3)
    for xi, t in zip(x, tails):
        a1.text(xi, t + 0.02, f"{t:.0%}", ha="center", va="bottom", fontsize=15, color=INK2)
    a1.set_ylim(0, 1.0); a1.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); a1.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    a1.set_title("share of the book in the 10%\nmost extreme stocks", loc="left", fontsize=15, color=INK, pad=10)
    wd = 0.38
    for k, (series, c, name) in enumerate(((val, ACC, "validation"), (tst, INK2, "test"))):
        xs = x + (k - 0.5) * wd
        a2.bar(xs, [r for r, _ in series], width=wd, color=c, zorder=3, label=name)
        for xi, (r, sh) in zip(xs, series):
            a2.text(xi, r + 0.004, f"{sh:.2f}", ha="center", va="bottom", fontsize=11, color=INK2)
    a2.set_ylim(0, 0.22); a2.set_yticks([0, 0.05, 0.10, 0.15, 0.20]); a2.set_yticklabels(["0%", "5%", "10%", "15%", "20%"])
    a2.set_title("return per year; Sharpe on each bar", loc="left", fontsize=15, color=INK, pad=10)
    a2.legend(frameon=False, fontsize=13, loc="upper left", labelcolor=INK2)
    for a in (a1, a2):
        a.set_xticks(x); a.set_xticklabels(labs, fontsize=16)
        a.tick_params(length=0, labelsize=13); a.tick_params(axis="x", labelsize=16)
        for sp in ("top", "right", "left"): a.spines[sp].set_visible(False)
        a.grid(axis="y", color=RULE, alpha=0.5, lw=0.6, zorder=0)
    save(fig, "alpha-cube")

def fig_nutshell():
    """Alpha research in a nutshell: a belief, an expression, its scores, the portfolio weights. The running example on
    March 10, 2025, from the closes on the data slide: rank(-returns(5)), then demeaned and scaled to gross one."""
    fig, ax = plt.subplots(figsize=(14.0, 3.8))
    ws, gaps, h = [3.0, 3.7, 2.8, 3.6], [0.85, 0.85, 1.25], 2.25
    xs = [0.0]
    for w, g in zip(ws[:-1], gaps): xs.append(xs[-1] + w + g)
    heads = ["a belief", "code", "scores", "portfolio weights"]
    for x, w, head in zip(xs, ws, heads):
        ax.add_patch(FancyBboxPatch((x, 0), w, h, boxstyle="round,pad=0,rounding_size=0.12", fc=PANEL,
                                    ec=RED if head == "code" else RULE, lw=1.6))
        ax.text(x + w / 2, h - 0.34, head, ha="center", va="center", color=ACC, fontsize=14.5, fontweight="bold")
    ax.text(xs[0] + ws[0] / 2, 0.85, "\u201cStocks that fell\nlast week tend to\nbounce back.\u201d", ha="center", va="center",
            color=INK2, fontsize=13, style="italic", linespacing=1.45)
    mess = ["d = raw[['dt','id','px']]", "d['r5'] = d.px.pct_change(5)", "d['r5'] = d['r5'].shift(1)",
            "d.loc[d.px < 2, 'r5'] = None", "d = d[d.dt.isin(cal)]", "s = d.pivot('dt','id','r5')",
            "s = (-s).rank(axis=1)", "s = s.loc[s.index > t0]"]
    for k, line in enumerate(mess):
        ax.text(xs[1] + 0.18, 1.52 - k * 0.19, line, ha="left", va="center", color=MUTED, fontsize=9.2)
    rows = [("JPM", "1.00", "+0.33"), ("AAPL", "0.80", "+0.17"), ("MSFT", "0.60", "0.00"), ("CVX", "0.40", "\u22120.17"), ("XOM", "0.20", "\u22120.33")]
    for col, x, w in ((1, xs[2], ws[2]), (2, xs[3], ws[3])):
        for k, r in enumerate(rows):
            y = 1.48 - k * 0.29
            ax.text(x + w / 2 - 0.85, y, r[0], ha="left", va="center", color=INK2, fontsize=13)
            ax.text(x + w / 2 + 0.85, y, r[col], ha="right", va="center", color=INK2, fontsize=13)
    for k in range(3):
        a, b = xs[k] + ws[k] + 0.08, xs[k + 1] - 0.08
        ax.annotate("", xy=(b, h / 2), xytext=(a, h / 2), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=2.2, mutation_scale=22))
    mid = xs[2] + ws[2] + gaps[2] / 2
    ax.text(xs[2] + ws[2] / 2, -0.3, "March 10, 2025", ha="center", va="center", color=MUTED, fontsize=11.5)
    ax.text(xs[3] + ws[3] / 2, -0.3, "sum 0, gross 1", ha="center", va="center", color=MUTED, fontsize=11.5)
    ax.set_xlim(-0.1, xs[3] + ws[3] + 0.1); ax.set_ylim(-0.5, h + 0.1); ax.axis("off")
    save(fig, "nutshell", pad=0.15)

def fig_trial():
    """One call of trial.sh in one picture: 2004-2017 cut into 12 blocks (embargo hatched), dealt into 6 folds (deal 1,
    the final book's), each fold scored on its own days; median and worst; then the same for 50 fresh deals."""
    folds = {1: ("2008\u201309 + 2016\u201317", 0.782), 2: ("2007\u201308 + 2011\u201312", 3.150), 3: ("2004\u201305 + 2006\u201307", 0.197),
             4: ("2009\u201310 + 2015\u201316", 2.045), 5: ("2005\u201306 + 2014\u201315", 2.144), 6: ("2012\u201313 + 2013\u201314", 1.044)}
    u = np.array([folds[k][1] for k in range(1, 7)]); med, worst_k = float(np.median(u)), int(np.argmin(u)) + 1
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12.0, 5.6), gridspec_kw=dict(height_ratios=[1.0, 2.3], hspace=0.3))
    h = 0.62
    for b in range(12):
        x0, x1 = EDGES[b], EDGES[b + 1]; k0, k1 = KEPT[b]; f = DEAL1[b]; bad = f == worst_k
        a1.add_patch(FancyBboxPatch((k0, -h / 2), k1 - k0, h, boxstyle="round,pad=0,rounding_size=0.06",
                                    fc=RED if bad else PANEL, ec=RED if bad else RULE, lw=1.0))
        for e0, e1 in ((x0, k0), (k1, x1)):
            a1.add_patch(Rectangle((e0 + 0.01, -h / 2), e1 - e0 - 0.02, h, fc="none", ec="#46516a", lw=0, hatch="////"))
        a1.text((k0 + k1) / 2, 0, str(f), ha="center", va="center", fontsize=14, color=BG if bad else INK, fontweight="bold" if bad else "normal")
    for yr in range(2004, 2019, 2):
        a1.text(yr, 0.62, str(yr), ha="center", va="bottom", color=MUTED, fontsize=12)
    a1.text(2003.75, 0, "deal 1", ha="right", va="center", color=INK2, fontsize=14)
    a1.text(2018.15, 0, "12 blocks, 21-day embargo\nat each edge, dealt at\nrandom into 6 folds of 2", ha="left", va="center", color=MUTED, fontsize=11.5, linespacing=1.35)
    a1.set_xlim(2001.6, 2022.4); a1.set_ylim(-0.6, 1.0); a1.axis("off")
    y = np.arange(6)[::-1]
    for yi, k in zip(y, range(1, 7)):
        yrs, v = folds[k]; bad = k == worst_k
        a2.barh(yi, v, height=0.62, color=RED if bad else "#4b5563", zorder=2)
        a2.text(-0.06, yi, f"fold {k} \u00b7 {yrs}", ha="right", va="center", color=INK2, fontsize=12.5)
        a2.text(v + 0.05, yi, f"{v:.2f}" + ("  worst" if bad else ""), ha="left", va="center", color=RED if bad else INK2, fontsize=12.5)
    a2.plot([med, med], [-0.6, 5.5], color=INK, lw=1.4, ls=(0, (4, 3)), zorder=3)
    a2.text(med, 5.6, f"median {med:.2f}", ha="center", va="bottom", color=INK, fontsize=12.5)
    a2.text(4.0, 2.5, "\u00d7 50 fresh deals, averaged:\n\nmedian  1.54 \u2192 1.47\nworst   0.20 \u2192 0.40\n\nthe two scores the\nkeep rule reads",
            ha="left", va="center", color=ACC, fontsize=13, linespacing=1.4)
    a2.set_xlim(0, 5.6); a2.set_ylim(-0.6, 6.2); a2.set_yticks([]); a2.tick_params(length=0, labelsize=11)
    a2.set_xlabel("each fold scored on its own days (the final book)", fontsize=12)
    for sp in ("top", "right", "left"): a2.spines[sp].set_visible(False)
    a2.grid(axis="x", color=RULE, alpha=0.5, lw=0.6, zorder=0)
    save(fig, "eval-trial", pad=0.25)

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
    fig_periods(); fig_deals(); fig_folds(); fig_noise(); fig_noise_runs(); fig_keep(); fig_cube(); fig_nutshell(); fig_trial(); fig_worth()
