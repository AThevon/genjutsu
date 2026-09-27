#!/usr/bin/env bash
# The version is written in three places, and a release reads a fourth.
#
# v3.6.0 was tagged and published while plugin.json and marketplace.json still
# said 3.5.0 and the CHANGELOG had no entry for it. Nothing failed: the tag, the
# manifests and the changelog are separate files and nothing compared them.
# This does. On every run the two manifests and the first CHANGELOG heading
# must agree; under a tag push the tag must agree too.
#
# Usage: scripts/check-version.sh [repo root]
# Reads GITHUB_REF_TYPE and GITHUB_REF_NAME, which GitHub Actions sets.
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"

json_field() { # <file> <dotted path>
  python3 - "$1" "$2" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
for key in sys.argv[2].split("."):
    value = value.get(key) if isinstance(value, dict) else None
print(value if isinstance(value, str) else "")
PY
}

plugin="$(json_field "$ROOT/.claude-plugin/plugin.json" version)"
market="$(json_field "$ROOT/.claude-plugin/marketplace.json" metadata.version)"

# The first level-two heading must be a release heading. An "Unreleased" or
# malformed heading on top fails instead of being skipped: skipping it would
# compare against the previous release and pass.
first="$(grep -m1 '^## ' "$ROOT/CHANGELOG.md" || true)"
if printf '%s\n' "$first" | grep -Eq '^## v[0-9]+\.[0-9]+\.[0-9]+ - [0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
  changelog="$(printf '%s\n' "$first" | sed -E 's/^## v([^ ]+) - .*/\1/')"
else
  echo "FAIL: the first heading of CHANGELOG.md is not '## vX.Y.Z - YYYY-MM-DD': ${first:-<none>}"
  exit 1
fi

status=0
echo "plugin.json          $plugin"
echo "marketplace.json     $market"
echo "CHANGELOG.md         $changelog"
if [ -z "$plugin" ] || [ "$plugin" != "$market" ] || [ "$plugin" != "$changelog" ]; then
  echo "FAIL: plugin.json .version, marketplace.json .metadata.version and the first CHANGELOG entry must be equal."
  status=1
fi

if [ "${GITHUB_REF_TYPE:-}" = "tag" ]; then
  echo "tag                  ${GITHUB_REF_NAME:-}"
  if [ "${GITHUB_REF_NAME:-}" != "v$plugin" ]; then
    echo "FAIL: the tag ${GITHUB_REF_NAME:-<empty>} does not match v$plugin."
    status=1
  fi
fi

[ "$status" -eq 0 ] && echo "OK   [version]: every version source agrees"
exit "$status"
