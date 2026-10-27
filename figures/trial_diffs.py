"""A trial's change to alpha.qex, as code the deck can show. Run from the repo root:

    python figures/trial_diffs.py 1            # trial 1: before (the best book at the time), after, and a unified diff
    python figures/trial_diffs.py 1 --width 46 # reflow long lines to at most 46 characters

Both expressions come from the lab's git history (results.tsv names the commits). Long lines are reflowed with
the formatter the run chart's tooltips use, so the two sides line up and a textual diff shows only the change.
A trailing ' #+' marks a line the trial added or changed, ' #-' one it removed; qex-highlight.html tints them
and draws a + or − in the gutter. The code is the agent's, verbatim.
"""
import csv, difflib, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress"))
import progress

LAB = os.path.expanduser("~/dev/alpha_lab")
ROWS = list(csv.DictReader(open("figures/progress/lab/results.tsv"), delimiter="\t"))

def expr(commit, width):
    progress.WIDTH = width
    commit = progress.SEED_COMMIT if commit == "seed" else commit
    e = subprocess.check_output(["git", "-C", LAB, "show", f"{commit}:alpha.qex"], text=True)
    e = e.strip()
    return [l for line in e.splitlines() for l in progress.wrap_line(line.rstrip())]

def trial(n, width=46):
    """(before lines, after lines, opcodes) for trial n: before is the best book kept before it."""
    best = ROWS[0]["commit"]
    for i, r in enumerate(ROWS[1:], 1):
        if i == n:
            a, b = expr(best, width), expr(r["commit"], width)
            key = lambda l: re.sub(r"^\s*(let\s+)?", "", l).rstrip(",")        # 'let' and trailing commas move when bindings are added
            return a, b, difflib.SequenceMatcher(None, [key(l) for l in a], [key(l) for l in b], autojunk=False).get_opcodes()
        if r["status"] == "keep":
            best = r["commit"]

def panels(n, width=46):
    """Before with removed lines marked, after with added lines marked."""
    a, b, ops = trial(n, width)
    left, right = list(a), list(b)
    for tag, i1, i2, j1, j2 in ops:
        if tag in ("replace", "delete"):
            for k in range(i1, i2): left[k] += " #-"
        if tag in ("replace", "insert"):
            for k in range(j1, j2): right[k] += " #+"
    return "\n".join(left), "\n".join(right)

def unified(n, width=46):
    a, b, ops = trial(n, width)
    out = []
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal": out += b[j1:j2]                                 # unchanged lines, as the trial wrote them
        if tag in ("replace", "delete"): out += [l + " #-" for l in a[i1:i2]]
        if tag in ("replace", "insert"): out += [l + " #+" for l in b[j1:j2]]
    return "\n".join(out)

if __name__ == "__main__":
    n = int(sys.argv[1]); w = int(sys.argv[sys.argv.index("--width") + 1]) if "--width" in sys.argv else 46
    L, R = panels(n, w)
    print(f"== before\n{L}\n== after\n{R}\n== unified\n{unified(n, w)}")
