#!/usr/bin/env bash
# Tests scripts/release-notes.sh, which turns one CHANGELOG entry into the body
# of the GitHub release. Until v4.0.0 the release body was generated from PR
# titles, so the notes users read were not the notes the maintainer wrote.
#
# The cases that matter: the heading itself never leaks into the body, a tag
# that is a prefix of another (v1.1.0 against v1.10.0) never picks the wrong
# entry, and a tag without an entry fails instead of publishing an empty body.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NOTES="$ROOT/scripts/release-notes.sh"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/genjutsu-notes.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

pass=0
fail=0
check() { # <name> <expected> <actual>
  if [ "$2" = "$3" ]; then
    echo "OK   $1"
    pass=$((pass + 1))
  else
    echo "FAIL $1"
    echo "       expected: ${2:-<empty>}"
    echo "       actual:   ${3:-<empty>}"
    fail=$((fail + 1))
  fi
}

FIX="$WORK/CHANGELOG.md"
cat > "$FIX" <<'EOF'
# Changelog

Intro paragraph, never part of a release.

## v2.0.0 - 2026-02-01

Second release.

### Added

- a thing

## v1.10.0 - 2026-01-15

Tenth minor.

## v1.1.0 - 2026-01-01

First minor.
EOF

check "middle entry, heading excluded, trailing blank trimmed" \
  "$(printf 'Second release.\n\n### Added\n\n- a thing')" \
  "$("$NOTES" v2.0.0 "$FIX" 2>/dev/null)"

check "last entry runs to end of file" \
  "First minor." "$("$NOTES" v1.1.0 "$FIX" 2>/dev/null)"

check "v1.10.0 is its own entry" \
  "Tenth minor." "$("$NOTES" v1.10.0 "$FIX" 2>/dev/null)"

"$NOTES" v3.0.0 "$FIX" >/dev/null 2>"$WORK/err"
check "a tag without an entry fails" "1" "$?"
check "and says which heading it looked for" "yes" \
  "$(grep -q "## v3.0.0 - YYYY-MM-DD" "$WORK/err" && echo yes || echo no)"

"$NOTES" 2.0.0 "$FIX" >/dev/null 2>&1
check "a version without the v prefix is refused" "2" "$?"

EMPTY="$WORK/empty.md"
printf '# Changelog\n\n## v0.9.0 - 2025-12-01\n\n## v0.8.0 - 2025-11-01\n\nOlder.\n' > "$EMPTY"
"$NOTES" v0.9.0 "$EMPTY" >/dev/null 2>&1
check "an empty entry fails rather than publishing an empty body" "1" "$?"

BADDATE="$WORK/baddate.md"
printf '# Changelog\n\n## v0.7.0 - soon\n\nNot dated.\n' > "$BADDATE"
"$NOTES" v0.7.0 "$BADDATE" >/dev/null 2>&1
check "a heading without a YYYY-MM-DD date is not an entry" "1" "$?"

# The real file: whatever its newest entry is, it must extract to something.
TOP="$(grep -m1 -E '^## v[0-9]+\.[0-9]+\.[0-9]+ - ' "$ROOT/CHANGELOG.md" | sed -E 's/^## (v[^ ]+) - .*/\1/')"
check "the newest entry of CHANGELOG.md ($TOP) extracts to a non-empty body" "yes" \
  "$([ -n "$("$NOTES" "$TOP" 2>/dev/null)" ] && echo yes || echo no)"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
