#!/usr/bin/env bash
# Waits until GitHub serves a release that was just published: releases/latest
# must redirect to this exact tag, and its genjutsu.zip must download with 200.
#
# The site's well-known index (what `npx skills add https://genjutsu.athevon.dev -g`
# reads) is built from the latest release: its tag from that redirect, its
# digest from those bytes. Calling the site deploy hook before both hold would
# rebuild the site on the previous release, so the workflow calls the hook only
# when this returns 0. Bounded: it gives up after RELEASE_WAIT_ATTEMPTS looks.
#
# Usage: scripts/wait-for-release.sh <owner/repo> <tag>
# Env:   RELEASE_WAIT_ATTEMPTS (default 30), RELEASE_WAIT_SECONDS (default 10),
#        GITHUB_SERVER_URL (default https://github.com; the tests point it at a
#        local stand-in).
set -uo pipefail

repo="${1:?usage: wait-for-release.sh <owner/repo> <tag>}"
tag="${2:?usage: wait-for-release.sh <owner/repo> <tag>}"
server="${GITHUB_SERVER_URL:-https://github.com}"
attempts="${RELEASE_WAIT_ATTEMPTS:-30}"
pause="${RELEASE_WAIT_SECONDS:-10}"

want="$server/$repo/releases/tag/$tag"
asset="$server/$repo/releases/download/$tag/genjutsu.zip"

n=0
while [ "$n" -lt "$attempts" ]; do
  n=$((n + 1))
  # No -L: the redirect target is the answer. Compared whole, so v4.0.0 never
  # accepts v4.0.01 or v4.0.0-rc1.
  latest="$(curl -sS -o /dev/null -w '%{redirect_url}' --max-time 20 "$server/$repo/releases/latest" 2>/dev/null || true)"
  if [ "$latest" = "$want" ]; then
    # A full GET, not HEAD: the asset redirects to a signed storage URL, and
    # what the site build does is a GET.
    code="$(curl -sSL -o /dev/null -w '%{http_code}' --max-time 60 "$asset" 2>/dev/null || true)"
    if [ "$code" = "200" ]; then
      echo "wait-for-release: $tag is the latest release and genjutsu.zip answers 200 (attempt $n/$attempts)"
      exit 0
    fi
    echo "wait-for-release: attempt $n/$attempts: latest is $tag, genjutsu.zip answered ${code:-nothing}"
  else
    echo "wait-for-release: attempt $n/$attempts: releases/latest points to ${latest:-nothing}, want $want"
  fi
  if [ "$n" -lt "$attempts" ]; then sleep "$pause"; fi
done

echo "wait-for-release: gave up after $attempts attempts; the site deploy hook was NOT called" >&2
exit 1
