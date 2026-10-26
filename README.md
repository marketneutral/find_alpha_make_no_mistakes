# find alpha, make no mistakes
### Guest Lecture at MIT
### By Jonathan Larkin

Can an AI agent do quantitative research without fooling itself? Three parts:

1. **qex**, a small language for quant alphas, so a hypothesis is one line.
2. **autoresearch**, a coding agent that proposes, tests, and keeps or discards changes against a score.
3. **find alpha, make no mistakes**, the loop rebuilt for finance and run once on data it never saw.

Each part has a companion post on my blog, [*Speculative Decoding*](https://marketneutral.github.io).

This presentation is for informational purposes only and reflects my personal views and interests. It does not constitute investment advice and is not representative of any current or former employer. The information presented is based on publicly available sources.

This repo is made available under the APACHE LICENSE, VERSION 2.0 (the "License"). As noted in the License, this repo is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

The rendered presentation deck is viewable at [https://marketneutral.github.io/find_alpha_make_no_mistakes/find_alpha.html](https://marketneutral.github.io/find_alpha_make_no_mistakes/find_alpha.html).

This presentation was created using [Quarto](https://quarto.org/). The final rendered self-contained `revealjs` presentation is `docs/find_alpha.html`. To reproduce it from the source `find_alpha.qmd`, install Quarto and run:

```bash
./render.sh
```

The figures in `images/` come from the blog posts' analysis scripts; the code for the experiment in part 3 is in [alpha_lab](https://github.com/marketneutral/alpha_lab) and the language in [alpha-parser](https://github.com/marketneutral/alpha-parser).
