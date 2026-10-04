#!/usr/bin/env bash
# Rebuild the example templates the fixtures copy, from the sources and lockfiles in
# examples/_templates/, into /private/tmp/genjutsu-ex-templates/<stack>/ with node_modules installed.
#
# The templates live outside $HOME on purpose: a `claude plugin eval` run that grants Bash
# cannot read $HOME, and the fixtures (which run as you) copy node_modules into the run's
# workspace from here. macOS clears /private/tmp after a few days without access, so run this
# again before a batch of example runs. Needs network (npm ci).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST=/private/tmp/genjutsu-ex-templates

for src in "$HERE"/_templates/*/; do
  stack="$(basename "$src")"
  out="$DEST/$stack"
  echo "== $stack -> $out"
  rm -rf "$out"
  mkdir -p "$out"
  cp -R "$src". "$out"/
  (cd "$out" && npm ci --no-audit --no-fund && npm run build && rm -rf dist node_modules/.vite node_modules/.vite-temp)
done

echo "Templates ready in $DEST"
