
<div align="center">

# ⚔️ GUADRAILS-RAG-WITH-ENDEE

### Privacy-First • Enterprise-Grade • High-Performance RAG
**Revolutionizing local document intelligence with Endee Vector Database.**

<br/>

![RAG Workflow](./docs/workflow.svg)

<br/>

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3b82f6?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.111-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Endee](https://img.shields.io/badge/Endee-Native_Vector_DB-FF3B30?style=flat-square&logo=database)](https://github.com/endee-io/endee)
[![Ollama](https://img.shields.io/badge/Ollama-Offline_LLM-black?style=flat-square&logo=ollama&logoColor=white)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

<br/>

> **Upload any document. Ask anything. Get answers — 100% locally.**  
> Built for professionals who demand zero-trust privacy and billion-scale performance.

</div>

---

## 🌟 Overview

**GUADRAILS-RAG-WITH-ENDEE** is a production-ready Retrieval-Augmented Generation (RAG) system. Unlike standard RAG implementations that rely on cloud vector stores or lightweight local solutions, this project leverages **Endee**, a high-performance C++ optimized vector database capable of indexing billions of vectors with sub-millisecond latency.

### Why this project?
- 🔒 **Absolute Privacy**: No data leaves your machine. Ever.
- ⚡ **Endee Engine**: Native C++ vector search for industry-leading speed.
- 🎨 **Premium UI**: A sleek, ChatGPT-inspired interface with multi-tab navigation.
- 🛡️ **Security Guardrails**: Tiered safety protocols to detect and mask sensitive data.

---

## 🎯 Key Features

- 🦅 **Endee Vector Core**: Native integration for lightning-fast retrieval at scale.
- 💬 **Multi-Model Support**: Use local models via Ollama (Llama3, Gemma2, Mistral) or cloud APIs.
- 📂 **Consolidated Navigation**: Dedicated **Chat**, **Documents**, and **Settings** views in a tabbed sidebar.
- 🏠 **Smart Onboarding**: Drag-and-drop landing page for instant document processing even without the sidebar.
- 🔐 **Tiered Safety**: Public, Internal, Confidential, and Restricted security modes.
- 🚀 **Zero-Config Setup**: One command to start, with sensible defaults for hardware.

---

## 🚀 Quick Start (2 Minutes)

### 1. Prerequisites
- **Ollama**: [Download & Run](https://ollama.com)
- **Endee**: [Clone & Run](https://github.com/endee-io/endee) (Port 8080)

### 2. Run Application
```bash
# Clone the repository
git clone https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE.git
cd GUADRAILS-RAG-WITH-ENDEE

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```
👉 Access the dashboard at: **[http://localhost:8000](http://localhost:8000)**

---

## 🛠️ Detailed Installation & Setup

### Local Development
1. **Pull and serve a model** with Ollama:
   ```bash
   ollama pull gemma2:2b
   ```
2. **Start Endee** (Optimized for your CPU):
   ```bash
   # From the Endee root directory
   ./install.sh --release --avx2
   ./run.sh
   ```
3. **Configure Environment** (Optional):
   Copy `.env.example` to `.env` to customize ports, models, or chunking parameters.

### Docker Deployment
Generate a production-ready container:
```bash
docker build -t guadrails-rag .
docker run -p 8000:8000 guadrails-rag
```

---

## 📊 Technical Architecture

- **Web Layer**: FastAPI + Vanilla JavaScript (Glassmorphism design)
- **Vector Intelligence**: Endee (C++ Native)
- **Orchestration**: LangChain + Custom Endee Bridge
- **Embeddings**: HuggingFace `all-MiniLM-L6-v2` (Local, CPU/GPU optimized)
- **Inference**: Ollama (Default) or OpenAI/Anthropic/Gemini APIs

---

## ⚖️ Security Guardrails

The application includes an active safety engine that monitors input/output for sensitive information:
- **PII Detection**: Automatically masks emails, phone numbers, and SSNs.
- **Level-Based Filtering**: Adjust sensitivity from "Public" to "Restricted" based on document confidentiality.

---

## 🤝 Contributing & Community

Refer to the following specialized guides for community standards:
- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Contributing Guidelines](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)

---

## 📜 License

This project is licensed under the **MIT License**.

---

<div align="center">

### ⭐ Star this repo if it helps you!

[Repository](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE) • [Issues](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE/issues)

<br/>

**Architected & Developed by [Sowmiyan S](https://github.com/sowmiyan-s)**  
*Performance-Driven AI Intelligence*

</div>
