#!/usr/bin/env bash
# Fails when a skill a host can invoke carries a token Claude Code would rewrite
# before the model reads it.
#
# Claude Code substitutes placeholders in the text of an invoked skill
# (https://code.claude.com/docs/en/skills, "Available string substitutions"):
# the arguments typed after the slash command replace $ARGUMENTS, $ARGUMENTS[N]
# and $N, and a named argument declared in the `arguments` frontmatter replaces
# its $name. A shell function that read its first parameter as a dollar sign and
# a 1 therefore received the second word the user typed: v4.1.0 shipped with
# genjutsu_is_jutsu checking "the/motion-principles/SKILL.md" after
# "/genjutsu:cast make the pricing cards feel physical", and every module failed
# to resolve unless the model noticed and repaired the code.
#
# Rules, over skills/*/SKILL.md and packaging/genjutsu-router.md (the files a
# host loads as a skill; the _jutsu modules are read with cat and never pass
# through substitution):
#   positional  a dollar sign followed by a digit, by {digit, by ARGUMENTS, by @
#               or by *. The last two are not substituted today; they read the
#               same argument list and are banned so that nothing depends on it.
#               Read arguments with a bare `for name; do` instead. An escaped
#               form is banned too: the escape rule is subtle (a doubled
#               backslash still expands), and the code has no use for it.
#   named       a $name matching a name declared in the `arguments` frontmatter.
#   claude-var  a braced CLAUDE_ variable other than CLAUDE_SKILL_DIR and
#               CLAUDE_PLUGIN_ROOT, the two genjutsu wants substituted. The
#               others (CLAUDE_SESSION_ID, CLAUDE_EFFORT, CLAUDE_PROJECT_DIR,
#               CLAUDE_PLUGIN_DATA) would be rewritten too, and nothing here
#               expects them.
#   injection   an exclamation mark followed by a backtick at the start of a
#               line or after whitespace, or a fence opened as three backticks
#               and an exclamation mark: Claude Code runs that command when the
#               skill loads and pastes its output in place.
#
# Usage: scripts/check-skill-placeholders.sh [repo root]
#        scripts/check-skill-placeholders.sh --self-test
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

run_check() { # <repo root>
  python3 - "$1" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
files = sorted(root.glob("skills/*/SKILL.md"))
router = root / "packaging" / "genjutsu-router.md"
if router.is_file():
    files.append(router)
if not files:
    print(f"FAIL: no skill file found under {root}: the check would pass on nothing")
    sys.exit(1)

D = "\\$"  # a literal dollar sign in the patterns below
POSITIONAL = re.compile(D + r"(?:[0-9]|\{[0-9@*]|ARGUMENTS|[@*])")
CLAUDE_VAR = re.compile(D + r"\{(CLAUDE_[A-Z_]+)\}")
WANTED = {"CLAUDE_SKILL_DIR", "CLAUDE_PLUGIN_ROOT"}
INJECTION = re.compile(r"(?:^|\s)!`|^\s*```!")


def declared_arguments(text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    end = text.find("\n---", 4)
    if end < 0:
        return []
    for line in text[4:end].splitlines():
        m = re.match(r"arguments:\s*(.*)$", line)
        if not m:
            continue
        value = m.group(1).strip()
        if value.startswith("["):
            value = value.strip("[]")
            return [n.strip().strip("'\"") for n in value.split(",") if n.strip()]
        if value:
            return value.split()
        # A YAML block list on the following lines.
        names = []
        after = text[4:end].splitlines()
        i = after.index(line) + 1
        while i < len(after) and re.match(r"\s+-\s+", after[i]):
            names.append(re.sub(r"^\s+-\s+", "", after[i]).strip().strip("'\""))
            i += 1
        return names
    return []


failed = False
for path in files:
    rel = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    names = declared_arguments(text)
    named = re.compile(D + r"(?:" + "|".join(re.escape(n) for n in names) + r")(?![A-Za-z0-9_-])") if names else None
    for n, line in enumerate(text.splitlines(), 1):
        hits = []
        for m in POSITIONAL.finditer(line):
            hits.append(("positional", m.group(0)))
        if named:
            for m in named.finditer(line):
                hits.append(("named", m.group(0)))
        for m in CLAUDE_VAR.finditer(line):
            if m.group(1) not in WANTED:
                hits.append(("claude-var", m.group(0)))
        if INJECTION.search(line):
            hits.append(("injection", line.strip()[:40]))
        for rule, token in hits:
            failed = True
            print(f"FAIL [{rule}] {rel}:{n}: {token}")
            print(f"       | {line.strip()}")

if failed:
    print()
    print("Claude Code rewrites these tokens in an invoked skill before the model reads it.")
    print("Read shell arguments with a bare `for name; do`, never as positional parameters")
    print("written out; see the comment at the top of scripts/check-skill-placeholders.sh.")
    sys.exit(1)
print(f"OK   [placeholders]: no substitutable token in {len(files)} invocable skill files")
PY
}

self_test() {
  local work pass=0 fail=0
  work="$(mktemp -d "${TMPDIR:-/tmp}/genjutsu-placeholders.XXXXXX")"
  trap 'rm -rf "$work"' RETURN

  copy() { # <name>: the real invocable files, in a tree of their own
    mkdir -p "$work/$1/skills" "$work/$1/packaging"
    for s in cast paint bunshin; do
      mkdir -p "$work/$1/skills/$s"
      cp "$ROOT/skills/$s/SKILL.md" "$work/$1/skills/$s/SKILL.md"
    done
    cp "$ROOT/packaging/genjutsu-router.md" "$work/$1/packaging/genjutsu-router.md"
  }
  # mutate <file> <python expression over t>
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
  # expect <name> <0|1> <tree> [<text the output must contain>]
  expect() {
    run_check "$work/$3" >"$work/$3.out" 2>&1
    local got=$?; [ "$got" -ne 0 ] && got=1
    if [ "$got" = "$2" ] && { [ -z "${4:-}" ] || grep -qF -- "$4" "$work/$3.out"; }; then
      echo "OK   $1"; pass=$((pass + 1))
    else
      echo "FAIL $1 (expected exit $2${4:+ and a line with \"$4\"}, got $got)"
      sed 's/^/       | /' "$work/$3.out"; fail=$((fail + 1))
    fi
  }
  # One dollar sign, spelled in Python so this file carries no token of its own.
  local anchor='genjutsu_is_jutsu() {'

  copy clean
  expect "the repository as it is passes" 0 clean

  copy positional
  mutate "$work/positional/skills/cast/SKILL.md" \
    "t.replace('$anchor', '$anchor\n  [ -d \"' + chr(36) + '1\" ] || return 1', 1)"
  expect "a first parameter written out in cast fails" 1 positional "FAIL [positional] skills/cast/SKILL.md"

  copy braced
  mutate "$work/braced/skills/paint/SKILL.md" \
    "t.replace('$anchor', '$anchor\n  [ -d \"' + chr(36) + '{2}\" ] || return 1', 1)"
  expect "a braced positional parameter in paint fails" 1 braced "FAIL [positional] skills/paint/SKILL.md"

  copy arguments
  mutate "$work/arguments/skills/bunshin/SKILL.md" \
    "t.replace('$anchor', '$anchor\n  echo \"' + chr(36) + 'ARGUMENTS[0]\"', 1)"
  expect "ARGUMENTS in bunshin fails" 1 arguments "FAIL [positional] skills/bunshin/SKILL.md"

  copy all-args
  mutate "$work/all-args/packaging/genjutsu-router.md" \
    "t.replace('genjutsu_bundle_entry() {', 'genjutsu_bundle_entry() {\n  set -- ' + chr(34) + chr(36) + '@' + chr(34), 1)"
  expect "the whole argument list in the router fails" 1 all-args "FAIL [positional] packaging/genjutsu-router.md"

  copy named
  mutate "$work/named/skills/cast/SKILL.md" \
    "t.replace('allowed-tools:', 'arguments: [target, mood]\nallowed-tools:', 1).replace('$anchor', '$anchor\n  echo ' + chr(36) + 'mood', 1)"
  expect "a declared named argument used in the body fails" 1 named "FAIL [named] skills/cast/SKILL.md"

  copy claude-var
  mutate "$work/claude-var/skills/paint/SKILL.md" \
    "t.replace('$anchor', '$anchor\n  echo ' + chr(36) + '{CLAUDE_SESSION_ID}', 1)"
  expect "a CLAUDE_ variable genjutsu does not want fails" 1 claude-var "FAIL [claude-var] skills/paint/SKILL.md"

  copy injection
  mutate "$work/injection/skills/cast/SKILL.md" \
    "t.replace('## ', 'Context: !' + chr(96) + 'ls' + chr(96) + '\n\n## ', 1)"
  expect "an inline command injection fails" 1 injection "FAIL [injection] skills/cast/SKILL.md"

  copy injection-fence
  mutate "$work/injection-fence/packaging/genjutsu-router.md" \
    "t.replace('## Loading it', chr(96) * 3 + '!\nls\n' + chr(96) * 3 + '\n\n## Loading it', 1)"
  expect "a fenced command injection fails" 1 injection-fence "FAIL [injection] packaging/genjutsu-router.md"

  mkdir -p "$work/empty"
  expect "a tree with no skill file fails" 1 empty "FAIL: no skill file found"

  echo
  echo "$pass passed, $fail failed"
  [ "$fail" -eq 0 ] || return 1
  echo "OK   [placeholders self-test]: every rule can fail"
}

case "${1:-}" in
  --self-test) self_test ;;
  -h | --help) echo "usage: $0 [repo root] | --self-test" >&2; exit 2 ;;
  "") run_check "$ROOT" ;;
  *) run_check "$1" ;;
esac
