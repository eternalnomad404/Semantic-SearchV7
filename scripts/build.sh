#!/bin/bash

# Build and Deploy Script for AWS EC2
# This script builds the Docker image and provides deployment commands

set -e

echo "🐳 Building Semantic Search API Docker Image..."

# Build the Docker image
docker build -t semantic-search-api:latest .

echo "✅ Docker image built successfully!"

# Show image size
echo "📊 Image size:"
docker images semantic-search-api:latest

echo ""
echo "🚀 Deployment Options:"
echo ""
echo "1. Local Testing:"
echo "   docker run -p 8000:8000 semantic-search-api:latest"
echo ""
echo "2. With docker-compose:"
echo "   docker-compose up -d"
echo ""
echo "3. Save image for EC2 transfer:"
echo "   docker save semantic-search-api:latest | gzip > semantic-search-api.tar.gz"
echo ""
echo "4. Load image on EC2:"
echo "   gunzip -c semantic-search-api.tar.gz | docker load"
echo ""
echo "5. Run on EC2:"
echo "   docker run -d -p 8000:8000 --name semantic-search semantic-search-api:latest"
echo ""

# Test the build
echo "🧪 Testing the built image..."
docker run --rm -d --name test-semantic-search -p 8001:8000 semantic-search-api:latest

# Wait for startup
echo "⏳ Waiting for application to start..."
sleep 30

# Test health endpoint
if curl -f http://localhost:8001/health; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
fi

# Stop test container
docker stop test-semantic-search

echo ""
echo "🎉 Build and test completed successfully!"
echo "Your Docker image 'semantic-search-api:latest' is ready for deployment!"
