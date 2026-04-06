#!/usr/bin/env sh
set -eu

# Ensure runtime directories exist for logs, outputs, and compliance artifacts.
mkdir -p /app/logs /app/data /app/audit /app/signatures /app/outputs /app/model_store

exec "$@"
