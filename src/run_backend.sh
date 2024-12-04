#!/bin/bash
cleanup() {
    docker compose down
}
trap cleanup EXIT
docker compose up --build
