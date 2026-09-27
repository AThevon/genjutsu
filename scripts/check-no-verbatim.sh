#!/usr/bin/env bash
# Principle P5 of v4: nothing from taste-skill (Leonxlnx, MIT) is copied word for
# word. genjutsu takes ideas and facts from it and rewrites them in its own voice,
# so it ships no MIT notice of theirs. This check is what makes that claim true
# rather than hoped for. It runs by hand, against a local clone, before a release.
#
#   scripts/check-no-verbatim.sh <path to a taste-skill clone>
#   scripts/check-no-verbatim.sh --self-test
#
# Three checks:
#   1. the clone is at the pinned commit (another commit is another comparison:
#      re-pin on purpose, after reading what changed upstream);
#   2. none of taste-skill's signature phrases appears under skills/, outside the
#      vendored ui-ux-pro-max files, which inherited some of them from upstream;
#      and no module is named after it;
#   3. no run of ten consecutive words, after lowercasing and dropping punctuation,
#      is shared between a file genjutsu wrote and skills/taste-skill/SKILL.md.
#      Code between backticks, inline or fenced, is left out on both sides:
#      `00 / INDEX` or `import gsap from "gsap"` is a fact both may cite, not prose.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Full hash of the taste-skill commit this check was last run against.
PINNED="a6153b39e495b8d62666f33f6a7019fcba3b777f"

run_check() { # <genjutsu root> <taste-skill clone> <pinned hash>
  python3 - "$1" "$2" "$3" <<'PY'
import os
import re
import subprocess
import sys
from pathlib import Path

root, clone, pin = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
failed = False

head = subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"], capture_output=True, text=True)
if head.returncode != 0:
    print(f"FAIL: {clone} is not a git clone of taste-skill")
    sys.exit(1)
if head.stdout.strip() != pin:
    print(f"FAIL: the clone is at {head.stdout.strip()}, this check is pinned to {pin}.")
    print("      Check out the pinned commit, or re-pin PINNED after reading the upstream diff.")
    sys.exit(1)
source = clone / "skills" / "taste-skill" / "SKILL.md"
if not source.is_file():
    print(f"FAIL: {source} not found")
    sys.exit(1)

VENDORED = re.compile(r"^skills/_jutsu/ui-ux-pro-max/(?:data|scripts|references)/"
                      r"|^skills/_jutsu/ui-ux-pro-max/LICENSE-upstream\.txt$")
SIGNATURES = ["Reading this as", "DESIGN_VARIANCE", "MOTION_INTENSITY", "VISUAL_DENSITY",
              "grid-flow-dense", "Production-Test Tells"]


def tree(base: Path) -> list[Path]:
    out = []
    for dp, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        out += [Path(dp) / f for f in files if not f.endswith(".pyc")]
    return sorted(out)


def rel(p: Path) -> str:
    return p.relative_to(root).as_posix()


own = [p for p in tree(root / "skills") if not VENDORED.search(rel(p))]

for p in own:
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    for sig in SIGNATURES:
        if sig in text:
            print(f"FAIL: signature phrase {sig!r} in {rel(p)}")
            failed = True
for d in sorted({p.parent for p in own}):
    if "taste" in d.name.lower():
        print(f"FAIL: a directory is named after taste-skill: {rel(d)}")
        failed = True


def words(text: str) -> list[str]:
    text = re.sub(r"```.*?```", " ", text.replace(chr(0x2019), "'"), flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)
    return re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)*", text.lower())


def windows(ws: list[str], n: int = 10) -> set[tuple[str, ...]]:
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


theirs = windows(words(source.read_text(encoding="utf-8")))
written = [p for p in own if p.suffix == ".md"]
written += [p for p in sorted((root / "packaging").glob("*.md"))]
written += [root / f for f in ("README.md", "CHANGELOG.md", "PLATFORM-CONTRACT.md", "CONTRIBUTING.md")
            if (root / f).is_file()]
compared = 0
for p in written:
    shared = windows(words(p.read_text(encoding="utf-8"))) & theirs
    compared += 1
    if shared:
        failed = True
        print(f"FAIL: {rel(p)} shares {len(shared)} ten-word run(s) with taste-skill, e.g.:")
        for w in sorted(shared)[:3]:
            print("      " + " ".join(w))

if failed:
    sys.exit(1)
print(f"OK   [no-verbatim]: {compared} file(s) compared with taste-skill at {pin[:12]}, "
      f"no shared ten-word run, no signature phrase")
PY
}

self_test() {
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  clone="$tmp/taste"
  mkdir -p "$clone/skills/taste-skill"
  cat > "$clone/skills/taste-skill/SKILL.md" <<'EOF'
# fixture
Never ship a hero section that forgets the one promise it was built to make for the visitor.
Remember that the grid template repeats three equal columns on every single feature row.
```js
import gsap from "gsap"; import { ScrollTrigger } from "gsap/ScrollTrigger"; gsap.registerPlugin(ScrollTrigger)
```
EOF
  git -C "$clone" init -q
  git -C "$clone" add -A
  git -C "$clone" -c user.email=self-test@genjutsu -c user.name=self-test commit -qm fixture
  pin="$(git -C "$clone" rev-parse HEAD)"

  mk_root() { # <body of the one genjutsu file>
    rm -rf "$tmp/root"
    mkdir -p "$tmp/root/skills/_jutsu/demo" "$tmp/root/skills/_jutsu/ui-ux-pro-max/scripts"
    printf '%s\n' "$1" > "$tmp/root/skills/_jutsu/demo/SKILL.md"
  }
  expect() { # <wanted exit status> <label> [pin]
    set +e
    run_check "$tmp/root" "$clone" "${3:-$pin}" > "$tmp/out" 2>&1
    got=$?
    set -e
    if [ "$got" -ne "$1" ]; then
      echo "SELF-TEST FAIL: $2 (exit $got, wanted $1)"
      cat "$tmp/out"
      exit 1
    fi
    echo "ok   $2"
  }

  mk_root "An original sentence, written for genjutsu and for nothing else, long enough to count."
  expect 0 "original prose passes"
  mk_root "As they put it: NEVER ship a hero-section that forgets the one promise it was built to make."
  expect 1 "a ten-word run copied with other case and punctuation fails"
  mk_root "Marker: \`the grid template repeats three equal columns on every single feature row\`."
  expect 0 "a shared run inside backticks is a literal marker, not prose"
  mk_root "$(printf '%s\n' '```js' 'import gsap from "gsap"; import { ScrollTrigger } from "gsap/ScrollTrigger"; gsap.registerPlugin(ScrollTrigger)' '```')"
  expect 0 "a shared fenced code block is code, not prose"
  mk_root "Set DESIGN_VARIANCE before anything else."
  expect 1 "a signature phrase fails"
  mk_root "Original."
  printf 'DESIGN_VARIANCE = 5\n' > "$tmp/root/skills/_jutsu/ui-ux-pro-max/scripts/search.py"
  expect 0 "a signature inside vendored ui-ux-pro-max files is inherited, not copied"
  mk_root "Original."
  mkdir -p "$tmp/root/skills/_jutsu/taste"
  printf 'x\n' > "$tmp/root/skills/_jutsu/taste/notes.md"
  expect 1 "a module named after taste-skill fails"
  mk_root "Original."
  expect 1 "a clone at another commit than the pinned one fails" "0000000000000000000000000000000000000000"
  echo "OK   [no-verbatim self-test]: every check can fail"
}

case "${1:-}" in
  --self-test) self_test ;;
  "" | -h | --help)
    echo "usage: $0 <path to a taste-skill clone> | --self-test" >&2
    exit 2
    ;;
  *) run_check "$ROOT" "$1" "$PINNED" ;;
esac
