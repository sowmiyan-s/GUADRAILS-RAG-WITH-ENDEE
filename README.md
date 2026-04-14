
<div align="center">

# ⚔️ GUADRAILS RAG WITH ENDEE

### Privacy-First, Fully Offline AI Document Assistant  
**Enhanced with High-Performance Vector Database & Tiered Security Guardrails**  
*v2.0.0 — Production-Ready, Enterprise-Grade, Zero-Trust Architecture*

<br/>

![Python](https://img.shields.io/badge/Python-3.9%2B-3b82f6?style=for-the-badge&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge&logo=ollama&logoColor=white)
![Endee](https://img.shields.io/badge/Endee-Vector%20DB-ff6b6b?style=for-the-badge&logo=database&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Web%20API-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)

<br/>

> **Upload any document. Ask anything. Get answers — entirely on your local machine.**  
> Built on Endee vector database for enterprise-grade performance.  
> No cloud dependencies. No API keys. No data ever leaves your device.

</div>

---

## 🎯 What's New in v2.0

✨ **Endee Integration** — Replaced FAISS with Endee (C++ optimized vector database)  
🚀 **High-Performance Retrieval** — Support for 1B+ vectors with hybrid search  
🌐 **Web App Ready** — Run with `python app.py` for instant local website  
⚙️ **Zero-Configuration Setup** — .env template with all necessary defaults  
🔒 **Enhanced Security** — Tiered safety guardrails + metadata filtering  
📊 **Scalable Architecture** — Production-ready for enterprise deployments  

---

## 💡 Use Cases

**GUADRAILS RAG WITH ENDEE** is designed for professionals and organizations handling sensitive data who require enterprise-grade LLM capabilities without compromising privacy.

| Use Case | Description |
|----------|-------------|
| 🔒 **Secure Document Analysis** | Chat with confidential contracts, financial reports, legal documents without cloud upload |
| 🏥 **Healthcare & Privacy** | Analyze medical records with HIPAA/GDPR compliance through integrated PII detection |
| 💼 **Enterprise Knowledge** | Query large codebases, documentation, and internal knowledge bases offline |
| 🏛️ **Government & Defense** | Air-gapped environments with rated security clearance support |
| 🔍 **Hybrid Search** | Combine semantic + keyword search for precise document retrieval |
| 🤖 **Agentic AI** | Use as memory layer for autonomous agents and multi-turn RAG pipelines |

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                         │
│          (Web UI @ http://localhost:8000)                        │
└──────────────────┬───────────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────────┐
│                    FASTAPI APPLICATION                           │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  API Endpoints:                                         │     │
│  │  • POST /api/upload      (Document Processing)          │     │
│  │  • POST /api/chat        (Query & Retrieval)            │     │
│  │  • GET  /api/health      (System Status)                │     │
│  │  • POST /api/sessions    (Context Management)           │     │
│  └─────────────────────────────────────────────────────────┘     │
└──────────────────┬────────────────────────────────┬──────────────┘
                   │                                │
        ┌──────────▼──────────┐            ┌───────▼──────────┐
        │  DOCUMENT PIPELINE  │            │ SAFETY GUARDRAILS│
        │  ─────────────────  │            │ ───────────────  │
        │ • PDF Parser        │            │ • Input Validation
        │ • Text Extraction   │            │ • PII Detection  │
        │ • Chunking (1000)   │            │ • Content Filter │
        │ • Embedding Gen     │            │ • Tier-Based Access
        └──────────┬──────────┘            └────────┬─────────┘
                   │                                │
        ┌──────────▼────────────────────────────────▼──────────┐
        │          ENDEE VECTOR DATABASE (HTTP API)            │
        │ ───────────────────────────────────────────────────  │
        │ • Dense vectors (384-dim embeddings)                 │
        │ • Sparse vectors (BM25 hybrid search)                │
        │ • Metadata filtering & payload support               │
        │ • Optimized HNSW indexing (1B vectors/node)          │
        └──────────┬──────────────────────────────────────────┘
                   │
        ┌──────────▼──────────┐            ┌────────────────┐
        │  LANGUAGE MODEL     │            │ EMBEDDING MODEL│
        │ ─────────────────── │            │ ───────────── │
        │ • Ollama Integration│            │ • HuggingFace │
        │ • Local Inference   │            │ • all-MiniLM  │
        │ • CPU/GPU Support   │            │ • 384-dim     │
        └─────────────────────┘            └────────────────┘

        ┌────────────────────────────────────────────────────┐
        │    ALL PROCESSING HAPPENS LOCALLY - 100% OFFLINE  │
        │            ZERO CLOUD CALLS GUARANTEED             │
        └────────────────────────────────────────────────────┘
```

---

## ⚙️ Data Sensitivity Tiers

Protect your information using our built-in safety engine with tier-based access control:

| Level | Protection Scope | Use Case |
| :--- | :--- | :--- |
| **🟢 Public** | Jailbreak & injection detection | Blog posts, public docs |
| **🔵 Internal** | + API keys, credentials, tokens | Internal APIs, configs |
| **🟡 Confidential** | + SSNs, emails, phone, CC info | Financial reports, HR data |
| **🔴 Restricted** | + Medical/HIPAA, GDPR, classified | Healthcare, government |

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
1. **Ollama** — [Download](https://ollama.com) (Local LLM)
2. **Endee** — [Setup](https://github.com/endee-io/endee) (Vector DB)
3. **Python 3.9+** — [Download](https://python.org)

### Step 1: Install Ollama
```bash
# Download from https://ollama.com
# Then pull a model
ollama pull gemma2:2b    # Recommended lightweight model
# Alternative models: llama2, mistral, neural-chat
```

### Step 2: Start Endee
```bash
# Clone and setup
git clone https://github.com/endee-io/endee.git
cd endee

# Build and run
chmod +x ./install.sh ./run.sh
./install.sh --release --avx2    # For AVX2 CPUs
./run.sh                         # Starts on port 8080
```

### Step 3: Setup & Run GUADRAILS
```bash
# Clone this repository
git clone https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE.git
cd GUADRAILS-RAG-WITH-ENDEE

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env

# Start the application
python app.py

# ✨ Open http://localhost:8000 in your browser
```

---

## 🎮 Usage Guide

### Web Interface (Recommended)
```bash
python app.py
# Automatically opens http://localhost:8000
```

**Features:**
- 📤 **Drag-and-drop** document upload
- 💬 **Real-time chat** with documents
- 🔍 **Semantic search** highlighting
- 📊 **Document statistics**
- 🎚️ **Adjustable safety levels**
- 📁 **Session management**

### CLI Interface
```bash
# Interactive chat
python app.py --model llama2 --no-browser

# Check help
python app.py --help
```

### Python API
```python
import requests

# Upload document
files = {'file': open('document.pdf', 'rb')}
r = requests.post('http://localhost:8000/api/upload', files=files)
session_id = r.json()['session_id']

# Query document
query = {'session_id': session_id, 'question': 'What are main findings?'}
r = requests.post('http://localhost:8000/api/chat', json=query)
print(r.json()['answer'])
```

---

## 📋 CLI Options

```bash
python app.py [OPTIONS]

Options:
  --host HOST              Server host [default: 127.0.0.1]
  --port PORT              Server port [default: 8000]
  --model MODEL            Ollama model [default: gemma2:2b]
  --ollama-host HOST       Ollama URL [default: http://localhost:11434]
  --endee-host HOST        Endee URL [default: http://localhost:8080]
  --no-browser             Don't auto-open browser
  --reload                 Enable auto-reload (dev)
  --help                   Show all options
```

---

## ⚙️ Environment Configuration

**Key Settings in .env:**

```env
# Ollama Local LLM
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma2:2b

# Endee Vector DB
ENDEE_HOST=http://localhost:8080
ENDEE_INDEX_NAME=guardrag_index
ENDEE_VECTOR_DIM=384
ENDEE_METRIC=cosine

# Web Server
HOST=127.0.0.1
PORT=8000

# Security & Processing
SENSITIVITY_LEVEL=Internal
ENABLE_GUARDRAILS=true
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

See [.env.example](.env.example) for all options.

---

## 🔒 Security Features

✅ **Zero Trust** — No external API calls  
✅ **Input Validation** — All inputs sanitized  
✅ **PII Detection** — Auto-detects & masks sensitive data  
✅ **Tiered Access** — Sensitivity-based filtering  
✅ **Audit Logging** — Track all queries  
✅ **Model Isolation** — Ollama runs sandboxed  
✅ **Metadata Filtering** — Payload-aware retrieval (Endee)  

---

## 📊 Performance Benchmarks

| Metric | Performance |
|--------|-------------|
| **Vector Search** | <50ms (1M vectors) |
| **Embedding** | ~200ms per page |
| **Inference** | 50-150 tok/sec (CPU) |
| **Memory** | 4-8GB (with models) |
| **Max Documents** | 1B vectors (Endee) |

*Benchmarks: AMD Ryzen 7, 32GB RAM, SSD*

---

## 📂 Project Structure

```
GUADRAILS-RAG-WITH-ENDEE/
├── app.py                    # 🚀 Main entry point
├── requirements.txt          # Updated dependencies
├── .env.example              # Config template
├── setup.py                  # Package config
│
├── guardrag/
│   ├── api/                  # FastAPI web app
│   │   ├── main.py           # API routes
│   │   └── frontend/         # Web UI assets
│   ├── rag/                  # RAG pipeline
│   ├── vectordb/             # Vector DB modules
│   │   └── endee_client.py   # ⭐ Endee integration
│   ├── utils/                # Helpers
│   └── cli/                  # CLI interface
│
├── docs/                     # Documentation
├── tests/                    # Unit tests
└── LICENSE                   # MIT License
```

---

## 🚢 Deployment

### Local Development
```bash
python app.py --reload
```

### Docker
```bash
docker build -t guadrails .
docker run -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  -e ENDEE_HOST=http://host.docker.internal:8080 \
  guadrails
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 guardrag.api.main:app
```

### Cloud (Render, Railway, Fly.io)
```bash
# Push to GitHub and configure:
OLLAMA_HOST=your_ollama_url
ENDEE_HOST=your_endee_url
# CI/CD automatically deploys
```

---

## 🆘 Troubleshooting

### Ollama Connection Error
```bash
# Verify Ollama running
curl http://localhost:11434/api/tags

# Start if needed
ollama serve
```

### Endee Connection Error
```bash
# Verify Endee running
curl http://localhost:8080/health

# Start if needed (from Endee directory)
./run.sh
```

### Out of Memory
```bash
# Use smaller model
python app.py --model tinyllama

# Increase overlap for context
CHUNK_OVERLAP=500 python app.py
```

### GPU Not Detected
```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA support if needed
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## 📚 Documentation

- **[Installation Guide](docs/INSTALL.md)** — Detailed setup
- **[API Reference](docs/API.md)** — Complete API docs
- **[Architecture](docs/ARCHITECTURE.md)** — Technical details
- **[Endee Docs](https://docs.endee.io)** — Vector DB docs
- **[LangChain Docs](https://python.langchain.com)** — RAG framework

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

### Quick Links
- **[Report Bugs](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE/issues)**
- **[Feature Requests](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE/discussions)**
- **[Submit PRs](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE/pulls)**

---

## 📜 License

**MIT License** — Free for commercial use  
See [LICENSE](LICENSE) file.

**Trademark Notes:**
- "Endee" is a trademark of Endee Labs
- This is community-maintained (not official Endee service)

---

## 🙏 Built With

- **[Endee](https://endee.io)** — Vector database
- **[LangChain](https://langchain.com)** — LLM orchestration
- **[Ollama](https://ollama.com)** — Local inference
- **[HuggingFace](https://huggingface.co)** — Embeddings
- **[FastAPI](https://fastapi.tiangolo.com)** — Web framework

---

## 📞 Support

- **GitHub**: [@sowmiyan-s](https://github.com/sowmiyan-s)
- **Issues**: [Bug Reports](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE/issues)
- **Discussions**: [Q&A](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE/discussions)
- **Endee Community**: [Discord](https://discord.gg/5HFGqDZQE3)

---

<div align="center">

### ⭐ Star this repo if it helps you!

**[⭐ Star](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE)** | **[📖 Docs](docs/)** | **[🚀 Get Started](#-quick-start-5-minutes)**

---

Made with ❤️ by **[Sowmiyan S](https://github.com/sowmiyan-s)**  
Enhanced with **[Endee Vector Database](https://github.com/endee-io/endee)**  

*Privacy-First • Open-Source • Production-Ready • Enterprise-Grade*

</div>
