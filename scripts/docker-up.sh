#!/usr/bin/env bash
set -euo pipefail

# WSL often exposes a local proxy as 127.0.0.1:PORT. Containers must use
# host.docker.internal instead, so derive the current port at startup.
proxy_url="${HTTPS_PROXY:-${https_proxy:-${HTTP_PROXY:-${http_proxy:-}}}}"
if [[ "$proxy_url" =~ :([0-9]+)$ ]]; then
  docker_proxy="http://host.docker.internal:${BASH_REMATCH[1]}"
  export DOCKER_HTTP_PROXY="$docker_proxy"
  export DOCKER_HTTPS_PROXY="$docker_proxy"
fi

docker compose build

volume_name="medical-health-assistant_medical_health_data"
if ! docker volume inspect "$volume_name" >/dev/null 2>&1; then
  docker volume create "$volume_name" >/dev/null
  if [[ -f medical_health.db || -d chroma_db ]]; then
    docker run --rm \
      -v "$volume_name":/target \
      -v "$PWD":/source \
      medical-health-assistant-api \
      sh -c '
        [ ! -f /source/medical_health.db ] || cp /source/medical_health.db /target/
        [ ! -d /source/chroma_db ] || cp -r /source/chroma_db /target/
      '
  fi
fi

docker compose up -d
