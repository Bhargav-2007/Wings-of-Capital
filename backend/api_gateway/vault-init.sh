#!/usr/bin/env bash
# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-${VAULT_DEV_ROOT_TOKEN_ID:-dev-token-12345}}"
VAULT_CONTAINER="${VAULT_CONTAINER:-woc_vault}"

export VAULT_ADDR
export VAULT_TOKEN

vault_cmd() {
  vault "$@"
}

if ! command -v vault >/dev/null 2>&1; then
  if command -v docker >/dev/null 2>&1; then
    vault_cmd() {
      docker exec \
        -e VAULT_ADDR="$VAULT_ADDR" \
        -e VAULT_TOKEN="$VAULT_TOKEN" \
        "$VAULT_CONTAINER" vault "$@"
    }
  else
    echo "Vault CLI is required but not installed, and docker is unavailable." >&2
    exit 1
  fi
fi

random_hex() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32
    return
  fi

  python - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
}

vault_cmd status >/dev/null

if ! vault_cmd secrets list -format=json | grep -q '"secret/"'; then
  vault_cmd secrets enable -path=secret kv-v2
fi

cat <<'HCL' | vault_cmd policy write wings-service -
path "secret/data/wings/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
path "secret/metadata/wings/*" {
  capabilities = ["read", "list"]
}
HCL

JWT_SECRET_KEY="${JWT_SECRET_KEY:-$(random_hex)}"
REDIS_PASSWORD="${REDIS_PASSWORD:-redis_secret_password}"
DATABASE_URL="${DATABASE_URL:-postgresql://woc_user:woc_password@postgres:5432/wings_of_capital}"
COINGECKO_API_KEY="${COINGECKO_API_KEY:-}"
ETHEREUM_RPC_URL="${ETHEREUM_RPC_URL:-}"

vault_cmd kv put secret/wings/jwt \
  secret_key="$JWT_SECRET_KEY" \
  algorithm="HS256"

vault_cmd kv put secret/wings/redis \
  password="$REDIS_PASSWORD"

vault_cmd kv put secret/wings/database \
  url="$DATABASE_URL"

vault_cmd kv put secret/wings/external \
  coingecko_api_key="$COINGECKO_API_KEY" \
  ethereum_rpc_url="$ETHEREUM_RPC_URL"

SERVICE_TOKEN=$(vault_cmd token create -policy=wings-service -field=token)

cat <<EOF
Vault initialized for Wings of Capital.
Service token: $SERVICE_TOKEN
Secrets path: secret/wings/
EOF
