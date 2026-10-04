#!/usr/bin/env bash
# Scaffold for the nocturne-planetarium example, run by `claude plugin eval --scaffold` in the
# run's empty workspace. An empty React 19 + Vite + TypeScript app with node_modules already
# installed (the run has no network), plus data/stars.json: the Yale Bright Star Catalogue
# stars above Lisbon at 22:00 on Friday 9 October 2026 and Saturn (JPL Horizons), with altitude and azimuth computed.
# The page starts as a bare <main />, so a run that writes nothing fails page-has-content.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE=/private/tmp/genjutsu-ex-templates/react

if [ ! -d "$TEMPLATE/node_modules" ]; then
  echo "nocturne-planetarium: template $TEMPLATE is missing or has no node_modules; run examples/make-templates.sh first" >&2
  exit 1
fi

cp -R "$TEMPLATE"/. .
mkdir -p data
cp "$HERE/data/stars.json" data/stars.json
