#!/usr/bin/env bash
# Tests scripts/wait-for-release.sh against a local stand-in for github.com.
#
# The release workflow calls the site deploy hook only once this script
# returns 0, because the site's well-known index hashes the latest release's
# genjutsu.zip at build time. Returning 0 too early rebuilds the site on the
# previous release; never returning keeps a job running for hours. So: it must
# wait through a lagging redirect, refuse a tag that merely starts with the
# right one, refuse a release whose asset is missing, and give up after exactly
# the number of attempts it was given.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WAIT="$ROOT/scripts/wait-for-release.sh"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/genjutsu-wait.XXXXXX")"
SERVER_PID=""
stop_server() {
  [ -n "$SERVER_PID" ] || return 0
  kill "$SERVER_PID" 2>/dev/null
  wait "$SERVER_PID" 2>/dev/null
  SERVER_PID=""
}
trap 'stop_server; rm -rf "$WORK"' EXIT

cat > "$WORK/server.py" <<'PY'
import http.server, sys

port_file, scenario, hits_file = sys.argv[1], sys.argv[2], sys.argv[3]
latest_hits = 0

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        global latest_hits
        base = "http://127.0.0.1:%d" % self.server.server_address[1]
        if self.path == "/o/r/releases/latest":
            latest_hits += 1
            with open(hits_file, "w") as fh:
                fh.write(str(latest_hits))
            if scenario == "late":
                tag = "v0.0.1" if latest_hits <= 2 else "v9.9.9"
            elif scenario == "prefix":
                tag = "v9.9.90"
            else:
                tag = "v9.9.9"
            self.send_response(302)
            self.send_header("Location", base + "/o/r/releases/tag/" + tag)
            self.end_headers()
            return
        ok = {
            "late": "/o/r/releases/download/v9.9.9/genjutsu.zip",
            "prefix": "/o/r/releases/download/v9.9.90/genjutsu.zip",
            "noasset": "",
        }[scenario]
        if self.path == ok:
            body = b"PK\x05\x06" + b"\x00" * 18
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

srv = http.server.HTTPServer(("127.0.0.1", 0), H)
with open(port_file, "w") as fh:
    fh.write(str(srv.server_address[1]))
srv.serve_forever()
PY

start_server() { # <scenario>
  stop_server
  rm -f "$WORK/port" "$WORK/hits"
  python3 "$WORK/server.py" "$WORK/port" "$1" "$WORK/hits" &
  SERVER_PID=$!
  for _ in $(seq 1 50); do [ -s "$WORK/port" ] && break; sleep 0.1; done
  PORT="$(cat "$WORK/port")"
}

run_wait() { # <attempts> -> exit code, output in $WORK/out
  GITHUB_SERVER_URL="http://127.0.0.1:$PORT" RELEASE_WAIT_ATTEMPTS="$1" RELEASE_WAIT_SECONDS=0 \
    "$WAIT" o/r v9.9.9 >"$WORK/out" 2>&1
}

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
    sed 's/^/       | /' "$WORK/out" 2>/dev/null
    fail=$((fail + 1))
  fi
}

start_server late
run_wait 5
check "waits through a lagging releases/latest, then succeeds" "0" "$?"
check "and it took the third look" "3" "$(cat "$WORK/hits")"

start_server prefix
run_wait 3
check "a tag that only starts with the wanted one never counts" "1" "$?"
check "gives up after exactly the attempts it was given" "3" "$(cat "$WORK/hits")"
check "and says the hook was not called" "yes" \
  "$(grep -q "deploy hook was NOT called" "$WORK/out" && echo yes || echo no)"

start_server noasset
run_wait 2
check "a release whose genjutsu.zip is missing never counts" "1" "$?"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
