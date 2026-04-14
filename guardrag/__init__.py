"""
Gurag Chat - A privacy-first, fully offline AI document assistant
powered by Guardrails, LangChain, Ollama, and HuggingFace embeddings.
"""

__version__ = "1.1.4"
__author__ = "Sowmiyan S"
__license__ = "MIT"


def __getattr__(name):
    """Lazy import of modules."""
    if name == "build_rag_chain":
        from guardrag.rag.core import build_rag_chain
        return build_rag_chain
    elif name == "load_stored_rag_chain":
        from guardrag.rag.core import load_stored_rag_chain
        return load_stored_rag_chain
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "build_rag_chain",
    "load_stored_rag_chain",
]
