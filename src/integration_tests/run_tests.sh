#!/bin/bash

set -e
cleanup() {
    docker compose -f docker-compose-integration-test.yml down
}
trap cleanup EXIT
docker compose -f docker-compose-integration-test.yml up --build --abort-on-container-exit --exit-code-from newman
