#!/usr/bin/env bash
# Tests scripts/check-version.sh against fixture repos, one per way the version
# sources can disagree. The check guards a release, so a check that passes on
# everything would be worse than none: every failing case below must fail.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHECK="$ROOT/scripts/check-version.sh"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/genjutsu-version.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

pass=0
fail=0

# fixture <name> <plugin> <marketplace> <first CHANGELOG heading>
fixture() {
  mkdir -p "$WORK/$1/.claude-plugin"
  printf '{ "name": "genjutsu", "version": "%s" }\n' "$2" > "$WORK/$1/.claude-plugin/plugin.json"
  printf '{ "name": "genjutsu", "metadata": { "version": "%s" } }\n' "$3" > "$WORK/$1/.claude-plugin/marketplace.json"
  printf '# Changelog\n\nIntro.\n\n%s\n\nBody.\n\n## v0.0.1 - 2020-01-01\n' "$4" > "$WORK/$1/CHANGELOG.md"
}

# expect <name> <expected exit: 0|1> <repo dir> [VAR=value ...]
expect() {
  name="$1"; want="$2"; dir="$3"; shift 3
  env -u GITHUB_REF_TYPE -u GITHUB_REF_NAME "$@" "$CHECK" "$dir" >/dev/null 2>&1
  got=$?
  [ "$got" -ne 0 ] && got=1
  if [ "$got" = "$want" ]; then
    echo "OK   $name"; pass=$((pass + 1))
  else
    echo "FAIL $name (expected exit $want, got $got)"; fail=$((fail + 1))
  fi
}

fixture agree 4.0.0 4.0.0 "## v4.0.0 - 2026-10-01"
fixture plugin-off 4.0.1 4.0.0 "## v4.0.0 - 2026-10-01"
fixture market-off 4.0.0 3.6.0 "## v4.0.0 - 2026-10-01"
fixture changelog-off 4.0.0 4.0.0 "## v3.6.0 - 2026-09-08"
fixture unreleased 4.0.0 4.0.0 "## Unreleased"
fixture no-date 4.0.0 4.0.0 "## v4.0.0"
fixture empty-version "" "" "## v4.0.0 - 2026-10-01"

expect "all three agree" 0 "$WORK/agree"
expect "plugin.json differs" 1 "$WORK/plugin-off"
expect "marketplace.json differs" 1 "$WORK/market-off"
expect "first CHANGELOG entry differs" 1 "$WORK/changelog-off"
expect "an Unreleased heading on top fails instead of being skipped" 1 "$WORK/unreleased"
expect "a heading without its date fails" 1 "$WORK/no-date"
expect "empty versions never count as agreeing" 1 "$WORK/empty-version"
expect "tag push, matching tag" 0 "$WORK/agree" GITHUB_REF_TYPE=tag GITHUB_REF_NAME=v4.0.0
expect "tag push, stale tag" 1 "$WORK/agree" GITHUB_REF_TYPE=tag GITHUB_REF_NAME=v3.6.0
expect "branch push ignores the ref name" 0 "$WORK/agree" GITHUB_REF_TYPE=branch GITHUB_REF_NAME=feat/v4.0
expect "this repository" 0 "$ROOT"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
