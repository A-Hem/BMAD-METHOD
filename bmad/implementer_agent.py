import json
from core.base_agent import BaseAgent

def write_code_for_task(task_description: str) -> dict:
    """
    Placeholder for your core logic to write code.
    Simulates an LLM generating code for a given task.
    """
    print(f"Implementer Agent: Generating code for task -> '{task_description}'")
    # In a real scenario, this would be a complex LLM call
    if "create a file named 'app.py'" in task_description.lower():
        file_path = "app.py"
        code = (
            "import os\n"
            "from flask import Flask\n\n"
            "app = Flask(__name__)\n\n"
            "@app.route('/')\n"
            "def hello_world():\n"
            "    return 'Hello, World!'\n\n"
            "if __name__ == '__main__':\n"
            "    app.run(debug=True)\n"
        )
    else:
        file_path = "unknown_file.py"
        code = "# Code generation failed: Task not understood"

    return {"file_path": file_path, "code": code, "task_completed": task_description}

class ImplementerAgent(BaseAgent):
    """
    The Implementer Agent writes the code for a specific task.
    """
    def __init__(self):
        super().__init__("implementer")

    def run(self, task: str):
        """
        Executes the agent's logic for a single task.
        """
        # 1. Check the collective memory for an existing solution to this task
        # We can use the task description itself to generate query topics
        analysis = self.context_analyzer.analyze_context(task)
        topics = analysis.get("topics", [])
        
        # A more specific topic for code implementation
        query_topics = topics + ["code_implementation", "python"]
        
        existing_knowledge = self.retrieve_knowledge(query_topics=query_topics, limit=3)
        
        for item in existing_knowledge:
            try:
                # The content stored by another implementer should be JSON
                data = json.loads(item.content)
                if data.get("task_completed") == task:
                    print(f"✅ Found existing code for this exact task in memory.")
                    return
            except json.JSONDecodeError:
                continue # Ignore items that aren't valid JSON

        # 2. If no solution exists, generate the code
        print(f"💡 No existing code found for '{task}'. Generating now.")
        implementation_result = write_code_for_task(task)
        
        # 3. Store the new code in the collective memory
        self.store_knowledge(content=json.dumps(implementation_result))
