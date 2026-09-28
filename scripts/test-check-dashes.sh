#!/usr/bin/env bash
# Tests scripts/check-dashes.sh against fixture git repos: a dash in a tracked
# genjutsu file fails, the vendored ui-ux-pro-max paths are the only exemption,
# an untracked file is not scanned, and a binary file never matches.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHECK="$ROOT/scripts/check-dashes.sh"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/genjutsu-dashes.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
DASH="$(printf '\xe2\x80\x94')"
UIUX="skills/_jutsu/ui-ux-pro-max"

pass=0
fail=0

# repo <name> <path=content>...   content "DASH" is replaced by the character
repo() {
  d="$WORK/$1"; shift
  mkdir -p "$d"
  git -C "$d" init -q
  for spec in "$@"; do
    path="${spec%%=*}"; content="${spec#*=}"
    mkdir -p "$d/$(dirname "$path")"
    printf '%s\n' "${content//DASH/$DASH}" > "$d/$path"
    git -C "$d" add "$path"
  done
}

expect() { # <name> <expected exit: 0|1> <repo dir>
  "$CHECK" "$3" >/dev/null 2>&1
  got=$?; [ "$got" -ne 0 ] && got=1
  if [ "$got" = "$2" ]; then echo "OK   $1"; pass=$((pass + 1))
  else echo "FAIL $1 (expected exit $2, got $got)"; fail=$((fail + 1)); fi
}

repo clean "README.md=plain - hyphen" "skills/cast/SKILL.md=no dash here"
repo prose "README.md=a DASH b"
repo skill "skills/cast/SKILL.md=Variant A DASH subtle"
repo script "scripts/x.py=print('DASH')"
repo vendored "$UIUX/data/styles.csv=a,DASH,b" "$UIUX/scripts/core.py=# DASH" \
  "$UIUX/references/pro-rules.md=DASH" "$UIUX/LICENSE-upstream.txt=DASH"
repo uiux-skill "$UIUX/SKILL.md=ours DASH not vendored"
repo lookalike "skills/_jutsu/ui-ux-pro-max-data/x.md=DASH"
repo untracked "README.md=clean"
printf 'a %s b\n' "$DASH" > "$WORK/untracked/notes.md"
repo binary "README.md=clean"
printf 'PNG\000\342\200\224\000' > "$WORK/binary/logo.png"
git -C "$WORK/binary" add logo.png

expect "clean repo passes" 0 "$WORK/clean"
expect "a dash in README fails" 1 "$WORK/prose"
expect "a dash in a skill fails" 1 "$WORK/skill"
expect "a dash in a script fails" 1 "$WORK/script"
expect "vendored ui-ux-pro-max paths are exempt" 0 "$WORK/vendored"
expect "ui-ux-pro-max/SKILL.md is ours, not exempt" 1 "$WORK/uiux-skill"
expect "a path that only starts like the vendored one is not exempt" 1 "$WORK/lookalike"
expect "untracked files are not scanned" 0 "$WORK/untracked"
expect "binary files never match" 0 "$WORK/binary"
expect "this repository" 0 "$ROOT"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
