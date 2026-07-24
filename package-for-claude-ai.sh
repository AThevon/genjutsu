#!/usr/bin/env bash
set -euo pipefail

DIST="dist"
SKILLS_DIR="skills"

# Prefer zip, fallback to python3 zipfile
if command -v zip &>/dev/null; then
  make_zip() { (cd "$1" && zip -rq "$2" . -x '.*' -x '*/__pycache__/*' -x '*.pyc'); }
elif command -v python3 &>/dev/null; then
  make_zip() {
    python3 -c "
import zipfile, os, sys
src, dst = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for f in files:
            if f.startswith('.') or f.endswith('.pyc'): continue
            fp = os.path.join(root, f)
            zf.write(fp, os.path.relpath(fp, src))
" "$1" "$2"
  }
else
  echo "Error: 'zip' or 'python3' is required."
  exit 1
fi

rm -rf "$DIST"
mkdir -p "$DIST"

echo "=== genjutsu - Packaging pour claude.ai ==="
echo ""

# --- Individual ZIPs per skill ---

# Orchestrators (skills/<name>/ -> <name>.zip, skip _jutsu/)
for dir in "$SKILLS_DIR"/*/; do
  name=$(basename "$dir")
  [[ "$name" == _* ]] && continue
  zip_path="$(pwd)/${DIST}/${name}.zip"
  make_zip "$dir" "$zip_path"
  echo "  + ${name}.zip"
done

# Sub-skills (_jutsu/<name>/ -> <name>.zip)
for dir in "$SKILLS_DIR"/_jutsu/*/; do
  name=$(basename "$dir")
  zip_path="$(pwd)/${DIST}/${name}.zip"
  make_zip "$dir" "$zip_path"
  echo "  + ${name}.zip"
done

# --- Single-upload bundle (recommended) ---
# One self-contained "genjutsu" skill: a thin router SKILL.md + cast/ + paint/
# + all _jutsu/ sub-skills. Uploaded once, it resolves sub-skills from its own
# bundled _jutsu/ (the orchestrators' path detection prefers the bundle).
BUNDLE_SRC="${DIST}/.bundle"
rm -rf "$BUNDLE_SRC"
mkdir -p "$BUNDLE_SRC"
cp "packaging/genjutsu-router.md" "$BUNDLE_SRC/SKILL.md"
cp -R "$SKILLS_DIR/cast" "$BUNDLE_SRC/cast"
cp -R "$SKILLS_DIR/paint" "$BUNDLE_SRC/paint"
cp -R "$SKILLS_DIR/_jutsu" "$BUNDLE_SRC/_jutsu"

# claude.ai rejects a skill ZIP that contains more than one SKILL.md. Keep only
# the router as SKILL.md: rename every bundled orchestrator/sub-skill SKILL.md
# to GUIDE.md, then repoint every in-bundle "SKILL.md" reference to "GUIDE.md"
# so the router's cat and the orchestrators' load_skill still resolve.
python3 - "$BUNDLE_SRC" <<'PY'
import os, sys
root = os.path.abspath(sys.argv[1])
# 1) rename inner SKILL.md -> GUIDE.md (leave the root router SKILL.md alone)
for dp, _, fs in os.walk(root):
    if "SKILL.md" in fs and os.path.abspath(dp) != root:
        os.rename(os.path.join(dp, "SKILL.md"), os.path.join(dp, "GUIDE.md"))
# 2) repoint references inside every markdown file
for dp, _, fs in os.walk(root):
    for fn in fs:
        if fn.endswith(".md"):
            p = os.path.join(dp, fn)
            with open(p, encoding="utf-8") as fh:
                s = fh.read()
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(s.replace("SKILL.md", "GUIDE.md"))
PY

make_zip "$BUNDLE_SRC" "$(pwd)/${DIST}/genjutsu.zip"
rm -rf "$BUNDLE_SRC"
echo "  + genjutsu.zip (single-upload bundle: 1 router SKILL.md + cast/paint/_jutsu as GUIDE.md)"

echo ""
echo "=== Résumé ==="
echo ""
ls -lh "$DIST"/*.zip | awk '{print "  " $NF " (" $5 ")"}'
echo ""
echo "claude.ai: upload genjutsu.zip once (Customize > Skills), or the individual"
echo "skill ZIPs a la carte (cast + paint + the sub-skills you need)."
