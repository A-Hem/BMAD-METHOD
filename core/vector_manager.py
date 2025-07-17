import redis
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VectorSearchResult:
    content: str
    source_agent: str
    similarity_score: float
    metadata: Dict[str, Any]

class VectorManager:
    """Manages vector embeddings and semantic search for the context system"""
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379, 
                 embedding_model: str = 'all-MiniLM-L6-v2'):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.embedding_model = SentenceTransformer(embedding_model)
        self.vector_dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.index_name = "context_knowledge_index"
        
        # Initialize vector index
        self._create_vector_index()
    
    def _create_vector_index(self):
        """Create Redis vector index for semantic search"""
        try:
            # Check if index already exists
            try:
                info = self.redis_client.ft(self.index_name).info()
                if info:
                    logger.info(f"Vector index {self.index_name} already exists")
                    return
            except redis.exceptions.ResponseError:
                # Index doesn't exist, continue to create it
                pass
        
        except Exception as e:
            logger.warning(f"Error checking index existence: {e}")
        
        # Create vector index schema
        schema = (
            redis.commands.search.field.TextField("content", weight=1.0),
            redis.commands.search.field.TagField("source_agent"),
            redis.commands.search.field.TagField("topics"),
            redis.commands.search.field.VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.vector_dimension,
                    "DISTANCE_METRIC": "COSINE"
                }
            )
        )
        
        try:
            self.redis_client.ft(self.index_name).create_index(schema)
            logger.info(f"Created vector index: {self.index_name}")
        except Exception as e:
            logger.warning(f"Index creation failed (may already exist): {e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text"""
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * self.vector_dimension
    
    def store_vector_knowledge(self, content: str, source_agent: str, 
                             topics: List[str], metadata: Optional[Dict[str, Any]] = None):
        """Store knowledge with vector embedding"""
        try:
            # Generate embedding
            embedding = self.get_embedding(content)
            
            # Prepare document
            doc_id = f"knowledge:{source_agent}:{hash(content)}"
            doc = {
                "content": content,
                "source_agent": source_agent,
                "topics": ",".join(topics),
                "embedding": np.array(embedding, dtype=np.float32).tobytes(),
                "metadata": json.dumps(metadata or {})
            }
            
            # Store in Redis
            self.redis_client.hset(doc_id, mapping=doc)
            logger.info(f"Stored vector knowledge: {doc_id}")
            
        except Exception as e:
            logger.error(f"Error storing vector knowledge: {e}")
    
    def semantic_search(self, query: str, top_k: int = 5, 
                       filter_agent: str = None) -> List[VectorSearchResult]:
        """Perform semantic search on stored knowledge"""
        try:
            # Generate query embedding
            query_embedding = self.get_embedding(query)
            
            # Build search query
            search_query = f"*=>[KNN {top_k} @embedding $embedding AS score]"
            query_params = {
                "embedding": np.array(query_embedding, dtype=np.float32).tobytes()
            }
            
            # Add filter if specified
            if filter_agent is not None:
                search_query += f" @source_agent:{{{filter_agent}}}"
            
            # Perform search
            results = self.redis_client.ft(self.index_name).search(
                search_query, query_params=query_params
            )
            
            # Process results
            search_results = []
            for doc in results.docs:
                metadata = json.loads(doc.metadata) if hasattr(doc, 'metadata') else {}
                search_results.append(VectorSearchResult(
                    content=doc.content,
                    source_agent=doc.source_agent,
                    similarity_score=float(doc.score),
                    metadata=metadata
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def get_similar_knowledge(self, content: str, top_k: int = 3) -> List[VectorSearchResult]:
        """Find similar knowledge based on content"""
        return self.semantic_search(content, top_k=top_k)
    
    def update_knowledge_embedding(self, content: str, source_agent: str):
        """Update embedding for existing knowledge"""
        try:
            doc_id = f"knowledge:{source_agent}:{hash(content)}"
            if self.redis_client.exists(doc_id):
                embedding = self.get_embedding(content)
                self.redis_client.hset(doc_id, "embedding", 
                                     np.array(embedding, dtype=np.float32).tobytes())
                logger.info(f"Updated embedding for: {doc_id}")
        except Exception as e:
            logger.error(f"Error updating embedding: {e}")
    
    def delete_knowledge(self, content: str, source_agent: str):
        """Delete knowledge from vector store"""
        try:
            doc_id = f"knowledge:{source_agent}:{hash(content)}"
            self.redis_client.delete(doc_id)
            logger.info(f"Deleted knowledge: {doc_id}")
        except Exception as e:
            logger.error(f"Error deleting knowledge: {e}") 
