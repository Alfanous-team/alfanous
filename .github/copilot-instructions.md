# Alfanous - GitHub Copilot Instructions

## Project Overview
Alfanous is a search engine API for the Holy Qur'an that provides simple and advanced search capabilities. The project is written in Python and uses Whoosh for indexing and search functionality.

## Technology Stack
- **Language**: Python 3.8+
- **Core Dependencies**: pyparsing, whoosh
- **Testing Framework**: pytest
- **License**: AGPL v3 or later

## Project Structure
```
alfanous/
├── src/
│   ├── alfanous/          # Main API package
│   │   ├── api.py         # Main API interface
│   │   ├── engines.py     # Search engines
│   │   ├── outputs.py     # Output formatting
│   │   ├── indexing.py    # Index management
│   │   ├── searching.py   # Search functionality
│   │   ├── Support/       # Support libraries
│   │   │   └── pyarabic/  # Arabic text processing
│   │   ├── configs/       # Configuration files
│   │   ├── resources/     # Static resources
│   │   └── indexes/       # Search indexes
│   ├── alfanous_import/   # Data import tools
│   └── tests/             # Test suite
├── store/                 # Quranic data storage
└── Makefile              # Build and deployment commands
```

## Development Workflow

### Setting Up the Development Environment
1. Install dependencies:
   ```bash
   pip install pyparsing pytest whoosh
   ```

2. Generate required configuration (use VERSION from Makefile):
   ```bash
   make install
   # Or manually:
   # perl -p -w -e 's|alfanous.release|$(VERSION)|g;s|alfanous.version|$(VERSION)|g;' src/alfanous/resources/information.json.in > src/alfanous/resources/information.json
   ```

3. Build indexes:
   ```bash
   make build
   ```

### Running Tests
```bash
# Run all tests
pytest -vv --rootdir=src/

# Run specific test file
pytest src/tests/test_searching.py -v
```

### Building the Project
```bash
# Build all indexes and resources
make build

# Clean temporary files
make clean

# Install locally
make install
```

## Code Style and Conventions

### Python Code Style
- All source files use UTF-8 encoding by default (Python 3 standard)
- Follow standard Python naming conventions (PEP 8)
- Add docstrings to modules, classes, and functions
- Use type hints where appropriate for better code clarity

### File Naming
- Python modules use lowercase with underscores: `text_processing.py`
- Test files prefixed with `test_`: `test_searching.py`

### Import Organization
- Standard library imports first
- Third-party imports (pyparsing, whoosh) second
- Local application imports last

## Testing Guidelines

### Writing Tests
- Place tests in `src/tests/` directory
- Prefix test files with `test_`
- Use pytest framework
- Test files should match the module they test (e.g., `test_engines.py` for `engines.py`)

### Test Structure
```python
from alfanous import paths
from alfanous.module import Component

def test_component_functionality():
    # Setup
    component = Component()
    
    # Execute and Assert
    assert component.method() == expected_result
```

## Quranic Data Handling

### Important Considerations
- This project handles religious texts (Qur'an) - treat data with respect
- Text encoding is critical - always use UTF-8
- Arabic text support is essential
- Buckwalter transliteration is supported for Latin character input

### Data Flow
1. Raw Quranic data stored in `store/` directory
2. Data processed and indexed using `alfanous_import`
3. Indexes stored in `src/alfanous/indexes/`
4. API provides search interface to indexed data

## API Design

### Main Entry Points
- `alfanous.api.search()` - Search in Quran verses and translations
- `alfanous.api.do()` - Unified interface for search, suggestion, and info retrieval
- `alfanous.api.get_info()` - Get metadata information

### API Parameters
- `action`: Operation to perform (search, suggest, show)
- `query`: Search query (supports Arabic and Buckwalter transliteration)
- `unit`: Search unit (aya, word, translation)
- `page`: Pagination support
- `sortedby`: Result ordering

## Common Development Tasks

### Adding a New Search Feature
1. Implement core logic in `src/alfanous/engines.py` or `src/alfanous/searching.py`
2. Update output formatting in `src/alfanous/outputs.py`
3. Add API interface in `src/alfanous/api.py`
4. Write tests in `src/tests/test_*.py`
5. Update documentation if needed

### Modifying Index Structure
1. Update indexing logic in `src/alfanous/indexing.py`
2. Update importer in `src/alfanous_import/`
3. Rebuild indexes using `make build`
4. Update tests to reflect changes

### Adding New Dependencies
1. Add to `install_requires` in `src/alfanous/setup.py`
2. Update GitHub Actions workflow in `.github/workflows/tests.yaml`
3. Document in this file

## CI/CD

### GitHub Actions Workflows
- **tests.yaml**: Runs test suite on Python 3.8, 3.9, 3.10, 3.11, 3.12
- **pypi-release.yaml**: Handles PyPI package releases

### Before Committing
1. Run tests: `pytest -vv --rootdir=src/`
2. Clean temporary files: `make clean`
3. Ensure no build artifacts are committed

## Special Notes

### Makefile Usage
- Use Makefile for building, not manual commands
- Key targets:
  - `make build` - Build indexes
  - `make clean` - Clean temporary files
  - `make install` - Install package locally
  - `make dist` - Create distribution packages

### Version Management
- Version defined in `Makefile` as `VERSION` variable
- Also managed through `information.json.in` template
- Update both locations when incrementing version

### Arabic Text Processing
- The `Support/pyarabic` subpackage handles Arabic text
- Always test with both Arabic script and transliteration
- Be aware of right-to-left text rendering considerations

## Resources and Documentation
- GitHub Repository: https://github.com/Alfanous-team/alfanous
- Issue Tracker: https://github.com/Alfanous-team/alfanous/issues
- Mailing List: alfanous@googlegroups.com
- Web API: http://alfanous.org/api/

## When Contributing Code
1. Understand the Quranic context and be respectful
2. Test with both Arabic and transliterated inputs
3. Ensure backward compatibility with the API
4. Update tests for any new functionality
5. Follow existing code patterns and style
6. Run the full test suite before submitting changes
