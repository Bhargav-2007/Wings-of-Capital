#!/usr/bin/env bash
set -euo pipefail

base_url=${BASE_URL:-http://localhost:8000}
attempts=${SMOKE_ATTEMPTS:-10}
delay_seconds=${SMOKE_DELAY_SECONDS:-1}

retry_curl() {
  local url=$1
  local attempt=1

  while (( attempt <= attempts )); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$delay_seconds"
    attempt=$((attempt + 1))
  done
  echo "Request failed after ${attempts} attempts: ${url}" >&2
  return 1
}

echo "== Kong health =="
retry_curl "$base_url/health"
echo "OK"

echo "== Auth health =="
retry_curl "$base_url/api/v1/auth/health"
echo "OK"

echo "== Ledger health =="
retry_curl "$base_url/api/v1/ledger/health"
echo "OK"

echo "== Crypto health =="
retry_curl "$base_url/api/v1/crypto/health"
echo "OK"

echo "== Crypto prices =="
retry_curl "$base_url/api/v1/crypto/prices?symbols=BTC,ETH"
echo "OK"

if [[ -n "${DIRECT_CHECKS:-}" ]]; then
  echo "== Direct health checks =="
  retry_curl http://localhost:8004/health
  retry_curl http://localhost:8002/health
  retry_curl http://localhost:8003/health
  echo "OK"
fi
