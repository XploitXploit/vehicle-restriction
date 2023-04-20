#!/bin/bash


build_tag=${1:-latest}
docker_file="Dockerfile"

export DOCKER_BUILDKIT=1
docker build $quiet -f $docker_file -t gcr.io/arquitectura-gowgo-brasil/bms-vehicle-restriction-service:$build_tag . > /dev/null