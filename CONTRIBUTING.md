# Contributing to GUADRAILS-RAG-WITH-ENDEE

Thank you for your interest in contributing to **GUADRAILS-RAG-WITH-ENDEE**! We welcome contributions from the community to help make this privacy-first, enterprise-grade Retrieval-Augmented Generation (RAG) system better for everyone.

## Table of Contents
- [How Can I Contribute?](#how-can-i-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Code Style](#code-style)
- [Supported LLM Providers](#supported-llm-providers)

## How Can I Contribute?

### Reporting Bugs
If you find a bug, please create a new issue on GitHub and include:
- A clear description of the problem.
- Steps to reproduce the issue.
- Your operating system and Python version.
- Any relevant logs or error messages.

### Feature Requests
We'd love to hear your ideas! Please open an issue and describe the feature you'd like to see, why it's useful, and any implementation thoughts you have.

### Pull Requests
If you're ready to contribute code:
1. Fork the repository.
2. Create a new branch (`git checkout -b feat/your-feature-name`).
3. Make your changes.
4. Add tests if applicable (see [Testing](#testing)).
5. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
6. Push to your fork and submit a pull request.
7. Ensure all CI/CD checks pass.

### Conventional Commit Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

Example:
```
feat(llm): add support for Anthropic Claude API

Implement Claude 3 integration with streaming support.
Adds new LLM_PROVIDER option for Anthropic backend.

Closes #234
```

## Development Setup

### Prerequisites
- Python 3.9+
- Git
- Endee Vector Database (required for all setups)
- **One of**: Ollama (local) OR OpenAI/Anthropic/Google API key (cloud)

### Step-by-Step Setup

1. **Fork & Clone the repository:**
   ```bash
   # Fork on GitHub, then:
   git clone https://github.com/YOUR-USERNAME/GUADRAILS-RAG-WITH-ENDEE.git
   cd GUADRAILS-RAG-WITH-ENDEE
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8 mypy
   ```

4. **Setup Endee Vector Database (Required):**
   ```bash
   git clone https://github.com/endee-io/endee.git ../endee
   cd ../endee
   ./install.sh --release --avx2
   ./run.sh  # In separate terminal
   ```

5. **Setup LLM Provider (Choose ONE):**
   
   **Option A: Local Ollama**
   ```bash
   # Install from https://ollama.com
   ollama serve  # In separate terminal
   ollama pull mistral  # Download a model
   
   # Set in .env
   echo "LLM_PROVIDER=ollama" >> .env
   echo "OLLAMA_MODEL=mistral" >> .env
   ```
   
   **Option B: OpenAI**
   ```bash
   # Get API key from https://platform.openai.com/api-keys
   echo "LLM_PROVIDER=openai" >> .env
   echo "OPENAI_API_KEY=sk-..." >> .env
   ```
   
   **Option C: Anthropic**
   ```bash
   # Get API key from https://console.anthropic.com/
   echo "LLM_PROVIDER=anthropic" >> .env
   echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
   ```

6. **Copy environment template:**
   ```bash
   cp .env.example .env
   # Edit .env with your LLM configuration
   ```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=guardrag

# Run specific test file
pytest tests/test_workflow.py

# Run with verbose output
pytest -v
```

### Writing Tests
When adding new features, please include tests:

```python
# tests/test_my_feature.py
import pytest
from guardrag.core import MyNewFeature

def test_my_feature_basic():
    """Test basic functionality of MyNewFeature."""
    feature = MyNewFeature()
    result = feature.process("test")
    assert result is not None

@pytest.mark.asyncio
async def test_my_feature_async():
    """Test async functionality."""
    feature = MyNewFeature()
    result = await feature.process_async("test")
    assert result is not None
```

---

## Code Style

### Python Style Guidelines
- **PEP 8**: Follow [PEP 8](https://pep8.org/) standards
- **Line Length**: Max 100 characters
- **Type Hints**: Always use type hints for function parameters and returns
- **Docstrings**: Use Google-style docstrings

### Formatting
```bash
# Format code with Black
black guardrag/ tests/

# Check with Flake8
flake8 guardrag/ tests/

# Type checking with Mypy
mypy guardrag/
```

### Code Example
```python
"""Module docstring explaining purpose."""

from typing import Optional
import logging

logger = logging.getLogger(__name__)

def process_document(file_path: str, chunk_size: int = 1024) -> Optional[dict]:
    """
    Process a document and return metadata.
    
    Args:
        file_path: Path to the document file.
        chunk_size: Number of tokens per chunk.
    
    Returns:
        Dictionary with processing results, or None if failed.
    
    Raises:
        FileNotFoundError: If document doesn't exist.
        ValueError: If chunk_size is invalid.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    
    logger.info(f"Processing {file_path}")
    # Implementation here
    return {"status": "success"}
```

---

## Supported LLM Providers

When contributing LLM-related features, ensure compatibility with:

| Provider | Module | Status | Notes |
|----------|--------|--------|-------|
| **Ollama** | `langchain-ollama` | ✅ Stable | Local, free, privacy-first |
| **OpenAI** | `langchain-openai` | ✅ Stable | gpt-4, gpt-3.5-turbo |
| **Anthropic** | `langchain-anthropic` | ✅ Stable | Claude 3, Claude 2 |
| **Google** | `langchain-google-genai` | ✅ Stable | Gemini Pro, Gemini Vision |
| **HuggingFace** | `langchain-huggingface` | ✅ Stable | Local inference via Ollama bridge |

See [LLM Configuration](./README.md#configuration--customization) in README for setup details.

---

## Areas for Contribution

We're always looking for contributions in:

- 🐛 **Bug Fixes**: Issues labeled `bug`
- ✨ **Features**: Check issues labeled `enhancement`
- 📚 **Documentation**: Improve guides and examples
- 🔍 **Performance**: Optimization proposals
- 🌍 **Localization**: Language/culture support
- 🧪 **Tests**: Expand test coverage
- 🔐 **Security**: Security improvements

---

## Questions?

- **GitHub Issues**: [Ask a question](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE/issues/new/choose)
- **GitHub Discussions**: [Community chat](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE/discussions)

---

## License

By contributing, you agree that your contributions will be licensed under the **MIT License**.

---

## Attribution

Thanks for contributing to making RAG more accessible, private, and powerful! 🙌
