"""
Core RAG pipeline for document processing and retrieval.
Supports multiple LLM providers: Ollama (offline), OpenAI, Anthropic, Gemini.
"""

import os
import time
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
try:
    from langchain.chains import create_retrieval_chain, create_history_aware_retriever
    from langchain.chains.combine_documents import create_stuff_documents_chain
except ImportError:
    # Handle future versions (1.0+) where chains moved to langchain_classic
    from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
    from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Proxy bypass
_NO_PROXY = "huggingface.co,*.huggingface.co,localhost,127.0.0.1"
os.environ.setdefault("NO_PROXY", _NO_PROXY)
os.environ.setdefault("no_proxy", _NO_PROXY)


from guardrag.vectordb.endee_client import EndeeVectorStore, EndeeConfig

_embeddings = None

def _get_embeddings():
    """Get HuggingFace embeddings model (cached)."""
    global _embeddings
    if _embeddings is None:
        try:
            _embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize HuggingFace embeddings. "
                f"Ensure 'sentence-transformers', 'torch', and 'transformers' are installed correctly. "
                f"Error: {str(e)}"
            )
    return _embeddings


def _get_llm(provider: str = "ollama", model: str = "gemma3:1b",
             api_key: str = "", ollama_host: str = "http://localhost:11434"):
    """
    Create the appropriate LangChain LLM based on the selected provider.
    """
    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model, base_url=ollama_host.rstrip("/"), num_ctx=2048)

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.3,
            max_tokens=2048,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            api_key=api_key,
            temperature=0.3,
            max_tokens=2048,
        )

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.3,
            max_output_tokens=2048,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun

class EndeeRetriever(BaseRetriever):
    """Custom LangChain retriever for Endee Vector Database."""
    vectorstore: EndeeVectorStore
    embeddings: Any
    top_k: int = 5

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        query_vector = self.embeddings.embed_query(query)
        results = self.vectorstore.search(query_vector, top_k=self.top_k)
        
        docs = []
        for doc_id, score, metadata in results:
            content = metadata.pop("text", "")
            docs.append(Document(page_content=content, metadata=metadata))
        return docs


def build_rag_chain(
    file_paths: List[str],
    model: str = "gemma3:1b",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    ollama_host: str = "http://localhost:11434",
    storage_dir: str = ".guardrag_storage",
    provider: str = "ollama",
    api_key: str = "",
) -> Tuple[str, Any]:
    """
    Build a RAG chain from document files using Endee.
    """
    embeddings = _get_embeddings()
    
    # Generate index name based on file content and settings
    hasher = hashlib.md5()
    for fp in file_paths:
        with open(fp, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
    
    provider_label = provider.lower()
    db_id = f"idx_{hasher.hexdigest()[:16]}"
    
    # Initialize Endee
    endee_host = os.environ.get("ENDEE_HOST", "http://localhost:8080")
    config = EndeeConfig(host=endee_host, index_name=db_id)
    vectorstore = EndeeVectorStore(config)
    
    # Check if index exists or needs creation
    stats = vectorstore.get_stats()
    if not stats or stats.get("point_count", 0) == 0:
        print(f"Creating Endee index: {db_id}")
        vectorstore.create_index()
        
        print(f"Loading documents...")
        docs = []
        for fp in file_paths:
            ext = os.path.splitext(fp)[-1].lower()
            try:
                if ext == ".pdf":
                    loader = PyPDFLoader(fp)
                elif ext == ".txt":
                    loader = TextLoader(fp, encoding="utf-8")
                elif ext in [".doc", ".docx"]:
                    loader = Docx2txtLoader(fp)
                else:
                    continue
                docs.extend(loader.load())
            except Exception as e:
                print(f"  Error loading {os.path.basename(fp)}: {e}")
                raise e
        
        if not docs:
            raise ValueError("No documents were successfully loaded.")
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        splits = splitter.split_documents(docs)
        
        print(f"Adding {len(splits)} chunks to Endee...")
        vectors = []
        ids = []
        metadata = []
        
        for i, split in enumerate(splits):
            vector = embeddings.embed_query(split.page_content)
            vectors.append(vector)
            ids.append(f"{db_id}_{i}")
            meta = split.metadata.copy()
            meta["text"] = split.page_content  # Store text in metadata for reconstruction
            metadata.append(meta)
            
            # Batch upsert every 50 vectors
            if len(vectors) >= 50:
                vectorstore.add_vectors(vectors, ids, metadata)
                vectors, ids, metadata = [], [], []
        
        if vectors:
            vectorstore.add_vectors(vectors, ids, metadata)
    else:
        print(f"Using existing Endee index: {db_id}")

    # Build RAG chain
    retriever = EndeeRetriever(vectorstore=vectorstore, embeddings=embeddings)
    rag_chain = _build_chain_from_retriever(
        retriever, model, ollama_host, provider, api_key
    )
    
    print("RAG chain ready (Endee powered)!")
    return db_id, rag_chain


def _build_chain_from_retriever(retriever, model: str, ollama_host: str,
                                 provider: str = "ollama", api_key: str = ""):
    """Build a LangChain RAG chain from an Endee retriever."""
    llm = _get_llm(provider, model, api_key, ollama_host)
    
    # History-aware retriever
    ctx_q_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Given a chat history and the latest user question which might reference "
         "context in the chat history, formulate a standalone question which can be "
         "understood without the chat history. Do NOT answer the question, just "
         "reformulate it if needed and otherwise return it as is."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_retriever = create_history_aware_retriever(llm, retriever, ctx_q_prompt)
    
    # Q&A chain
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an assistant for question-answering tasks. "
         "Use the following pieces of retrieved context to answer the question. "
         "If you don't know the answer, say that you don't know. "
         "Keep the answer as concise as possible based on the context.\n\n"
         "Context:\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    qa_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    return create_retrieval_chain(history_retriever, qa_chain)


def load_stored_rag_chain(
    db_id: str,
    model: str = "gemma3:1b",
    ollama_host: str = "http://localhost:11434",
    storage_dir: str = ".guardrag_storage",
    provider: str = "ollama",
    api_key: str = "",
):
    """
    Load a previously created Endee index and build the RAG chain.
    """
    endee_host = os.environ.get("ENDEE_HOST", "http://localhost:8080")
    config = EndeeConfig(host=endee_host, index_name=db_id)
    vectorstore = EndeeVectorStore(config)
    
    embeddings = _get_embeddings()
    retriever = EndeeRetriever(vectorstore=vectorstore, embeddings=embeddings)
    
    return _build_chain_from_retriever(retriever, model, ollama_host, provider, api_key)
