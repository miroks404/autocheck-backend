#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Building Android checker image..."
docker build -t autocheck-android-checker:latest "${ROOT_DIR}/docker/checkers/android"

echo "Done. Available images:"
docker images | awk 'NR==1 || /autocheck-android-checker/'
