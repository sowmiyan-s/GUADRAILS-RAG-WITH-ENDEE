# GuardRAG Installation Guide

## What is GuardRAG?

GuardRAG is a privacy-first, fully offline AI document assistant that has been restructured as a pip-installable Python package. You can now install and use it via the command line with a single command.

## Installation

### Using pip (Recommended)

```bash
pip install guard-rag
```

To install from the local source directory:

```bash
git clone https://github.com/sowmiyan-s/GUARD-RAG.git
cd GUARD-RAG
pip install .
```

Or with dependencies:

```bash
pip install -e .[all]
```

### Requirements

- Python 3.9+
- Ollama (for local LLM execution)

**Core dependencies:**
- langchain
- langchain-core
- langchain-community
- langchain-ollama
- langchain-huggingface
- sentence-transformers
- pypdf
- docx2txt
- python-dotenv
- nest_asyncio
- faiss-cpu

## Usage

### Command Line Interface

Once installed, you can use GuardRAG from the command line with the `guardrag` command:

```bash
guard-rag --pdf /path/to/document.pdf
```

#### Available Options

```
guard-rag --help
```

- `--pdf PATH` (required): Path to the document to query (PDF, TXT, or DOCX)
- `--model MODEL` (default: gemma3:1b): Ollama model name (e.g., llama2, mistral, neural-chat)
- `--ollama-host URL` (default: http://localhost:11434): Ollama server URL
- `--chunk-size INT` (default: 1000): Document chunk size for processing
- `--chunk-overlap INT` (default: 200): Overlap between chunks
- `--no-guardrails`: Disable safety features
- `--sensitivity LEVEL` (default: Internal): Data sensitivity level
  - `Public`: Basic jailbreak protection only
  - `Internal`: Blocks credentials and API keys
  - `Confidential`: Adds PII protection (SSN, email, etc.)
  - `Restricted`: Maximum protection for sensitive data

#### Example Commands

```bash
# Basic usage
guard-rag --pdf document.pdf

# With custom model
guard-rag --pdf document.pdf --model llama2

# With remote Ollama instance
guard-rag --pdf document.pdf --ollama-host http://remote-server:11434

# With maximum security
guard-rag --pdf document.pdf --sensitivity Restricted

# Disable guardrails (not recommended)
guard-rag --pdf document.pdf --no-guardrails
```

### Python API

You can also use GuardRAG programmatically:

```python
from guardrag import build_rag_chain
from guardrag.utils.ollama import is_ollama_running
from langchain_core.messages import HumanMessage, AIMessage

# Check if Ollama is running
if not is_ollama_running():
    print("Please start Ollama: ollama serve")
    exit(1)

# Build RAG chain
db_id, rag_chain = build_rag_chain(
    ["path/to/document.pdf"],
    model="gemma3:1b",
    chunk_size=1000,
    chunk_overlap=200,
    ollama_host="http://localhost:11434"
)

# Create a query
messages = []
result = rag_chain.invoke({
    "input": "What is the main topic?",
    "chat_history": messages
})

print(result["answer"])

# Add to message history for multi-turn conversation
messages.append(HumanMessage(content="What is the main topic?"))
messages.append(AIMessage(content=result["answer"]))
```

## Prerequisites

### Ollama

GuardRAG requires Ollama for local LLM execution. Download and install from:
https://ollama.ai

After installation, start the Ollama server:

```bash
ollama serve
```

To download and run a specific model (e.g., Gemma):

```bash
ollama pull gemma3:1b
ollama run gemma3:1b
```

Supported models:
- `gemma3:1b` - Small and fast
- `llama2` - Powerful general purpose
- `mistral` - Balanced and efficient
- `neural-chat` - Fine-tuned for conversation

## Package Structure

```
guardrag/
├── __init__.py           # Package entry point
├── api/                  # FastAPI local server
│   ├── frontend/         # Static web interface files
│   └── main.py           # Web application logic
├── cli/
│   └── main.py           # Command-line interface logic
├── rag/
│   └── core.py           # RAG pipeline implementation
└── utils/
    ├── ollama.py         # Ollama utilities
    └── safety.py         # Safety guardrails
```

## Configuration

### Environment Variables

Create a `.env` file in your project directory:

```env
# Ollama configuration
OLLAMA_HOST=http://localhost:11434

# Model settings
OLLAMA_MODEL=gemma3:1b

# Data sensitivity (Public, Internal, Confidential, Restricted)
DATA_SENSITIVITY=Internal

# Enable/disable guardrails
ENABLE_GUARDRAILS=true
```

## Features

### ✓ 100% Offline
- No cloud API calls
- All processing local to your machine
- No data leaves your device

### ✓ Multi-format Support
- PDF documents
- Text files (TXT)
- Word documents (DOCX)

### ✓ Multi-turn Conversations
- Full chat history support
- Context-aware responses
- Conversation memory

### ✓ Safety Guardrails
- Jailbreak/prompt injection detection
- Credential and API key protection
- PII (Personally Identifiable Information) masking
- Regulated data protection (HIPAA, GDPR)

### ✓ Persistent Caching
- FAISS vector store caching
- Re-uploading same documents uses cached embeddings
- Fast subsequent queries

## Troubleshooting

### "Ollama is not running"
Start Ollama:
```bash
ollama serve
```

### "ModuleNotFoundError: No module named 'langchain'"
Install dependencies:
```bash
pip install langchain langchain-core langchain-community langchain-ollama langchain-huggingface
```

### "No module named 'torch'"
Install PyTorch:
```bash
pip install torch
```

### "FAISS not found"
Install FAISS:
```bash
pip install faiss-cpu
# or for GPU support:
pip install faiss-gpu
```

## Development

To set up a development environment:

```bash
# Clone repository
git clone https://github.com/sowmiyan-s/GUARD-RAG.git
cd GUARD-RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please visit:
https://github.com/sowmiyan-s/GUARD-RAG

## Citation

If you use GuardRAG in your research or project, please cite:

```bibtex
@software{guardrag2024,
  title = {GuardRAG: Privacy-First Offline AI Document Assistant},
  author = {Sowmiyan S},
  year = {2024},
  url = {https://github.com/sowmiyan-s/GUARD-RAG}
}
```
