#!/usr/bin/env bash

# Apply idempotent SQL to fix/reset password-related tables on production
# Usage:
#   # With connection string:
#   export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
#   ./reset_password.sh
#   # Or with PG* env vars (can come from .env/.env.production):
#   export PGHOST=host PGPORT=5432 PGUSER=user PGPASSWORD=pass PGDATABASE=dbname
#   ./reset_password.sh

set -euo pipefail

# Auto-load environment from .env files if present (no hardcoding)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$SCRIPT_DIR/.env"
  set +a
fi
if [ -f "$SCRIPT_DIR/.env.production" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$SCRIPT_DIR/.env.production"
  set +a
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "psql not found in PATH. Please install PostgreSQL client." >&2
  exit 1
fi

echo "Applying password/OTP table fixes..."

# Prefer DATABASE_URL; else use discrete PG* vars
if [ -n "${DATABASE_URL:-}" ]; then
  psql_cmd=(psql "$DATABASE_URL")
else
  : "${PGHOST:?PGHOST not set and DATABASE_URL missing}"
  : "${PGPORT:?PGPORT not set and DATABASE_URL missing}"
  : "${PGUSER:?PGUSER not set and DATABASE_URL missing}"
  : "${PGDATABASE:?PGDATABASE not set and DATABASE_URL missing}"
  # PGPASSWORD is read from env by psql if set
  psql_cmd=(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE")
fi

"${psql_cmd[@]}" <<'SQL'
BEGIN;

-- Ensure uuid type available (built-in on modern Postgres). Extensions not required for app-side UUID generation.

-- 1) OTP table (otp_verifications)
CREATE TABLE IF NOT EXISTS otp_verifications (
  id UUID PRIMARY KEY,
  phone_number VARCHAR(20),
  email VARCHAR(255),
  otp_code VARCHAR(10) NOT NULL,
  purpose VARCHAR(50) NOT NULL DEFAULT 'phone_verification',
  attempts INTEGER NOT NULL DEFAULT 0,
  is_verified BOOLEAN NOT NULL DEFAULT FALSE,
  expires_at TIMESTAMPTZ NOT NULL,
  verified_at TIMESTAMPTZ NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Make existing columns align with the app model (idempotent alters)
ALTER TABLE otp_verifications ALTER COLUMN phone_number DROP NOT NULL;
ALTER TABLE otp_verifications ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE otp_verifications ADD COLUMN IF NOT EXISTS purpose VARCHAR(50) NOT NULL DEFAULT 'phone_verification';
ALTER TABLE otp_verifications ADD COLUMN IF NOT EXISTS attempts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE otp_verifications ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE otp_verifications ADD COLUMN IF NOT EXISTS verified_at TIMESTAMPTZ NULL;
ALTER TABLE otp_verifications ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Add indexes for faster lookups
CREATE INDEX IF NOT EXISTS ix_otp_verifications_email ON otp_verifications (email);
CREATE INDEX IF NOT EXISTS ix_otp_verifications_phone ON otp_verifications (phone_number);
CREATE INDEX IF NOT EXISTS ix_otp_verifications_purpose ON otp_verifications (purpose);

-- 2) Password reset tokens table (password_reset_tokens)
CREATE TABLE IF NOT EXISTS password_reset_tokens (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  token VARCHAR(255) NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  is_used BOOLEAN NOT NULL DEFAULT FALSE,
  used_at TIMESTAMPTZ NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_password_reset_tokens_token UNIQUE (token)
);

-- Add helpful indexes
CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_user_id ON password_reset_tokens (user_id);
CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_token ON password_reset_tokens (token);

COMMIT;
SQL

echo "✅ Database table fixes applied successfully."


