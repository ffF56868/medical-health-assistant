#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "$script_dir/.." && pwd)"
cd "$project_dir"

show_usage() {
  cat <<'EOF'
Usage: bash scripts/docker-manage.sh <command>

Commands:
  start    Build when needed and start the API.
  status   Show the container status and call /health.
  logs     Follow the API container logs. Press Ctrl+C to exit.
  stop     Stop the API without deleting persisted data.
  rebuild  Rebuild the API image without cache, then start it.
  test     Run the isolated Docker test suite.
EOF
}

configure_proxy() {
  local proxy_url docker_proxy
  proxy_url="${HTTPS_PROXY:-${https_proxy:-${HTTP_PROXY:-${http_proxy:-}}}}"
  if [[ "$proxy_url" =~ :([0-9]+)$ ]]; then
    docker_proxy="http://host.docker.internal:${BASH_REMATCH[1]}"
    export DOCKER_HTTP_PROXY="$docker_proxy"
    export DOCKER_HTTPS_PROXY="$docker_proxy"
  fi
}

case "${1:-}" in
  start)
    bash scripts/docker-up.sh
    ;;
  status)
    docker compose ps
    echo
    curl --fail --silent http://127.0.0.1:8003/health || true
    echo
    ;;
  logs)
    docker compose logs --follow api
    ;;
  stop)
    docker compose down
    ;;
  rebuild)
    configure_proxy
    docker compose build --no-cache
    docker compose up --detach
    ;;
  test)
    bash scripts/docker-test.sh
    ;;
  *)
    show_usage
    exit 1
    ;;
esac
