@echo off
REM Docker build script for Semantic Search Application (Windows)
REM Usage: docker-build.bat [tag-name]

setlocal enabledelayedexpansion

REM Default image name and tag
set IMAGE_NAME=semantic-search
set TAG=%1
if "%TAG%"=="" set TAG=latest
set FULL_IMAGE_NAME=%IMAGE_NAME%:%TAG%

echo 🐳 Building Docker image: %FULL_IMAGE_NAME%

REM Check if we're in the right directory
if not exist "Dockerfile" (
    echo ❌ Error: Dockerfile not found. Please run this script from the project root directory.
    exit /b 1
)

REM Check if required files exist
set required_files=requirements.txt api_main.py search_engine.py models.py
for %%f in (%required_files%) do (
    if not exist "%%f" (
        echo ❌ Error: Required file '%%f' not found.
        exit /b 1
    )
)

REM Check if data and vectorstore directories exist
if not exist "data" (
    echo ⚠️  Warning: data/ directory not found.
    echo    The application may not work correctly without this directory.
)
if not exist "vectorstore" (
    echo ⚠️  Warning: vectorstore/ directory not found.
    echo    Make sure to run generate_embeddings.py first to create the vectorstore.
)

REM Build the Docker image
echo 📦 Building Docker image...
docker build -t "%FULL_IMAGE_NAME%" .

if %ERRORLEVEL% equ 0 (
    echo ✅ Docker image built successfully: %FULL_IMAGE_NAME%
    
    echo.
    echo 🚀 To run the containers:
    echo    API Server:     docker run -p 8000:8000 %FULL_IMAGE_NAME%
    echo    Streamlit App:  docker run -p 8501:8501 %FULL_IMAGE_NAME% streamlit run app_main.py --server.port=8501 --server.address=0.0.0.0
    echo    Docker Compose: docker-compose up
    echo.
    echo 🌐 Endpoints:
    echo    API Health:     http://localhost:8000/health
    echo    API Docs:       http://localhost:8000/docs
    echo    Streamlit App:  http://localhost:8501
) else (
    echo ❌ Docker image build failed!
    exit /b 1
)
