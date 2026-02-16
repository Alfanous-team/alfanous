#!/usr/bin/env python
# coding: utf-8

"""
Alfanous FastAPI Web Application

A minimal FastAPI application that exposes the Alfanous Quranic search API
through RESTful endpoints.

Usage:
    uvicorn alfanous.web_api:app --reload
    
    or
    
    python -m alfanous.web_api
"""

from typing import Optional, Dict, Any, Union, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import alfanous.api as alfanous_api


# FastAPI app instance
app = FastAPI(
    title="Alfanous API",
    description="""
    Alfanous is a search engine for the Holy Qur'an that provides simple and advanced search capabilities.
    
    ## Features
    - Search in Quranic verses with advanced filters
    - Get suggestions and autocompletion
    - Access metadata about the Quran (chapters, translations, recitations)
    - Support for Arabic script and Buckwalter transliteration
    - Faceted search and filtering capabilities
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Pydantic models for request/response validation
class SearchRequest(BaseModel):
    """Request model for search endpoint"""
    query: str = Field(..., description="Search query in Arabic or Buckwalter transliteration")
    unit: str = Field("aya", description="Search unit: 'aya' (verse), 'word', or 'translation'")
    page: int = Field(1, ge=1, description="Page number for pagination")
    perpage: int = Field(10, ge=1, le=100, description="Results per page")
    sortedby: str = Field("relevance", description="Sort order: 'score', 'relevance', 'mushaf', 'tanzil', 'subject'")
    fuzzy: bool = Field(False, description="Enable fuzzy search")
    view: str = Field("normal", description="View mode: 'minimal', 'normal', 'full', 'statistic', 'linguistic', 'custom'")
    highlight: str = Field("bold", description="Highlight mode: 'css', 'html', 'bold', 'bbcode'")
    script: Optional[str] = Field(None, description="Script type: 'standard' or 'uthmani'")
    vocalized: Optional[bool] = Field(None, description="Include vocalization (tashkeel)")
    translation: Optional[str] = Field(None, description="Translation ID")
    recitation: Optional[str] = Field(None, description="Recitation ID")
    prev_aya: Optional[bool] = Field(None, description="Include previous verse")
    next_aya: Optional[bool] = Field(None, description="Include next verse")
    sura_info: Optional[bool] = Field(None, description="Include surah information")
    word_info: Optional[bool] = Field(None, description="Include word information")
    aya_theme_info: Optional[bool] = Field(None, description="Include verse theme information")
    aya_stat_info: Optional[bool] = Field(None, description="Include verse statistics")
    facets: Optional[Union[str, List[str]]] = Field(None, description="Facets to include in results")
    filter: Optional[Dict[str, Any]] = Field(None, description="Filters to apply (field: value pairs)")


class SuggestRequest(BaseModel):
    """Request model for suggest endpoint"""
    query: str = Field(..., description="Query string for suggestions")
    unit: str = Field("aya", description="Search unit: 'aya', 'word', or 'translation'")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    message: str


# Root endpoint
@app.get("/", tags=["Info"])
async def root():
    """
    Root endpoint - provides basic API information and available endpoints.
    """
    return {
        "name": "Alfanous API",
        "description": "A search engine API for the Holy Qur'an",
        "version": "1.0.0",
        "endpoints": {
            "search": {
                "GET": "/api/search",
                "POST": "/api/search",
                "description": "Search in Quranic verses and translations"
            },
            "suggest": {
                "POST": "/api/suggest",
                "description": "Get search suggestions and autocompletion"
            },
            "info": {
                "GET": "/api/info",
                "GET_specific": "/api/info/{category}",
                "description": "Get metadata about the Quran (chapters, translations, recitations, etc.)"
            },
            "health": {
                "GET": "/health",
                "description": "Health check endpoint"
            },
            "docs": {
                "Swagger UI": "/docs",
                "ReDoc": "/redoc",
                "description": "Interactive API documentation"
            }
        },
        "usage": "Visit /docs for interactive documentation and testing"
    }


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return HealthResponse(
        status="healthy",
        message="Alfanous API is running"
    )


# Search endpoint (POST)
@app.post("/api/search", tags=["Search"])
async def search_post(request: SearchRequest):
    """
    Search in Quranic verses and translations (POST method).
    
    This endpoint allows you to search the Quran with various filters and options.
    Supports Arabic text and Buckwalter transliteration.
    
    Returns:
        JSON response with search results, metadata, and pagination info
    """
    try:
        # Build flags dictionary from request
        flags = {
            "action": "search",
            "query": request.query,
            "unit": request.unit,
            "page": request.page,
            "range": request.perpage,
            "sortedby": request.sortedby,
            "fuzzy": request.fuzzy,
            "view": request.view,
            "highlight": request.highlight,
        }
        
        # Add optional parameters if provided
        if request.script is not None:
            flags["script"] = request.script
        if request.vocalized is not None:
            flags["vocalized"] = request.vocalized
        if request.translation is not None:
            flags["translation"] = request.translation
        if request.recitation is not None:
            flags["recitation"] = request.recitation
        if request.prev_aya is not None:
            flags["prev_aya"] = request.prev_aya
        if request.next_aya is not None:
            flags["next_aya"] = request.next_aya
        if request.sura_info is not None:
            flags["sura_info"] = request.sura_info
        if request.word_info is not None:
            flags["word_info"] = request.word_info
        if request.aya_theme_info is not None:
            flags["aya_theme_info"] = request.aya_theme_info
        if request.aya_stat_info is not None:
            flags["aya_stat_info"] = request.aya_stat_info
        if request.facets is not None:
            flags["facets"] = request.facets
        if request.filter is not None:
            flags["filter"] = request.filter
        
        # Execute search
        result = alfanous_api.do(flags)
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Search endpoint (GET)
@app.get("/api/search", tags=["Search"])
async def search_get(
    query: str = Query(..., description="Search query in Arabic or Buckwalter transliteration"),
    unit: str = Query("aya", description="Search unit: 'aya', 'word', or 'translation'"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    perpage: int = Query(10, ge=1, le=100, description="Results per page"),
    sortedby: str = Query("relevance", description="Sort order: 'score', 'relevance', 'mushaf', 'tanzil', 'subject'"),
    fuzzy: bool = Query(False, description="Enable fuzzy search"),
    view: str = Query("normal", description="View mode: 'minimal', 'normal', 'full', 'statistic', 'linguistic', 'custom'"),
    highlight: str = Query("bold", description="Highlight mode: 'css', 'html', 'bold', 'bbcode'"),
    script: Optional[str] = Query(None, description="Script type: 'standard' or 'uthmani'"),
    vocalized: Optional[bool] = Query(None, description="Include vocalization (tashkeel)"),
    translation: Optional[str] = Query(None, description="Translation ID"),
    recitation: Optional[str] = Query(None, description="Recitation ID"),
    prev_aya: Optional[bool] = Query(None, description="Include previous verse"),
    next_aya: Optional[bool] = Query(None, description="Include next verse"),
    sura_info: Optional[bool] = Query(None, description="Include surah information"),
    word_info: Optional[bool] = Query(None, description="Include word information"),
    aya_theme_info: Optional[bool] = Query(None, description="Include verse theme information"),
    aya_stat_info: Optional[bool] = Query(None, description="Include verse statistics"),
):
    """
    Search in Quranic verses and translations (GET method).
    
    This endpoint allows you to search the Quran with various filters and options.
    Supports Arabic text and Buckwalter transliteration.
    
    Returns:
        JSON response with search results, metadata, and pagination info
    """
    try:
        # Build flags dictionary from query parameters
        flags = {
            "action": "search",
            "query": query,
            "unit": unit,
            "page": page,
            "range": perpage,
            "sortedby": sortedby,
            "fuzzy": fuzzy,
            "view": view,
            "highlight": highlight,
        }
        
        # Add optional parameters if provided
        if script is not None:
            flags["script"] = script
        if vocalized is not None:
            flags["vocalized"] = vocalized
        if translation is not None:
            flags["translation"] = translation
        if recitation is not None:
            flags["recitation"] = recitation
        if prev_aya is not None:
            flags["prev_aya"] = prev_aya
        if next_aya is not None:
            flags["next_aya"] = next_aya
        if sura_info is not None:
            flags["sura_info"] = sura_info
        if word_info is not None:
            flags["word_info"] = word_info
        if aya_theme_info is not None:
            flags["aya_theme_info"] = aya_theme_info
        if aya_stat_info is not None:
            flags["aya_stat_info"] = aya_stat_info
        
        # Execute search
        result = alfanous_api.do(flags)
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Suggest endpoint
@app.post("/api/suggest", tags=["Search"])
async def suggest(request: SuggestRequest):
    """
    Get search suggestions and autocompletion.
    
    This endpoint provides suggestions based on the query string to help
    users formulate their search queries.
    
    Returns:
        JSON response with suggestions
    """
    try:
        flags = {
            "action": "suggest",
            "query": request.query,
            "unit": request.unit,
        }
        
        result = alfanous_api.do(flags)
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Info endpoint - get all metadata
@app.get("/api/info", tags=["Info"])
async def get_info_all():
    """
    Get all available metadata information.
    
    Returns information about:
    - Chapters (surates)
    - Translations available
    - Recitations available
    - Default values
    - Available fields
    - Help messages
    - And more
    
    Returns:
        JSON response with all metadata
    """
    try:
        result = alfanous_api.get_info("all")
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Info endpoint - get specific category
@app.get("/api/info/{category}", tags=["Info"])
async def get_info_category(category: str):
    """
    Get specific metadata information.
    
    Available categories:
    - chapters: Information about Quranic chapters
    - surates: Same as chapters
    - translations: Available translations
    - recitations: Available recitations
    - defaults: Default search parameters
    - domains: Valid values for parameters
    - fields: Available search fields
    - flags: All available flags/parameters
    - help_messages: Help text for parameters
    - hints: Search hints and tips
    - information: General API information
    - errors: Error codes and messages
    
    Returns:
        JSON response with requested metadata
    """
    try:
        result = alfanous_api.get_info(category)
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Entry point for console script
def main():
    """Entry point for alfanous-server command"""
    import uvicorn
    uvicorn.run("alfanous.web_api:app", host="0.0.0.0", port=8000, reload=False)


# Entry point for running the server directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
