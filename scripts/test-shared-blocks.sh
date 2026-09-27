#!/usr/bin/env bash
# Tests scripts/check-shared-blocks.sh on mutated copies of the real files. A
# guard that passes on drift is worse than none, so every mutation below must
# make it fail, and the untouched copy must pass.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/genjutsu-shared.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

pass=0
fail=0

# copy <name>: a minimal tree holding the check and the three files it reads.
copy() {
  d="$WORK/$1"
  mkdir -p "$d/scripts" "$d/skills/cast" "$d/skills/paint" "$d/packaging"
  cp "$ROOT/scripts/check-shared-blocks.sh" "$d/scripts/"
  cp "$ROOT/skills/cast/SKILL.md" "$d/skills/cast/SKILL.md"
  cp "$ROOT/skills/paint/SKILL.md" "$d/skills/paint/SKILL.md"
  cp "$ROOT/packaging/genjutsu-router.md" "$d/packaging/genjutsu-router.md"
}

# mutate <file> <python expression over t>: rewrite a file in place.
mutate() {
  python3 - "$1" "$2" <<'PY'
import sys
path, expr = sys.argv[1], sys.argv[2]
t = open(path, encoding="utf-8").read()
new = eval(expr, {"t": t})
assert new != t, "mutation changed nothing: " + expr
open(path, "w", encoding="utf-8").write(new)
PY
}

expect() { # <name> <expected exit: 0|1> <tree>
  "$WORK/$3/scripts/check-shared-blocks.sh" >"$WORK/$3.out" 2>&1
  got=$?; [ "$got" -ne 0 ] && got=1
  if [ "$got" = "$2" ]; then echo "OK   $1"; pass=$((pass + 1))
  else echo "FAIL $1 (expected exit $2, got $got)"; sed 's/^/       | /' "$WORK/$3.out"; fail=$((fail + 1)); fi
}

copy clean
expect "the repository as it is passes" 0 clean

copy region-drift
mutate "$WORK/region-drift/skills/paint/SKILL.md" \
  't.replace("# 2. Android / Compose", "# 2. Android and Compose", 1)'
expect "a shared region edited in paint only fails" 1 region-drift

copy router-drift
mutate "$WORK/router-drift/packaging/genjutsu-router.md" \
  't[:t.index("<!-- genjutsu:router:paint:start -->")] + t[t.index("<!-- genjutsu:router:paint:start -->"):].replace("w=\"${PWD:-$(pwd)}\"; n=0", "w=\"$PWD\"; n=0", 1)'
expect "a router block edited in paint only fails" 1 router-drift

copy router-wrong-p
mutate "$WORK/router-wrong-p/packaging/genjutsu-router.md" \
  't.replace("<!-- genjutsu:router:paint:start -->\n```bash\np=paint", "<!-- genjutsu:router:paint:start -->\n```bash\np=cast", 1)'
expect "a paint router block that runs cast fails" 1 router-wrong-p

copy router-no-markers
mutate "$WORK/router-no-markers/packaging/genjutsu-router.md" \
  't.replace("<!-- genjutsu:router:cast:start -->", "", 1)'
expect "a router block without its markers fails" 1 router-no-markers

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
