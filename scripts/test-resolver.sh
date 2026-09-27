#!/usr/bin/env bash
# Tests the $SKILL_BASE resolver that lives inside cast/SKILL.md.
#
# That block has shipped two total failures. In v3.3.0 it resolved to nothing on
# Cowork and the whole pipeline ran without a single one of its sub-skills. In
# v3.4.0 a cache was added to it and made the orchestrator serve the previous
# release's sub-skills after a plugin update, because the old version directory
# is still on disk and passes an "is it a directory" check.
#
# Both were silent. Both would have been caught by this file. The resolver is
# shell embedded in markdown, which is why it had no tests; the fix is to
# extract it and run it against fixture layouts rather than to leave it untested.
# Rule: no new install layout ships without a fixture here.
#
# What this cannot cover: the claude.ai layouts probe /mnt/skills/user, and
# Cowork probes /sessions. Neither is creatable outside a container, so those
# branches are exercised only by the negative case (they must not match here).
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_CAST="$ROOT/skills/cast/SKILL.md"
SRC_ROUTER="$ROOT/packaging/genjutsu-router.md"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/genjutsu-resolver.XXXXXX")"
# $TMPDIR often ends in a slash, which leaves a // in the fixture paths. The
# resolver returns physical paths (pwd -P), so normalise here too or every
# comparison fails on a difference that is not real.
WORK="$(cd "$WORK" && pwd -P)"
trap 'rm -rf "$WORK"' EXIT
echo "source: repository"

# extract <file> <start marker> <end marker> <out>: the fenced code between two
# markers, fences stripped, so what runs here is byte-for-byte what ships.
extract() {
  awk -v s="$2" -v e="$3" '
    index($0, s) == 1          { inregion = 1; next }
    index($0, e) == 1          { inregion = 0 }
    inregion && /^```/         { infence = !infence; next }
    inregion && infence        { print }
  ' "$1" > "$4"
  if [ ! -s "$4" ]; then
    echo "FAIL: could not extract the block between $2 and $3 from $1"
    exit 1
  fi
}

BLOCK="$WORK/resolver.sh"
extract "$SRC_CAST" '<!-- genjutsu:shared:skill-base:start -->' \
  '<!-- genjutsu:shared:skill-base:end -->' "$BLOCK"

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

check_grep() { # <name> <fixed string> <file>: the file must contain the string
  if grep -qF -- "$2" "$3"; then
    echo "OK   $1"
    pass=$((pass + 1))
  else
    echo "FAIL $1"
    echo "       expected to find: $2"
    sed 's/^/       | /' "$3"
    fail=$((fail + 1))
  fi
}

# Fixture builders. The membership rule only accepts a _jutsu that holds
# motion-principles, with the entry file a plugin ships (SKILL) or the one the
# bundle ships (GUIDE).
mkjutsu() { # <dir> <SKILL|GUIDE>
  mkdir -p "$1/motion-principles" "$1/gsap"
  printf 'MOTION PRINCIPLES\n' > "$1/motion-principles/$2.md"
  printf 'GSAP MODULE\n' > "$1/gsap/$2.md"
}
mkplugin() { # <plugin root>: a Claude Code plugin checkout
  mkdir -p "$1/skills/cast" "$1/skills/paint"
  printf 'CAST PIPELINE\n' > "$1/skills/cast/SKILL.md"
  printf 'PAINT PIPELINE\n' > "$1/skills/paint/SKILL.md"
  mkjutsu "$1/skills/_jutsu" SKILL
}
mkbundle() { # <dir>: the genjutsu.zip bundle, unpacked
  mkdir -p "$1/cast" "$1/paint"
  printf 'ROUTER\n' > "$1/SKILL.md"
  printf 'CAST PIPELINE\n' > "$1/cast/GUIDE.md"
  printf 'PAINT PIPELINE\n' > "$1/paint/GUIDE.md"
  mkjutsu "$1/_jutsu" GUIDE
}

# run_block <home> <pwd> <plugin root> <CLAUDE_SKILL_DIR> <GENJUTSU_SKILL_DIR>
# Sources the block in a fresh subshell, as a model's shell call would: no
# nounset, no pipefail. SKILL_BASE goes to $WORK/out, stderr to $WORK/err, and
# the block's own exit status is returned. Assign inside the subshell, not as a
# command prefix: a prefix would apply only to `cd`.
run_block() {
  (
    set +u +o pipefail
    HOME="$1"; export HOME
    CLAUDE_PLUGIN_ROOT="${3:-}"; export CLAUDE_PLUGIN_ROOT
    CLAUDE_SKILL_DIR="${4:-}"; export CLAUDE_SKILL_DIR
    GENJUTSU_SKILL_DIR="${5:-}"; export GENJUTSU_SKILL_DIR
    cd "$2" 2>/dev/null || exit 97
    # shellcheck disable=SC1090
    . "$BLOCK" >/dev/null 2>"$WORK/err"
    rc=$?
    printf '%s' "${SKILL_BASE:-}" > "$WORK/out"
    exit "$rc"
  )
}
resolve() { run_block "$@"; cat "$WORK/out"; }

# --- 1. Claude Code, CLAUDE_PLUGIN_ROOT substituted -------------------------
H="$WORK/t1/home"; P="$WORK/t1/plugin"
mkdir -p "$H" "$WORK/t1/cwd"; mkplugin "$P"
check "claude code: \$CLAUDE_PLUGIN_ROOT wins" \
  "$P/skills/_jutsu" "$(resolve "$H" "$WORK/t1/cwd" "$P")"

# --- 2. Claude Code, placeholder not substituted, cache fallback ------------
H="$WORK/t2/home"; C="$H/.claude/plugins/cache/genjutsu/genjutsu"
mkdir -p "$WORK/t2/cwd"; mkplugin "$C/3.5.0"
check "claude code: falls back to the versioned cache" \
  "$C/3.5.0/skills/_jutsu" "$(resolve "$H" "$WORK/t2/cwd" "")"

# --- 3. The v3.4.0 regression: two versions on disk, newest must win --------
H="$WORK/t3/home"; C="$H/.claude/plugins/cache/genjutsu/genjutsu"
mkdir -p "$WORK/t3/cwd"; mkplugin "$C/3.1.0"; mkplugin "$C/3.5.0"
check "stale version on disk: newest wins, not the leftover" \
  "$C/3.5.0/skills/_jutsu" "$(resolve "$H" "$WORK/t3/cwd" "")"

# 3b. sort -V, not lexical: 3.10.0 must beat 3.9.0
H="$WORK/t3b/home"; C="$H/.claude/plugins/cache/genjutsu/genjutsu"
mkdir -p "$WORK/t3b/cwd"; mkplugin "$C/3.9.0"; mkplugin "$C/3.10.0"
check "version ordering is numeric, not lexical" \
  "$C/3.10.0/skills/_jutsu" "$(resolve "$H" "$WORK/t3b/cwd" "")"

# 3c. The v3.4.0 bug, exercised directly. If any future version consults a cache
# file, a stale one pointing at the previous release will win here and this fails.
H="$WORK/t3c/home"; C="$H/.claude/plugins/cache/genjutsu/genjutsu"
mkdir -p "$WORK/t3c/cwd"; mkplugin "$C/3.1.0"; mkplugin "$C/3.5.0"
printf '%s\n' "$C/3.1.0/skills/_jutsu" > "${TMPDIR:-/tmp}/genjutsu-skill-base"
check "a stale cache file must not be consulted" \
  "$C/3.5.0/skills/_jutsu" "$(resolve "$H" "$WORK/t3c/cwd" "")"
rm -f "${TMPDIR:-/tmp}/genjutsu-skill-base"

# 3d. A newest version directory that is not a genjutsu install (half-deleted
# during an update) must not shadow the complete one below it.
H="$WORK/t3d/home"; C="$H/.claude/plugins/cache/genjutsu/genjutsu"
mkdir -p "$WORK/t3d/cwd" "$C/3.9.9/skills/_jutsu/gsap"; mkplugin "$C/3.5.0"
check "a newer cache dir without motion-principles is skipped" \
  "$C/3.5.0/skills/_jutsu" "$(resolve "$H" "$WORK/t3d/cwd" "")"

# --- 4. Skills-directory install under $HOME --------------------------------
H="$WORK/t4/home"
mkdir -p "$WORK/t4/cwd"; mkbundle "$H/.claude/skills/genjutsu"
check "skills directory under \$HOME" \
  "$H/.claude/skills/genjutsu/_jutsu" "$(resolve "$H" "$WORK/t4/cwd" "")"

# --- 5. Session-rooted mount found by walking up from $PWD ------------------
H="$WORK/t5/home"; S="$WORK/t5/session"
mkdir -p "$H" "$S/project/nested/deep"; mkbundle "$S/.claude/skills/genjutsu"
check "walks up from \$PWD to a session root" \
  "$S/.claude/skills/genjutsu/_jutsu" "$(resolve "$H" "$S/project/nested/deep" "")"

# --- 6. Nothing anywhere: stop, with the install command --------------------
H="$WORK/t6/home"
mkdir -p "$H" "$WORK/t6/cwd"
run_block "$H" "$WORK/t6/cwd" "" "" ""; rc=$?
check "nothing installed: resolves empty rather than guessing" "" "$(cat "$WORK/out")"
check "nothing installed: the block exits non-zero" "1" "$([ "$rc" -ne 0 ] && echo 1 || echo 0)"
check_grep "nothing installed: the message gives the npx command" \
  "npx skills add https://genjutsu.athevon.dev -g" "$WORK/err"
check_grep "nothing installed: the message tells the model to stop" \
  "stop the pipeline" "$WORK/err"

# --- 7. A plugin root that does not exist must not be trusted ---------------
H="$WORK/t7/home"
mkdir -p "$H" "$WORK/t7/cwd"
check "a \$CLAUDE_PLUGIN_ROOT pointing nowhere is discarded" \
  "" "$(resolve "$H" "$WORK/t7/cwd" "$WORK/t7/does-not-exist")"

# --- 8. The block must not write a cache file -------------------------------
# Writing one is how the staleness bug got in. Start from no file and assert
# none appears, rather than comparing counts, which passes if one already exists.
H="$WORK/t8/home"
mkdir -p "$WORK/t8/cwd"; mkbundle "$H/.claude/skills/genjutsu"
rm -f "${TMPDIR:-/tmp}/genjutsu-skill-base"
resolve "$H" "$WORK/t8/cwd" "" >/dev/null
check "writes no cache file" "absent" \
  "$([ -e "${TMPDIR:-/tmp}/genjutsu-skill-base" ] && echo present || echo absent)"

# --- 9. Path 1: GENJUTSU_SKILL_DIR set before the block ---------------------
# Two installs of different versions: a 3.x plugin in the cache and a 4.x
# bundle from npx. The orchestrator that runs is the bundle's, so it must load
# the bundle's modules, never the cache's.
H="$WORK/t9/home"; B="$H/.agents/skills/genjutsu"
mkdir -p "$WORK/t9/cwd"; mkbundle "$B"; mkplugin "$H/.claude/plugins/cache/genjutsu/genjutsu/3.6.0"
# The old plugin is reachable through path 2 as well, so only the order (path 1 first) keeps the bundle.
check "path 1: GENJUTSU_SKILL_DIR wins over an older plugin in the cache" \
  "$B/_jutsu" "$(resolve "$H" "$WORK/t9/cwd" "$H/.claude/plugins/cache/genjutsu/genjutsu/3.6.0" "" "$B/cast")"

# 9b. The reverse: the plugin is the one running. Claude Code substitutes
# CLAUDE_SKILL_DIR with the plugin's skills/cast, and a bundle also sits in
# ~/.agents/skills. The plugin keeps its own modules.
H="$WORK/t9b/home"; P="$WORK/t9b/plugin"
mkdir -p "$WORK/t9b/cwd"; mkplugin "$P"; mkbundle "$H/.agents/skills/genjutsu"
check "path 1: a substituted CLAUDE_SKILL_DIR keeps the plugin on its own modules" \
  "$P/skills/_jutsu" "$(resolve "$H" "$WORK/t9b/cwd" "" "$P/skills/cast" "")"

# 9c. Both variables empty: the skill directory is unknown, and "$DIR/_jutsu"
# would become "/_jutsu". Trace the block and assert no such candidate is tried.
H="$WORK/t9c/home"
mkdir -p "$WORK/t9c/cwd"; mkbundle "$H/.claude/skills/genjutsu"
(
  set +u +o pipefail
  HOME="$H"; export HOME
  CLAUDE_PLUGIN_ROOT=""; CLAUDE_SKILL_DIR=""; GENJUTSU_SKILL_DIR=""
  export CLAUDE_PLUGIN_ROOT CLAUDE_SKILL_DIR GENJUTSU_SKILL_DIR
  cd "$WORK/t9c/cwd" || exit 1
  set -x
  . "$BLOCK" >/dev/null
) 2>"$WORK/trace"
check "path 1: an empty skill dir never probes /_jutsu" "0" \
  "$(grep -cE "[ '](/\.\.)?/_jutsu(/|'|$)" "$WORK/trace")"

# 9d. A relative GENJUTSU_SKILL_DIR with a trailing slash, as a model may write it.
H="$WORK/t9d/home"; B="$WORK/t9d/work/genjutsu"
mkdir -p "$H" "$WORK/t9d/work/project"; mkbundle "$B"
check "path 1: a relative skill dir with a trailing slash resolves" \
  "$B/_jutsu" "$(resolve "$H" "$WORK/t9d/work/project" "" "" "../genjutsu/cast/")"

# --- 10. Bundle copied into the project's .claude/skills --------------------
H="$WORK/t10/home"; PR="$WORK/t10/project"
mkdir -p "$H" "$PR/src"; mkbundle "$PR/.claude/skills/genjutsu"
check "project copy under .claude/skills, found from a subdirectory" \
  "$PR/.claude/skills/genjutsu/_jutsu" "$(resolve "$H" "$PR/src" "")"

# --- 11. npx default layout: .claude/skills/genjutsu -> .agents/skills/genjutsu
# with an old 3.x plugin in the cache. The bundle must win.
H="$WORK/t11/home"; PR="$WORK/t11/project"
mkdir -p "$PR/src" "$PR/.claude/skills"; mkbundle "$PR/.agents/skills/genjutsu"
ln -s "../../.agents/skills/genjutsu" "$PR/.claude/skills/genjutsu"
mkplugin "$H/.claude/plugins/cache/genjutsu/genjutsu/3.6.0"
check "npx project layout (symlink) beats an older plugin in the cache" \
  "$PR/.agents/skills/genjutsu/_jutsu" "$(resolve "$H" "$PR/src" "")"

# --- 12. npx global install: ~/.agents/skills/genjutsu ----------------------
H="$WORK/t12/home"
mkdir -p "$WORK/t12/cwd"; mkbundle "$H/.agents/skills/genjutsu"
check "npx global install under ~/.agents/skills" \
  "$H/.agents/skills/genjutsu/_jutsu" "$(resolve "$H" "$WORK/t12/cwd" "")"

# --- 13. Collision in the shared skills directory ---------------------------
# Another package's cast, and another package's _jutsu without motion-principles,
# sit next to genjutsu. The model even points GENJUTSU_SKILL_DIR at the wrong
# cast. Neither foreign directory may be taken.
H="$WORK/t13/home"; A="$H/.agents/skills"
mkdir -p "$WORK/t13/cwd" "$A/cast" "$A/aaa-kit/_jutsu/gsap"
printf 'FOREIGN CAST\n' > "$A/cast/SKILL.md"
mkbundle "$A/genjutsu"
check "collision: a foreign cast and a foreign _jutsu are never taken" \
  "$A/genjutsu/_jutsu" "$(resolve "$H" "$WORK/t13/cwd" "" "" "$A/cast")"

# --- 14. cast alone: installed from the repo route, no _jutsu anywhere --------
H="$WORK/t14/home"; A="$H/.agents/skills"
mkdir -p "$WORK/t14/cwd" "$A/cast" "$A/paint"
printf 'CAST PIPELINE\n' > "$A/cast/SKILL.md"
printf 'PAINT PIPELINE\n' > "$A/paint/SKILL.md"
run_block "$H" "$WORK/t14/cwd" "" "" "$A/cast"; rc=$?
check "cast alone: the block exits non-zero" "1" "$([ "$rc" -ne 0 ] && echo 1 || echo 0)"
check_grep "cast alone: stderr names genjutsu.athevon.dev" "genjutsu.athevon.dev" "$WORK/err"
check "cast alone: load_skill is never defined, nothing runs on empty" "undefined" "$(
  (
    set +u
    HOME="$H"; export HOME; GENJUTSU_SKILL_DIR="$A/cast"; export GENJUTSU_SKILL_DIR
    CLAUDE_SKILL_DIR=""; CLAUDE_PLUGIN_ROOT=""; export CLAUDE_SKILL_DIR CLAUDE_PLUGIN_ROOT
    cd "$WORK/t14/cwd" || exit 1
    . "$BLOCK" >/dev/null 2>&1
    command -v load_skill >/dev/null 2>&1 && echo defined || echo undefined
  )
)"

# --- 15. npx --copy mode into an agent's own directory ----------------------
H="$WORK/t15/home"
mkdir -p "$WORK/t15/cwd"; mkbundle "$H/.cursor/skills/genjutsu"
check "npx --copy into ~/.cursor/skills" \
  "$H/.cursor/skills/genjutsu/_jutsu" "$(resolve "$H" "$WORK/t15/cwd" "")"
H="$WORK/t15b/home"
mkdir -p "$WORK/t15b/cwd"; mkbundle "$H/.codex/skills/genjutsu"
check "npx --copy into ~/.codex/skills" \
  "$H/.codex/skills/genjutsu/_jutsu" "$(resolve "$H" "$WORK/t15b/cwd" "")"

# --- 16. A home directory with a space in it --------------------------------
H="$WORK/t16/home with space"; P="$WORK/t16/plugin dir"
mkdir -p "$WORK/t16/cwd"; mkbundle "$H/.agents/skills/genjutsu"; mkplugin "$P"
check "a space in \$HOME is quoted through every probe" \
  "$H/.agents/skills/genjutsu/_jutsu" "$(resolve "$H" "$WORK/t16/cwd" "")"
check "a space in the skill dir is quoted through path 1" \
  "$P/skills/_jutsu" "$(resolve "$H" "$WORK/t16/cwd" "" "$P/skills/cast" "")"

# --- 17. load_skill and load_ref --------------------------------------------
# run_loader <home> <snippet>: source the block from a plugin layout, then run
# the snippet in the same shell, as the model does. stdout to $WORK/out.
run_loader() {
  (
    set +u +o pipefail
    HOME="$1"; export HOME
    CLAUDE_PLUGIN_ROOT=""; CLAUDE_SKILL_DIR=""; GENJUTSU_SKILL_DIR=""
    export CLAUDE_PLUGIN_ROOT CLAUDE_SKILL_DIR GENJUTSU_SKILL_DIR
    cd "$WORK" || exit 1
    . "$BLOCK" >/dev/null 2>&1
    eval "$2"
  ) >"$WORK/out" 2>"$WORK/err"
}
H="$WORK/t17/home"
mkbundle "$H/.agents/skills/genjutsu"
mkdir -p "$H/.agents/skills/genjutsu/_jutsu/tells/references"
printf 'WEB TELLS\n' > "$H/.agents/skills/genjutsu/_jutsu/tells/references/web.md"
run_loader "$H" 'load_skill gsap'
check "load_skill prints a GUIDE entry (bundle)" "GSAP MODULE" "$(cat "$WORK/out")"
run_loader "$H" 'load_ref tells references/web.md'
check "load_ref prints a reference file" "WEB TELLS" "$(cat "$WORK/out")"
run_loader "$H" 'load_skill threejs-r3f; echo "rc=$?"'
check "load_skill on a missing module returns 1 and carries on" "rc=1" "$(cat "$WORK/out")"
check_grep "load_skill on a missing module says NOT LOADED" \
  "genjutsu: sub-skill 'threejs-r3f' NOT LOADED" "$WORK/err"
run_loader "$H" 'load_ref tells references/compose.md; echo "rc=$?"'
check "load_ref on a missing file returns 1" "rc=1" "$(cat "$WORK/out")"
check_grep "load_ref on a missing file says NOT LOADED" \
  "genjutsu: reference 'tells/references/compose.md' NOT LOADED" "$WORK/err"
H="$WORK/t17b/home"
mkplugin "$H/.claude/plugins/cache/genjutsu/genjutsu/4.0.0"
run_loader "$H" 'load_skill gsap'
check "load_skill prints a SKILL entry (plugin)" "GSAP MODULE" "$(cat "$WORK/out")"

# --- 18. The block under zsh ------------------------------------------------
# The shell call runs in the user's login shell, which is /bin/zsh on macOS.
# zsh treats unquoted expansions, globs and some names differently, so run the
# two main paths under it. Pinned to /bin/zsh: a nix-packaged zsh 5.9 hangs on
# any $(... | ...) followed by $(dirname ...), the v3 block included.
if [ -x /bin/zsh ]; then
  H="$WORK/t18/home"
  mkdir -p "$WORK/t18/cwd"; mkbundle "$H/.agents/skills/genjutsu"
  got="$(cd "$WORK/t18/cwd" && HOME="$H" CLAUDE_PLUGIN_ROOT="" CLAUDE_SKILL_DIR="" GENJUTSU_SKILL_DIR="" \
    /bin/zsh -fc '. "$1" >/dev/null 2>&1; print -rn -- "$SKILL_BASE"' zsh "$BLOCK")"
  check "zsh: the probes resolve" "$H/.agents/skills/genjutsu/_jutsu" "$got"
  got="$(cd "$WORK/t18/cwd" && HOME="$WORK/t6/home" CLAUDE_PLUGIN_ROOT="" CLAUDE_SKILL_DIR="" GENJUTSU_SKILL_DIR="" \
    /bin/zsh -fc '. "$1" >/dev/null 2>&1; print -rn -- "rc=$?"' zsh "$BLOCK")"
  check "zsh: nothing installed stops with a non-zero status" "rc=1" "$got"
else
  echo "SKIP zsh cases: /bin/zsh is not present (they run on macOS)"
fi

# --- 19. The router of the bundle -------------------------------------------
# The router is the only file a host loads as a skill in the bundle: cast and
# paint are read through it. It must find its own bundle, never another
# package's cast, and hand the pipeline its directory as GENJUTSU_SKILL_DIR.
ROUTER_CAST="$WORK/router-cast.sh"; ROUTER_PAINT="$WORK/router-paint.sh"
extract "$SRC_ROUTER" '<!-- genjutsu:router:cast:start -->' \
  '<!-- genjutsu:router:cast:end -->' "$ROUTER_CAST"
extract "$SRC_ROUTER" '<!-- genjutsu:router:paint:start -->' \
  '<!-- genjutsu:router:paint:end -->' "$ROUTER_PAINT"

# run_router <block> <home> <pwd> <CLAUDE_SKILL_DIR> <GENJUTSU_BUNDLE_DIR>
run_router() {
  (
    set +u +o pipefail
    HOME="$2"; export HOME
    CLAUDE_SKILL_DIR="${4:-}"; export CLAUDE_SKILL_DIR
    GENJUTSU_BUNDLE_DIR="${5:-}"; export GENJUTSU_BUNDLE_DIR
    cd "$3" 2>/dev/null || exit 97
    # shellcheck disable=SC1090
    . "$1"
  ) >"$WORK/out" 2>"$WORK/err"
}

H="$WORK/r1/home"; B="$WORK/r1/skills/genjutsu"
mkdir -p "$H" "$WORK/r1/cwd"; mkbundle "$B"
run_router "$ROUTER_CAST" "$H" "$WORK/r1/cwd" "$B" ""
check_grep "router: a substituted CLAUDE_SKILL_DIR prints the cast dir" "GENJUTSU_SKILL_DIR=$B/cast" "$WORK/out"
check_grep "router: then prints the cast pipeline" "CAST PIPELINE" "$WORK/out"
run_router "$ROUTER_PAINT" "$H" "$WORK/r1/cwd" "" "$B"
check_grep "router: GENJUTSU_BUNDLE_DIR set by the model, paint block" "GENJUTSU_SKILL_DIR=$B/paint" "$WORK/out"
check_grep "router: the paint block prints the paint pipeline" "PAINT PIPELINE" "$WORK/out"

H="$WORK/r2/home"; A="$H/.agents/skills"
mkdir -p "$WORK/r2/cwd" "$A/cast" "$A/aaa-kit/cast"
printf 'FOREIGN CAST\n' > "$A/cast/SKILL.md"
printf 'FOREIGN CAST\n' > "$A/aaa-kit/cast/SKILL.md"
mkbundle "$A/genjutsu"
run_router "$ROUTER_CAST" "$H" "$WORK/r2/cwd" "" ""
check_grep "router: no substitution, finds ~/.agents/skills/genjutsu" "GENJUTSU_SKILL_DIR=$A/genjutsu/cast" "$WORK/out"
check "router: a foreign cast is never printed" "0" "$(grep -c 'FOREIGN CAST' "$WORK/out")"

H="$WORK/r3/home"
mkdir -p "$WORK/r3/cwd"; mkbundle "$H/.cursor/skills/genjutsu"
run_router "$ROUTER_CAST" "$H" "$WORK/r3/cwd" "" ""
check_grep "router: npx --copy into ~/.cursor/skills" "GENJUTSU_SKILL_DIR=$H/.cursor/skills/genjutsu/cast" "$WORK/out"

H="$WORK/r4/home"; PR="$WORK/r4/project"
mkdir -p "$H" "$PR/src" "$PR/.claude/skills"; mkbundle "$PR/.agents/skills/genjutsu"
ln -s "../../.agents/skills/genjutsu" "$PR/.claude/skills/genjutsu"
run_router "$ROUTER_CAST" "$H" "$PR/src" "" ""
check_grep "router: npx project layout through the symlink" "GENJUTSU_SKILL_DIR=$PR/.agents/skills/genjutsu/cast" "$WORK/out"

H="$WORK/r5/home"
mkdir -p "$WORK/r5/cwd" "$H/.agents/skills/cast"
printf 'FOREIGN CAST\n' > "$H/.agents/skills/cast/SKILL.md"
run_router "$ROUTER_CAST" "$H" "$WORK/r5/cwd" "" ""; rc=$?
check "router: no bundle anywhere exits non-zero" "1" "$([ "$rc" -ne 0 ] && echo 1 || echo 0)"
check_grep "router: no bundle gives the npx command" \
  "npx skills add https://genjutsu.athevon.dev -g" "$WORK/err"
check "router: no bundle prints no pipeline" "0" "$(grep -c 'PIPELINE' "$WORK/out")"

# The router hands the pipeline its GENJUTSU_SKILL_DIR; the pipeline's block
# must then resolve the bundle's modules from it, end to end.
H="$WORK/r6/home"; B="$WORK/r6/skills/genjutsu"
mkdir -p "$H" "$WORK/r6/cwd"; mkbundle "$B"
mkplugin "$H/.claude/plugins/cache/genjutsu/genjutsu/3.6.0"
run_router "$ROUTER_CAST" "$H" "$WORK/r6/cwd" "$B" ""
dir="$(sed -n 's/^GENJUTSU_SKILL_DIR=//p' "$WORK/out")"
check "router to resolver: the printed dir resolves the bundle's modules" \
  "$B/_jutsu" "$(resolve "$H" "$WORK/r6/cwd" "" "" "$dir")"

# --- summary ---
echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
