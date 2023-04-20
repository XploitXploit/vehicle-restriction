#!/bin/bash

print_usage() {
    echo "Usage:";
    echo -e "\t'-h' this help"
    echo -e "\t'-t' for a image tag name (defaults to '0.0.0')"
    echo -e "\t'-l' for push image as latest"
}

build_tag="0.0.0"
push_as_latest=0
image_name=ds-scraper-scheduler

while getopts 'hlqt:' flag; do
    case "${flag}" in
        h) print_usage
            exit 0 ;;
        t) build_tag="${OPTARG:-0.0.0}" ;;
        l) push_as_latest=1 ;;
        *) print_usage
            exit 1 ;;
    esac
done

echo "building and pushing with tag: $build_tag"

export DOCKER_BUILDKIT=1
docker build \
    -f Dockerfile \
    -t gcr.io/arquitectura-gowgo/$image_name:$build_tag \
    . > /dev/null

docker push gcr.io/arquitectura-gowgo/$image_name:$build_tag

if [ $push_as_latest -eq 1 ]; then
    echo "Pushing also with tag 'latest'"
    docker build -q -f Dockerfile \
        -t gcr.io/arquitectura-gowgo/$image_name:latest \
        . > /dev/null
    docker push gcr.io/arquitectura-gowgo/$image_name:latest
fi

echo -e ""
echo "do NOT forget to tag the git commit with:"
echo "> git tag -a v$build_tag -m 'gcr.io version $build_tag'"
echo "> git push origin v$build_tag"
