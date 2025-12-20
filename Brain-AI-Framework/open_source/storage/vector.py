"""
Semantic/Similarity Memory
Vector-based storage for semantic memory and similarity search.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import sqlite3
import asyncio
from pathlib import Path
from loguru import logger

from storage.persistence import PersistenceManager


@dataclass
class VectorEmbedding:
    """Represents a vector embedding"""
    id: str
    content_hash: str
    vector: List[float]
    metadata: Dict[str, Any]
    created_at: datetime
    access_count: int = 0
    last_accessed: datetime = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at


@dataclass
class SimilaritySearchResult:
    """Result from similarity search"""
    embedding: VectorEmbedding
    similarity_score: float
    rank: int


class VectorStore:
    """
    Vector-based Semantic Memory Store
    
    Provides semantic similarity search using vector embeddings:
    - Vector storage and retrieval
    - Similarity-based search
    - Semantic clustering
    - Dimensionality reduction
    - Performance optimization
    """
    
    def __init__(self, persistence_manager: PersistenceManager):
        self.persistence_manager = persistence_manager
        self.embedding_model = None
        self.vector_dimension = 384  # Default for sentence transformers
        
        # In-memory cache for frequently accessed embeddings
        self._embedding_cache: Dict[str, VectorEmbedding] = {}
        self._similarity_index: Dict[str, Dict[str, float]] = {}
        
        # Performance settings
        self.cache_size = 10000
        self.similarity_threshold = 0.7
        self.max_search_results = 100
        
        # Statistics
        self.stats = {
            "total_embeddings": 0,
            "search_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "similarity_calculations": 0
        }
    
    async def initialize(self):
        """Initialize the vector store"""
        logger.info("🔍 Initializing vector store...")
        
        try:
            # Initialize embedding model
            await self._initialize_embedding_model()
            
            # Load existing embeddings
            await self._load_embeddings()
            
            # Build similarity index
            await self._build_similarity_index()
            
            logger.info("✅ Vector store initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize vector store: {e}")
            raise
    
    async def store_embedding(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store content as vector embedding
        
        Args:
            content: Text content to embed
            metadata: Optional metadata
            
        Returns:
            Embedding ID
        """
        try:
            # Generate embedding
            vector = await self._generate_embedding(content)
            
            # Create embedding object
            import hashlib
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            embedding = VectorEmbedding(
                id=f"vec_{datetime.now().timestamp()}_{len(self._embedding_cache)}",
                content_hash=content_hash,
                vector=vector,
                metadata=metadata or {},
                created_at=datetime.now()
            )
            
            # Store in cache
            self._embedding_cache[embedding.id] = embedding
            
            # Update similarity index
            await self._update_similarity_index(embedding)
            
            # Persist to database
            await self._persist_embedding(embedding)
            
            self.stats["total_embeddings"] += 1
            
            logger.debug(f"Stored embedding {embedding.id} with {len(vector)} dimensions")
            return embedding.id
            
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            raise
    
    async def find_similar(
        self, 
        query: str, 
        limit: int = 10,
        threshold: float = None
    ) -> List[SimilaritySearchResult]:
        """
        Find similar content using semantic similarity
        
        Args:
            query: Query text
            limit: Maximum number of results
            threshold: Similarity threshold
            
        Returns:
            List of similar embeddings with scores
        """
        try:
            self.stats["search_operations"] += 1
            
            # Generate query embedding
            query_vector = await self._generate_embedding(query)
            threshold = threshold or self.similarity_threshold
            
            # Calculate similarities
            similarities = []
            for embedding_id, embedding in self._embedding_cache.items():
                similarity = self._cosine_similarity(query_vector, embedding.vector)
                
                if similarity >= threshold:
                    similarities.append((embedding, similarity))
            
            # Sort by similarity score
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Limit results
            results = similarities[:limit]
            
            # Create result objects
            search_results = [
                SimilaritySearchResult(
                    embedding=embedding,
                    similarity_score=similarity,
                    rank=idx + 1
                )
                for idx, (embedding, similarity) in enumerate(results)
            ]
            
            # Update access statistics
            for result in search_results:
                result.embedding.access_count += 1
                result.embedding.last_accessed = datetime.now()
            
            logger.debug(f"Found {len(search_results)} similar embeddings")
            return search_results
            
        except Exception as e:
            logger.error(f"Error finding similar content: {e}")
            raise
    
    async def find_similar_to_embedding(
        self, 
        embedding_id: str, 
        limit: int = 10
    ) -> List[SimilaritySearchResult]:
        """
        Find embeddings similar to existing embedding
        
        Args:
            embedding_id: ID of reference embedding
            limit: Maximum number of results
            
        Returns:
            List of similar embeddings
        """
        try:
            if embedding_id not in self._embedding_cache:
                raise ValueError(f"Embedding {embedding_id} not found")
            
            reference_embedding = self._embedding_cache[embedding_id]
            
            # Use pre-computed similarities if available
            if embedding_id in self._similarity_index:
                similarities = []
                for other_id, similarity in self._similarity_index[embedding_id].items():
                    if other_id != embedding_id and similarity >= self.similarity_threshold:
                        if other_id in self._embedding_cache:
                            similarities.append((self._embedding_cache[other_id], similarity))
            else:
                # Calculate similarities on the fly
                similarities = []
                for other_id, embedding in self._embedding_cache.items():
                    if other_id != embedding_id:
                        similarity = self._cosine_similarity(
                            reference_embedding.vector, 
                            embedding.vector
                        )
                        if similarity >= self.similarity_threshold:
                            similarities.append((embedding, similarity))
            
            # Sort and limit
            similarities.sort(key=lambda x: x[1], reverse=True)
            results = similarities[:limit]
            
            return [
                SimilaritySearchResult(
                    embedding=embedding,
                    similarity_score=similarity,
                    rank=idx + 1
                )
                for idx, (embedding, similarity) in enumerate(results)
            ]
            
        except Exception as e:
            logger.error(f"Error finding similar embeddings: {e}")
            raise
    
    async def cluster_embeddings(
        self, 
        method: str = "kmeans",
        n_clusters: int = 5,
        threshold: float = 0.8
    ) -> Dict[str, List[str]]:
        """
        Cluster embeddings based on similarity
        
        Args:
            method: Clustering method ('kmeans', 'hierarchical')
            n_clusters: Number of clusters
            threshold: Similarity threshold for clustering
            
        Returns:
            Dictionary mapping cluster IDs to embedding IDs
        """
        try:
            if method == "kmeans":
                return await self._kmeans_clustering(n_clusters)
            elif method == "hierarchical":
                return await self._hierarchical_clustering(threshold)
            else:
                raise ValueError(f"Unsupported clustering method: {method}")
                
        except Exception as e:
            logger.error(f"Error clustering embeddings: {e}")
            raise
    
    async def get_embedding_by_id(self, embedding_id: str) -> Optional[VectorEmbedding]:
        """
        Get embedding by ID
        
        Args:
            embedding_id: ID of embedding
            
        Returns:
            Embedding object or None
        """
        # Check cache first
        if embedding_id in self._embedding_cache:
            self.stats["cache_hits"] += 1
            return self._embedding_cache[embedding_id]
        else:
            self.stats["cache_misses"] += 1
        
        # Try to load from database
        try:
            embedding_data = await self._load_embedding_from_db(embedding_id)
            if embedding_data:
                embedding = VectorEmbedding(**embedding_data)
                self._embedding_cache[embedding_id] = embedding
                return embedding
        except Exception as e:
            logger.error(f"Error loading embedding {embedding_id}: {e}")
        
        return None
    
    async def delete_embedding(self, embedding_id: str) -> bool:
        """
        Delete embedding
        
        Args:
            embedding_id: ID of embedding to delete
            
        Returns:
            True if successful
        """
        try:
            # Remove from cache
            if embedding_id in self._embedding_cache:
                del self._embedding_cache[embedding_id]
            
            # Remove from similarity index
            if embedding_id in self._similarity_index:
                del self._similarity_index[embedding_id]
            
            # Remove from other indices
            for other_id, similarities in self._similarity_index.items():
                if embedding_id in similarities:
                    del similarities[embedding_id]
            
            # Delete from database
            await self._delete_embedding_from_db(embedding_id)
            
            logger.debug(f"Deleted embedding {embedding_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting embedding {embedding_id}: {e}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        
        cache_hit_rate = (
            self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
        ) * 100
        
        # Calculate average similarity if we have data
        all_similarities = []
        for similarities in self._similarity_index.values():
            all_similarities.extend(similarities.values())
        
        avg_similarity = (
            sum(all_similarities) / len(all_similarities) 
            if all_similarities else 0.0
        )
        
        return {
            **self.stats,
            "cache_size": len(self._embedding_cache),
            "similarity_index_size": len(self._similarity_index),
            "cache_hit_rate_percent": cache_hit_rate,
            "average_similarity": avg_similarity,
            "vector_dimension": self.vector_dimension
        }
    
    async def _initialize_embedding_model(self):
        """Initialize embedding model (placeholder)"""
        # In a real implementation, this would load:
        # - Sentence Transformers model
        # - OpenAI embeddings API
        # - Hugging Face transformers
        # For now, we'll use a simple placeholder
        
        self.embedding_model = "placeholder_model"
        logger.info("Initialized embedding model (placeholder)")
    
    async def _generate_embedding(self, content: str) -> List[float]:
        """Generate embedding for content"""
        
        # Placeholder implementation - in reality would use:
        # - sentence_transformers.SentenceTransformer
        # - openai.embeddings.create
        # - or other embedding models
        
        # For demonstration, create a simple hash-based embedding
        import hashlib
        content_hash = hashlib.md5(content.encode()).digest()
        
        # Convert hash to list of floats (normalized)
        vector = []
        for byte in content_hash:
            vector.append((byte / 255.0) * 2 - 1)  # Normalize to [-1, 1]
        
        # Pad or truncate to desired dimension
        while len(vector) < self.vector_dimension:
            vector.extend(vector[:min(len(vector), self.vector_dimension - len(vector))])
        
        return vector[:self.vector_dimension]
    
    def _cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        
        try:
            v1 = np.array(vector1)
            v2 = np.array(vector2)
            
            # Calculate cosine similarity
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    async def _load_embeddings(self):
        """Load embeddings from database"""
        
        try:
            embeddings_data = await self._load_all_embeddings_from_db()
            
            for embedding_data in embeddings_data:
                embedding = VectorEmbedding(**embedding_data)
                self._embedding_cache[embedding.id] = embedding
            
            logger.info(f"Loaded {len(embeddings_data)} embeddings from database")
            
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
    
    async def _build_similarity_index(self):
        """Build similarity index for fast searching"""
        
        try:
            embeddings = list(self._embedding_cache.values())
            n_embeddings = len(embeddings)
            
            # Build pairwise similarity matrix
            for i, embedding1 in enumerate(embeddings):
                self._similarity_index[embedding1.id] = {}
                
                for j, embedding2 in enumerate(embeddings):
                    if i != j:
                        similarity = self._cosine_similarity(
                            embedding1.vector, 
                            embedding2.vector
                        )
                        self._similarity_index[embedding1.id][embedding2.id] = similarity
            
            logger.info(f"Built similarity index for {n_embeddings} embeddings")
            
        except Exception as e:
            logger.error(f"Error building similarity index: {e}")
    
    async def _update_similarity_index(self, new_embedding: VectorEmbedding):
        """Update similarity index with new embedding"""
        
        try:
            # Add similarities with existing embeddings
            for existing_id, existing_embedding in self._embedding_cache.items():
                if existing_id != new_embedding.id:
                    similarity = self._cosine_similarity(
                        new_embedding.vector,
                        existing_embedding.vector
                    )
                    
                    # Add to new embedding's index
                    if new_embedding.id not in self._similarity_index:
                        self._similarity_index[new_embedding.id] = {}
                    self._similarity_index[new_embedding.id][existing_id] = similarity
                    
                    # Add to existing embedding's index
                    if existing_id not in self._similarity_index:
                        self._similarity_index[existing_id] = {}
                    self._similarity_index[existing_id][new_embedding.id] = similarity
            
        except Exception as e:
            logger.error(f"Error updating similarity index: {e}")
    
    async def _kmeans_clustering(self, n_clusters: int) -> Dict[str, List[str]]:
        """Perform K-means clustering"""
        
        # Simple K-means implementation using numpy
        embeddings = list(self._embedding_cache.values())
        if len(embeddings) < n_clusters:
            return {str(i): [emb.id] for i, emb in enumerate(embeddings)}
        
        # Extract vectors
        vectors = np.array([emb.vector for emb in embeddings])
        
        # Initialize centroids randomly
        np.random.seed(42)
        centroids = vectors[np.random.choice(len(vectors), n_clusters, replace=False)]
        
        # K-means iterations
        max_iterations = 100
        for _ in range(max_iterations):
            # Assign points to nearest centroid
            distances = np.linalg.norm(vectors[:, np.newaxis] - centroids, axis=2)
            assignments = np.argmin(distances, axis=1)
            
            # Update centroids
            new_centroids = np.array([vectors[assignments == k].mean(axis=0) for k in range(n_clusters)])
            
            # Check convergence
            if np.allclose(centroids, new_centroids):
                break
            
            centroids = new_centroids
        
        # Create clusters
        clusters = {}
        for i, embedding in enumerate(embeddings):
            cluster_id = str(assignments[i])
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(embedding.id)
        
        return clusters
    
    async def _hierarchical_clustering(self, threshold: float) -> Dict[str, List[str]]:
        """Perform hierarchical clustering"""
        
        # Simple hierarchical clustering based on similarity
        embeddings = list(self._embedding_cache.values())
        clusters = {str(i): [emb.id] for i, emb in enumerate(embeddings)}
        
        # Merge similar clusters iteratively
        while len(clusters) > 1:
            max_similarity = -1
            merge_pair = None
            
            cluster_ids = list(clusters.keys())
            
            for i, cluster1_id in enumerate(cluster_ids):
                for j, cluster2_id in enumerate(cluster_ids[i+1:], i+1):
                    # Calculate average similarity between clusters
                    similarities = []
                    for emb1_id in clusters[cluster1_id]:
                        for emb2_id in clusters[cluster2_id]:
                            if emb1_id in self._similarity_index and emb2_id in self._similarity_index[emb1_id]:
                                similarities.append(self._similarity_index[emb1_id][emb2_id])
                    
                    if similarities:
                        avg_similarity = sum(similarities) / len(similarities)
                        if avg_similarity > max_similarity:
                            max_similarity = avg_similarity
                            merge_pair = (cluster1_id, cluster2_id)
            
            # Merge if similarity is above threshold
            if max_similarity >= threshold and merge_pair:
                cluster1_id, cluster2_id = merge_pair
                clusters[cluster1_id].extend(clusters[cluster2_id])
                del clusters[cluster2_id]
            else:
                break  # No more merges above threshold
        
        return clusters
    
    async def _persist_embedding(self, embedding: VectorEmbedding):
        """Persist embedding to database"""
        
        async def store_embedding(conn):
            conn.execute("""
                INSERT OR REPLACE INTO embeddings 
                (id, content_hash, embedding_vector, metadata, created_at, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                embedding.id,
                embedding.content_hash,
                ",".join(map(str, embedding.vector)),
                str(embedding.metadata),
                embedding.created_at.isoformat(),
                embedding.access_count,
                embedding.last_accessed.isoformat() if embedding.last_accessed else None
            ))
        
        await self.persistence_manager.execute_sql(store_embedding)
    
    async def _load_embedding_from_db(self, embedding_id: str) -> Optional[Dict[str, Any]]:
        """Load single embedding from database"""
        
        async def load_embedding(conn):
            cursor = conn.execute(
                "SELECT * FROM embeddings WHERE id = ?",
                (embedding_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "content_hash": row[1],
                    "vector": list(map(float, row[2].split(","))),
                    "metadata": eval(row[3]),  # In production, use proper JSON parsing
                    "created_at": datetime.fromisoformat(row[4]),
                    "access_count": row[5],
                    "last_accessed": datetime.fromisoformat(row[6]) if row[6] else None
                }
            return None
        
        return await self.persistence_manager.execute_sql(load_embedding)
    
    async def _load_all_embeddings_from_db(self) -> List[Dict[str, Any]]:
        """Load all embeddings from database"""
        
        async def load_embeddings(conn):
            cursor = conn.execute("SELECT * FROM embeddings")
            rows = cursor.fetchall()
            
            embeddings = []
            for row in rows:
                embeddings.append({
                    "id": row[0],
                    "content_hash": row[1],
                    "vector": list(map(float, row[2].split(","))),
                    "metadata": eval(row[3]),
                    "created_at": datetime.fromisoformat(row[4]),
                    "access_count": row[5],
                    "last_accessed": datetime.fromisoformat(row[6]) if row[6] else None
                })
            
            return embeddings
        
        return await self.persistence_manager.execute_sql(load_embeddings)
    
    async def _delete_embedding_from_db(self, embedding_id: str):
        """Delete embedding from database"""
        
        async def delete_embedding(conn):
            conn.execute("DELETE FROM embeddings WHERE id = ?", (embedding_id,))
        
        await self.persistence_manager.execute_sql(delete_embedding)