import json
from core.base_agent import BaseAgent

# This function would use an LLM to review code
def review_code_with_llm(code_to_review: str, task: str, context: str) -> str:
    """Simulates an LLM reviewing code for quality and correctness."""
    print(f"Critic Agent: Reviewing code for task -> '{task}'")

    # In a real scenario, you'd create a detailed prompt
    # full_prompt = f"{context}\n\nReview the following code for the task '{task}'.
    # Check for bugs, style issues, and adherence to best practices.\n\nCode:\n{code_to_review}"
    # llm_response = call_llm(full_prompt)

    # Simulate a review
    review = {
        "score": 8.5,
        "feedback": "The code is functional and correct.",
        "suggestions": [
            "Add comments explaining the purpose of the app and route.",
            "Consider adding a requirements.txt file for dependencies."
        ]
    }
    return json.dumps(review)


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__("critic")

    def run(self, code_json_str: str, task: str):
        """
        Executes the agent's logic: think, act (review), learn.
        """
        # 1. THINK: Retrieve context on coding best practices for the given task
        context = self.think(query=f"coding best practices for {task}", top_k=2)

        # 2. ACT: Review the code using the retrieved context
        review_json_str = review_code_with_llm(code_json_str, task, context)

        # 3. LEARN: Store the review in the vector memory
        self.learn(
            text=review_json_str,
            metadata={"task": task, "type": "code_review"}
        )
        print("✅ Code review complete and stored in memory.")

