#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

cd "$SCRIPT_DIR"

docker-compose -f ./docker-compose-unit-test.yml up --build -d

echo "Waiting for containers to initialize..."
sleep 5

newman run ./unit_test.postman_collection.json --insecure

docker-compose -f ./docker-compose-unit-test.yml down
