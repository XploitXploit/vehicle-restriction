#!/bin/bash

print_usage() {
    echo "Usage: '-t' for tag name, '-n' for container_name."
}

# grab args
while getopts 'ht:n:' flag; do
    case "${flag}" in
        h) print_usage
            exit 0 ;;
        t) tag="${OPTARG:-latest}" ;;
        n) container_name="${OPTARG:-}" ;;
        *) print_usage
            exit 1 ;;
    esac
done

docker run --rm -p 10000:80 \
    --env-file .env \
    --name "${container_name:-some_name}" \
    gcr.io/arquitectura-gowgo-brasil/bms-vehicle-restriction-service:${tag:-latest}