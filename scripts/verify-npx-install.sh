#!/usr/bin/env bash
# Verifies the npx channel end to end, in a throwaway HOME, with the real
# `npx skills` CLI. Run by hand before and after a release, never in CI: it
# downloads the CLI from npm, and the live mode reads the production site.
#
#   scripts/verify-npx-install.sh local [zip]
#     Serves a well-known index from 127.0.0.1 (python3 -m http.server). The
#     index first points at a small test archive: `npx skills add <url> -g`
#     must install it. Then the index is switched to <zip> (default:
#     dist/genjutsu.zip, so run ./package-for-claude-ai.sh first):
#     `npx skills update -g` must report and install the new version. Finally
#     the skill-base block is extracted from the installed cast/GUIDE.md and
#     run with that HOME: SKILL_BASE must be ~/.agents/skills/genjutsu/_jutsu.
#
#   scripts/verify-npx-install.sh live [site]
#     Reads the deployed index (default https://genjutsu.athevon.dev), checks
#     that its URL names the latest release (and EXPECT_TAG when set) and that
#     its digest matches a fresh download, installs from the site, and runs
#     the same skill-base check.
#
# Env: SKILLS_CLI, the npm package npx runs (default "skills"; skills@1.7.0 to
# pin). `npx -y` and the CLI's own `-y` only answer prompts a terminal would
# show: the flags a user types (-g) are the ones under test.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODE="${1:-}"
SKILLS_CLI="${SKILLS_CLI:-skills}"
SCHEMA="https://schemas.agentskills.io/discovery/0.2.0/schema.json"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/genjutsu-npx.XXXXXX")"
# Physical path: the resolver may normalise what it returns, and on macOS
# $TMPDIR sits behind the /var -> /private/var symlink.
WORK="$(cd "$WORK" && pwd -P)"
H="$WORK/home"
mkdir -p "$H/.claude" "$WORK/cwd" "$WORK/tmp" "$WORK/srv/.well-known/agent-skills"
# ~/.claude exists so the CLI detects Claude Code, as it would on a real
# machine; without any detected agent `-y` installs into every agent it knows.

SERVER_PID=""
# shellcheck disable=SC2329  # called from the EXIT trap
stop_server() {
  [ -n "$SERVER_PID" ] || return 0
  kill "$SERVER_PID" 2>/dev/null
  wait "$SERVER_PID" 2>/dev/null
  SERVER_PID=""
}
trap 'stop_server; rm -rf "$WORK"' EXIT

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
finish() {
  echo
  echo "$pass passed, $fail failed"
  [ "$fail" -eq 0 ] || exit 1
  exit 0
}

# Everything the CLI sees comes from here: no CLAUDE_CONFIG_DIR, XDG_*,
# CODEX_HOME or npm cache of the real user leaks in.
iso() {
  (cd "$WORK/cwd" && env -i HOME="$H" PATH="$PATH" TMPDIR="$WORK/tmp" \
    DISABLE_TELEMETRY=1 DO_NOT_TRACK=1 \
    npm_config_cache="$WORK/npm-cache" npm_config_update_notifier=false \
    "$@" </dev/null)
}

sha256_of() { python3 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }

lock_digest() {
  python3 - "$H/.agents/.skill-lock.json" <<'PY'
import json, sys
try:
    print(json.load(open(sys.argv[1]))["skills"]["genjutsu"]["wellKnownDigest"])
except Exception:
    print("")
PY
}

# The block exactly as it ships inside the installed bundle, run with the
# throwaway HOME, from a directory with no skills tree above it, and with
# none of the variables a host could substitute.
check_skill_base() {
  guide="$H/.agents/skills/genjutsu/cast/GUIDE.md"
  block="$WORK/skill-base.sh"
  awk '
    /<!-- genjutsu:shared:skill-base:start -->/ { inregion = 1; next }
    /<!-- genjutsu:shared:skill-base:end -->/   { inregion = 0 }
    inregion && /^```/                          { infence = !infence; next }
    inregion && infence                         { print }
  ' "$guide" > "$block" 2>/dev/null
  check "skill-base block extracted from the installed cast/GUIDE.md" "yes" \
    "$([ -s "$block" ] && echo yes || echo no)"
  cat > "$WORK/probe.sh" <<'SH'
. "$1" >/dev/null 2>&1
printf 'SKILL_BASE=%s\n' "${SKILL_BASE:-}"
load_skill motion-principles 2>/dev/null | head -5 | grep -q '^name: motion-principles' && echo "MOTION=loaded"
load_skill tells 2>/dev/null | head -5 | grep -q '^name: tells' && echo "TELLS=loaded"
SH
  out="$(cd "$WORK/cwd" && env -i HOME="$H" PATH="$PATH" bash "$WORK/probe.sh" "$block")"
  check "SKILL_BASE resolves to ~/.agents/skills/genjutsu/_jutsu" \
    "$H/.agents/skills/genjutsu/_jutsu" "$(printf '%s\n' "$out" | sed -n 's/^SKILL_BASE=//p')"
  check "load_skill motion-principles reads the bundled module" "yes" \
    "$(printf '%s\n' "$out" | grep -q '^MOTION=loaded$' && echo yes || echo no)"
  check "load_skill tells reads the bundled module" "yes" \
    "$(printf '%s\n' "$out" | grep -q '^TELLS=loaded$' && echo yes || echo no)"
}

write_index() { # <archive file name under srv/>
  python3 - "$WORK/srv" "$1" "$PORT" "$SCHEMA" <<'PY'
import hashlib, json, sys
srv, name, port, schema = sys.argv[1:5]
data = open(f"{srv}/{name}", "rb").read()
index = {"$schema": schema, "skills": [{
    "name": "genjutsu",
    "type": "archive",
    "description": "genjutsu npx verification fixture",
    "url": f"http://127.0.0.1:{port}/{name}",
    "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
}]}
json.dump(index, open(f"{srv}/.well-known/agent-skills/index.json", "w"), indent=2)
PY
}

run_local() {
  zip="${1:-$ROOT/dist/genjutsu.zip}"
  [ -f "$zip" ] || { echo "verify-npx-install: $zip not found (run ./package-for-claude-ai.sh)" >&2; exit 2; }
  check "the release archive has SKILL.md at its root" "yes" \
    "$(unzip -Z1 "$zip" | grep -qx 'SKILL.md' && echo yes || echo no)"
  cp "$zip" "$WORK/srv/genjutsu-release.zip"

  # The "previous version": a minimal valid archive that the release must replace.
  python3 - "$WORK/srv/genjutsu-previous.zip" <<'PY'
import sys, zipfile
with zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("SKILL.md", "---\nname: genjutsu\ndescription: genjutsu npx verification fixture, previous version.\n---\n\nFixture.\n")
    z.writestr("PREVIOUS-FIXTURE", "if this file survives the update, the update did not install\n")
PY

  PORT="$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1]);s.close()')"
  python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$WORK/srv" >/dev/null 2>&1 &
  SERVER_PID=$!
  write_index genjutsu-previous.zip
  for _ in $(seq 1 50); do
    curl -fsS "http://127.0.0.1:$PORT/.well-known/agent-skills/index.json" >/dev/null 2>&1 && break
    sleep 0.1
  done
  URL="http://127.0.0.1:$PORT"

  iso npx -y "$SKILLS_CLI" add "$URL" -g -y >"$WORK/add.log" 2>&1
  check "npx skills add <url> -g exits 0" "0" "$?"
  check "installed into ~/.agents/skills/genjutsu" "yes" \
    "$([ -f "$H/.agents/skills/genjutsu/PREVIOUS-FIXTURE" ] && echo yes || echo no)"
  check "linked for Claude Code at ~/.claude/skills/genjutsu" "yes" \
    "$([ -e "$H/.claude/skills/genjutsu/SKILL.md" ] && echo yes || echo no)"
  check "recorded in the global lock with the index digest" \
    "sha256:$(sha256_of "$WORK/srv/genjutsu-previous.zip")" "$(lock_digest)"

  iso npx -y "$SKILLS_CLI" update -g >"$WORK/update0.log" 2>&1
  check "update -g with an unchanged index updates nothing" "no" \
    "$(grep -q 'Updated genjutsu' "$WORK/update0.log" && echo yes || echo no)"

  write_index genjutsu-release.zip
  iso npx -y "$SKILLS_CLI" update -g >"$WORK/update1.log" 2>&1
  check "update -g after the switch exits 0" "0" "$?"
  check "update -g reports the new version" "yes" \
    "$(grep -q 'Updated genjutsu' "$WORK/update1.log" && echo yes || echo no)"
  check "the lock now carries the release digest" \
    "sha256:$(sha256_of "$WORK/srv/genjutsu-release.zip")" "$(lock_digest)"
  check "the previous version's files are gone" "no" \
    "$([ -e "$H/.agents/skills/genjutsu/PREVIOUS-FIXTURE" ] && echo yes || echo no)"
  check "the release's cast/GUIDE.md is installed" "yes" \
    "$([ -f "$H/.agents/skills/genjutsu/cast/GUIDE.md" ] && echo yes || echo no)"

  check_skill_base
  if [ "$fail" -ne 0 ]; then
    echo "--- npx logs ---"
    tail -n 20 "$WORK/add.log" "$WORK/update0.log" "$WORK/update1.log"
  fi
  finish
}

run_live() {
  site="${1:-https://genjutsu.athevon.dev}"
  site="${site%/}"
  curl -fsS --max-time 30 "$site/.well-known/agent-skills/index.json" -o "$WORK/index.json"
  check "the deployed index answers" "0" "$?"
  [ -s "$WORK/index.json" ] || finish
  python3 - "$WORK/index.json" "$SCHEMA" > "$WORK/index.vars" <<'PY'
import json, re, sys
d = json.load(open(sys.argv[1]))
s = d["skills"][0]
m = re.fullmatch(r"https://github\.com/AThevon/genjutsu/releases/download/(v\d+\.\d+\.\d+)/genjutsu\.zip", s["url"])
print("SCHEMA_OK=" + ("yes" if d.get("$schema") == sys.argv[2] else "no"))
print("COUNT=" + str(len(d["skills"])))
print("NAME=" + s["name"])
print("TYPE=" + s["type"])
print("URL=" + s["url"])
print("TAG=" + (m.group(1) if m else ""))
print("DIGEST=" + s["digest"])
PY
  SCHEMA_OK="$(sed -n 's/^SCHEMA_OK=//p' "$WORK/index.vars")"
  COUNT="$(sed -n 's/^COUNT=//p' "$WORK/index.vars")"
  NAME="$(sed -n 's/^NAME=//p' "$WORK/index.vars")"
  TYPE="$(sed -n 's/^TYPE=//p' "$WORK/index.vars")"
  URL="$(sed -n 's/^URL=//p' "$WORK/index.vars")"
  TAG="$(sed -n 's/^TAG=//p' "$WORK/index.vars")"
  DIGEST="$(sed -n 's/^DIGEST=//p' "$WORK/index.vars")"
  check "index \$schema is discovery 0.2.0" "yes" "$SCHEMA_OK"
  check "index lists exactly one skill" "1" "$COUNT"
  check "that skill is genjutsu, an archive" "genjutsu archive" "$NAME $TYPE"
  LATEST="$(curl -sS -o /dev/null -w '%{redirect_url}' --max-time 20 https://github.com/AThevon/genjutsu/releases/latest | sed 's#.*/releases/tag/##')"
  check "index URL names the latest release" "$LATEST" "$TAG"
  if [ -n "${EXPECT_TAG:-}" ]; then
    check "index URL names $EXPECT_TAG" "$EXPECT_TAG" "$TAG"
  fi
  curl -fsSL --max-time 120 "$URL" -o "$WORK/fresh.zip"
  check "index digest matches a fresh download of its URL" "$DIGEST" "sha256:$(sha256_of "$WORK/fresh.zip")"

  iso npx -y "$SKILLS_CLI" add "$site" -g -y >"$WORK/add.log" 2>&1
  check "npx skills add $site -g exits 0" "0" "$?"
  check "the lock carries the index digest" "$DIGEST" "$(lock_digest)"
  check "cast/GUIDE.md is installed" "yes" \
    "$([ -f "$H/.agents/skills/genjutsu/cast/GUIDE.md" ] && echo yes || echo no)"
  check_skill_base
  if [ "$fail" -ne 0 ]; then
    echo "--- npx log ---"
    tail -n 20 "$WORK/add.log"
  fi
  finish
}

case "$MODE" in
  local) shift; run_local "$@" ;;
  live)  shift; run_live "$@" ;;
  *) echo "usage: scripts/verify-npx-install.sh local [zip] | live [site]" >&2; exit 2 ;;
esac
