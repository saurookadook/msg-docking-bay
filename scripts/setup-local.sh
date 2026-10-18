#!/usr/bin/env bash
# Prepare a fresh clone for the local Compose stack. Safe to rerun: it never overwrites
# an existing .env file, certificate, or secret.
#
#   - .env and .env.test from their templates (ENV-1)
#   - TLS certificates for APP_DOMAIN with mkcert, in nginx-reverse-proxy/certs/ (ENV-39)
#   - database passwords in .docker/secrets/ (ENV-13, PG-13)
#   - a check that APP_DOMAIN resolves to this machine
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!!\033[0m %s\n' "$*" >&2; }

copy_template() {
  local template="$1" target="$2"
  if [[ -f "$target" ]]; then
    info "$target exists; leaving it as it is"
  else
    cp "$template" "$target"
    info "created $target from $template"
  fi
}

copy_template .env.example .env
copy_template .env.test.example .env.test

app_domain="$(sed -n 's/^APP_DOMAIN=//p' .env | tail -n 1)"
if [[ -z "$app_domain" ]]; then
  warn "APP_DOMAIN is not set in .env"
  exit 1
fi

# --- TLS certificates -------------------------------------------------------------
if ! command -v mkcert >/dev/null 2>&1; then
  warn "mkcert is not installed (https://github.com/FiloSottile/mkcert); install it and rerun"
  exit 1
fi
certs_dir=nginx-reverse-proxy/certs
if [[ -f "$certs_dir/local.pem" && -f "$certs_dir/local-key.pem" ]]; then
  info "$certs_dir/local.pem exists; leaving it as it is"
else
  mkcert -install
  mkcert -cert-file "$certs_dir/local.pem" -key-file "$certs_dir/local-key.pem" "$app_domain"
  info "created certificates for $app_domain in $certs_dir/"
fi

# --- Database passwords -----------------------------------------------------------
mkdir -p .docker/secrets
chmod 700 .docker/secrets
for secret in postgres_password db_owner_password db_app_password; do
  secret_file=".docker/secrets/$secret"
  if [[ -f "$secret_file" ]]; then
    info "$secret_file exists; leaving it as it is"
  else
    # Hex only, so the value never needs escaping in a URL or in SQL.
    (umask 077 && openssl rand -hex 24 | tr -d '\n' >"$secret_file")
    info "generated $secret_file"
  fi
done

# --- Name resolution --------------------------------------------------------------
if grep -Eq "^[[:space:]]*127\.0\.0\.1[[:space:]].*\b${app_domain//./\\.}\b" /etc/hosts; then
  info "$app_domain resolves to 127.0.0.1 through /etc/hosts"
else
  warn "$app_domain is not in /etc/hosts. Add it (this needs sudo):"
  warn "  sudo sh -c 'echo \"127.0.0.1 $app_domain\" >> /etc/hosts'"
fi

https_port="$(sed -n 's/^PROXY_HTTPS_PORT=//p' .env | tail -n 1)"
app_url="https://$app_domain"
if [[ -n "$https_port" && "$https_port" != "443" ]]; then
  # Without the port, the browser goes to whatever holds 443, with another certificate.
  app_url="$app_url:$https_port"
fi

info "done. Start the stack with: moon run root:dev, then open $app_url"
