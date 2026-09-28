#!/usr/bin/env bash
# Prints the CHANGELOG.md entry of one release, without its heading, for the
# body of the GitHub release. The release used to take GitHub's generated notes,
# a list of PR titles, so what users read was not what the maintainer wrote.
#
# Fails when the tag has no `## vX.Y.Z - YYYY-MM-DD` entry or the entry is empty:
# publishing a release with no notes means the version check was skipped.
#
# Usage: scripts/release-notes.sh <tag> [changelog]
set -euo pipefail

tag="${1:-}"
file="${2:-$(cd "$(dirname "$0")/.." && pwd)/CHANGELOG.md}"

case "$tag" in
  v[0-9]*.[0-9]*.[0-9]*) ;;
  *) echo "release-notes: '$tag' is not a vX.Y.Z tag" >&2; exit 2 ;;
esac
[ -f "$file" ] || { echo "release-notes: $file not found" >&2; exit 2; }

# The heading must be exactly "## <tag> - YYYY-MM-DD". Matching on the full
# prefix including " - " is what keeps v1.1.0 from matching "## v1.10.0 - ".
body="$(awk -v want="## $tag - " '
  !done && index($0, want) == 1 && substr($0, length(want) + 1) ~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/ {
    inside = 1; found = 1; next
  }
  inside && /^## v[0-9]/ { inside = 0; done = 1 }
  inside { print }
  END { exit found ? 0 : 3 }
' "$file")" || { echo "release-notes: no '## $tag - YYYY-MM-DD' entry in $file" >&2; exit 1; }

# Drop leading blank lines; $(...) already dropped the trailing ones.
body="$(printf '%s\n' "$body" | sed '/[^[:space:]]/,$!d')"
if [ -z "$body" ]; then
  echo "release-notes: the $tag entry in $file is empty" >&2
  exit 1
fi
printf '%s\n' "$body"
