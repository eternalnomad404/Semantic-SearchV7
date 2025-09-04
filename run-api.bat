@echo off
echo 🚀 Starting Semantic Search API...
docker run --rm -d --name semantic-search-api -p 8000:8000 semantic-search:latest
echo ✅ API started at http://localhost:8000
echo 📚 Health check: http://localhost:8000/health
echo 🔍 Search endpoint: http://localhost:8000/search
echo.
echo To stop: docker stop semantic-search-api
