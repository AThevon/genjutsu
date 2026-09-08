#!/usr/bin/env bash
# Tests the $SKILL_BASE resolver that lives inside cast/SKILL.md.
#
# That block has shipped two total failures. In v3.3.0 it resolved to nothing on
# Cowork and the whole pipeline ran without a single one of its fifteen
# sub-skills. In v3.4.0 a cache was added to it and made the orchestrator serve
# the previous release's sub-skills after a plugin update, because the old
# version directory is still on disk and passes an "is it a directory" check.
#
# Both were silent. Both would have been caught by this file. The resolver is
# shell embedded in markdown, which is why it had no tests; the fix is to
# extract it and run it against fixture layouts rather than to leave it untested.
#
# What this cannot cover: the two claude.ai layouts probe /mnt/skills/user, and
# Cowork probes /sessions. Neither is creatable outside a container, so those
# branches are exercised only by the negative case (they must not match here).
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CAST="$ROOT/skills/cast/SKILL.md"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/genjutsu-resolver.XXXXXX")"
# $TMPDIR often ends in a slash, which leaves a // in the fixture paths. The
# resolver normalises what it returns, so normalise here too or every
# comparison fails on a difference that is not real.
WORK="$(cd "$WORK" && pwd -P)"
trap 'rm -rf "$WORK"' EXIT

# Pull the guarded region out of the markdown and strip the fences, so what runs
# here is byte-for-byte what ships.
BLOCK="$WORK/resolver.sh"
awk '
  /<!-- genjutsu:shared:skill-base:start -->/ { inregion = 1; next }
  /<!-- genjutsu:shared:skill-base:end -->/   { inregion = 0 }
  inregion && /^```/                          { infence = !infence; next }
  inregion && infence                         { print }
' "$CAST" > "$BLOCK"

if [ ! -s "$BLOCK" ]; then
  echo "FAIL: could not extract the skill-base block from $CAST"
  exit 1
fi

pass=0
fail=0

# resolve <fake-home> <fake-pwd> <plugin-root>  -> prints the resolved SKILL_BASE
resolve() {
  # Assign inside the subshell, not as a command prefix: a prefix would apply
  # only to `cd` and the sourced block would still see the real $HOME.
  (
    HOME="$1"; export HOME
    CLAUDE_PLUGIN_ROOT="${3:-}"; export CLAUDE_PLUGIN_ROOT
    cd "$2" 2>/dev/null || exit 1
    # shellcheck disable=SC1090
    . "$BLOCK" >/dev/null 2>&1
    printf '%s' "${SKILL_BASE:-}"
  )
}

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

# --- 1. Claude Code, CLAUDE_PLUGIN_ROOT substituted -------------------------
H="$WORK/t1/home"; P="$WORK/t1/plugin"
mkdir -p "$H" "$P/skills/_jutsu/gsap" "$WORK/t1/cwd"
check "claude code: \$CLAUDE_PLUGIN_ROOT wins" \
  "$P/skills/_jutsu" "$(resolve "$H" "$WORK/t1/cwd" "$P")"

# --- 2. Claude Code, placeholder not substituted, cache fallback ------------
H="$WORK/t2/home"
mkdir -p "$H/.claude/plugins/cache/genjutsu/genjutsu/3.5.0/skills/_jutsu/gsap" "$WORK/t2/cwd"
check "claude code: falls back to the versioned cache" \
  "$H/.claude/plugins/cache/genjutsu/genjutsu/3.5.0/skills/_jutsu" \
  "$(resolve "$H" "$WORK/t2/cwd" "")"

# --- 3. The v3.4.0 regression: two versions on disk, newest must win --------
H="$WORK/t3/home"
mkdir -p "$H/.claude/plugins/cache/genjutsu/genjutsu/3.1.0/skills/_jutsu/gsap" \
         "$H/.claude/plugins/cache/genjutsu/genjutsu/3.5.0/skills/_jutsu/gsap" "$WORK/t3/cwd"
check "stale version on disk: newest wins, not the leftover" \
  "$H/.claude/plugins/cache/genjutsu/genjutsu/3.5.0/skills/_jutsu" \
  "$(resolve "$H" "$WORK/t3/cwd" "")"

# 3b. sort -V, not lexical: 3.10.0 must beat 3.9.0
H="$WORK/t3b/home"
mkdir -p "$H/.claude/plugins/cache/genjutsu/genjutsu/3.9.0/skills/_jutsu/gsap" \
         "$H/.claude/plugins/cache/genjutsu/genjutsu/3.10.0/skills/_jutsu/gsap" "$WORK/t3b/cwd"
check "version ordering is numeric, not lexical" \
  "$H/.claude/plugins/cache/genjutsu/genjutsu/3.10.0/skills/_jutsu" \
  "$(resolve "$H" "$WORK/t3b/cwd" "")"

# 3c. The v3.4.0 bug, exercised directly. If any future version consults a cache
# file, a stale one pointing at the previous release will win here and this fails.
H="$WORK/t3c/home"
mkdir -p "$H/.claude/plugins/cache/genjutsu/genjutsu/3.1.0/skills/_jutsu/gsap" \
         "$H/.claude/plugins/cache/genjutsu/genjutsu/3.5.0/skills/_jutsu/gsap" "$WORK/t3c/cwd"
printf '%s\n' "$H/.claude/plugins/cache/genjutsu/genjutsu/3.1.0/skills/_jutsu" \
  > "${TMPDIR:-/tmp}/genjutsu-skill-base"
check "a stale cache file must not be consulted" \
  "$H/.claude/plugins/cache/genjutsu/genjutsu/3.5.0/skills/_jutsu" \
  "$(resolve "$H" "$WORK/t3c/cwd" "")"
rm -f "${TMPDIR:-/tmp}/genjutsu-skill-base"

# --- 4. Skills-directory install under $HOME --------------------------------
H="$WORK/t4/home"
mkdir -p "$H/.claude/skills/genjutsu/_jutsu/gsap" "$WORK/t4/cwd"
check "skills directory under \$HOME" \
  "$H/.claude/skills/genjutsu/_jutsu" "$(resolve "$H" "$WORK/t4/cwd" "")"

# --- 5. Session-rooted mount found by walking up from $PWD ------------------
H="$WORK/t5/home"; S="$WORK/t5/session"
mkdir -p "$H" "$S/.claude/skills/genjutsu/_jutsu/gsap" "$S/project/nested/deep"
check "walks up from \$PWD to a session root" \
  "$S/.claude/skills/genjutsu/_jutsu" "$(resolve "$H" "$S/project/nested/deep" "")"

# --- 6. Nothing anywhere: must resolve empty, not to a bogus path -----------
H="$WORK/t6/home"
mkdir -p "$H" "$WORK/t6/cwd"
check "nothing installed: resolves empty rather than guessing" \
  "" "$(resolve "$H" "$WORK/t6/cwd" "")"

# --- 7. A plugin root that does not exist must not be trusted ---------------
H="$WORK/t7/home"
mkdir -p "$H" "$WORK/t7/cwd"
check "a \$CLAUDE_PLUGIN_ROOT pointing nowhere is discarded" \
  "" "$(resolve "$H" "$WORK/t7/cwd" "$WORK/t7/does-not-exist")"

# --- 8. The block must not write a cache file -------------------------------
# Writing one is how the staleness bug got in. Start from no file and assert
# none appears, rather than comparing counts, which passes if one already exists.
H="$WORK/t8/home"
mkdir -p "$H/.claude/skills/genjutsu/_jutsu/gsap" "$WORK/t8/cwd"
rm -f "${TMPDIR:-/tmp}/genjutsu-skill-base"
resolve "$H" "$WORK/t8/cwd" "" >/dev/null
check "writes no cache file" "absent" \
  "$([ -e "${TMPDIR:-/tmp}/genjutsu-skill-base" ] && echo present || echo absent)"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
