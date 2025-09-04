# Docker Deployment Guide

This guide covers how to build and run the Semantic Search application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for multi-container setup)
- Git (for cloning the repository)

## Quick Start

### 1. Build the Docker Image

#### Windows:
```bash
./docker-build.bat
```

#### Linux/macOS:
```bash
chmod +x docker-build.sh
./docker-build.sh
```

#### Manual build:
```bash
docker build -t semantic-search:latest .
```

### 2. Run the Application

#### Option A: API Server (FastAPI)
```bash
docker run -p 8000:8000 semantic-search:latest
```
- Access API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

#### Option B: Streamlit Web App
```bash
docker run -p 8501:8501 semantic-search:latest streamlit run app_main.py --server.port=8501 --server.address=0.0.0.0
```
- Access app: http://localhost:8501

#### Option C: Both Services (Docker Compose)
```bash
docker-compose up
```
- API: http://localhost:8000
- Streamlit: http://localhost:8501

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:
- `GROQ_API_KEY`: Optional Groq API key for enhanced features
- `MODEL_NAME`: Sentence transformer model name (default: all-MiniLM-L6-v2)
- `CORS_ORIGINS`: CORS settings for API

### Volume Mounts

For development or custom data:

```bash
# Mount custom data
docker run -p 8000:8000 \
  -v /path/to/your/data:/app/data:ro \
  -v /path/to/your/vectorstore:/app/vectorstore:ro \
  semantic-search:latest
```

## API Usage

### Search Endpoint
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "digital transformation tools",
    "k": 10,
    "min_score": 0.3
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Data Requirements

The application requires:

1. **Data files** (in `data/` directory):
   - `tools.xlsx` - Tools and software data
   - `service-providers.xlsx` - Service provider data  
   - `training-courses.xlsx` - Training course data
   - `case_studies_metadata.json` - Case study data

2. **Vector store** (in `vectorstore/` directory):
   - `faiss_index.index` - FAISS vector index
   - `metadata.json` - Document metadata
   - `tfidf.pkl` - TF-IDF vectorizer

### Generating Vector Store

If you don't have the vector store files:

```bash
# Generate embeddings locally first
python generate_embeddings.py

# Then build Docker image
docker build -t semantic-search:latest .
```

## Troubleshooting

### Common Issues

1. **"Search engine not initialized"**
   - Ensure vector store files exist in `vectorstore/`
   - Check file permissions
   - Verify data files are present

2. **High memory usage**
   - Adjust Docker memory limits
   - Use smaller model if needed

3. **Port conflicts**
   - Change port mapping: `-p 8080:8000`

### Debugging

Run with debug logs:
```bash
docker run -p 8000:8000 -e LOG_LEVEL=DEBUG semantic-search:latest
```

Access container shell:
```bash
docker run -it semantic-search:latest /bin/bash
```

## Production Deployment

### Security Considerations

1. Use non-root user (already configured)
2. Set appropriate CORS origins
3. Use secrets management for API keys
4. Enable HTTPS with reverse proxy

### Performance Optimization

1. Use multi-stage builds (already implemented)
2. Set resource limits:
   ```bash
   docker run --memory=2g --cpus=1 semantic-search:latest
   ```
3. Use Docker volumes for persistent storage

### Example Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  semantic-search:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CORS_ORIGINS=https://yourdomain.com
    volumes:
      - ./data:/app/data:ro
      - ./vectorstore:/app/vectorstore:ro
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1'
```

## Image Information

- **Base Image**: python:3.11-slim
- **Size**: ~1.2GB (approximate)
- **Architecture**: Multi-stage build for optimization
- **User**: Non-root user for security
- **Health Check**: Included
- **Exposed Ports**: 8000 (API), 8501 (Streamlit)
