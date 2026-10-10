#!/usr/bin/env bash
# 本機預覽。用法：./serve.sh [埠，預設 41731]
set -euo pipefail
cd "$(dirname "$0")"
python3 build_site.py
exec python3 -m http.server "${1:-41731}" --bind 0.0.0.0
