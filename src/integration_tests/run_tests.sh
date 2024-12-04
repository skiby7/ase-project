#!/bin/bash

set -e

docker compose -f docker-compose-integration-test.yml up --build --abort-on-container-exit --exit-code-from newman
docker compose -f docker-compose-integration-test.yml down
