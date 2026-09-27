#!/usr/bin/env bash
# Guards the blocks intentionally duplicated between the cast and paint
# orchestrators. They cannot be shared at runtime: each orchestrator ships as a
# self-contained skill (on claude.ai they are separate uploads), and these blocks
# bootstrap sub-skill loading before anything can be cat'd. So they must stay
# byte-identical by hand - this check fails CI if they drift apart.
#
# Each guarded region is delimited in both SKILL.md files by:
#   <!-- genjutsu:shared:<name>:start -->  ...  <!-- genjutsu:shared:<name>:end -->
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CAST="$ROOT/skills/cast/SKILL.md"
PAINT="$ROOT/skills/paint/SKILL.md"
REGIONS=(scan skill-base load preview audit headless)

extract() { # <file> <region>
  awk -v s="<!-- genjutsu:shared:$2:start -->" -v e="<!-- genjutsu:shared:$2:end -->" '
    $0 == s { f = 1; next }
    $0 == e { f = 0 }
    f { print }
  ' "$1"
}

status=0
for r in "${REGIONS[@]}"; do
  a="$(extract "$CAST" "$r")"
  b="$(extract "$PAINT" "$r")"
  if [ -z "$a" ] || [ -z "$b" ]; then
    echo "FAIL [$r]: markers missing in cast and/or paint"
    status=1
    continue
  fi
  if [ "$a" != "$b" ]; then
    echo "FAIL [$r]: shared block drifted between cast and paint:"
    diff <(printf '%s\n' "$a") <(printf '%s\n' "$b") || true
    status=1
  else
    echo "OK   [$r]: cast and paint match"
  fi
done

# A region can be added to the two files and forgotten here, which is how the
# audit checklist drifted unguarded for three releases. Fail if the markers
# present in the files do not match REGIONS exactly, in either direction.
found="$(grep -ho '<!-- genjutsu:shared:[a-z-]*:start -->' "$CAST" "$PAINT" \
  | sed 's/.*shared:\([a-z-]*\):start.*/\1/' | sort -u)"
declared="$(printf '%s\n' "${REGIONS[@]}" | sort -u)"
if [ "$found" != "$declared" ]; then
  echo "FAIL: the guarded regions in the files do not match REGIONS in this script."
  diff <(printf '%s\n' "$declared") <(printf '%s\n' "$found") \
    | sed 's/^</  only in REGIONS: /; s/^>/  only in the files: /' || true
  status=1
else
  echo "OK   [markers]: REGIONS matches the markers found in cast and paint"
fi

# The bundle's router carries the same search twice, once per pipeline, and a
# fix applied to one block and not the other is exactly the drift this file
# exists to catch. The two blocks must match line for line once their own
# `p=cast` / `p=paint` line is normalised to `p=X`.
ROUTER="$ROOT/packaging/genjutsu-router.md"
extract_router() { # <pipeline>
  awk -v s="<!-- genjutsu:router:$1:start -->" -v e="<!-- genjutsu:router:$1:end -->" '
    $0 == s { f = 1; next }
    $0 == e { f = 0 }
    f { print }
  ' "$ROUTER"
}
router_cast="$(extract_router cast)"
router_paint="$(extract_router paint)"
if [ -z "$router_cast" ] || [ -z "$router_paint" ]; then
  echo "FAIL [router]: router markers missing in packaging/genjutsu-router.md"
  status=1
elif ! printf '%s\n' "$router_cast" | grep -qx 'p=cast' \
  || ! printf '%s\n' "$router_paint" | grep -qx 'p=paint'; then
  echo "FAIL [router]: each router block must name its own pipeline on a line of its own (p=cast, p=paint)"
  status=1
else
  norm_cast="$(printf '%s\n' "$router_cast" | sed 's/^p=cast$/p=X/')"
  norm_paint="$(printf '%s\n' "$router_paint" | sed 's/^p=paint$/p=X/')"
  if [ "$norm_cast" != "$norm_paint" ]; then
    echo "FAIL [router]: the cast and paint blocks of the router drifted apart:"
    diff <(printf '%s\n' "$norm_cast") <(printf '%s\n' "$norm_paint") || true
    status=1
  else
    echo "OK   [router]: the cast and paint router blocks match, p= line aside"
  fi
fi

if [ "$status" -ne 0 ]; then
  echo ""
  echo "One or more shared blocks drifted. Edit skills/cast/SKILL.md and"
  echo "skills/paint/SKILL.md so the marked regions stay byte-identical."
fi
exit "$status"
