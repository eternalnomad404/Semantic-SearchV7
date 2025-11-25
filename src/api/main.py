"""
FastAPI REST API for Semantic Search System
Converts Streamlit app to REST API endpoints
"""

import time
import traceback
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.models import (
    SearchRequest, SearchResponse, SearchResult, SearchResultMetadata,
    ErrorResponse, HealthResponse, StatsResponse, CategoriesResponse
)
from src.core.search_engine import SemanticSearcher, get_git_commit_hash

# Global search engine instance
search_engine: SemanticSearcher = None


def extract_slug_from_url(url: str) -> str:
    """
    Extract slug from URL by getting the last path segment.
    Example: 
        "https://dt4si.com/case-studies/learning-link-foundation" -> "learning-link-foundation"
        "https://dt4si.com/tools/chatgpt" -> "chatgpt"
    """
    if not url:
        return ""
    
    # Remove trailing slash if present
    url = url.rstrip('/')
    
    # Get the last segment after the last slash
    slug = url.split('/')[-1]
    
    return slug


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - initialize search engine on startup"""
    global search_engine
    try:
        print("🚀 Initializing Semantic Search Engine...")
        search_engine = SemanticSearcher()
        print(f"✅ Search engine loaded with {len(search_engine.metadata)} documents")
        yield
    except Exception as e:
        print(f"❌ Failed to initialize search engine: {e}")
        raise
    finally:
        print("🔄 Shutting down...")


# Create FastAPI app with lifespan manager
app = FastAPI(
    title="Hybrid Semantic Search API",
    description="REST API for semantic search across tools, services, courses, and case studies",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def transform_result_to_api_format(result: Dict[str, Any], rank: int) -> SearchResult:
    """Transform internal search result to API format"""
    metadata = result['metadata']
    
    # Get category information using the same logic as the search engine
    sheet_name = metadata.get('sheet', '').lower()
    values = metadata.get('values', [])
    
    # Determine category type and display header based on source
    if "case-studies" in sheet_name:
        category_type = "CASE STUDY"
        # For case studies, use the clean title as header
        case_study_title = metadata.get('values', ['Unknown'])[0]
        # Clean up the title display
        display_header = case_study_title.replace('- ', '').split('(')[0].strip()
    elif "tools" in sheet_name.lower() or "cleaned sheet" in sheet_name.lower():
        category_type = "TOOL"
        # For tools, use the tool name (index 2)
        display_header = values[2] if len(values) >= 3 else ' | '.join(values)
    elif "training" in sheet_name.lower():
        category_type = "COURSE"
        # For courses, use the course title (index 2)
        display_header = values[2] if len(values) >= 3 else ' | '.join(values)
    else:
        category_type = "SERVICE PROVIDER"
        # For service providers, use the provider name (index 0)
        display_header = values[0] if len(values) >= 1 else ' | '.join(values)
    
    # Generate URL
    url = search_engine._generate_result_url(result)
    
    # Extract slug from the generated URL
    slug = extract_slug_from_url(url)
    
    # Create metadata object
    result_metadata = SearchResultMetadata(
        values=metadata.get('values', []),
        sheet=metadata.get('sheet', ''),
        industry=metadata.get('industry'),
        problem_type=metadata.get('problem_type'),
        case_study_id=metadata.get('case_study_id'),
        summary=metadata.get('summary'),
        word_count=metadata.get('word_count'),
        short_description=metadata.get('short_description', ''),  # Add short_description
        slug=slug,  # Add extracted slug
        image=metadata.get('image')  # Add image path from external API
    )
    
    return SearchResult(
        rank=rank,
        title=display_header,
        category_type=category_type,
        url=url,
        score=result['score'],
        semantic_score=result['semantic_score'],
        tfidf_score=result['tfidf_score'],
        source_sheet=metadata.get('sheet', ''),
        metadata=result_metadata
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    error_details = traceback.format_exc()
    print(f"❌ Unhandled exception: {error_details}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            details=str(exc)
        ).dict()
    )


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Hybrid Semantic Search API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        commit_hash = get_git_commit_hash()
        
        if search_engine is None:
            raise HTTPException(status_code=503, detail="Search engine not initialized")
        
        return HealthResponse(
            status="healthy",
            version=f"1.0.0-{commit_hash}",
            search_engine_loaded=True,
            total_documents=len(search_engine.metadata)
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get search engine statistics"""
    try:
        if search_engine is None:
            raise HTTPException(status_code=503, detail="Search engine not initialized")
        
        stats = search_engine.get_stats()
        
        return StatsResponse(
            total_documents=stats['total_documents'],
            categories=stats['categories'],
            model_name=stats['model_name'],
            index_dimension=stats['index_dimension']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.get("/categories", response_model=CategoriesResponse)
async def get_categories():
    """Get available search categories"""
    try:
        if search_engine is None:
            raise HTTPException(status_code=503, detail="Search engine not initialized")
        
        categories_data = search_engine.get_categories()
        
        return CategoriesResponse(
            categories=categories_data['categories'],
            category_counts=categories_data['category_counts']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Main search endpoint
    
    Performs hybrid semantic search (70% semantic + 30% TF-IDF) across:
    - Tools and software
    - Service providers
    - Training courses
    - Case studies
    
    Returns ranked, categorized results with clickable URLs.
    """
    try:
        if search_engine is None:
            raise HTTPException(status_code=503, detail="Search engine not initialized")
        
        # Validate query length
        if len(request.query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters long")
        
        # Start timing
        start_time = time.time()
        
        # Perform search
        results, detected_category = search_engine.search(
            query=request.query,
            k=request.k,
            min_score=request.min_score
        )
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Transform results to API format
        api_results = []
        for rank, result in enumerate(results, 1):
            try:
                api_result = transform_result_to_api_format(result, rank)
                api_results.append(api_result)
            except Exception as e:
                print(f"⚠️ Error transforming result {rank}: {e}")
                continue
        
        return SearchResponse(
            status="success",
            query=request.query,
            total_results=len(api_results),
            detected_category=detected_category,
            execution_time_ms=execution_time_ms,
            results=api_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Search error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# Test endpoint for debugging
@app.post("/search/debug", response_model=Dict[str, Any])
async def search_debug(request: SearchRequest):
    """Debug endpoint that returns raw search results"""
    try:
        if search_engine is None:
            raise HTTPException(status_code=503, detail="Search engine not initialized")
        
        start_time = time.time()
        results, detected_category = search_engine.search(
            query=request.query,
            k=request.k,
            min_score=request.min_score
        )
        execution_time_ms = (time.time() - start_time) * 1000
        
        return {
            "query": request.query,
            "execution_time_ms": execution_time_ms,
            "total_results": len(results),
            "detected_category": detected_category,
            "raw_results": results[:5]  # First 5 results for debugging
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug search failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
