# Alfanous Web API Tests

The comprehensive test suite for the Alfanous FastAPI web application is located in `src/tests/test_web_api.py`.

## Test Coverage

The test suite includes 43 tests organized into the following categories:

### 1. Root Endpoint Tests (3 tests)
- Tests that root endpoint returns 200 status code
- Verifies API information is returned correctly
- Checks that all endpoints are listed

### 2. Health Endpoint Tests (3 tests)
- Tests health check endpoint availability
- Verifies healthy status response
- Validates response model structure

### 3. Search Endpoint Tests (13 tests)
- Basic GET and POST search functionality
- Response structure validation
- Pagination parameters
- Script parameter validation (standard/uthmani)
- Invalid parameter handling
- Buckwalter transliteration support
- Pydantic model validation
- All search options (unit, sortedby, fuzzy, view, highlight, etc.)

### 4. Suggest Endpoint Tests (5 tests)
- Basic suggest functionality
- Response structure validation
- Different unit types (aya, word, translation)
- Missing parameter handling
- Pydantic model validation

### 5. Info Endpoint Tests (10 tests)
- All info categories (chapters, translations, recitations, etc.)
- Response structure validation
- Category-specific info retrieval
- Pydantic model validation

### 6. Interactive Documentation Tests (3 tests)
- Swagger UI availability
- ReDoc availability
- OpenAPI schema accessibility

### 7. Error Handling Tests (3 tests)
- Invalid endpoint handling (404)
- Wrong HTTP method (405)
- Invalid JSON body (422)

### 8. Response Model Tests (3 tests)
- SearchResponse model field validation
- SuggestResponse model field validation
- InfoResponse model field validation

## Running the Tests

### Run all web API tests:
```bash
pytest src/tests/test_web_api.py -v
```

### Run specific test class:
```bash
pytest src/tests/test_web_api.py::TestSearchEndpoints -v
```

### Run specific test:
```bash
pytest src/tests/test_web_api.py::TestSearchEndpoints::test_search_get_basic -v
```

### Run with coverage:
```bash
pytest src/tests/test_web_api.py --cov=alfanous_webapi --cov-report=html
```

## Prerequisites

The tests require:
- `pytest` - Testing framework
- `fastapi` - Web framework
- `httpx` - HTTP client for TestClient
- `pydantic` - Data validation
- Built search indexes (run `make build` first)

## Test Philosophy

These tests follow best practices:
- **Comprehensive coverage**: All endpoints and major code paths tested
- **Clear naming**: Test names describe what they test
- **Organized structure**: Tests grouped by endpoint/functionality
- **Model validation**: Pydantic models validated in tests
- **Error cases**: Both success and failure scenarios tested
- **Independent tests**: Each test is independent and can run in any order

## Continuous Integration

These tests are designed to run in CI/CD pipelines and provide quick feedback on API functionality.
