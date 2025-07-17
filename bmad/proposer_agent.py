# Path: BMAD-METHOD/bmad/proposer_agent.py
from core.base_agent import BaseAgent

class ProposerAgent(BaseAgent):
    def __init__(self):
        # Initialize the BaseAgent with the agent's name
        super().__init__("proposer") 

    def run(self, user_prompt):
        # Your logic to generate a plan
        plan_payload = {
            "summary": "Create a web server with a single endpoint.",
            "proposed_plan": ["Create 'main.py'", "Define a Flask server"]
        }
        
        # The publish method is inherited from BaseAgent
        self.publish(plan_payload)
