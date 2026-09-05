#!/bin/sh
set -eu

board_data_dir="${BOARD_DATA_DIR:-/app/data}"
board_port="${BOARD_PORT:-3000}"

mkdir -p "$board_data_dir"

./node_modules/.bin/wrangler d1 migrations apply DB \
  --local \
  --config wrangler.container.jsonc \
  --persist-to "$board_data_dir"

exec ./node_modules/.bin/wrangler dev \
  --local \
  --ip 0.0.0.0 \
  --port "$board_port" \
  --config dist/server/wrangler.json \
  --persist-to "$board_data_dir" \
  --show-interactive-dev-session=false \
  --log-level info
