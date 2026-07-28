#!/usr/bin/env bash
# Build the shared base image first, then all service images.
# (docker compose can't order image builds, and every service is `FROM gms-base`.)
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Building shared base image (gms-base) ..."
docker build -t gms-base -f gms-base.Dockerfile .

echo "==> Building service images ..."
docker compose build "$@"

echo "==> Done. Start the fleet with:  docker compose up -d"
