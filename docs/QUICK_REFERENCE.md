# GuardRAG Quick Reference

## Installation
```bash
pip install guard-rag
```

## Usage
```bash
guard-rag --pdf document.pdf
```

## Basic Examples

### Simple Query
```bash
guard-rag --pdf report.pdf
```

### With Custom Model
```bash
guard-rag --pdf report.pdf --model llama2
```

### With Sensitivity
```bash
guard-rag --pdf sensitive.pdf --sensitivity Restricted
```

### Remote Ollama
```bash
guard-rag --pdf doc.pdf --ollama-host http://remote:11434
```

### Disable Guardrails
```bash
guard-rag --pdf doc.pdf --no-guardrails
```

## Python API

```python
from guardrag import build_rag_chain
from langchain_core.messages import HumanMessage, AIMessage

# Build RAG
db_id, chain = build_rag_chain(["document.pdf"])

# Query with history
messages = []
result = chain.invoke({
    "input": "Your question",
    "chat_history": messages
})

print(result["answer"])

# Add to history
messages.append(HumanMessage(content="Your question"))
messages.append(AIMessage(content=result["answer"]))
```

## CLI Options

```
--pdf PATH              Document path (required)
--model MODEL           Ollama model [default: gemma3:1b]
--ollama-host HOST      Ollama URL [default: http://localhost:11434]
--chunk-size INT        Chunk size [default: 1000]
--chunk-overlap INT     Overlap [default: 200]
--sensitivity LEVEL     Public|Internal|Confidential|Restricted
--no-guardrails         Disable safety
--help                  Show help
```

## Setup

### 1. Install Ollama
- Download: https://ollama.ai
- Run: `ollama serve`
- Pull model: `ollama pull gemma3:1b`

### 2. Install GuardRAG
```bash
pip install guard-rag
```

### 3. Test Installation
```bash
python test_installation.py
```

### 4. Run
```bash
guard-rag --pdf document.pdf
```

## Supported Models

```
ollama pull gemma3:1b          # Small & fast
ollama pull llama2             # Powerful
ollama pull mistral            # Efficient
ollama pull neural-chat        # Conversational
ollama pull orca-mini          # Compact
```

## Environment Variables

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:1b
DATA_SENSITIVITY=Internal
ENABLE_GUARDRAILS=true
```

## Sensitivity Levels

| Level | Protection |
|-------|-----------|
| Public | Jailbreak only |
| Internal | + Credentials |
| Confidential | + PII |
| Restricted | + Medical/Financial |

## Troubleshooting

**Ollama not found**
```bash
ollama serve
```

**No models**
```bash
ollama pull gemma3:1b
ollama run gemma3:1b
```

**Module not found**
```bash
pip install --upgrade guard-rag
```

**Permission error**
```bash
pip install --user guard-rag
# or use virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install guard-rag
```

## Useful Commands

```bash
# List installed Ollama models
ollama list

# Check Ollama status
curl http://localhost:11434/api/tags

# Show CLI help
guard-rag --help

# Test installation
python test_installation.py

# Interactive query
guard-rag --pdf document.pdf
```

## Performance Tips

- **Small models** (gemma3:1b) - Faster responses, less accurate
- **Large models** (llama2) - Slower, more accurate
- **GPU support** - Install `faiss-gpu` and `torch[cuda]`
- **Caching** - First run slower, subsequent faster
- **Chunk size** - Smaller chunks = more retrieval, slower

## Common Workflows

### Document Analysis
```bash
guard-rag --pdf research.pdf --sensitivity Confidential
# Follow prompts to ask questions
```

### Batch Processing
```bash
for file in *.pdf; do
  echo "Analyzing $file"
  guard-rag --pdf "$file" --model gemma3:1b
done
```

### Development
```python
import sys
sys.path.insert(0, '.')

from guardrag.rag.core import build_rag_chain
from guardrag.utils.safety import check_input_safety

# Your custom logic here
```

## Package Structure

```
guardrag/
├── api/          - Web server & interface
├── cli/          - Command-line interface
├── rag/          - Core RAG pipeline
└── utils/        - Support utilities
```

## Links

- 📦 PyPI: https://pypi.org/project/guard-rag/
- 📖 Docs: See INSTALL.md
- 🐛 Issues: GitHub Issues
- 🎮 Demo: Try `guard-rag --help`

---

**Made with ❤️ for privacy-conscious AI**
make it available to pip publicly
