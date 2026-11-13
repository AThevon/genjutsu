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

# copy <name>: a minimal tree holding the check and the files it reads.
copy() {
  d="$WORK/$1"
  mkdir -p "$d/scripts" "$d/skills/cast" "$d/skills/paint" "$d/skills/bunshin" "$d/packaging"
  cp "$ROOT/scripts/check-shared-blocks.sh" "$d/scripts/"
  cp "$ROOT/skills/cast/SKILL.md" "$d/skills/cast/SKILL.md"
  cp "$ROOT/skills/paint/SKILL.md" "$d/skills/paint/SKILL.md"
  cp "$ROOT/skills/bunshin/SKILL.md" "$d/skills/bunshin/SKILL.md"
  cp "$ROOT/packaging/genjutsu-router.md" "$d/packaging/genjutsu-router.md"
  mkdir -p "$d/.github/ISSUE_TEMPLATE"
  cp "$ROOT"/.github/ISSUE_TEMPLATE/*.yml "$d/.github/ISSUE_TEMPLATE/"
}

# mutate <file> <python expression over t> [<file read as s>]: rewrite a file in
# place. The optional second file is there to copy a region from one file into
# another, which is how a region lands where it does not belong.
mutate() {
  python3 - "$1" "$2" "${3:-}" <<'PY'
import sys
path, expr, other = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(path, encoding="utf-8").read()
s = open(other, encoding="utf-8").read() if other else ""
new = eval(expr, {"t": t, "s": s})
assert new != t, "mutation changed nothing: " + expr
open(path, "w", encoding="utf-8").write(new)
PY
}

# expect <name> <expected exit: 0|1> <tree> [<text the output must contain>]
# With three orchestrators, a mutation can fail the check for a reason other
# than the one it tests: a tree that lost bunshin fails every case at once and
# would make each of them look proven. So a failing case also names the line
# the check must print for it.
expect() {
  "$WORK/$3/scripts/check-shared-blocks.sh" >"$WORK/$3.out" 2>&1
  got=$?; [ "$got" -ne 0 ] && got=1
  if [ "$got" = "$2" ] && { [ -z "${4:-}" ] || grep -qF -- "$4" "$WORK/$3.out"; }; then
    echo "OK   $1"; pass=$((pass + 1))
  elif [ "$got" = "$2" ]; then
    echo "FAIL $1 (exit $got as expected, but no line with \"$4\")"
    sed 's/^/       | /' "$WORK/$3.out"; fail=$((fail + 1))
  else
    echo "FAIL $1 (expected exit $2, got $got)"
    sed 's/^/       | /' "$WORK/$3.out"; fail=$((fail + 1))
  fi
}

copy clean
expect "the repository as it is passes" 0 clean

copy region-drift
mutate "$WORK/region-drift/skills/paint/SKILL.md" \
  't.replace("# 2. Android / Compose", "# 2. Android and Compose", 1)'
expect "a shared region edited in paint only fails" 1 region-drift \
  "FAIL [scan]: shared block drifted between cast and paint"

copy router-drift
mutate "$WORK/router-drift/packaging/genjutsu-router.md" \
  't[:t.index("<!-- genjutsu:router:paint:start -->")] + t[t.index("<!-- genjutsu:router:paint:start -->"):].replace("w=\"${PWD:-$(pwd)}\"; n=0", "w=\"$PWD\"; n=0", 1)'
expect "a router block edited in paint only fails" 1 router-drift \
  "FAIL [router]: the cast and paint blocks of the router drifted apart"

copy router-wrong-p
mutate "$WORK/router-wrong-p/packaging/genjutsu-router.md" \
  't.replace("<!-- genjutsu:router:paint:start -->\n```bash\np=paint", "<!-- genjutsu:router:paint:start -->\n```bash\np=cast", 1)'
expect "a paint router block that runs cast fails" 1 router-wrong-p \
  "FAIL [router]: the paint router block must name its own pipeline"

copy router-no-markers
mutate "$WORK/router-no-markers/packaging/genjutsu-router.md" \
  't.replace("<!-- genjutsu:router:cast:start -->", "", 1)'
expect "a router block without its markers fails" 1 router-no-markers \
  "FAIL [router]: the cast router markers are missing"

copy headless-missing
mutate "$WORK/headless-missing/skills/paint/SKILL.md" \
  't[:t.index("<!-- genjutsu:shared:headless:start -->")] + t[t.index("<!-- genjutsu:shared:headless:end -->") + len("<!-- genjutsu:shared:headless:end -->"):]'
expect "the headless region removed from paint fails" 1 headless-missing \
  "FAIL [headless]: markers missing in cast and/or paint"

copy headless-drift
mutate "$WORK/headless-drift/skills/cast/SKILL.md" \
  't.replace("never install one. Where the thesis wants", "install only what the thesis wants. Where the thesis wants", 1)'
expect "the headless region edited in cast only fails" 1 headless-drift \
  "FAIL [headless]: shared block drifted between cast and paint"

copy escalate-drift
mutate "$WORK/escalate-drift/skills/paint/SKILL.md" \
  't.replace("do not propose it again in this session", "propose it again when the brief grows", 1)'
expect "the escalate region edited in paint only fails" 1 escalate-drift \
  "FAIL [escalate]: shared block drifted between cast and paint"

copy thesis-modules-drift
mutate "$WORK/thesis-modules-drift/skills/paint/SKILL.md" \
  't.replace("so the module\x27s way stands: rewrite", "so the thesis stands: keep", 1)'
expect "the thesis-modules region edited in paint only fails" 1 thesis-modules-drift \
  "FAIL [thesis-modules]: shared block drifted between cast and paint"

# feedback closes the final report of all three. Its link names the form's file
# and field ids, so one copy left on an old link sends reports nowhere.
copy feedback-drift
mutate "$WORK/feedback-drift/skills/paint/SKILL.md" \
  't.replace("template=1-output.yml", "template=output.yml", 1)'
expect "the feedback region edited in paint only fails" 1 feedback-drift \
  "FAIL [feedback]: shared block drifted between cast and paint"

copy feedback-bunshin-drift
mutate "$WORK/feedback-bunshin-drift/skills/bunshin/SKILL.md" \
  't.replace("never open it, never file the issue", "open it when the user is away", 1)'
expect "the feedback region edited in bunshin only fails" 1 feedback-bunshin-drift \
  "FAIL [feedback]: shared block drifted between cast and bunshin"

copy feedback-missing
mutate "$WORK/feedback-missing/skills/bunshin/SKILL.md" \
  't[:t.index("<!-- genjutsu:shared:feedback:start -->")] + t[t.index("<!-- genjutsu:shared:feedback:end -->") + len("<!-- genjutsu:shared:feedback:end -->"):]'
expect "the feedback region removed from bunshin fails" 1 feedback-missing \
  "FAIL [feedback]: markers missing in bunshin"

# The three copies can also be stale together: identical, and pointing at a form
# or a field that no longer exists. The link is checked against the form itself.
copy feedback-form-renamed
mv "$WORK/feedback-form-renamed/.github/ISSUE_TEMPLATE/1-output.yml" \
  "$WORK/feedback-form-renamed/.github/ISSUE_TEMPLATE/1-feedback.yml"
expect "the output form renamed under the link fails" 1 feedback-form-renamed \
  "FAIL [feedback-link]: the link names template=1-output.yml"

copy feedback-id-renamed
mutate "$WORK/feedback-id-renamed/.github/ISSUE_TEMPLATE/1-output.yml" \
  't.replace("    id: host\n", "    id: where\n", 1)'
expect "a field id renamed under the link fails" 1 feedback-id-renamed \
  'FAIL [feedback-link]: the link fills "host"'

# A dropdown has an id too, and GitHub does not fill it from the URL.
copy feedback-dropdown
for f in cast paint bunshin; do
  mutate "$WORK/feedback-dropdown/skills/$f/SKILL.md" \
    't.replace("&model=<model>", "&model=<model>&skill=<skill>", 1)'
done
expect "a link that fills a dropdown fails" 1 feedback-dropdown \
  'FAIL [feedback-link]: the link fills "skill"'

copy feedback-no-link
for f in cast paint bunshin; do
  mutate "$WORK/feedback-no-link/skills/$f/SKILL.md" \
    't.replace("https://github.com/AThevon/genjutsu/issues/new?template=1-output.yml", "https://github.com/AThevon/genjutsu/issues", 1)'
done
expect "a feedback region without the form link fails" 1 feedback-no-link \
  "FAIL [feedback-link]: no issues/new link"

# bunshin carries seven of the regions, compared with cast's, and never escalate
# or thesis-modules.
copy bunshin-drift
mutate "$WORK/bunshin-drift/skills/bunshin/SKILL.md" \
  't.replace("# 2. Android / Compose", "# 2. Android and Compose", 1)'
expect "a shared region edited in bunshin only fails" 1 bunshin-drift \
  "FAIL [scan]: shared block drifted between cast and bunshin"

copy bunshin-region-missing
mutate "$WORK/bunshin-region-missing/skills/bunshin/SKILL.md" \
  't[:t.index("<!-- genjutsu:shared:audit:start -->")] + t[t.index("<!-- genjutsu:shared:audit:end -->") + len("<!-- genjutsu:shared:audit:end -->"):]'
expect "the audit region removed from bunshin fails" 1 bunshin-region-missing \
  "FAIL [audit]: markers missing in bunshin"

# The realistic mistake: escalate copied into bunshin byte for byte, so no
# comparison of contents can see it. Only the marker inventory does.
copy escalate-in-bunshin
mutate "$WORK/escalate-in-bunshin/skills/bunshin/SKILL.md" \
  't.replace("<!-- genjutsu:shared:headless:end -->\n", "<!-- genjutsu:shared:headless:end -->\n\n" + s[s.index("<!-- genjutsu:shared:escalate:start -->"):s.index("<!-- genjutsu:shared:escalate:end -->\n") + len("<!-- genjutsu:shared:escalate:end -->\n")], 1)' \
  "$WORK/escalate-in-bunshin/skills/cast/SKILL.md"
expect "the escalate region copied into bunshin fails" 1 escalate-in-bunshin \
  "FAIL: the guarded regions in bunshin do not match BUNSHIN_REGIONS"

copy bunshin-missing
rm "$WORK/bunshin-missing/skills/bunshin/SKILL.md"
expect "a tree without bunshin fails" 1 bunshin-missing "FAIL [bunshin]: "

copy router-bunshin-drift
mutate "$WORK/router-bunshin-drift/packaging/genjutsu-router.md" \
  't[:t.index("<!-- genjutsu:router:bunshin:start -->")] + t[t.index("<!-- genjutsu:router:bunshin:start -->"):].replace("w=\"${PWD:-$(pwd)}\"; n=0", "w=\"$PWD\"; n=0", 1)'
expect "a router block edited in bunshin only fails" 1 router-bunshin-drift \
  "FAIL [router]: the cast and bunshin blocks of the router drifted apart"

copy router-bunshin-wrong-p
mutate "$WORK/router-bunshin-wrong-p/packaging/genjutsu-router.md" \
  't.replace("<!-- genjutsu:router:bunshin:start -->\n```bash\np=bunshin", "<!-- genjutsu:router:bunshin:start -->\n```bash\np=paint", 1)'
expect "a bunshin router block that runs paint fails" 1 router-bunshin-wrong-p \
  "FAIL [router]: the bunshin router block must name its own pipeline"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
