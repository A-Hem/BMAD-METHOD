import ollama
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ContextAnalyzer:
    """Analyzes context and extracts relevant topics and insights"""

    def __init__(self, model_name: str = "llama3.2:3b", 
                 ollama_host: str = "127.0.0.1",
                 ollama_port: int = 11434):
        self.model_name = model_name
        # Create URL for Ollama client
        ollama_url = f"http://{ollama_host}:{ollama_port}"
        self.ollama_client = ollama.Client(host=ollama_url)

    def analyze_context(self, text: str, conversation_history: List[str] = None) -> Dict[str, Any]:
        """Analyze text to extract topics, entities, and insights"""
        
        analysis_prompt = f"""
        Analyze the following text and extract:
        1. Main topics (3-5 key topics as single words or short phrases)
        2. Key entities (people, places, concepts mentioned)
        3. Domain/field (technology, science, business, etc.)
        4. Any actionable insights or patterns
        
        Text to analyze: "{text}"
        
        Return your analysis in this exact JSON format, with no additional text or explanation:
        {{
            "topics": ["topic1", "topic2", "topic3"],
            "entities": ["entity1", "entity2"],
            "domain": "domain_name",
            "insights": ["insight1", "insight2"],
            "confidence": 0.8
        }}
        """
        
        try:
            response = self.ollama_client.generate(
                model=self.model_name,
                prompt=analysis_prompt,
                stream=False
            )
            
            analysis = json.loads(response['response'])
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing context: {e}")
            return {
                "topics": ["general"],
                "entities": [],
                "domain": "general",
                "insights": [],
                "confidence": 0.1
            }
