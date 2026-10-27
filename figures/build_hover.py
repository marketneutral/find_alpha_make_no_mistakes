"""Inline figures/progress/lab/progress-hover.json into progress-hover.html (the deck is self-contained, so the run
chart's tooltips carry their data with them), and copy the chart to images/. Run from the repo root."""
import json, re, shutil
data = json.load(open("figures/progress/lab/progress-hover.json"))
js = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
p = "progress-hover.html"; s = open(p).read()
s, n = re.subn(r"const trials = \[.*?\];\n", lambda m: f"const trials = {js};\n", s, count=1, flags=re.S)
assert n == 1
open(p, "w").write(s)
shutil.copy("figures/progress/progress.svg", "images/alpha-progress.svg")
print("progress-hover.html:", len(data), "trials; images/alpha-progress.svg")
