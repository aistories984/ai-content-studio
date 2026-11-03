#!/bin/sh
# Local macOS/Linux launcher. Keeps data in studio-data unless DIRECTOR_DATA is set.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PATH="$PWD/.tools/node/bin:$PWD/.tools/media/node_modules/@ffmpeg-installer/darwin-arm64:$PWD/.tools/media/node_modules/@ffprobe-installer/darwin-arm64:$PATH"
export PATH
if [ ! -x .venv/bin/python ]; then
  echo 'Python environment missing. Follow README.md: macOS / Linux setup.' >&2
  exit 1
fi
if [ ! -f dist/index.html ]; then
  echo 'Dashboard build missing. Run npm ci and npm run build first.' >&2
  exit 1
fi
printf '%s\n' 'Director Studio: http://127.0.0.1:8767 (Ctrl+C to stop)'
exec .venv/bin/python -m uvicorn studio.app:app --host 127.0.0.1 --port 8767
