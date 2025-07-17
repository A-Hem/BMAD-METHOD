import json
from core.base_agent import BaseAgent

# This function would use an LLM to generate code
def write_code_for_task(task_description: str, context: str) -> str:
    """Simulates an LLM generating code, now with context."""
    print(f"Implementer Agent: Generating code for task -> '{task_description}'")
    
    # In a real scenario, you would combine the task and context into a prompt
    # full_prompt = f"{context}\n\nBased on the context, complete the following task:\n{task_description}"
    # llm_response = call_llm(full_prompt)
    
    code = (
        "from flask import Flask\n\n"
        "app = Flask(__name__)\n\n"
        "@app.route('/')\n"
        "def hello_world():\n"
        "    return 'Hello, World!'\n"
    )
    # The output should be a structured JSON string
    return json.dumps({
        "task_completed": task_description,
        "file_path": "app.py",
        "code": code
    })


class ImplementerAgent(BaseAgent):
    def __init__(self):
        super().__init__("implementer")

    def run(self, task: str):
        """
        Executes the agent's logic: think, act, learn.
        """
        # 1. THINK: Retrieve context relevant to the task
        context = self.think(query=task, top_k=3)
        
        # 2. ACT: Generate the code using the retrieved context
        implementation_json = write_code_for_task(task, context)
        
        # 3. LEARN: Store the newly generated code in the vector memory
        self.learn(
            text=implementation_json,
            metadata={"task": task, "type": "code_implementation"}
        )
