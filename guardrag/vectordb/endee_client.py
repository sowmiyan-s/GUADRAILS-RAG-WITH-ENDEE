"""
Endee Vector Database Client Integration

This module provides a wrapper around the Endee HTTP API for vector storage
and retrieval, replacing FAISS as the vector database backend.

Endee is a high-performance vector database designed for RAG pipelines,
semantic search, and AI retrieval workloads.

GitHub: https://github.com/endee-io/endee
"""

import os
import json
import requests
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EndeeConfig:
    """Configuration for Endee vector database connection."""
    host: str = "http://localhost:8080"
    index_name: str = "guardrag_index"
    vector_dim: int = 384  # Default for sentence-transformers/all-MiniLM-L6-v2
    metric: str = "cosine"  # Options: cosine, l2, dot


class EndeeVectorStore:
    """
    Endee Vector Store client for managing embeddings and retrieval.
    
    Endee is a production-grade, open-source vector database optimized for:
    - High-performance vector search at scale (up to 1B vectors per node)
    - Hybrid retrieval with sparse vectors
    - Metadata-aware filtering
    - RAG and AI retrieval workflows
    """

    def __init__(self, config: Optional[EndeeConfig] = None):
        """
        Initialize Endee vector store client.

        Args:
            config: EndeeConfig instance with host, index_name, etc.
        """
        self.config = config or EndeeConfig()
        self.host = self.config.host.rstrip("/")
        self.index_name = self.config.index_name
        self.vector_dim = self.config.vector_dim
        self.metric = self.config.metric

        # Verify Endee is running
        if not self._is_healthy():
            logger.warning(
                f"Endee server not responding at {self.host}. "
                "Ensure Endee is running: ./run.sh"
            )

    def _is_healthy(self) -> bool:
        """Check if Endee server is healthy."""
        try:
            response = requests.get(
                f"{self.host}/health",
                timeout=2
            )
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def create_index(self) -> bool:
        """
        Create a new vector index in Endee.

        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "index_name": self.index_name,
                "metric_type": self.metric,
                "vector_dim": self.vector_dim,
                "enable_metadata": True,
            }
            response = requests.post(
                f"{self.host}/v1/indexes",
                json=payload,
                timeout=10
            )

            if response.status_code in [200, 201]:
                logger.info(f"Created Endee index: {self.index_name}")
                return True
            elif response.status_code == 409:
                logger.info(f"Index {self.index_name} already exists")
                return True
            else:
                logger.error(f"Failed to create index: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error creating Endee index: {e}")
            return False

    def add_vectors(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Add vectors to the Endee index.

        Args:
            vectors: List of embedding vectors
            ids: Unique IDs for each vector
            metadata: Optional metadata dictionaries for each vector

        Returns:
            True if successful
        """
        try:
            if metadata is None:
                metadata = [{} for _ in vectors]

            points = []
            for idx, (vector, doc_id) in enumerate(zip(vectors, ids)):
                point = {
                    "id": doc_id,
                    "vector": vector,
                    "metadata": metadata[idx] if idx < len(metadata) else {},
                }
                points.append(point)

            payload = {
                "index_name": self.index_name,
                "points": points,
            }

            response = requests.post(
                f"{self.host}/v1/upsert",
                json=payload,
                timeout=30
            )

            if response.status_code in [200, 201]:
                logger.info(f"Added {len(vectors)} vectors to Endee index")
                return True
            else:
                logger.error(f"Failed to add vectors: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error adding vectors to Endee: {e}")
            return False

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar vectors in Endee.

        Args:
            query_vector: Query embedding vector
            top_k: Number of top results to return
            filters: Optional metadata filters for retrieval

        Returns:
            List of tuples: (document_id, similarity_score, metadata)
        """
        try:
            payload = {
                "index_name": self.index_name,
                "query_vector": query_vector,
                "top_k": top_k,
            }

            if filters:
                payload["filters"] = filters

            response = requests.post(
                f"{self.host}/v1/search",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                results = response.json().get("results", [])
                return [
                    (r.get("id"), r.get("score", 0.0), r.get("metadata", {}))
                    for r in results
                ]
            else:
                logger.error(f"Search failed: {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error searching Endee: {e}")
            return []

    def hybrid_search(
        self,
        dense_query: List[float],
        sparse_query: Optional[Dict[str, float]] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Perform hybrid search combining dense and sparse (BM25) retrieval.

        Args:
            dense_query: Dense vector embedding
            sparse_query: Sparse BM25 representation (term -> weight)
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of tuples: (document_id, score, metadata)
        """
        try:
            payload = {
                "index_name": self.index_name,
                "dense_query": dense_query,
                "top_k": top_k,
            }

            if sparse_query:
                payload["sparse_query"] = sparse_query

            if filters:
                payload["filters"] = filters

            response = requests.post(
                f"{self.host}/v1/hybrid_search",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                results = response.json().get("results", [])
                return [
                    (r.get("id"), r.get("score", 0.0), r.get("metadata", {}))
                    for r in results
                ]
            else:
                logger.error(f"Hybrid search failed: {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []

    def delete_index(self) -> bool:
        """Delete the Endee index."""
        try:
            response = requests.delete(
                f"{self.host}/v1/indexes/{self.index_name}",
                timeout=10
            )
            if response.status_code in [200, 204]:
                logger.info(f"Deleted index: {self.index_name}")
                return True
            else:
                logger.error(f"Failed to delete index: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            response = requests.get(
                f"{self.host}/v1/indexes/{self.index_name}/stats",
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {}

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

    @staticmethod
    def from_env() -> "EndeeVectorStore":
        """Create EndeeVectorStore from environment variables."""
        config = EndeeConfig(
            host=os.environ.get("ENDEE_HOST", "http://localhost:8080"),
            index_name=os.environ.get("ENDEE_INDEX_NAME", "guardrag_index"),
            vector_dim=int(os.environ.get("ENDEE_VECTOR_DIM", "384")),
            metric=os.environ.get("ENDEE_METRIC", "cosine"),
        )
        return EndeeVectorStore(config)
