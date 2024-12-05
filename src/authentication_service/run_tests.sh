#!/bin/bash

cleanup() {
    docker compose -f docker-compose-test.yml down
}
trap cleanup EXIT
docker compose -f docker-compose-test.yml up --build --abort-on-container-exit --exit-code-from newman
