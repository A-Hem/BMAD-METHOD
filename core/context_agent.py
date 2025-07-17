import json
# ... other imports

def context_manager_agent():
    # ... (setup code for redis connection and pubsub) ...
    print("🚀 Context Agent started. Listening for updates...")

    # Load initial context from Redis
    shared_context = r.get('shared_context')
    shared_context = json.loads(shared_context) if shared_context else {}

    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            try:
                # Standardized message from an agent
                agent_message = json.loads(message['data'])
                agent_name = agent_message.get('agent_name')
                agent_payload = agent_message.get('payload', {})
                
                print(f"✅ Received update from '{agent_name}' agent.")

                # =============================================================
                # ▼▼▼ YOUR LOGIC GOES HERE ▼▼▼
                # =============================================================
                # Adapt the logic from your original context_manager.py file
                # to modify the `shared_context` dictionary.

                # Example:
                if agent_name == 'proposer' and agent_payload.get('status') == 'success':
                    plan = agent_payload.get('payload', {})
                    shared_context['project_summary'] = plan.get('summary')
                    shared_context['tasks'] = plan.get('proposed_plan', [])
                    shared_context['completed_tasks'] = [] # Reset completed tasks on new plan

                if agent_name == 'implementer' and agent_payload.get('status') == 'success':
                    impl = agent_payload.get('payload', {})
                    file_path = impl.get('file_path')
                    code = impl.get('code')
                    task_completed = impl.get('task_completed')
                    if file_path and code:
                        shared_context['code_files'][file_path] = code
                    if task_completed and task_completed not in shared_context.get('completed_tasks', []):
                        shared_context['completed_tasks'].append(task_completed)
                
                # =============================================================
                # ▲▲▲ END OF YOUR LOGIC ▲▲▲
                # =============================================================

                # Save and publish the newly updated context
                r.set('shared_context', json.dumps(shared_context))
                r.publish('global:context:update', json.dumps(shared_context))
                print("   New context published to 'global:context:update'.")

            except Exception as e:
                print(f"⚠️ Error processing message: {e}")

if __name__ == '__main__':
    context_manager_agent()
