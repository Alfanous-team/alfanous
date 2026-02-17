"""
Tests for the Alfanous FastAPI Web Application

This module contains comprehensive tests for all endpoints in the web API,
including search, suggest, info, health, and root endpoints.
"""

import sys
import os

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

# Try to import FastAPI dependencies - skip all tests if not available
try:
    from fastapi.testclient import TestClient
    from alfanous_webapi.web_api import app, SearchResponse, SuggestResponse, InfoResponse, HealthResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="FastAPI dependencies not installed. Install with: pip install alfanous-webapi or pip install fastapi httpx")


# Create test client only if FastAPI is available
if FASTAPI_AVAILABLE:
    client = TestClient(app)
else:
    client = None


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_returns_200(self):
        """Test that root endpoint returns 200 status code"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_returns_api_info(self):
        """Test that root endpoint returns API information"""
        response = client.get("/")
        data = response.json()
        assert "name" in data
        assert data["name"] == "Alfanous API"
        assert "version" in data
        assert "endpoints" in data
    
    def test_root_lists_all_endpoints(self):
        """Test that root endpoint lists all available endpoints"""
        response = client.get("/")
        data = response.json()
        endpoints = data["endpoints"]
        assert "search" in endpoints
        assert "suggest" in endpoints
        assert "info" in endpoints
        assert "health" in endpoints


class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_returns_200(self):
        """Test that health endpoint returns 200 status code"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_returns_healthy_status(self):
        """Test that health endpoint returns healthy status"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
    
    def test_health_response_model(self):
        """Test that health endpoint returns HealthResponse model"""
        response = client.get("/health")
        data = response.json()
        # Validate against Pydantic model
        health_response = HealthResponse(**data)
        assert health_response.status == "healthy"


class TestSearchEndpoints:
    """Tests for search endpoints (GET and POST)"""
    
    def test_search_get_basic(self):
        """Test basic GET search endpoint"""
        response = client.get("/api/search?query=الله&perpage=5")
        assert response.status_code == 200
    
    def test_search_get_response_structure(self):
        """Test that GET search returns proper structure"""
        response = client.get("/api/search?query=الله&perpage=5")
        data = response.json()
        assert "error" in data
        assert "search" in data
        assert data["error"]["code"] == 0
    
    def test_search_get_with_pagination(self):
        """Test GET search with pagination parameters"""
        response = client.get("/api/search?query=الله&page=2&perpage=10")
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
    
    def test_search_get_with_script_parameter(self):
        """Test GET search with script parameter"""
        response = client.get("/api/search?query=الله&perpage=5&script=uthmani")
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
    
    def test_search_get_invalid_script(self):
        """Test GET search with invalid script parameter"""
        response = client.get("/api/search?query=الله&perpage=5&script=invalid")
        assert response.status_code == 422  # Validation error
    
    def test_search_post_basic(self):
        """Test basic POST search endpoint"""
        response = client.post("/api/search", json={
            "query": "الله",
            "perpage": 5
        })
        assert response.status_code == 200
    
    def test_search_post_response_structure(self):
        """Test that POST search returns proper structure"""
        response = client.post("/api/search", json={
            "query": "الله",
            "perpage": 5
        })
        data = response.json()
        assert "error" in data
        assert "search" in data
        assert data["error"]["code"] == 0
    
    def test_search_post_with_all_options(self):
        """Test POST search with various options"""
        response = client.post("/api/search", json={
            "query": "الله",
            "unit": "aya",
            "page": 1,
            "perpage": 5,
            "sortedby": "relevance",
            "fuzzy": False,
            "view": "normal",
            "highlight": "bold",
            "script": "standard",
            "vocalized": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
    
    def test_search_post_with_script_uthmani(self):
        """Test POST search with uthmani script"""
        response = client.post("/api/search", json={
            "query": "الله",
            "perpage": 3,
            "script": "uthmani"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
    
    def test_search_post_invalid_script(self):
        """Test POST search with invalid script value"""
        response = client.post("/api/search", json={
            "query": "الله",
            "perpage": 5,
            "script": "invalid"
        })
        assert response.status_code == 422  # Pydantic validation error
    
    def test_search_response_model_validation(self):
        """Test that search response matches SearchResponse model"""
        response = client.get("/api/search?query=الله&perpage=2")
        data = response.json()
        # Validate against Pydantic model
        search_response = SearchResponse(**data)
        assert search_response.error.code == 0
        assert search_response.search is not None
    
    def test_search_with_buckwalter_transliteration(self):
        """Test search with Buckwalter transliteration"""
        response = client.get("/api/search?query=Allh&perpage=5")
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
    
    def test_search_missing_query(self):
        """Test search without query parameter"""
        response = client.get("/api/search?perpage=5")
        assert response.status_code == 422  # Missing required parameter


class TestSuggestEndpoint:
    """Tests for the suggest endpoint"""
    
    def test_suggest_basic(self):
        """Test basic suggest endpoint"""
        response = client.post("/api/suggest", json={
            "query": "الح",
            "unit": "aya"
        })
        assert response.status_code == 200
    
    def test_suggest_response_structure(self):
        """Test that suggest returns proper structure"""
        response = client.post("/api/suggest", json={
            "query": "الح",
            "unit": "aya"
        })
        data = response.json()
        assert "error" in data
        assert "suggest" in data
        assert data["error"]["code"] == 0
    
    def test_suggest_response_model_validation(self):
        """Test that suggest response matches SuggestResponse model"""
        response = client.post("/api/suggest", json={
            "query": "الح",
            "unit": "aya"
        })
        data = response.json()
        # Validate against Pydantic model
        suggest_response = SuggestResponse(**data)
        assert suggest_response.error.code == 0
        assert suggest_response.suggest is not None
    
    def test_suggest_with_different_units(self):
        """Test suggest with different unit types"""
        units = ["aya", "word", "translation"]
        for unit in units:
            response = client.post("/api/suggest", json={
                "query": "الح",
                "unit": unit
            })
            assert response.status_code == 200
            data = response.json()
            assert data["error"]["code"] == 0
    
    def test_suggest_missing_query(self):
        """Test suggest without query parameter"""
        response = client.post("/api/suggest", json={
            "unit": "aya"
        })
        assert response.status_code == 422  # Missing required parameter


class TestInfoEndpoints:
    """Tests for info endpoints"""
    
    def test_info_all(self):
        """Test getting all info"""
        response = client.get("/api/info")
        assert response.status_code == 200
    
    def test_info_all_response_structure(self):
        """Test that info all returns proper structure"""
        response = client.get("/api/info")
        data = response.json()
        assert "error" in data
        assert "show" in data
        assert data["error"]["code"] == 0
    
    def test_info_chapters(self):
        """Test getting chapters info"""
        response = client.get("/api/info/chapters")
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
        assert "show" in data
        assert "chapters" in data["show"]
    
    def test_info_surates(self):
        """Test getting surates info (same as chapters)"""
        response = client.get("/api/info/surates")
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
    
    def test_info_translations(self):
        """Test getting translations info"""
        response = client.get("/api/info/translations")
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
        assert "show" in data
    
    def test_info_recitations(self):
        """Test getting recitations info"""
        response = client.get("/api/info/recitations")
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
    
    def test_info_defaults(self):
        """Test getting defaults info"""
        response = client.get("/api/info/defaults")
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
    
    def test_info_domains(self):
        """Test getting domains info"""
        response = client.get("/api/info/domains")
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
    
    def test_info_fields(self):
        """Test getting fields info"""
        response = client.get("/api/info/fields")
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == 0
    
    def test_info_response_model_validation(self):
        """Test that info response matches InfoResponse model"""
        response = client.get("/api/info/chapters")
        data = response.json()
        # Validate against Pydantic model
        info_response = InfoResponse(**data)
        assert info_response.error.code == 0
        assert info_response.show is not None


class TestInteractiveDocumentation:
    """Tests for interactive documentation endpoints"""
    
    def test_swagger_ui_available(self):
        """Test that Swagger UI is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_available(self):
        """Test that ReDoc is accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self):
        """Test that OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint"""
        response = client.get("/api/invalid")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test using wrong HTTP method"""
        response = client.get("/api/suggest")  # Should be POST
        assert response.status_code == 405
    
    def test_invalid_json_body(self):
        """Test sending invalid JSON"""
        response = client.post(
            "/api/search",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestResponseModels:
    """Tests for Pydantic response models"""
    
    def test_search_response_model_fields(self):
        """Test SearchResponse model has required fields"""
        response = client.get("/api/search?query=الله&perpage=2")
        data = response.json()
        model = SearchResponse(**data)
        assert hasattr(model, 'error')
        assert hasattr(model, 'search')
        assert hasattr(model.error, 'code')
        assert hasattr(model.error, 'msg')
    
    def test_suggest_response_model_fields(self):
        """Test SuggestResponse model has required fields"""
        response = client.post("/api/suggest", json={"query": "الح", "unit": "aya"})
        data = response.json()
        model = SuggestResponse(**data)
        assert hasattr(model, 'error')
        assert hasattr(model, 'suggest')
    
    def test_info_response_model_fields(self):
        """Test InfoResponse model has required fields"""
        response = client.get("/api/info/chapters")
        data = response.json()
        model = InfoResponse(**data)
        assert hasattr(model, 'error')
        assert hasattr(model, 'show')


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
