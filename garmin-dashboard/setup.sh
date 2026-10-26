#!/bin/bash
# Copies the dashboard into ~/garmin-dashboard, checks Python, creates .env.local.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/garmin-dashboard"

if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
  echo "You need Python 3.10 or newer."
  echo "Download it from https://www.python.org/downloads/ , install it, then run this again."
  open "https://www.python.org/downloads/" 2>/dev/null || true
  exit 1
fi
echo "Python OK: $(python3 --version)"

mkdir -p "$DEST/data"
if [ "$SRC" != "$DEST" ]; then
  cp "$SRC"/*.py "$SRC"/*.sh "$SRC"/*.bat "$SRC"/.gitignore "$DEST"/ 2>/dev/null || true
fi
chmod +x "$DEST"/*.sh
[ -f "$DEST/.env.local" ] || echo "GARMIN_PERSONAL_API_KEY=" > "$DEST/.env.local"
chmod 600 "$DEST/.env.local"
echo "Ready: $DEST"
