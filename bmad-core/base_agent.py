import json
from .redis_client import RedisClient

class BaseAgent:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.redis_conn = RedisClient().get_connection()
        print(f"✅ {self.agent_name.title()} Agent: Online")

    def publish(self, payload):
        """
        Publishes a standardized message to this agent's output channel.
        """
        channel = f"agent:{self.agent_name}:output"
        message = {
            "agent_name": self.agent_name,
            "payload": payload
        }
        self.redis_conn.publish(channel, json.dumps(message))
        print(f"🚀 {self.agent_name.title()} Agent: Published update to {channel}")

