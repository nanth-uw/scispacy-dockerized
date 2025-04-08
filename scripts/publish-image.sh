#! /usr/bin/env bash

# publish new tag, will always publish latest as well
# usage: ./scripts/publish-image.sh <tag>
# example: ./scripts/publish-image.sh v0.3.0

# check if tag is provided
if [ -z "$1" ]; then
  echo "No tag provided. Usage: ./scripts/publish-image.sh <tag>"
  exit 1
fi

# build and push the image with the provided tag and latest
echo "Building and pushing image with tag"
# build and push the image with the provided tag
docker build --platform linux/amd64,linux/arm64 -t ghcr.io/nanth-uw/scispacy-dockerized/ner:$1 --push .
echo "Image published with tag: $1"
docker build --platform linux/amd64,linux/arm64 -t ghcr.io/nanth-uw/scispacy-dockerized/ner:latest --push .
echo "Image published with tag: latest"

echo "Done for image ghcr.io/nanth-uw/scispacy-dockerized/ner"