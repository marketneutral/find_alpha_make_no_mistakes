# Run 3, exactly as it ran

The deck's results slides, and `figures/partitions.py`, use run 3's own setup: its evaluator, its qex
version, and its data. Rebuild that lab in a scratch directory (nothing in the lab repo changes):

```bash
git -C ~/dev/alpha_lab archive run3 | tar -x -C /tmp/run3lab        # run 3's tree: eval.py, uv.lock pinning qex 0.3.1
ln -s ~/dev/alpha_lab/data_20260811_pre_mcapfix /tmp/run3lab/data   # the data run 3 ran on, to 2026-08-11
(cd /tmp/run3lab && uv sync --frozen)
```

Then, from this directory:

```bash
CACHE=/tmp/run3cache ALPHA_LAB=/tmp/run3lab uv run --project /tmp/run3lab python analysis.py   # lab/stats.txt, lab/weekly_pnl.csv, figures
uv run --no-project --python 3.12 --with "pymc<5.30" --with "arviz<0.23" --with "numpy<2.4" \
    --with pandas --with matplotlib python bayes.py                                            # lab/bayes.txt, bayes.svg
CACHE=/tmp/run3cache ALPHA_LAB=/tmp/run3lab uv run --project /tmp/run3lab python drawdown.py   # the 2026 drawdown
```

The figures are copied to `../../images/` as `alpha-*.svg`. `analysis.py` and `bayes.py` are the blog post's
scripts; `analysis.py` is adapted to run 3's evaluator interface, and the Bayes pins are what current library
versions need to run the model. The trial commits (seed `318c23d`, final `b89945f`, T55 `5596bb7`) are read
from `~/dev/alpha_lab`.

Checks against the run's record: the final book's test Sharpe 0.77, 13.6% a year, max drawdown −26%, as in
run 3's `summary.md`; validation Sharpe 1.26 (the agent saw 1.27 from the evaluator's own book); and deal 1's
six fold utilities in `partitions.py` match the evaluator's printed output to three decimals.

After the run, the universe screen was found to leak future share splits into market cap (the vendor
restates share counts). On corrected data the final book's test Sharpe is 0.76 instead of 0.77.
