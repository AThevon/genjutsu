#!/usr/bin/env bash
# Symbols and claims that were shipped once and must never come back.
#
# Every entry here was in a released version of genjutsu and made the agent emit
# code that does not compile, or advice that is wrong in the dangerous direction
# (support claimed where there is none, so the fallback gets dropped). A grep is a
# blunt instrument, but these are exact strings, and the failure mode they guard
# against is a silent reintroduction during an unrelated edit.
#
# Format: three TAB-separated columns.
#
#   pattern <TAB> why it is banned <TAB> exemption regex (optional)
#
# The exemption exists because the best place to document a non-existent API is
# next to its name: "Never write .asAndroidPath().asComposePath()" has to be
# allowed to say the thing it is banning. Keep exemptions narrow - they should
# match the teaching sentence and nothing else. An exemption wide enough to cover
# a real use means the string is not actually banned.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="$ROOT/skills"

DENYLIST=$(cat <<'ENTRIES'
Modifier.recomposeHighlighter	not an androidx API, it is a sample from android/snippets. Point at Layout Inspector > Show Recomposition Counts.	There is no |no `Modifier.recomposeHighlighter`|not an androidx
.asAndroidPath().asComposePath()	Morph.toPath() already returns an android Path; the chain does not compile.	Never write
UIBlurEffect.systemMaterial()	not a Kotlin/Native binding. UIKit exposes UIBlurEffect(style:) with UIBlurEffectStyle constants.	does not exist|Never write|no such
IOSKeyboardEventListener	no such type in Compose Multiplatform; the real knob is ComposeUIViewControllerConfiguration.onFocusBehavior.	does not exist|Never write|no such|There is no|is \*\*no\*\*
no-op on macOS	something was documented as harmless on macOS when it is a compile error. `.hoverEffect` is @available(macOS, unavailable): gate it with #if os(macOS), never call it in a macOS path.
Firefox | 128+ | Supported (shipped July 2024)	no stable Firefox ships scroll-driven animations; claiming it makes the agent drop the @supports fallback.
staggerChildren:	deprecated in Motion 12.22 in favour of delayChildren: stagger(...). Fine to mention, not to teach.	DEPRECATED|deprecated
ENTRIES
)

status=0
found_any=0
n_entries=0

while IFS=$'\t' read -r pattern why exempt; do
  [ -z "${pattern:-}" ] && continue
  n_entries=$((n_entries + 1))
  # VERSIONS.md is the other half of this contract: it exists to record what was
  # wrong and what replaced it, so it names these strings on purpose.
  hits=$(grep -rFn --include='*.md' --exclude='VERSIONS.md' -- "$pattern" "$TARGET" 2>/dev/null) || continue
  if [ -n "${exempt:-}" ]; then
    hits=$(printf '%s\n' "$hits" | grep -Ev -- "$exempt") || continue
  fi
  [ -z "$hits" ] && continue
  found_any=1
  status=1
  echo "FAIL: banned string \"$pattern\""
  echo "      $why"
  printf '%s\n' "$hits" | sed "s|^$ROOT/|      |"
  echo
done <<< "$DENYLIST"

if [ "$found_any" -eq 0 ]; then
  echo "OK   [denylist]: none of the $n_entries banned strings are present"
fi

exit "$status"
