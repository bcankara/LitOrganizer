#!/bin/sh
set -e

# If the mounted /app/config is empty, seed it with the default config
if [ -d "/app/default-config" ] && [ -z "$(ls -A /app/config 2>/dev/null)" ]; then
    echo "[entrypoint] Seeding default config to /app/config"
    cp -a /app/default-config/. /app/config/
fi

# Ensure required directories exist
mkdir -p /app/pdf /app/processed /app/logs /app/config

exec "$@"
