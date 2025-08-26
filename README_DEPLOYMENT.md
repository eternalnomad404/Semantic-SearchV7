# 🚀 Semantic Search API - Railway Deployment

## Overview
This is a production-ready FastAPI application that provides hybrid semantic search across tools, services, courses, and case studies.

## Features
- **Hybrid Search**: 70% Semantic + 30% TF-IDF
- **RESTful API**: JSON request/response
- **Auto-scaling**: Railway handles scaling
- **Health Monitoring**: Built-in health checks
- **CORS Support**: Cross-origin requests enabled

## API Endpoints

### Main Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `POST /search` - Main search endpoint

### Example Request
```bash
curl -X POST "https://your-app.railway.app/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI tools", "k": 5}'
```

## Deployment Info
- **Platform**: Railway
- **Runtime**: Python 3.11.9
- **Framework**: FastAPI + Uvicorn
- **Database**: Vector store (FAISS) + TF-IDF
- **Health Check**: `/health` endpoint

## Environment Variables
The app automatically detects Railway environment and configures itself accordingly.

## Performance
- **Search Engine**: 373+ indexed documents
- **Response Time**: ~50-200ms per search
- **Memory Usage**: ~512MB-1GB
- **Concurrent Users**: Supports multiple users

## Support
For issues or questions, check the `/docs` endpoint for interactive API documentation.
