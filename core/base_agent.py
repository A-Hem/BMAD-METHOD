from .config_manager import ConfigManager
from .vector_manager import VectorManager
from .context_injector import ContextInjector

class BaseAgent:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        
        # Load configuration
        self.config = ConfigManager('config.yml').get_config()
        
        # Initialize core components
        self.vector_manager = VectorManager(
            embedding_model_name=self.config['embedding_model'],
            index_path=self.config['vector_db_path']
        )
        self.context_injector = ContextInjector()
        
        print(f"✅ {self.agent_name.title()} Agent: Online with Vector Memory")

    def think(self, query: str, top_k: int = 3) -> str:
        """
        Retrieves relevant context from the vector DB and prepares it for an LLM prompt.
        """
        print(f"🤔 {self.agent_name.title()} Agent: Thinking about '{query}'...")
        
        # Search for relevant knowledge
        search_results = self.vector_manager.search(query, k=top_k)
        
        if not search_results:
            print("   No relevant context found in memory.")
            return ""
        
        # Use the injector to format the context
        injected_context = self.context_injector.inject(search_results)
        print(f"   Found and injected {len(search_results)} pieces of context.")
        return injected_context

    def learn(self, text: str, metadata: dict = None):
        """
        Learns a new piece of information by adding it to the vector DB.
        """
        print(f"🧠 {self.agent_name.title()} Agent: Learning new information...")
        
        # Add the agent's name to the metadata
        if metadata is None:
            metadata = {}
        metadata['source_agent'] = self.agent_name
        
        self.vector_manager.add(text, metadata=metadata)
        print("   Information successfully stored in vector memory.")

