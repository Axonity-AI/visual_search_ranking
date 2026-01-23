"""
Vector Database Interface

Enterprise-grade abstraction layer for vector databases.
Supports Pinecone (production) and Weaviate (local dev).
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
from pinecone import Pinecone, ServerlessSpec
import weaviate
from weaviate.classes.config import Configure, DataType, Property


logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Unified search result format."""
    id: str
    score: float
    metadata: Dict


class VectorDB(ABC):
    """Abstract base class for vector database operations."""

    @abstractmethod
    def create_index(self, index_name: str, dimension: int, metric: str = "cosine") -> bool:
        """Create a new vector index."""
        pass

    @abstractmethod
    def index_exists(self, index_name: str) -> bool:
        """Check if index exists."""
        pass

    @abstractmethod
    def upsert_vectors(
        self,
        index_name: str,
        vectors: np.ndarray,
        ids: List[str],
        metadata: List[Dict],
        batch_size: int = 100
    ) -> int:
        """Upload vectors with metadata to the index."""
        pass

    @abstractmethod
    def search(
        self,
        index_name: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        pass

    @abstractmethod
    def get_index_stats(self, index_name: str) -> Dict:
        """Get index statistics."""
        pass

    @abstractmethod
    def delete_index(self, index_name: str) -> bool:
        """Delete an index."""
        pass


class PineconeDB(VectorDB):
    """Pinecone vector database implementation (production)."""

    def __init__(self, api_key: str, environment: str = "us-east-1"):
        """
        Initialize Pinecone client.

        Args:
            api_key: Pinecone API key
            environment: Cloud region (default: us-east-1 for free tier)
        """
        self.api_key = api_key
        self.environment = environment
        self.pc = Pinecone(api_key=api_key)
        logger.info(f"Pinecone client initialized (region: {environment})")

    def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine"
    ) -> bool:
        """Create a serverless Pinecone index."""
        try:
            if self.index_exists(index_name):
                logger.info(f"Index '{index_name}' already exists")
                return True

            # Create serverless index (free tier)
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region=self.environment
                )
            )

            logger.info(f"Created Pinecone index '{index_name}' (dim={dimension}, metric={metric})")
            return True

        except Exception as e:
            logger.error(f"Failed to create Pinecone index: {e}")
            return False

    def index_exists(self, index_name: str) -> bool:
        """Check if Pinecone index exists."""
        try:
            indexes = self.pc.list_indexes()
            return any(idx.name == index_name for idx in indexes)
        except Exception as e:
            logger.error(f"Error checking index existence: {e}")
            return False

    def upsert_vectors(
        self,
        index_name: str,
        vectors: np.ndarray,
        ids: List[str],
        metadata: List[Dict],
        batch_size: int = 100
    ) -> int:
        """Upload vectors to Pinecone in batches."""
        try:
            index = self.pc.Index(index_name)
            total_uploaded = 0

            num_vectors = len(vectors)
            num_batches = (num_vectors + batch_size - 1) // batch_size

            for i in range(0, num_vectors, batch_size):
                batch_end = min(i + batch_size, num_vectors)
                batch_vectors = vectors[i:batch_end]
                batch_ids = ids[i:batch_end]
                batch_metadata = metadata[i:batch_end]

                # Prepare upsert data
                upsert_data = [
                    {
                        "id": str(vid),
                        "values": vec.tolist(),
                        "metadata": meta
                    }
                    for vid, vec, meta in zip(batch_ids, batch_vectors, batch_metadata)
                ]

                # Upsert batch
                index.upsert(vectors=upsert_data)
                total_uploaded += len(upsert_data)

                batch_num = (i // batch_size) + 1
                logger.info(f"Uploaded batch {batch_num}/{num_batches} ({len(upsert_data)} vectors)")

            logger.info(f"Successfully uploaded {total_uploaded} vectors to '{index_name}'")
            return total_uploaded

        except Exception as e:
            logger.error(f"Error upserting vectors to Pinecone: {e}")
            raise

    def search(
        self,
        index_name: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[SearchResult]:
        """Search Pinecone index for similar vectors."""
        try:
            index = self.pc.Index(index_name)

            # Query index
            results = index.query(
                vector=query_vector.tolist(),
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )

            # Convert to unified format
            search_results = [
                SearchResult(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata
                )
                for match in results.matches
            ]

            return search_results

        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            raise

    def get_index_stats(self, index_name: str) -> Dict:
        """Get Pinecone index statistics."""
        try:
            index = self.pc.Index(index_name)
            stats = index.describe_index_stats()

            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }

        except Exception as e:
            logger.error(f"Error getting Pinecone stats: {e}")
            return {}

    def delete_index(self, index_name: str) -> bool:
        """Delete Pinecone index."""
        try:
            self.pc.delete_index(index_name)
            logger.info(f"Deleted Pinecone index '{index_name}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting Pinecone index: {e}")
            return False


class WeaviateDB(VectorDB):
    """Weaviate vector database implementation (local dev)."""

    def __init__(self, host: str = "localhost", port: int = 8080):
        """
        Initialize Weaviate client.

        Args:
            host: Weaviate host
            port: Weaviate port
        """
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"

        try:
            self.client = weaviate.connect_to_local(
                host=host,
                port=port
            )
            logger.info(f"Connected to Weaviate at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise

    def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine"
    ) -> bool:
        """Create a Weaviate collection (class)."""
        try:
            if self.index_exists(index_name):
                logger.info(f"Collection '{index_name}' already exists")
                return True

            # Map metric to Weaviate distance
            distance_metric = {
                "cosine": "cosine",
                "euclidean": "l2-squared",
                "dot": "dot"
            }.get(metric, "cosine")

            # Create collection with HNSW indexing
            self.client.collections.create(
                name=index_name,
                properties=[
                    Property(name="product_id", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                    Property(name="category", data_type=DataType.TEXT),
                    Property(name="image_path", data_type=DataType.TEXT),
                ],
                vectorizer_config=Configure.Vectorizer.none(),
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric=distance_metric
                )
            )

            logger.info(f"Created Weaviate collection '{index_name}' (dim={dimension}, metric={distance_metric})")
            return True

        except Exception as e:
            logger.error(f"Failed to create Weaviate collection: {e}")
            return False

    def index_exists(self, index_name: str) -> bool:
        """Check if Weaviate collection exists."""
        try:
            return self.client.collections.exists(index_name)
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            return False

    def upsert_vectors(
        self,
        index_name: str,
        vectors: np.ndarray,
        ids: List[str],
        metadata: List[Dict],
        batch_size: int = 100
    ) -> int:
        """Upload vectors to Weaviate in batches."""
        try:
            collection = self.client.collections.get(index_name)
            total_uploaded = 0

            num_vectors = len(vectors)
            num_batches = (num_vectors + batch_size - 1) // batch_size

            # Use batch insert for efficiency
            with collection.batch.dynamic() as batch:
                for i, (vid, vec, meta) in enumerate(zip(ids, vectors, metadata)):
                    # Add object to batch
                    batch.add_object(
                        properties=meta,
                        vector=vec.tolist()
                    )
                    total_uploaded += 1

                    # Log progress
                    if (i + 1) % batch_size == 0:
                        batch_num = (i // batch_size) + 1
                        logger.info(f"Uploaded batch {batch_num}/{num_batches} ({batch_size} vectors)")

            logger.info(f"Successfully uploaded {total_uploaded} vectors to '{index_name}'")
            return total_uploaded

        except Exception as e:
            logger.error(f"Error upserting vectors to Weaviate: {e}")
            raise

    def search(
        self,
        index_name: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[SearchResult]:
        """Search Weaviate collection for similar vectors."""
        try:
            collection = self.client.collections.get(index_name)

            # Build query
            query = collection.query.near_vector(
                near_vector=query_vector.tolist(),
                limit=top_k,
                return_metadata=["distance"]
            )

            # Execute query
            results = query

            # Convert to unified format
            search_results = [
                SearchResult(
                    id=str(obj.uuid),
                    score=1.0 - obj.metadata.distance if obj.metadata.distance else 0.0,
                    metadata=obj.properties
                )
                for obj in results.objects
            ]

            return search_results

        except Exception as e:
            logger.error(f"Error searching Weaviate: {e}")
            raise

    def get_index_stats(self, index_name: str) -> Dict:
        """Get Weaviate collection statistics."""
        try:
            collection = self.client.collections.get(index_name)
            agg = collection.aggregate.over_all(total_count=True)

            return {
                "total_vectors": agg.total_count,
                "collection_name": index_name
            }

        except Exception as e:
            logger.error(f"Error getting Weaviate stats: {e}")
            return {}

    def delete_index(self, index_name: str) -> bool:
        """Delete Weaviate collection."""
        try:
            self.client.collections.delete(index_name)
            logger.info(f"Deleted Weaviate collection '{index_name}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting Weaviate collection: {e}")
            return False

    def close(self):
        """Close Weaviate connection."""
        try:
            self.client.close()
            logger.info("Closed Weaviate connection")
        except Exception as e:
            logger.error(f"Error closing Weaviate connection: {e}")


def get_vector_db(
    db_type: str = "pinecone",
    **kwargs
) -> VectorDB:
    """
    Factory function to get vector database instance.

    Args:
        db_type: Type of database ("pinecone" or "weaviate")
        **kwargs: Database-specific configuration

    Returns:
        VectorDB instance

    Example:
        # Pinecone (production)
        db = get_vector_db("pinecone", api_key="xxx", environment="us-east-1")

        # Weaviate (local dev)
        db = get_vector_db("weaviate", host="localhost", port=8080)
    """
    if db_type.lower() == "pinecone":
        api_key = kwargs.get("api_key") or os.getenv("PINECONE_API_KEY")
        environment = kwargs.get("environment", "us-east-1")

        if not api_key:
            raise ValueError("Pinecone API key required (set PINECONE_API_KEY env var)")

        return PineconeDB(api_key=api_key, environment=environment)

    elif db_type.lower() == "weaviate":
        host = kwargs.get("host", "localhost")
        port = kwargs.get("port", 8080)

        return WeaviateDB(host=host, port=port)

    else:
        raise ValueError(f"Unknown database type: {db_type}. Use 'pinecone' or 'weaviate'")
