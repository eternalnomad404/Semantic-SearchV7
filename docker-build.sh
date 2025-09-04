#!/bin/bash

# Docker build script for Semantic Search Application
# Usage: ./docker-build.sh [tag-name]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default image name and tag
IMAGE_NAME="semantic-search"
TAG=${1:-"latest"}
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo -e "${BLUE}🐳 Building Docker image: ${FULL_IMAGE_NAME}${NC}"

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Error: Dockerfile not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

# Check if required files exist
required_files=("requirements.txt" "api_main.py" "search_engine.py" "models.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Error: Required file '$file' not found.${NC}"
        exit 1
    fi
done

# Check if data and vectorstore directories exist
if [ ! -d "data" ] || [ ! -d "vectorstore" ]; then
    echo -e "${YELLOW}⚠️  Warning: data/ or vectorstore/ directory not found.${NC}"
    echo -e "${YELLOW}   The application may not work correctly without these directories.${NC}"
    echo -e "${YELLOW}   Make sure to run generate_embeddings.py first to create the vectorstore.${NC}"
fi

# Build the Docker image
echo -e "${BLUE}📦 Building Docker image...${NC}"
docker build -t "${FULL_IMAGE_NAME}" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully: ${FULL_IMAGE_NAME}${NC}"
    
    # Show image size
    SIZE=$(docker images --format "table {{.Size}}" "${FULL_IMAGE_NAME}" | tail -1)
    echo -e "${BLUE}📊 Image size: ${SIZE}${NC}"
    
    echo ""
    echo -e "${GREEN}🚀 To run the containers:${NC}"
    echo -e "${YELLOW}   API Server:     docker run -p 8000:8000 ${FULL_IMAGE_NAME}${NC}"
    echo -e "${YELLOW}   Streamlit App:  docker run -p 8501:8501 ${FULL_IMAGE_NAME} streamlit run app_main.py --server.port=8501 --server.address=0.0.0.0${NC}"
    echo -e "${YELLOW}   Docker Compose: docker-compose up${NC}"
    echo ""
    echo -e "${BLUE}🌐 Endpoints:${NC}"
    echo -e "${YELLOW}   API Health:     http://localhost:8000/health${NC}"
    echo -e "${YELLOW}   API Docs:       http://localhost:8000/docs${NC}"
    echo -e "${YELLOW}   Streamlit App:  http://localhost:8501${NC}"
    
else
    echo -e "${RED}❌ Docker image build failed!${NC}"
    exit 1
fi
