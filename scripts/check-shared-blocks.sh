#!/usr/bin/env bash
# Guards the blocks intentionally duplicated between the orchestrators (cast,
# paint and bunshin). They cannot be shared at runtime: each orchestrator ships
# as a self-contained skill, and these blocks bootstrap sub-skill loading before
# anything can be cat'd. So they must stay byte-identical by hand - this check
# fails CI if they drift apart.
#
# Each guarded region is delimited in the SKILL.md files by:
#   <!-- genjutsu:shared:<name>:start -->  ...  <!-- genjutsu:shared:<name>:end -->
#
# cast and paint carry every region in REGIONS. bunshin carries every region in
# BUNSHIN_REGIONS, byte-identical to cast's, and never escalate: escalate is the
# proposal cast and paint make to switch to bunshin.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CAST="$ROOT/skills/cast/SKILL.md"
PAINT="$ROOT/skills/paint/SKILL.md"
BUNSHIN="$ROOT/skills/bunshin/SKILL.md"
REGIONS=(scan skill-base load preview audit headless escalate)
BUNSHIN_REGIONS=(scan skill-base load preview audit headless)

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

# bunshin: every region it must carry, byte-identical to cast's, and no other.
if [ ! -f "$BUNSHIN" ]; then
  echo "FAIL [bunshin]: $BUNSHIN is missing"
  status=1
else
  for r in "${BUNSHIN_REGIONS[@]}"; do
    a="$(extract "$CAST" "$r")"
    b="$(extract "$BUNSHIN" "$r")"
    if [ -z "$b" ]; then
      echo "FAIL [$r]: markers missing in bunshin"
      status=1
    elif [ "$a" != "$b" ]; then
      echo "FAIL [$r]: shared block drifted between cast and bunshin:"
      diff <(printf '%s\n' "$a") <(printf '%s\n' "$b") || true
      status=1
    else
      echo "OK   [$r]: cast and bunshin match"
    fi
  done
  # grep exits 1 when bunshin has no marker at all: that is a finding, not a crash.
  found_b="$({ grep -ho '<!-- genjutsu:shared:[a-z-]*:start -->' "$BUNSHIN" || true; } \
    | sed 's/.*shared:\([a-z-]*\):start.*/\1/' | sort -u)"
  declared_b="$(printf '%s\n' "${BUNSHIN_REGIONS[@]}" | sort -u)"
  if [ "$found_b" != "$declared_b" ]; then
    echo "FAIL: the guarded regions in bunshin do not match BUNSHIN_REGIONS in this script."
    diff <(printf '%s\n' "$declared_b") <(printf '%s\n' "$found_b") \
      | sed 's/^</  only in BUNSHIN_REGIONS: /; s/^>/  only in bunshin: /' || true
    status=1
  else
    echo "OK   [markers]: BUNSHIN_REGIONS matches the markers found in bunshin"
  fi
fi

# The bundle's router carries the same search three times, once per pipeline,
# and a fix applied to one block and not the others is exactly the drift this
# file exists to catch. The blocks must match line for line once their own
# `p=cast` / `p=paint` / `p=bunshin` line is normalised to `p=X`.
ROUTER="$ROOT/packaging/genjutsu-router.md"
extract_router() { # <pipeline>
  awk -v s="<!-- genjutsu:router:$1:start -->" -v e="<!-- genjutsu:router:$1:end -->" '
    $0 == s { f = 1; next }
    $0 == e { f = 0 }
    f { print }
  ' "$ROUTER"
}
router_cast="$(extract_router cast)"
router_status=0
for pipeline in cast paint bunshin; do
  block="$(extract_router "$pipeline")"
  if [ -z "$block" ]; then
    echo "FAIL [router]: the $pipeline router markers are missing in packaging/genjutsu-router.md"
    router_status=1
  elif ! printf '%s\n' "$block" | grep -qx "p=$pipeline"; then
    echo "FAIL [router]: the $pipeline router block must name its own pipeline on a line of its own (p=$pipeline)"
    router_status=1
  elif [ "$pipeline" != cast ] && [ -n "$router_cast" ]; then
    norm_cast="$(printf '%s\n' "$router_cast" | sed 's/^p=cast$/p=X/')"
    norm_this="$(printf '%s\n' "$block" | sed "s/^p=$pipeline\$/p=X/")"
    if [ "$norm_cast" != "$norm_this" ]; then
      echo "FAIL [router]: the cast and $pipeline blocks of the router drifted apart:"
      diff <(printf '%s\n' "$norm_cast") <(printf '%s\n' "$norm_this") || true
      router_status=1
    fi
  fi
done
if [ "$router_status" -eq 0 ]; then
  echo "OK   [router]: the cast, paint and bunshin router blocks match, p= line aside"
else
  status=1
fi

if [ "$status" -ne 0 ]; then
  echo ""
  echo "One or more shared blocks drifted. Edit skills/cast/SKILL.md,"
  echo "skills/paint/SKILL.md and skills/bunshin/SKILL.md so the marked regions stay"
  echo "byte-identical."
fi
exit "$status"
