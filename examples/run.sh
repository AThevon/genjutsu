#!/usr/bin/env bash
# Run one example case for real: examples/run.sh <id> [runs] [output root]
#
# Every run is a billed `claude` session (claude-opus-5-5, capped at 30 USD for the whole call).
# The plugin is copied outside $HOME first (a run that grants Bash cannot read $HOME, see
# evals/README.md section 2), and the eval runs from that copy. Results land in
# <output root>/<id>/runs/<UTC timestamp>/; the output root defaults to $GENJUTSU_EXAMPLES_OUT,
# else to examples/results/ in this repository (gitignored).
#
# After the eval, each kept run directory is unsealed and its workspace copied out (without
# node_modules or dist) to <run dir>/workspace-<n>/. Nothing is executed inside the kept
# directory: build, preview and capture the copy, never the original.
set -euo pipefail

if [ $# -lt 1 ] || [ $# -gt 3 ]; then
  echo "usage: examples/run.sh <id> [runs] [output root]" >&2
  exit 64
fi

ID="$1"
RUNS="${2:-1}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$HERE")"
OUT_ROOT="${3:-${GENJUTSU_EXAMPLES_OUT:-$HERE/results}}"
COPY=/private/tmp/genjutsu-eval-ex
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

if [ ! -f "$HERE/$ID/prompt.md" ] || [ ! -f "$HERE/$ID/fixture.sh" ]; then
  echo "run.sh: no example case named '$ID' in $HERE" >&2
  exit 64
fi
if ! [[ "$RUNS" =~ ^[1-9][0-9]*$ ]]; then
  echo "run.sh: runs must be a positive integer, got '$RUNS'" >&2
  exit 64
fi

# Free preflight: the fixture must succeed before any paid run starts (missing templates fail
# here instead of in the runner).
PREFLIGHT="$(mktemp -d /private/tmp/genjutsu-ex-preflight.XXXXXX)"
if ! (cd "$PREFLIGHT" && bash "$HERE/$ID/fixture.sh"); then
  rm -rf "$PREFLIGHT"
  echo "run.sh: the $ID fixture fails; fix that first (nothing was billed)" >&2
  exit 1
fi
rm -rf "$PREFLIGHT"

mkdir -p "$OUT_ROOT"
OUT="$(cd "$OUT_ROOT" && pwd)/$ID/runs/$STAMP"

rsync -a --delete \
  --exclude .git \
  --exclude evals/results \
  --exclude examples/results \
  --exclude dist \
  --exclude docs/superpowers \
  --exclude node_modules \
  "$REPO"/ "$COPY"/

mkdir -p "$OUT"
cd "$COPY"

set +e
claude plugin eval . \
  --eval-dir examples \
  --case "$ID" \
  --runs "$RUNS" \
  --ablation none \
  --scaffold \
  --allow-tools Bash Write Edit \
  --keep-temp \
  --no-publish \
  --trust-plugin \
  --model claude-opus-5-5 \
  --max-cost-usd 30 \
  --output-dir "$OUT" 2>&1 | tee "$OUT/run.log"
STATUS="${PIPESTATUS[0]}"
set -e

echo
echo "== $ID: claude plugin eval exited $STATUS"
if [ -f "$OUT/aggregate-result.json" ]; then
  echo "aggregate-result.json: $OUT/aggregate-result.json"
else
  echo "aggregate-result.json: NOT WRITTEN (expected at $OUT/aggregate-result.json)"
fi
[ -f "$OUT/report.html" ] && echo "report.html:           $OUT/report.html"
echo "log:                   $OUT/run.log"

# The runner seals each kept directory: its root becomes read-only, and home/ and tmp/ (the
# workspace is home/cwd) are moved into a mode-000 directory. It announces each one with a line
#   kept <root>: home/ and tmp/ ... are sealed in <dir> ... open them with `chmod 700 <root> <dir>` ...
# Print those lines, then unseal and copy each workspace out. Never run git, npm or vite inside.
SEALS="$(grep -a 'kept /.*chmod 700 ' "$OUT/run.log" | sort -u || true)"
if [ -z "$SEALS" ]; then
  echo "kept workspaces: no seal line in the log; look for 'kept' in $OUT/run.log:"
  grep -a 'kept' "$OUT/run.log" || true
  exit "$STATUS"
fi
echo "kept and sealed by the runner:"
printf '%s\n' "$SEALS" | sed 's/^/  /'
N=0
while IFS= read -r line; do
  pair="$(printf '%s\n' "$line" | sed -n 's/.*chmod 700 \([^ `]*\) \([^ `]*\)`.*/\1 \2/p' | tr -d "'\"")"
  root="${pair%% *}"
  sealed="${pair#* }"
  if [ -z "$pair" ] || [ ! -d "$root" ]; then
    echo "  could not read the paths from that line; unseal by hand with the chmod it gives" >&2
    continue
  fi
  N=$((N + 1))
  chmod 700 "$root" "$sealed"
  if [ -d "$sealed/home/cwd" ]; then
    rsync -a --exclude node_modules --exclude dist "$sealed/home/cwd/" "$OUT/workspace-$N/"
    echo "  workspace $N copied to $OUT/workspace-$N/ (from $sealed/home/cwd)"
  else
    echo "  $sealed has no home/cwd; inspect it by hand (it is unsealed now)" >&2
  fi
done <<< "$SEALS"
echo "Collect today: macOS cleans /tmp. To build a copy: cd $OUT/workspace-<n>, copy node_modules from /private/tmp/genjutsu-ex-templates/<stack>/, then npm run build."
exit "$STATUS"
