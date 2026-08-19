#!/usr/bin/env bash
set -euo pipefail

# Docker cannot use WSL's 127.0.0.1 proxy directly. Convert its current
# port to the host address containers can reach before building the image.
proxy_url="${HTTPS_PROXY:-${https_proxy:-${HTTP_PROXY:-${http_proxy:-}}}}"
if [[ "$proxy_url" =~ :([0-9]+)$ ]]; then
  docker_proxy="http://host.docker.internal:${BASH_REMATCH[1]}"
  export DOCKER_HTTP_PROXY="$docker_proxy"
  export DOCKER_HTTPS_PROXY="$docker_proxy"
fi

docker compose -f docker-compose.test.yml build
docker compose -f docker-compose.test.yml run --rm test
