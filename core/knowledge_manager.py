import redis
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ContextItem:
    """Represents a piece of contextual knowledge"""
    id: str
    content: str
    source_agent: str
    timestamp: float
    relevance_score: float
    topic_tags: List[str]
    usage_count: int = 0
    last_accessed: float = 0.0
    confidence: float = 1.0

class SubConsciousKnowledgeManager:
    """Manages shared knowledge base in Redis"""
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        self.knowledge_prefix = "subconscious:knowledge:"
        self.topic_index_prefix = "subconscious:topics:"
        self.agent_index_prefix = "subconscious:agents:"
        self.stats_prefix = "subconscious:stats:"

    def store_knowledge(self, content: str, source_agent: str, topic_tags: List[str], 
                       relevance_score: float = 1.0, confidence: float = 1.0) -> str:
        knowledge_id = hashlib.md5(f"{content}_{source_agent}_{time.time()}".encode()).hexdigest()
        
        context_item = ContextItem(
            id=knowledge_id,
            content=content,
            source_agent=source_agent,
            timestamp=time.time(),
            relevance_score=relevance_score,
            topic_tags=topic_tags,
            confidence=confidence
        )
        
        item_dict = asdict(context_item)
        item_dict['topic_tags'] = json.dumps(item_dict['topic_tags'])

        self.redis_client.hset(f"{self.knowledge_prefix}{knowledge_id}", mapping=item_dict)
        
        for topic in topic_tags:
            self.redis_client.sadd(f"{self.topic_index_prefix}{topic}", knowledge_id)
        
        self.redis_client.sadd(f"{self.agent_index_prefix}{source_agent}", knowledge_id)
        
        self.redis_client.hincrby(f"{self.stats_prefix}global", "total_knowledge", 1)
        self.redis_client.hincrby(f"{self.stats_prefix}agent:{source_agent}", "contributions", 1)
        
        logger.info(f"Stored knowledge {knowledge_id} from {source_agent} with topics {topic_tags}")
        return knowledge_id

    def retrieve_relevant_knowledge(self, query_topics: List[str], 
                                  exclude_agent: str = None, 
                                  limit: int = 10) -> List[ContextItem]:
        candidate_ids = set()
        
        for topic in query_topics:
            topic_ids = self.redis_client.smembers(f"{self.topic_index_prefix}{topic}")
            candidate_ids.update(topic_ids)
        
        if exclude_agent:
            agent_ids = self.redis_client.smembers(f"{self.agent_index_prefix}{exclude_agent}")
            candidate_ids -= agent_ids
        
        knowledge_items = []
        for knowledge_id in list(candidate_ids):
            item_data = self.redis_client.hgetall(f"{self.knowledge_prefix}{knowledge_id}")
            if item_data:
                item_data['timestamp'] = float(item_data['timestamp'])
                item_data['relevance_score'] = float(item_data['relevance_score'])
                item_data['usage_count'] = int(item_data['usage_count'])
                item_data['last_accessed'] = float(item_data['last_accessed'])
                item_data['confidence'] = float(item_data['confidence'])
                item_data['topic_tags'] = json.loads(item_data['topic_tags'])
                knowledge_items.append(ContextItem(**item_data))
        
        knowledge_items.sort(key=lambda x: (x.relevance_score, x.timestamp), reverse=True)
        
        for item in knowledge_items[:limit]:
            self.redis_client.hincrby(f"{self.knowledge_prefix}{item.id}", "usage_count", 1)
            self.redis_client.hset(f"{self.knowledge_prefix}{item.id}", "last_accessed", time.time())
        
        return knowledge_items[:limit]
