#!/usr/bin/env bash
# Fails on any U+2014 (em dash) in a tracked file.
#
# The character is the most recognisable tell of model-written prose, and this
# repo is a catalogue of such tells. It is written literally nowhere, not even
# where it is the subject: an escape sequence in Python, JS and YAML,
# "U+2014 (em dash)" in prose, and the printf below in shell.
#
# The only exemption is the vendored part of ui-ux-pro-max (data/, scripts/,
# references/, LICENSE-upstream.txt): it mirrors an upstream release, and
# hand-editing it would make the mirror undiffable.
#
# Usage: scripts/check-dashes.sh [repo root]
set -uo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
DASH="$(printf '\xe2\x80\x94')"
VENDORED='^skills/_jutsu/ui-ux-pro-max/(data/|scripts/|references/|LICENSE-upstream\.txt$)'

files="$(git -C "$ROOT" ls-files)" || { echo "FAIL: $ROOT is not a git checkout"; exit 1; }

status=0
n_files=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  printf '%s\n' "$f" | grep -Eq "$VENDORED" && continue
  [ -f "$ROOT/$f" ] || continue
  n_files=$((n_files + 1))
  # -I skips binary files: a PNG can hold these three bytes by chance.
  if hits="$(grep -I -n -F -- "$DASH" "$ROOT/$f")"; then
    status=1
    printf '%s\n' "$hits" | sed "s|^|FAIL $f:|"
  fi
done <<< "$files"

if [ "$status" -eq 0 ]; then
  echo "OK   [dashes]: no U+2014 in $n_files tracked files (vendored ui-ux-pro-max excluded)"
else
  echo ""
  echo "Replace each U+2014 with a hyphen or rephrase. Where the character is the subject,"
  echo "write it as an escape sequence in code, or as U+2014 (em dash) in prose."
fi
exit "$status"
