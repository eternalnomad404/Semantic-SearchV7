# Technology Stack Case Study: Semantic Search System
### Comprehensive Analysis of Technologies Used

**Project Name:** Hybrid Semantic Search System (DT4SI)  
**Analysis Date:** December 28, 2025  
**Architecture Type:** Python-based Microservices with REST API & Web UI

---

## 📊 Executive Summary

This is a **100% Python-based** application with **NO React, Node.js, or JavaScript frameworks**. The system uses modern Python web frameworks (FastAPI & Streamlit) for both API and UI components.

### Core Technology Stack:
- **Backend Framework:** FastAPI (Python web framework)
- **Web UI Framework:** Streamlit (Python-based web interface)
- **Machine Learning:** Sentence Transformers, FAISS, scikit-learn
- **Containerization:** Docker & Docker Compose
- **Database:** FAISS Vector Database + JSON metadata storage

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│  • Web Browsers (any modern browser)                        │
│  • HTTP Clients (cURL, Postman, etc.)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP/HTTPS
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                  APPLICATION LAYER (Python)                  │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐         ┌──────────────────┐          │
│  │   FastAPI API   │         │  Streamlit UI    │          │
│  │   (Port 8000)   │         │   (Port 8501)    │          │
│  │  REST Endpoints │         │   Web Interface  │          │
│  └────────┬────────┘         └────────┬─────────┘          │
│           │                           │                     │
│           └──────────┬────────────────┘                     │
│                      │                                      │
│           ┌──────────▼──────────┐                          │
│           │  SemanticSearcher   │                          │
│           │   (Core Engine)     │                          │
│           │  • Hybrid Algorithm │                          │
│           │  • 70% Semantic     │                          │
│           │  • 30% TF-IDF       │                          │
│           └──────────┬──────────┘                          │
└──────────────────────┼──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                   DATA LAYER (Python)                        │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ FAISS Index  │  │  TF-IDF     │  │  JSON Metadata   │   │
│  │ (Vectors)    │  │  Vectors    │  │  (Documents)     │   │
│  └──────────────┘  └─────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 🐍 Python Technologies Breakdown

### 1. **Web Frameworks**

#### **FastAPI** (REST API Backend)
- **Files Using:** 
  - [src/api/main.py](src/api/main.py)
  - [main.py](main.py) (entry point)
- **Purpose:** RESTful API server providing search endpoints
- **Key Features Used:**
  - `@app.get()`, `@app.post()` decorators for routing
  - `Pydantic` models for request/response validation
  - `CORSMiddleware` for cross-origin requests
  - `lifespan` context manager for startup/shutdown
  - Health check endpoints
  - Automatic OpenAPI documentation (Swagger UI)
- **Runs on:** Uvicorn ASGI server (Port 8000)
- **Example Endpoints:**
  ```python
  POST /search          # Search endpoint
  GET /health           # Health check
  GET /stats            # System statistics
  GET /categories       # Available categories
  ```

#### **Streamlit** (Web UI)
- **Files Using:**
  - [src/ui/streamlit_app.py](src/ui/streamlit_app.py)
  - [streamlit_app.py](streamlit_app.py) (entry point)
  - [golden_dataset_ui.py](golden_dataset_ui.py)
- **Purpose:** Interactive web interface for search
- **Key Features Used:**
  - `st.text_input()` for search queries
  - `st.expander()` for collapsible results
  - `st.progress()` for score visualization
  - `st.cache_resource` for caching search engine
  - `st.set_page_config()` for UI configuration
  - Columns layout (`st.columns()`)
  - Markdown rendering
- **Runs on:** Built-in Streamlit server (Port 8501)
- **No React/JavaScript:** Pure Python-based reactive UI

---

### 2. **Machine Learning & NLP**

#### **Sentence Transformers** (Semantic Embeddings)
- **Files Using:** [src/core/search_engine.py](src/core/search_engine.py), [src/utils/generate_embeddings.py](src/utils/generate_embeddings.py)
- **Model:** `all-MiniLM-L6-v2`
- **Purpose:** Convert text to 384-dimensional semantic vectors
- **Usage:**
  ```python
  model = SentenceTransformer("all-MiniLM-L6-v2")
  embeddings = model.encode(texts)
  ```

#### **FAISS** (Facebook AI Similarity Search)
- **Files Using:** [src/core/search_engine.py](src/core/search_engine.py), [src/utils/generate_embeddings.py](src/utils/generate_embeddings.py)
- **Purpose:** High-performance vector similarity search
- **Library:** `faiss-cpu` (CPU-optimized version)
- **Storage:** [vectorstore/faiss_index.index](vectorstore/faiss_index.index)
- **Operations:**
  - Index creation: `faiss.IndexFlatL2()`
  - Vector search: `index.search(query_vector, k)`
  - Persistence: `faiss.write_index()` / `faiss.read_index()`

#### **scikit-learn** (TF-IDF)
- **Files Using:** [src/core/search_engine.py](src/core/search_engine.py), [src/utils/generate_embeddings.py](src/utils/generate_embeddings.py)
- **Purpose:** Keyword-based search with TF-IDF
- **Components:**
  - `TfidfVectorizer` for text vectorization
  - `cosine_similarity` for similarity scoring
- **Storage:** [vectorstore/tfidf.pkl](vectorstore/tfidf.pkl) (pickled)

---

### 3. **Data Processing**

#### **Pandas**
- **Files Using:** [golden_dataset_ui.py](golden_dataset_ui.py)
- **Purpose:** Data analysis and display in UI
- **Usage:** DataFrame creation for tabular data display

#### **NumPy**
- **Files Using:** [src/utils/generate_embeddings.py](src/utils/generate_embeddings.py), [src/core/search_engine.py](src/core/search_engine.py)
- **Purpose:** Numerical operations, array manipulation
- **Usage:** Vector operations, normalization

---

### 4. **API & HTTP**

#### **Requests**
- **Files Using:** [src/utils/fetch_data_from_apis.py](src/utils/fetch_data_from_apis.py)
- **Purpose:** HTTP client for fetching data from external APIs
- **External API:** `https://dt4si.com/api/v1`
- **Endpoints Called:**
  - `/tools`, `/services`, `/courses`, `/case-studies`

#### **Uvicorn**
- **Files Using:** [main.py](main.py)
- **Purpose:** ASGI server for FastAPI
- **Configuration:**
  ```python
  uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
  ```

---

### 5. **Data Validation & Models**

#### **Pydantic**
- **Files Using:** [src/api/models.py](src/api/models.py)
- **Purpose:** Data validation and serialization
- **Models Defined:**
  - `SearchRequest` - API request schema
  - `SearchResponse` - API response schema
  - `SearchResult` - Individual result schema
  - `HealthResponse`, `StatsResponse`, etc.
- **Features:**
  - Type validation
  - Field constraints (`min_length`, `ge`, `le`)
  - Default values
  - Automatic JSON serialization

---

### 6. **Utilities & Supporting Libraries**

#### **python-dotenv**
- **Files Using:** [src/core/search_engine.py](src/core/search_engine.py)
- **Purpose:** Environment variable management
- **Usage:** `load_dotenv()` for loading `.env` files

#### **fuzzywuzzy + python-Levenshtein**
- **Listed in:** [requirements.txt](requirements.txt)
- **Purpose:** Fuzzy string matching (for potential enhancements)

#### **Groq**
- **Listed in:** [requirements.txt](requirements.txt)
- **Purpose:** AI/LLM integration (currently not actively used in search)
- **Note:** Client initialized but not used in main search flow

---

## 🐳 Containerization & Deployment

### **Docker**
- **Files Using:**
  - [docker/Dockerfile](docker/Dockerfile)
  - [docker/docker-compose.yml](docker/docker-compose.yml)
  
#### Dockerfile Analysis:
```dockerfile
# Base Image: Python 3.11 Slim
FROM python:3.11-slim

# Multi-stage build for optimization
# Stage 1: Builder (installs dependencies)
# Stage 2: Production (minimal runtime)
```

**Key Features:**
- Multi-stage build for smaller image size
- Non-root user for security
- Layer caching optimization
- Git included for version tracking

#### Docker Compose Services:
1. **semantic-search-api**
   - Port: 8000
   - Healthcheck: `curl http://localhost:8000/health`
   - Volumes: `data/` and `vectorstore/` (read-only)

2. **semantic-search-streamlit**
   - Port: 8501
   - Healthcheck: `curl http://localhost:8501/_stcore/health`
   - Same data volumes

---

## 📦 Python Dependencies (from requirements.txt)

| Package | Version | Purpose | Category |
|---------|---------|---------|----------|
| `faiss-cpu` | Latest | Vector similarity search | ML/AI |
| `pandas` | Latest | Data analysis | Data Processing |
| `sentence-transformers` | Latest | Text embeddings | ML/NLP |
| `streamlit` | Latest | Web UI framework | Web Framework |
| `numpy` | Latest | Numerical computing | Scientific Computing |
| `openpyxl` | Latest | Excel file handling | Data I/O |
| `scikit-learn` | Latest | TF-IDF, ML utilities | ML/AI |
| `groq` | Latest | LLM integration | AI/LLM |
| `python-dotenv` | Latest | Environment variables | Configuration |
| `fuzzywuzzy` | Latest | Fuzzy string matching | Text Processing |
| `python-Levenshtein` | Latest | String distance | Text Processing |
| `fastapi` | Latest | REST API framework | Web Framework |
| `uvicorn[standard]` | Latest | ASGI server | Web Server |
| `pydantic` | Latest | Data validation | Data Validation |
| `requests` | Latest | HTTP client | HTTP/API |

**Total Dependencies:** 15 Python packages  
**No JavaScript/Node.js dependencies**

---

## 📂 Project Structure Analysis

### Source Code Organization (`src/`)

```
src/
├── api/                    # FastAPI REST API
│   ├── main.py            # 312 lines - API endpoints & logic
│   ├── models.py          # 100+ lines - Pydantic schemas
│   └── __init__.py
│
├── core/                   # Business Logic
│   ├── search_engine.py   # 329 lines - Hybrid search algorithm
│   └── __init__.py
│
├── ui/                     # Streamlit UI
│   ├── streamlit_app.py   # 166 lines - Web interface
│   └── __init__.py
│
└── utils/                  # Utilities
    ├── data_loader.py           # 131 lines - Multi-file data loader
    ├── fetch_data_from_apis.py  # 273 lines - API data fetcher
    ├── generate_embeddings.py   # 234 lines - Embedding generator
    └── __init__.py
```

### Data Storage (`data/`)

```
data/
├── tools/              # 6 JSON files (tools_part_01 to 06)
├── courses/            # 3 JSON files (courses_part_01 to 03)
├── service_providers/  # 1 JSON file (providers_part_01)
└── case_studies/       # 1 JSON file (case_studies_part_01)
```

**Storage Strategy:** JSON-based file storage (no traditional database)  
**Rationale:** Simple, version-controllable, no database overhead

### Vector Storage (`vectorstore/`)

```
vectorstore/
├── faiss_index.index   # Binary FAISS index
├── metadata.json       # Document metadata (searchable fields)
└── tfidf.pkl           # Pickled TF-IDF vectors & vectorizer
```

---

## 🔄 Data Flow & Processing Pipeline

### 1. **Data Ingestion Flow**
```
External APIs (dt4si.com)
         ↓
fetch_data_from_apis.py (Python requests)
         ↓
JSON files (data/ folder)
         ↓
data_loader.py (loads & combines split files)
         ↓
generate_embeddings.py (creates vectors)
         ↓
vectorstore/ (FAISS + TF-IDF + metadata)
```

### 2. **Search Request Flow**
```
User Query (Browser/HTTP Client)
         ↓
FastAPI Endpoint (/search) OR Streamlit UI
         ↓
SemanticSearcher.search()
         ↓
┌──────────────┴──────────────┐
│                             │
Semantic Search (70%)    TF-IDF Search (30%)
FAISS Index              scikit-learn
│                             │
└──────────────┬──────────────┘
         ↓
Hybrid Score Calculation
         ↓
Results Ranking & Filtering
         ↓
JSON Response (FastAPI) OR UI Rendering (Streamlit)
```

---

## 🚀 Deployment Methods

### Local Development
```bash
# Method 1: Direct Python execution
python main.py                    # Runs FastAPI on port 8000
streamlit run streamlit_app.py    # Runs Streamlit on port 8501

# Method 2: Using uvicorn/streamlit CLI
uvicorn src.api.main:app --reload --port 8000
streamlit run src/ui/streamlit_app.py --server.port=8501
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f docker/docker-compose.yml up --build

# Both services run simultaneously:
# - API: http://localhost:8000
# - UI: http://localhost:8501
```

### Script-based Deployment
- **Windows:** [scripts/build.bat](scripts/build.bat), [scripts/run-api.bat](scripts/run-api.bat)
- **Linux/Mac:** [scripts/build.sh](scripts/build.sh), [scripts/ec2-setup.sh](scripts/ec2-setup.sh)
- **Docker:** [scripts/docker-build.bat](scripts/docker-build.bat), [scripts/docker-build.sh](scripts/docker-build.sh)

---

## 🔍 Technology Usage by Feature

### Feature: REST API
- **Primary:** FastAPI (routing, validation, CORS)
- **Supporting:** Pydantic (schemas), Uvicorn (server)
- **File:** [src/api/main.py](src/api/main.py)

### Feature: Web UI
- **Primary:** Streamlit (reactive UI)
- **Supporting:** Pandas (data display)
- **Files:** [src/ui/streamlit_app.py](src/ui/streamlit_app.py), [golden_dataset_ui.py](golden_dataset_ui.py)

### Feature: Semantic Search
- **Primary:** Sentence Transformers (embeddings), FAISS (vector search)
- **Supporting:** NumPy (array operations)
- **File:** [src/core/search_engine.py](src/core/search_engine.py)

### Feature: Keyword Search
- **Primary:** scikit-learn (TF-IDF)
- **Supporting:** NumPy (cosine similarity)
- **File:** [src/core/search_engine.py](src/core/search_engine.py)

### Feature: Data Fetching
- **Primary:** Requests (HTTP client)
- **Supporting:** JSON (stdlib), Pathlib
- **File:** [src/utils/fetch_data_from_apis.py](src/utils/fetch_data_from_apis.py)

### Feature: Embedding Generation
- **Primary:** Sentence Transformers, FAISS, scikit-learn
- **Supporting:** Pickle (serialization), JSON
- **File:** [src/utils/generate_embeddings.py](src/utils/generate_embeddings.py)

---

## 🎯 Technology Choices & Rationale

### Why FastAPI (not Flask)?
✅ **Automatic API documentation** (OpenAPI/Swagger)  
✅ **Type validation** with Pydantic  
✅ **Async support** for scalability  
✅ **Modern Python** (type hints, async/await)  
✅ **Fast performance** (Starlette-based)

### Why Streamlit (not React)?
✅ **Pure Python** - no JavaScript knowledge needed  
✅ **Rapid prototyping** - minimal code for UI  
✅ **Built-in widgets** - no custom components needed  
✅ **Auto-refresh** - reactive updates  
❌ **Limitation:** Less customizable than React

### Why FAISS (not Elasticsearch)?
✅ **Fast vector search** - optimized for embeddings  
✅ **No server** - file-based, no deployment complexity  
✅ **Memory efficient** - in-memory index  
✅ **Facebook-backed** - well-maintained  
❌ **Limitation:** No built-in filtering (handled in Python)

### Why JSON files (not PostgreSQL/MongoDB)?
✅ **Simplicity** - no database setup  
✅ **Version control** - Git-friendly  
✅ **Portability** - works everywhere  
✅ **Small dataset** - ~200-500 documents total  
❌ **Limitation:** Not suitable for millions of records

---

## 📊 Code Statistics

### Lines of Code (Python Only)
- **API Layer:** ~412 lines ([src/api/main.py](src/api/main.py) + [src/api/models.py](src/api/models.py))
- **Core Engine:** ~329 lines ([src/core/search_engine.py](src/core/search_engine.py))
- **UI Layer:** ~764 lines ([src/ui/streamlit_app.py](src/ui/streamlit_app.py) + [golden_dataset_ui.py](golden_dataset_ui.py))
- **Utilities:** ~638 lines (data_loader + fetch_data + generate_embeddings)
- **Entry Points:** ~24 lines ([main.py](main.py) + [streamlit_app.py](streamlit_app.py))

**Total Estimated:** ~2,167 lines of Python code (excluding comments/blanks)

### File Count
- **Python files:** 12+ `.py` files
- **JSON data files:** 11 files (split across categories)
- **Docker files:** 2 ([Dockerfile](docker/Dockerfile), [docker-compose.yml](docker/docker-compose.yml))
- **Shell scripts:** 5+ (build & deployment)
- **Documentation:** 3+ markdown files

---

## 🔐 Security & Best Practices

### Docker Security
✅ Non-root user (`app` user)  
✅ Multi-stage builds (smaller attack surface)  
✅ Read-only volume mounts  
✅ Health checks  

### API Security
✅ CORS middleware (configurable origins)  
✅ Input validation (Pydantic)  
✅ Error handling & logging  
⚠️ **Missing:** Rate limiting, authentication (add if public)

### Code Quality
✅ Type hints (Python 3.11+)  
✅ Docstrings  
✅ Error handling  
✅ Modular structure  
⚠️ **Missing:** Unit tests, integration tests

---

## 🚫 Technologies NOT Used

| Technology | Status | Why Not? |
|------------|--------|----------|
| **React** | ❌ Not Used | Streamlit provides Python-based UI |
| **Node.js** | ❌ Not Used | Python handles all backend/frontend |
| **JavaScript** | ❌ Not Used | Pure Python stack |
| **Flask** | ❌ Not Used | FastAPI chosen for modern features |
| **Django** | ❌ Not Used | Too heavy for API-only service |
| **PostgreSQL** | ❌ Not Used | JSON files sufficient for dataset size |
| **MongoDB** | ❌ Not Used | JSON files + FAISS sufficient |
| **Redis** | ❌ Not Used | In-memory FAISS index used instead |
| **Elasticsearch** | ❌ Not Used | FAISS + TF-IDF more suitable for vectors |
| **GraphQL** | ❌ Not Used | REST API simpler for use case |
| **Vue/Angular** | ❌ Not Used | Streamlit chosen |
| **TypeScript** | ❌ Not Used | No JavaScript in project |
| **Webpack/Vite** | ❌ Not Used | No frontend build needed |

---

## 📈 Scalability Considerations

### Current Limitations
- **In-memory storage:** FAISS index loaded in RAM
- **Single server:** No distributed search
- **File-based data:** Not suitable for millions of documents

### Scaling Options (if needed)
1. **Horizontal scaling:** Multiple API instances behind load balancer
2. **Database migration:** PostgreSQL with pgvector extension
3. **Caching:** Redis for frequently searched queries
4. **Async workers:** Celery for background embedding generation
5. **CDN:** For static assets (if UI grows)

---

## 🎓 Learning Resources

### For This Tech Stack:
- **FastAPI:** https://fastapi.tiangolo.com/
- **Streamlit:** https://docs.streamlit.io/
- **Sentence Transformers:** https://www.sbert.net/
- **FAISS:** https://github.com/facebookresearch/faiss
- **Pydantic:** https://docs.pydantic.dev/

---

## 📝 Summary Table

| Component | Technology | Type | Purpose |
|-----------|-----------|------|---------|
| **Backend API** | FastAPI | Python Web Framework | REST endpoints |
| **Web UI** | Streamlit | Python UI Framework | Interactive search interface |
| **Embeddings** | Sentence Transformers | ML/NLP Library | Text-to-vector conversion |
| **Vector Search** | FAISS | Vector Database | Similarity search |
| **Keyword Search** | scikit-learn TF-IDF | ML Library | Keyword matching |
| **Data Validation** | Pydantic | Validation Library | Request/response schemas |
| **HTTP Client** | Requests | HTTP Library | External API calls |
| **Server** | Uvicorn | ASGI Server | FastAPI runtime |
| **Containerization** | Docker + Compose | Container Platform | Deployment |
| **Data Storage** | JSON files | File Format | Document storage |
| **Programming Language** | Python 3.11+ | Language | Everything |

---

## ✅ Final Technology Verdict

### **This is a:**
- ✅ **100% Python Application**
- ✅ **Microservices Architecture** (API + UI as separate services)
- ✅ **Machine Learning Application** (Semantic search, embeddings)
- ✅ **RESTful Web Service**
- ✅ **Containerized Application** (Docker-ready)

### **This is NOT a:**
- ❌ **React Application** (no React used)
- ❌ **Node.js Application** (no Node.js used)
- ❌ **Full-stack JavaScript App** (no JavaScript)
- ❌ **Flask Application** (FastAPI instead)
- ❌ **Django Application** (FastAPI instead)
- ❌ **Traditional Database Application** (file + vector storage)

---

## 📞 Contact & Documentation

- **Main README:** [README.md](README.md)
- **Docker Guide:** [docs/DOCKER.md](docs/DOCKER.md)
- **Deployment Guide:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Refactor Summary:** REFACTOR_SUMMARY.md (if exists)

---

**Document Version:** 1.0  
**Last Updated:** December 28, 2025  
**Maintained By:** Development Team  
**Purpose:** Technology stack documentation for developers and stakeholders
