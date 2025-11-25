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
│   │   ├── __init__.py
│   │   ├── main.py              # API endpoints
│   │   └── models.py            # Pydantic models
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   └── search_engine.py     # Search algorithm
│   ├── ui/                       # User interfaces
│   │   ├── __init__.py
│   │   └── streamlit_app.py     # Streamlit UI
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── generate_embeddings.py
│       └── process_case_studies.py
├── data/                         # Data files
│   ├── tools.xlsx
│   ├── service-providers.xlsx
│   ├── training-courses.xlsx
│   ├── Case-Studies.docx
│   └── case_studies_metadata.json
├── vectorstore/                  # Generated embeddings
│   ├── faiss_index.index        # FAISS vector index
│   ├── metadata.json            # Document metadata
│   └── tfidf.pkl                # TF-IDF vectors
├── docker/                       # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
├── scripts/                      # Build & deployment scripts
│   ├── build.bat
│   ├── build.sh
│   ├── docker-build.bat
│   ├── docker-build.sh
│   ├── ec2-setup.sh
│   └── run-api.bat
├── docs/                         # Documentation
│   ├── DEPLOYMENT.md
│   └── DOCKER.md
├── main.py                       # API entry point
├── streamlit_app.py             # UI entry point
├── requirements.txt
├── .env.example
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
   # Edit .env and add your GROQ_API_KEY (optional, for case study processing)
   ```

5. **Generate embeddings** (if not already done)
   ```bash
   python src/utils/generate_embeddings.py
   ```

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

### Generating New Embeddings

```bash
# Process case studies from Word doc
python src/utils/process_case_studies.py

# Generate FAISS embeddings
python src/utils/generate_embeddings.py
```

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

Configuration is managed through environment variables:

```bash
# .env file
GROQ_API_KEY=your_api_key_here  # Optional: for case study processing
MODEL_NAME=all-MiniLM-L6-v2
INDEX_PATH=vectorstore/faiss_index.index
METADATA_PATH=vectorstore/metadata.json
TFIDF_PATH=vectorstore/tfidf.pkl
```

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
