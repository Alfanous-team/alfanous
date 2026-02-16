# Alfanous FastAPI Web Application

A minimal FastAPI application that exposes the Alfanous Quranic search API through RESTful endpoints.

## Features

- **Search in Quranic verses** with advanced filters and faceted search
- **Get suggestions and autocompletion** for search queries
- **Access metadata** about the Quran (chapters, translations, recitations)
- **Support for Arabic script** and Buckwalter transliteration
- **Interactive API documentation** with Swagger UI and ReDoc
- **Health check endpoint** for monitoring

## Installation

### Install with web dependencies

```bash
pip install alfanous3[web]
```

Or install manually:

```bash
pip install alfanous3
pip install fastapi uvicorn[standard] pydantic
```

## Usage

### Starting the Server

#### Using the command-line tool:

```bash
alfanous-server
```

#### Using Python module:

```bash
python -m alfanous.web_api
```

#### Using uvicorn directly:

```bash
uvicorn alfanous.web_api:app --reload
```

The server will start at `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Root Endpoint
- **GET /** - API information and available endpoints

### Health Check
- **GET /health** - Health check endpoint

### Search Endpoints

#### Search in Quranic Verses (GET)
```bash
GET /api/search?query=الله&page=1&perpage=10
```

#### Search in Quranic Verses (POST)
```bash
POST /api/search
Content-Type: application/json

{
  "query": "الله",
  "page": 1,
  "perpage": 10,
  "view": "normal",
  "highlight": "bold"
}
```

**Parameters:**
- `query` (required): Search query in Arabic or Buckwalter transliteration
- `unit`: Search unit - "aya" (verse), "word", or "translation" (default: "aya")
- `page`: Page number for pagination (default: 1)
- `perpage`: Results per page (1-100, default: 10)
- `sortedby`: Sort order - "score", "relevance", "mushaf", "tanzil", "subject" (default: "relevance")
- `fuzzy`: Enable fuzzy search (default: false)
- `view`: View mode - "minimal", "normal", "full", "statistic", "linguistic", "custom" (default: "normal")
- `highlight`: Highlight mode - "css", "html", "bold", "bbcode" (default: "bold")
- `script`: Script type - "standard" or "uthmani"
- `vocalized`: Include vocalization (tashkeel)
- `translation`: Translation ID
- `recitation`: Recitation ID
- `prev_aya`: Include previous verse
- `next_aya`: Include next verse
- `sura_info`: Include surah information
- `word_info`: Include word information
- `aya_theme_info`: Include verse theme information
- `aya_stat_info`: Include verse statistics
- `facets`: Facets to include in results
- `filter`: Filters to apply (JSON object with field: value pairs)

### Suggest Endpoint

#### Get Search Suggestions
```bash
POST /api/suggest
Content-Type: application/json

{
  "query": "الح",
  "unit": "aya"
}
```

### Info Endpoints

#### Get All Metadata
```bash
GET /api/info
```

#### Get Specific Metadata Category
```bash
GET /api/info/{category}
```

Available categories:
- `chapters` or `surates`: Information about Quranic chapters
- `translations`: Available translations
- `recitations`: Available recitations
- `defaults`: Default search parameters
- `domains`: Valid values for parameters
- `fields`: Available search fields
- `flags`: All available flags/parameters
- `help_messages`: Help text for parameters
- `hints`: Search hints and tips
- `information`: General API information
- `errors`: Error codes and messages

## Example Usage

### Using curl

```bash
# Search for verses containing "الله"
curl "http://localhost:8000/api/search?query=الله&perpage=5"

# Get suggestions
curl -X POST "http://localhost:8000/api/suggest" \
  -H "Content-Type: application/json" \
  -d '{"query": "الح", "unit": "aya"}'

# Get chapter information
curl "http://localhost:8000/api/info/chapters"

# Health check
curl "http://localhost:8000/health"
```

### Using Python requests

```python
import requests

# Search for verses
response = requests.get(
    "http://localhost:8000/api/search",
    params={
        "query": "الله",
        "page": 1,
        "perpage": 10,
        "view": "normal"
    }
)
print(response.json())

# Get suggestions
response = requests.post(
    "http://localhost:8000/api/suggest",
    json={
        "query": "الح",
        "unit": "aya"
    }
)
print(response.json())

# Get metadata
response = requests.get("http://localhost:8000/api/info/translations")
print(response.json())
```

### Using JavaScript fetch

```javascript
// Search for verses
fetch('http://localhost:8000/api/search?query=الله&perpage=5')
  .then(response => response.json())
  .then(data => console.log(data));

// Get suggestions
fetch('http://localhost:8000/api/suggest', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'الح',
    unit: 'aya'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Response Format

All endpoints return JSON responses with the following structure:

### Search Response
```json
{
  "error": 0,
  "interval": {
    "start": 1,
    "end": 10,
    "total": 6236
  },
  "search": {
    "ayas": [
      {
        "identifier": {...},
        "aya": {...},
        "translation": {...},
        "recitation": {...}
      }
    ],
    "words": [...],
    "runtime": 0.123
  },
  "facets": {...}
}
```

### Info Response
```json
{
  "error": 0,
  "show": {
    "chapters": [...],
    "translations": [...],
    "recitations": [...],
    ...
  }
}
```

## Development

### Running in Development Mode

```bash
uvicorn alfanous.web_api:app --reload --host 0.0.0.0 --port 8000
```

### Custom Configuration

```python
from alfanous.web_api import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
```

## Notes

- The API respects the original Alfanous library's functionality and parameters
- All text input supports both Arabic script and Buckwalter transliteration
- Results are paginated for better performance
- The API is stateless and does not require authentication
- CORS is not enabled by default - add middleware if needed for browser access

## Support

For issues and questions:
- GitHub: https://github.com/Alfanous-team/alfanous
- Mailing List: alfanous@googlegroups.com

## License

This API wrapper follows the same license as Alfanous: AGPL v3 or later
