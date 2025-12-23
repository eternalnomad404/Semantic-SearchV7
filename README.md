A hybrid search system combining semantic search (70%) and TF-IDF keyword matching (30%) for intelligent search across tools, service providers, training courses, and case studies.

## 📋 Table of Contents
Money. 
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)

## ✨ Features

- **Hybrid Search Algorithm**: 70% semantic similarity + 30% TF-IDF keyword matching
- **Multi-Category Search**: Tools, Services, Courses, Case Studies
- **RESTful API**: FastAPI-based REST API with automatic documentation
- **Interactive UI**: Streamlit web interface for easy searching
- **Docker Support**: Fully containerized with Docker and Docker Compose
- **Production Ready**: Health checks, logging, error handling

## 🏗️ Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
    ┌────▼────┐
    │  API /  │
    │   UI    │
    └────┬────┘
         │
    ┌────▼─────────────────┐
    │  Semantic Searcher   │
    │  (Hybrid Algorithm)  │
    └────┬─────────┬───────┘
         │         │
    ┌────▼────┐ ┌─▼──────┐
    │  FAISS  │ │ TF-IDF │
    │  Index  │ │ Vectors│
    └─────────┘ └────────┘
```

## 📁 Project Structure

```
semantic-search/
├── src/                          # Source code
│   ├── api/                      # FastAPI REST API
│   │   ├── main.py              # API endpoints
│   │   └── models.py            # Pydantic models
│   ├── core/                     # Core functionality
│   │   └── search_engine.py     # Search algorithm
│   ├── ui/                       # User interfaces
│   │   └── streamlit_app.py     # Streamlit UI
│   └── utils/                    # Utilities
│       ├── fetch_data_from_apis.py   # API data fetcher
│       ├── generate_embeddings.py    # Embedding generator
│       ├── data_loader.py            # Multi-file data loader
│       └── fetch_external_images.py  # Image fetcher
├── data/                         # Split API data (JSON files organized by category)
│   ├── tools/                   # Tools data (split into multiple files)
│   │   ├── tools_part_01.json
│   │   ├── tools_part_02.json
│   │   └── ...
│   ├── service_providers/       # Service provider data
│   │   └── providers_part_01.json
│   ├── courses/                 # Course data (split into multiple files)
│   │   ├── courses_part_01.json
│   │   └── ...
│   ├── case_studies/            # Case study data
│   │   └── case_studies_part_01.json
│   └── slug_to_image_mapping.json
├── vectorstore/                  # Generated embeddings
│   ├── faiss_index.index        # FAISS vector index
│   ├── metadata.json            # Document metadata
│   └── tfidf.pkl                # TF-IDF vectors
├── docker/                       # Docker configuration
├── scripts/                      # Build & deployment scripts
├── docs/                         # Documentation
├── main.py                       # API entry point
├── streamlit_app.py             # UI entry point
├── requirements.txt
├── verify_refactor.py           # Verification script for data structure
├── REFACTOR_SUMMARY.md          # Technical documentation of storage refactor
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip
- (Optional) Docker & Docker Compose

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/eternalnomad404/Semantic-SearchV7.git
   cd Semantic-SearchV7
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

5. **Fetch data from live API and generate embeddings**
   ```bash
   # Step 1: Fetch fresh data from DT4SI APIs
   python src/utils/fetch_data_from_apis.py
   
   # Step 2: Generate embeddings from cached data
   python src/utils/generate_embeddings.py
   ```
   
   **Note:** Step 1 requires internet to fetch from live APIs. Step 2 works offline using cached JSON files.

## 🎮 Running the Application

### Option 1: FastAPI REST API

```bash
# Using Python directly
python main.py

# Or using uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Access at:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Option 2: Streamlit Web UI

```bash
streamlit run streamlit_app.py
```

**Access at:** http://localhost:8501

### Option 3: Docker

```bash
# Build the image
docker build -t semantic-search:latest -f docker/Dockerfile .

# Run API
docker run -p 8000:8000 semantic-search:latest

# Run Streamlit UI
docker run -p 8501:8501 semantic-search:latest streamlit run src/ui/streamlit_app.py --server.port=8501 --server.address=0.0.0.0

# Or use Docker Compose
cd docker
docker-compose up
```

## 📚 API Documentation

### Search Endpoint

**POST** `/search`

**Request:**
```json
{
  "query": "AI tools for data analysis",
  "k": 20,
  "min_score": 0.3
}
```

**Response:**
```json
{
  "status": "success",
  "query": "AI tools for data analysis",
  "total_results": 15,
  "detected_category": "all",
  "execution_time_ms": 12.5,
  "results": [
    {
      "rank": 1,
      "title": "TensorFlow",
      "category_type": "TOOL",
      "url": "https://dt4si.com/tools/tensorflow",
      "score": 0.875,
      "semantic_score": 0.892,
      "tfidf_score": 0.823,
      "source_sheet": "Cleaned Sheet",
      "metadata": {...}
    }
  ]
}
```

### Other Endpoints

- `GET /health` - Health check
- `GET /stats` - Search engine statistics
- `GET /categories` - Available categories

See full API documentation at: http://localhost:8000/docs

## 💻 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/
```

### Code Structure

- **Search Engine** (`src/core/search_engine.py`): Core hybrid search algorithm
- **API** (`src/api/main.py`): FastAPI REST endpoints
- **UI** (`src/ui/streamlit_app.py`): Streamlit interface
- **Models** (`src/api/models.py`): Pydantic data models
- **Utilities** (`src/utils/`): Data processing scripts

### Updating Search Data

When content is updated in your database, refresh the search system:

```bash
# Step 1: Fetch fresh data from DT4SI live APIs
python src/utils/fetch_data_from_apis.py

# Step 2: Generate new embeddings
python src/utils/generate_embeddings.py

# Step 3: Restart your services
# Press Ctrl+C to stop, then restart:
python main.py              # For API
streamlit run streamlit_app.py  # For UI
```

**API Endpoints Used:**
- `https://dt4si.com/api/v1/tools`
- `https://dt4si.com/api/v1/services`
- `https://dt4si.com/api/v1/courses`
- `https://dt4si.com/api/v1/case-studies`

**What Gets Updated:**
- Tools: 199 items → `data/tools/` (6 split files)
- Services: 22 items → `data/service_providers/` (1 file)
- Courses: 108 items → `data/courses/` (3 split files)
- Case Studies: 14 items → `data/case_studies/` (1 file)

The system fetches data from live APIs and caches it locally in structured folders with split JSON files (each under 600 lines for better tooling support). Embeddings are then generated from the cached data, allowing offline regeneration without repeated API calls.

## 🐳 Docker Deployment

See detailed Docker documentation: [docs/DOCKER.md](docs/DOCKER.md)

### Quick Docker Commands

```bash
# Build
.\scripts\docker-build.bat  # Windows
./scripts/docker-build.sh   # Linux/Mac

# Run with compose
cd docker && docker-compose up -d

# Stop
docker-compose down
```

## ⚙️ Configuration

Configuration is managed through environment variables in `.env` file (optional):

```bash
# .env file (all optional)
MODEL_NAME=all-MiniLM-L6-v2
INDEX_PATH=vectorstore/faiss_index.index
METADATA_PATH=vectorstore/metadata.json
TFIDF_PATH=vectorstore/tfidf.pkl
```

**Note:** The system fetches data directly from DT4SI APIs. No API keys required for data fetching.

## 📖 Additional Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [Docker Guide](docs/DOCKER.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License

## 👤 Author

**eternalnomad404**

---

**Version:** 1.0.0  
**Last Updated:** November 2025
