#!/usr/bin/env sh

set -eu

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker bulunamadı. Docker Desktop'ı kurup çalıştırın."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker çalışmıyor. Docker Desktop'ı başlatın."
  exit 1
fi

docker compose up --build
