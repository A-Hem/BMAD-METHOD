from .knowledge_manager import SubConsciousKnowledgeManager
from .context_analyzer import ContextAnalyzer
import logging

logger = logging.getLogger(__name__)

class ContextInjector:
    """Injects relevant context into agent prompts"""

    def __init__(self, knowledge_manager: SubConsciousKnowledgeManager, context_analyzer: ContextAnalyzer):
        self.knowledge_manager = knowledge_manager
        self.context_analyzer = context_analyzer

    def build_enhanced_template_data(self, user_query: str, agent_name: str, max_context_items: int = 5) -> dict:
        analysis = self.context_analyzer.analyze_context(user_query)
        relevant_knowledge = self.knowledge_manager.retrieve_relevant_knowledge(
            query_topics=analysis.get('topics', []),
            exclude_agent=agent_name,
            limit=max_context_items
        )
        
        context_section = ""
        if relevant_knowledge:
            context_pieces = []
            for item in relevant_knowledge:
                context_pieces.append(f"- From {item.source_agent} (Confidence: {item.confidence:.2f}): {item.content}")
            context_section = "\n".join(context_pieces)

        return {
            "SharedKnowledge": context_section,
            "Prompt": user_query
        }

    def learn_from_response(self, agent_name: str, user_query: str, agent_response: str, feedback_score: float = None):
        analysis = self.context_analyzer.analyze_context(
            f"Query: {user_query}\nResponse: {agent_response}"
        )
        
        confidence = float(analysis.get('confidence', 0.5))
        if confidence > 0.7 and analysis.get('insights'):
            for insight in analysis['insights']:
                self.knowledge_manager.store_knowledge(
                    content=insight,
                    source_agent=agent_name,
                    topic_tags=analysis.get('topics', []),
                    relevance_score=confidence,
                    confidence=confidence
                )
                logger.info(f"Agent {agent_name} learned new insight: {insight}")
