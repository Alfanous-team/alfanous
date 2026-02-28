# Contributing to Alfanous

Thank you for your interest in contributing to Alfanous! This document provides guidelines and instructions for setting up your development environment and contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Building from Source](#building-from-source)
- [Running Tests](#running-tests)
- [Making Changes](#making-changes)
- [Submitting Contributions](#submitting-contributions)
- [Code Style Guidelines](#code-style-guidelines)
- [Project Structure](#project-structure)
- [Important Notes](#important-notes)

## Code of Conduct

This project handles sacred religious text (the Holy Qur'an). Please treat the data, code, and community members with respect. We expect all contributors to:

- Be respectful and considerate in all interactions
- Focus on constructive feedback
- Welcome newcomers and help them get started
- Respect different viewpoints and experiences

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/alfanous.git
   cd alfanous
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/Alfanous-team/alfanous.git
   ```

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Make (optional, but recommended)

### Installing Dependencies

Install the required Python packages:

```bash
pip install pyparsing whoosh pytest
```

For development with the web API:

```bash
pip install fastapi uvicorn pydantic
```

### Building Indexes

Alfanous uses pre-built indexes for searching. These must be built before you can run the API:

```bash
# From the repository root
make build
```

This command will:
1. Process Quranic data from the `store/` directory
2. Build search indexes in `src/alfanous/indexes/`
3. Generate required configuration files

**Note**: The build process may take several minutes to complete.

### Installing from Source

After building the indexes, you can install Alfanous in development mode:

```bash
cd src/alfanous
pip install -e .
```

This installs the package in "editable" mode, meaning changes to the source code will immediately affect the installed package without reinstalling.

## Building from Source

For a complete build from source:

1. **Install build dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev python3-pip
   
   # Install Python dependencies
   pip install pyparsing whoosh
   ```

2. **Build the project**:
   ```bash
   make build
   ```

3. **Install**:
   ```bash
   cd src/alfanous
   python setup.py install
   ```

4. **Verify installation**:
   ```bash
   alfanous-console -h
   python -c "from alfanous import api; print(api.search('الله'))"
   ```

## Running Tests

### Running All Tests

```bash
# From the repository root
pytest -vv --rootdir=src/
```

### Running Specific Tests

```bash
# Run tests for a specific module
pytest src/tests/test_searching.py -v

# Run a specific test function
pytest src/tests/test_searching.py::test_simple_search -v
```

### Test Coverage

To check test coverage:

```bash
pip install pytest-cov
pytest --cov=alfanous --cov-report=html --rootdir=src/
```

## Making Changes

### Creating a Branch

Create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Development Workflow

1. **Make your changes** in your branch
2. **Test your changes** thoroughly:
   ```bash
   pytest -vv --rootdir=src/
   ```
3. **Update documentation** if needed
4. **Commit your changes** with clear commit messages:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

### Commit Message Guidelines

- Use clear, descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update", "Remove")
- Keep the first line under 72 characters
- Add detailed description in the body if needed

Example:
```
Add faceted search support for topics

- Implement topic faceting in search engine
- Add tests for topic facets
- Update documentation with examples
```

## Submitting Contributions

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub:
   - Go to the original Alfanous repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template with:
     - Description of changes
     - Related issue numbers (if applicable)
     - Testing performed
     - Any breaking changes

3. **Address review feedback**:
   - Make requested changes
   - Push updates to the same branch
   - Reply to review comments

## Code Style Guidelines

### Python Code

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to modules, classes, and functions
- Use type hints where appropriate

Example:

```python
def search_verses(query: str, page: int = 1, perpage: int = 10) -> dict:
    """
    Search for verses matching the given query.
    
    Args:
        query: Search query string in Arabic or transliteration
        page: Page number for pagination (default: 1)
        perpage: Results per page (default: 10)
    
    Returns:
        Dictionary containing search results and metadata
    """
    # Implementation here
    pass
```

### File Encoding

- All Python source files use UTF-8 encoding (Python 3 default)
- Ensure proper handling of Arabic text

### Testing Code

- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage
- Use descriptive test names

Example:

```python
def test_search_with_arabic_query():
    """Test that Arabic queries return expected results."""
    result = api.search("الله")
    assert result["error"]["code"] == 0
    assert len(result["search"]["ayas"]) > 0
```

## Project Structure

```
alfanous/
├── src/
│   ├── alfanous/          # Main API package
│   │   ├── api.py         # Public API interface
│   │   ├── engines.py     # Search engines
│   │   ├── searching.py   # Search functionality
│   │   ├── indexing.py    # Index management
│   │   ├── outputs.py     # Output formatting
│   │   ├── Support/       # Support libraries
│   │   ├── configs/       # Configuration files
│   │   ├── resources/     # Static resources
│   │   └── indexes/       # Search indexes (generated)
│   ├── alfanous_import/   # Data import tools
│   ├── alfanous_webapi/   # FastAPI web service
│   └── tests/             # Test suite
├── store/                 # Quranic data storage
├── examples/              # Example scripts
├── Makefile              # Build and installation commands
├── README.rst            # Project documentation
└── CONTRIBUTING.md       # This file
```

## Important Notes

### Working with Quranic Text

- **Respect the sacred text**: Be careful when modifying code that handles Quranic verses
- **Preserve accuracy**: Test thoroughly to ensure no corruption of text or metadata
- **Encoding**: Always use UTF-8 encoding for Arabic text
- **Vocalization**: Be careful with diacritical marks (tashkeel)

### Performance Considerations

- Alfanous handles large indexes - optimize for both speed and accuracy
- Profile your code if making performance changes
- Consider memory usage when working with large datasets

### Index Building

- Don't commit generated indexes to Git (they're in `.gitignore`)
- Always rebuild indexes after modifying data import code
- Test with rebuilt indexes before submitting PRs

### Documentation

- Update relevant documentation when adding features
- Add examples for new functionality
- Keep README.rst concise - detailed docs can go in separate files
- Use docstrings for in-code documentation

## Getting Help

If you need help or have questions:

- **GitHub Issues**: https://github.com/Alfanous-team/alfanous/issues
- **Mailing List**: alfanous@googlegroups.com
- **Discussions**: Use GitHub Discussions for questions and ideas

## Recognition

All contributors are recognized in our `AUTHORS.md` file. Thank you for contributing to Alfanous!

## License

By contributing to Alfanous, you agree that your contributions will be licensed under the GNU Affero General Public License v3 or later (AGPLv3+), the same license as the project.
