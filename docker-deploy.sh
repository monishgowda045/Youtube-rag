#!/bin/bash

# Docker Build and Deploy Script for YouTube RAG
# Usage: ./docker-deploy.sh [build|push|run|all]

set -e

IMAGE_NAME="youtube-rag"
TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 YouTube RAG Docker Deployment${NC}"

# Function to build Docker image
build() {
    echo -e "${YELLOW}🔨 Building Docker image...${NC}"
    docker build -t ${IMAGE_NAME}:${TAG} .
    echo -e "${GREEN}✅ Build complete!${NC}"
}

# Function to run the container
run() {
    echo -e "${YELLOW}🏃 Running container...${NC}"
    if [ ! -f .env ]; then
        echo -e "${RED}❌ .env file not found! Please copy .env.template to .env and add your OpenAI API key${NC}"
        exit 1
    fi
    docker run -p 8501:8501 --env-file .env ${IMAGE_NAME}:${TAG}
}

# Function to push to registry (requires login)
push() {
    echo -e "${YELLOW}📤 Pushing to registry...${NC}"
    # For GitHub Container Registry
    echo "Make sure you're logged in: docker login ghcr.io"
    docker tag ${IMAGE_NAME}:${TAG} ghcr.io/${GITHUB_REPOSITORY:-your-username/youtube-rag}:${TAG}
    docker push ghcr.io/${GITHUB_REPOSITORY:-your-username/youtube-rag}:${TAG}
    echo -e "${GREEN}✅ Push complete!${NC}"
}

# Function to do everything
all() {
    build
    run
}

# Main logic
case "${1:-all}" in
    build)
        build
        ;;
    run)
        run
        ;;
    push)
        push
        ;;
    all)
        all
        ;;
    *)
        echo -e "${RED}Usage: $0 [build|run|push|all]${NC}"
        echo "  build - Build Docker image"
        echo "  run   - Run the container"
        echo "  push  - Push to container registry"
        echo "  all   - Build and run (default)"
        exit 1
        ;;
esac