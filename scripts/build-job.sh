#!/bin/bash
# Build and push Job Docker image

set -e

REGISTRY=${1:-docker.io}
IMAGE_NAME=${2:-openai-newsletter-job}
VERSION=${3:-latest}

echo "Building Job image: $REGISTRY/$IMAGE_NAME:$VERSION"
docker build -t $REGISTRY/$IMAGE_NAME:$VERSION -f openai_scheduled_newsletter_job/Dockerfile .

echo "✓ Job image built successfully"
echo "To push: docker push $REGISTRY/$IMAGE_NAME:$VERSION"
