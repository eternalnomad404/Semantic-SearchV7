"""
Pydantic models for API request and response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union


class SearchRequest(BaseModel):
    """Request schema for search endpoint"""
    query: str = Field(..., min_length=1, description="Search query string")
    k: Optional[int] = Field(20, ge=1, le=100, description="Number of results to return")
    min_score: Optional[float] = Field(0.3, ge=0.0, le=1.0, description="Minimum relevance score threshold")


class SearchResultMetadata(BaseModel):
    """Metadata for search results"""
    values: List[str] = Field(default_factory=list, description="Display values from the original data")
    sheet: Optional[str] = Field(None, description="Source sheet/category name")
    industry: Optional[str] = Field(None, description="Industry (case studies only)")
    problem_type: Optional[str] = Field(None, description="Problem type (case studies only)")
    case_study_id: Optional[int] = Field(None, description="Case study ID")
    summary: Optional[str] = Field(None, description="Case study summary")
    word_count: Optional[int] = Field(None, description="Word count (case studies only)")
    short_description: Optional[str] = Field(None, description="Short description of the item")


class SearchResult(BaseModel):
    """Individual search result"""
    rank: int = Field(..., description="Result ranking position")
    title: str = Field(..., description="Display title of the result")
    category_type: str = Field(..., description="Category type: TOOL, COURSE, SERVICE PROVIDER, or CASE STUDY")
    url: str = Field(..., description="Clickable URL to the resource")
    score: float = Field(..., description="Combined relevance score (0-1)")
    semantic_score: float = Field(..., description="Semantic similarity score (0-1)")
    tfidf_score: float = Field(..., description="TF-IDF keyword matching score (0-1)")
    source_sheet: str = Field(..., description="Source data sheet name")
    metadata: SearchResultMetadata = Field(..., description="Additional metadata")


class SearchResponse(BaseModel):
    """Response schema for search endpoint"""
    status: str = Field(..., description="Response status: success or error")
    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., description="Total number of results returned")
    detected_category: str = Field("all", description="Detected search category")
    execution_time_ms: float = Field(..., description="Search execution time in milliseconds")
    results: List[SearchResult] = Field(default_factory=list, description="List of search results")


class ErrorResponse(BaseModel):
    """Error response schema"""
    status: str = Field("error", description="Response status")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field("healthy", description="Service health status")
    version: str = Field(..., description="Application version")
    search_engine_loaded: bool = Field(..., description="Whether search engine is properly loaded")
    total_documents: int = Field(..., description="Total number of indexed documents")


class StatsResponse(BaseModel):
    """Statistics response schema"""
    total_documents: int = Field(..., description="Total number of indexed documents")
    categories: Dict[str, int] = Field(..., description="Document count by category")
    model_name: str = Field(..., description="Semantic model name")
    index_dimension: int = Field(..., description="Vector index dimension")


class CategoriesResponse(BaseModel):
    """Categories response schema"""
    categories: List[str] = Field(..., description="Available search categories")
    category_counts: Dict[str, int] = Field(..., description="Document count per category")
    description: str = Field("Available search categories in the system", description="Response description")
