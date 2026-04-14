"""
GUARDRAILS LOCAL RAG BOT — FastAPI Backend
==========================================
Replaces the Streamlit frontend with a proper REST API so the app
can be served as a standard web application and deployed anywhere
(Render, Railway, Fly.io, Docker, bare-metal, etc.).

Endpoints
---------
GET  /api/health          → overall health (Ollama status, model list)
GET  /api/config          → server-side config (OLLAMA_HOST env var) sent to frontend
POST /api/ollama/start    → try to start the local Ollama process
POST /api/upload          → upload one or more documents, build / load RAG chain
POST /api/chat            → send a question, get an answer
POST /api/clear           → clear conversation history
GET  /api/storage         → list all persisted FAISS document collections
POST /api/sessions/load   → rehydrate a stored FAISS session (no re-upload needed)
GET  /                    → serve frontend index.html
"""

# ─────────────────────────────────────────────────────────────────────────────
# Server-wide Ollama host — set OLLAMA_HOST env var to pre-configure all users.
# When deployed online (Render, Fly.io, etc.) with a tunnel URL set as
# OLLAMA_HOST, every visitor automatically uses that endpoint with zero
# configuration on their part.
# ─────────────────────────────────────────────────────────────────────────────
# NOTE: This constant is defined AFTER load_dotenv() below.

import os
import tempfile
import hashlib
import time
import json
import urllib.request
import subprocess

from pathlib import Path
from typing import Optional

# Fix OMP error for FAISS (must be before FAISS import)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Proxy bypass — keeps HuggingFace downloads & Ollama calls out of corporate proxies
_NO_PROXY = "huggingface.co,*.huggingface.co,localhost,127.0.0.1"
os.environ.setdefault("NO_PROXY", _NO_PROXY)
os.environ.setdefault("no_proxy", _NO_PROXY)

import nest_asyncio
try:
    nest_asyncio.apply()
except (ValueError, RuntimeError):
    # nest_asyncio cannot patch uvloop (used by uvicorn[standard] in production).
    # That's fine — uvloop doesn't need the patch; skip silently.
    pass

from dotenv import load_dotenv
load_dotenv()

# Server-wide default Ollama host — reads from environment variable.
# Override at any time by setting OLLAMA_HOST in .env or your PaaS settings.
SERVER_OLLAMA_HOST: str = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from langchain_core.messages import HumanMessage, AIMessage

# Internal imports
from guardrag.rag.core import (
    build_rag_chain,
    load_stored_rag_chain,
)
from guardrag.utils.ollama import (
    is_ollama_running,
    get_installed_models,
    start_ollama_server,
    get_ollama_version,
)

# ─────────────────────────────────────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Guardrails Local RAG Bot",
    description="Privacy-first, fully offline AI document assistant secured by tiered safety guardrails.",
    version="1.1.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent / "frontend"
RAG_STORAGE = Path.cwd() / ".guardrag_storage"
RAG_STORAGE.mkdir(exist_ok=True)

# Meta file that maps db_id → human-readable info (file names, date, model)
RAG_META_FILE = RAG_STORAGE / "_meta.json"

# ─────────────────────────────────────────────────────────────────────────────
# RAG metadata helpers
# ─────────────────────────────────────────────────────────────────────────────
def _load_rag_meta() -> dict:
    if RAG_META_FILE.exists():
        try:
            return json.loads(RAG_META_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save_rag_meta(meta: dict):
    RAG_META_FILE.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

def _register_rag_entry(db_id: str, file_names: list, model: str, chunk_size: int, chunk_overlap: int):
    meta = _load_rag_meta()
    meta[db_id] = {
        "files": file_names,
        "model": model,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _save_rag_meta(meta)

# ─────────────────────────────────────────────────────────────────────────────
# In-memory session store (single-user; extend with Redis for multi-user)
# ─────────────────────────────────────────────────────────────────────────────
_sessions: dict = {}   # session_id → { rag_chain, messages, settings }


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: str
    question: str
    model: str = "gemma3:1b"
    provider: str = "ollama"
    api_key: str = ""
    enable_guardrails: bool = True
    sensitivity_level: str = "Internal"
    # Frontend sends whatever the user has in the Endpoint URL box;
    # if blank the server default (SERVER_OLLAMA_HOST) is used.
    ollama_host: str = ""

    def resolved_host(self) -> str:
        return (self.ollama_host or SERVER_OLLAMA_HOST).rstrip("/")

class ClearRequest(BaseModel):
    session_id: str

class LoadSessionRequest(BaseModel):
    db_id: str
    model: str = "gemma3:1b"
    provider: str = "ollama"
    api_key: str = ""
    ollama_host: str = ""

    def resolved_host(self) -> str:
        return (self.ollama_host or SERVER_OLLAMA_HOST).rstrip("/")


# ─────────────────────────────────────────────────────────────────────────────
# Ollama utilities
# ─────────────────────────────────────────────────────────────────────────────
def is_ollama_running(host: str = "http://localhost:11434") -> bool:
    try:
        req = urllib.request.Request(host.rstrip("/") + "/", method="GET")
        urllib.request.urlopen(req, timeout=3)
        return True
    except Exception:
        return False

def get_installed_models(host: str = "http://localhost:11434") -> list[str]:
    try:
        req = urllib.request.urlopen(host.rstrip("/") + "/api/tags", timeout=3)
        data = json.loads(req.read().decode("utf-8"))
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []

def start_ollama_server() -> bool:
    """Attempt to start a locally-installed Ollama process."""
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        subprocess.Popen(["ollama", "serve"], creationflags=flags)
        for _ in range(20):
            if is_ollama_running():
                return True
            time.sleep(0.5)
        return False
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Safety system
# ─────────────────────────────────────────────────────────────────────────────
JAILBREAK_PATTERNS = [
    "ignore previous", "forget your instructions", "ignore all prior",
    "jailbreak", "dan mode", "pretend you are", "act as if you are",
    "you are now", "disregard your", "override your",
]

SENSITIVITY_PROFILES = {
    "Public": {
        "description": "No data classification restrictions. Basic jailbreak protection only.",
        "input_patterns": [],
        "output_patterns": [],
        "badge": "public",
    },
    "Internal": {
        "description": "Suitable for internal business data. Blocks credential and API key exposure.",
        "input_patterns": ["api key", "api_key", "password", "secret key", "access token", "private key", "credential"],
        "output_patterns": ["api_key", "api key", "password", "access_token", "credential", "private_key", "bearer token"],
        "badge": "internal",
    },
    "Confidential": {
        "description": "For confidential data. Adds PII protection.",
        "input_patterns": [
            "api key", "api_key", "password", "secret key", "access token", "private key", "credential",
            "social security", "ssn", "date of birth", "home address", "phone number", "email address",
            "credit card", "bank account",
        ],
        "output_patterns": [
            "api_key", "api key", "password", "access_token", "credential", "private_key", "bearer token",
            "ssn", "social security", "date of birth", "credit card", "bank account",
        ],
        "badge": "confidential",
    },
    "Restricted": {
        "description": "Maximum protection. For highly sensitive or regulated data (HIPAA, GDPR, financial).",
        "input_patterns": [
            "api key", "api_key", "password", "secret key", "access token", "private key", "credential",
            "social security", "ssn", "date of birth", "home address", "phone number", "email address",
            "credit card", "bank account", "medical record", "diagnosis", "prescription", "patient",
            "salary", "tax return", "financial statement", "trading", "investment",
        ],
        "output_patterns": [
            "api_key", "api key", "password", "access_token", "credential", "private_key", "bearer token",
            "ssn", "social security", "date of birth", "credit card", "bank account",
            "medical record", "diagnosis", "prescription", "patient id",
            "salary", "tax", "financial",
        ],
        "badge": "restricted",
    },
}

def check_input_safety(user_input: str, sensitivity: str, enabled: bool) -> Optional[str]:
    if not enabled:
        return None
    lower = user_input.lower()
    for pat in JAILBREAK_PATTERNS:
        if pat in lower:
            return "This request has been blocked. Prompt injection and instruction-override attempts are not permitted."
    profile = SENSITIVITY_PROFILES.get(sensitivity, SENSITIVITY_PROFILES["Internal"])
    for pat in profile["input_patterns"]:
        if pat in lower:
            return f"This request has been blocked under the active **{sensitivity}** data sensitivity policy."
    return None

def check_output_safety(response: str, sensitivity: str, enabled: bool) -> Optional[str]:
    if not enabled:
        return None
    lower = response.lower()
    profile = SENSITIVITY_PROFILES.get(sensitivity, SENSITIVITY_PROFILES["Internal"])
    for pat in profile["output_patterns"]:
        if pat in lower:
            return f"[REDACTED — Output blocked by {sensitivity} data sensitivity policy.]"
    return None


# RAG functions are now imported from guardrag.rag.core


# ─────────────────────────────────────────────────────────────────────────────
# API routes
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/config")
def get_config():
    """Return server-side configuration to the frontend.
    The frontend reads SERVER_OLLAMA_HOST from here on startup so users
    don’t need to configure anything manually when the app is deployed.
    """
    return {
        "server_ollama_host": SERVER_OLLAMA_HOST,
        "is_remote": not ("localhost" in SERVER_OLLAMA_HOST or "127.0.0.1" in SERVER_OLLAMA_HOST),
    }


@app.get("/api/health")
def health(ollama_host: str = ""):
    """Check Ollama health. Uses SERVER_OLLAMA_HOST when no host is supplied."""
    host = (ollama_host or SERVER_OLLAMA_HOST).rstrip("/")
    running = is_ollama_running(host)
    models = get_installed_models(host) if running else []
    version = get_ollama_version(host) if running else "unknown"
    return {
        "ollama_running": running,
        "ollama_host": host,
        "ollama_version": version,
        "models": models,
        "sensitivity_profiles": {
            k: {"description": v["description"], "badge": v["badge"]}
            for k, v in SENSITIVITY_PROFILES.items()
        },
    }


@app.post("/api/ollama/start")
def ollama_start():
    """Attempt to start a locally-installed Ollama process."""
    if is_ollama_running(SERVER_OLLAMA_HOST):
        return {"started": True, "message": "Ollama is already running."}
    ok = start_ollama_server()
    if ok:
        return {"started": True, "message": "Ollama started successfully."}
    raise HTTPException(
        status_code=503,
        detail="Failed to start Ollama. Verify it is installed and the OLLAMA_HOST is correct.",
    )


@app.post("/api/upload")
async def upload_documents(
    files: list[UploadFile] = File(...),
    model: str = "gemma3:1b",
    provider: str = "ollama",
    api_key: str = "",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    ollama_host: str = "",
):
    # Use server-configured host if the client didn't supply one
    host = (ollama_host or SERVER_OLLAMA_HOST).rstrip("/")

    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    # Validate cloud provider has API key
    if provider != "ollama" and not api_key:
        raise HTTPException(status_code=400, detail=f"API key is required for {provider}.")

    allowed_ext = {".pdf", ".txt", ".doc", ".docx"}
    temp_paths = []
    file_names = []

    try:
        for uf in files:
            ext = os.path.splitext(uf.filename)[-1].lower()
            if ext not in allowed_ext:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(await uf.read())
                temp_paths.append(tmp.name)
            file_names.append(uf.filename)

        # Only check Ollama if using the Ollama provider
        if provider == "ollama" and not is_ollama_running(host):
            raise HTTPException(
                status_code=503,
                detail=f"Ollama is not reachable at {host}. Check the OLLAMA_HOST setting.",
            )

        try:
            db_id, rag_chain = build_rag_chain(
                temp_paths, model, chunk_size, chunk_overlap, host,
                provider=provider, api_key=api_key,
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Error building RAG index: {str(e)}"
            )

        h = hashlib.md5(
            ("|".join(sorted(file_names)) + model + str(chunk_size) + str(chunk_overlap)).encode()
        ).hexdigest()[:16]

        _sessions[h] = {
            "rag_chain": rag_chain,
            "messages": [],
            "model": model,
            "provider": provider,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "files": file_names,
            "db_id": db_id,
            "ollama_host": host,
        }

        _register_rag_entry(db_id, file_names, model, chunk_size, chunk_overlap)
        return {"session_id": h, "db_id": db_id, "files": file_names, "model": model}

    finally:
        for p in temp_paths:
            if os.path.exists(p):
                os.remove(p)


@app.get("/api/storage")
def list_storage():
    """
    Return all persisted RAG document collections (metadata).
    The frontend uses this to show the Document Library panel.
    """
    meta = _load_rag_meta()
    entries = []
    for db_id, info in meta.items():
        # Check if Endee index exists via its metadata or by checking Endee health
        # For now, we trust the metadata entry
        entries.append({
            "db_id": db_id,
            "files": info.get("files", []),
            "model": info.get("model", "unknown"),
            "chunk_size": info.get("chunk_size", 1000),
            "chunk_overlap": info.get("chunk_overlap", 200),
            "created_at": info.get("created_at", ""),
            "available": True, # Assume available if in metadata for Endee
        })
    # Newest first
    entries.sort(key=lambda x: x["created_at"], reverse=True)
    return {"collections": entries}


@app.post("/api/sessions/load")
def load_session(req: LoadSessionRequest):
    host = req.resolved_host()
    meta = _load_rag_meta()
    if req.db_id not in meta:
        raise HTTPException(status_code=404, detail="Collection not found in storage.")

    # With Endee, we don't necessarily check local files, but we could check Endee stats

    # Only check Ollama if using the Ollama provider
    if req.provider == "ollama" and not is_ollama_running(host):
        raise HTTPException(
            status_code=503,
            detail=f"Ollama is not reachable at {host}.",
        )

    if req.provider != "ollama" and not req.api_key:
        raise HTTPException(status_code=400, detail=f"API key is required for {req.provider}.")

    try:
        rag_chain = load_stored_rag_chain(
            req.db_id, req.model, host,
            provider=req.provider, api_key=req.api_key,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load index: {str(e)}")

    info = meta[req.db_id]
    h = hashlib.md5((req.db_id + req.model + host).encode()).hexdigest()[:16]

    _sessions[h] = {
        "rag_chain": rag_chain,
        "messages": [],
        "model": req.model,
        "provider": req.provider,
        "chunk_size": info.get("chunk_size", 1000),
        "chunk_overlap": info.get("chunk_overlap", 200),
        "files": info.get("files", []),
        "db_id": req.db_id,
        "ollama_host": host,
    }

    return {
        "session_id": h,
        "db_id": req.db_id,
        "files": info.get("files", []),
        "model": req.model,
    }


@app.post("/api/storage/delete")
def delete_storage_entry(body: dict):
    """Delete a stored RAG collection (metadata and Endee index if possible)."""
    db_id = body.get("db_id", "")
    if not db_id:
        raise HTTPException(status_code=400, detail="db_id is required.")

    meta = _load_rag_meta()
    if db_id not in meta:
        raise HTTPException(status_code=404, detail="Collection not found.")

    # Attempt to delete from Endee if host is known
    try:
        from guardrag.vectordb.endee_client import EndeeVectorStore, EndeeConfig
        endee_host = os.environ.get("ENDEE_HOST", "http://localhost:8080")
        vectorstore = EndeeVectorStore(EndeeConfig(host=endee_host, index_name=db_id))
        vectorstore.delete_index()
    except Exception:
        pass

    del meta[db_id]
    _save_rag_meta(meta)
    return {"deleted": True, "db_id": db_id}


@app.post("/api/chat")
def chat(req: ChatRequest):
    session = _sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please upload documents first.")

    # Input safety
    blocked = check_input_safety(req.question, req.sensitivity_level, req.enable_guardrails)
    if blocked:
        return {"answer": blocked, "blocked": True, "source": "input_guard"}

    # Build chat history
    history = []
    for msg in session["messages"]:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history.append(AIMessage(content=msg["content"]))

    try:
        result = session["rag_chain"].invoke({"input": req.question, "chat_history": history})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    if isinstance(result, dict) and "answer" in result:
        answer = result["answer"]
    elif isinstance(result, str):
        answer = result
    else:
        answer = str(result)

    # Output safety
    blocked_out = check_output_safety(answer, req.sensitivity_level, req.enable_guardrails)
    if blocked_out:
        answer = blocked_out
        session["messages"].append({"role": "user", "content": req.question})
        session["messages"].append({"role": "assistant", "content": answer})
        return {"answer": answer, "blocked": True, "source": "output_guard"}

    session["messages"].append({"role": "user", "content": req.question})
    session["messages"].append({"role": "assistant", "content": answer})

    return {"answer": answer, "blocked": False, "source": "llm"}


@app.post("/api/clear")
def clear_chat(req: ClearRequest):
    session = _sessions.get(req.session_id)
    if session:
        session["messages"] = []
    return {"cleared": True}


# ─────────────────────────────────────────────────────────────────────────────
# Static file serving (frontend)
# ─────────────────────────────────────────────────────────────────────────────
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        requested = FRONTEND_DIR / full_path
        if requested.exists() and requested.is_file():
            return FileResponse(str(requested))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
