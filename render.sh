#!/bin/bash
# render the deck to docs/ (served by GitHub Pages)
cd "$(dirname "$0")" && quarto render find_alpha.qmd --output-dir docs
