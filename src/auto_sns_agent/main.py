import asyncio
from auto_sns_agent.agents.orchestrator import get_orchestrator_agent
from auto_sns_agent.config import OPENAI_API_KEY # To check if API key is loaded
from auto_sns_agent.workflows.content_creation_workflow import ContentCreationWorkflow

# Global instance of the workflow, initialized once.
# This is okay for a CLI tool; for other contexts, you might manage lifetime differently.
_content_creation_workflow = None

def get_content_creation_workflow():
    global _content_creation_workflow
    if _content_creation_workflow is None:
        _content_creation_workflow = ContentCreationWorkflow()
    return _content_creation_workflow

def run_chat_loop():
    """Runs a chat loop to interact with the OrchestratorAgent or ContentCreationWorkflow."""
    print("Initializing Social Media Creation Agent...")
    
    if not OPENAI_API_KEY:
        print("\nERROR: OPENAI_API_KEY is not set. Please ensure it's in your .env file and accessible.")
        print("The agent cannot function without the API key.")
        return

    orchestrator = get_orchestrator_agent() # Still have direct access if needed or for non-workflow tasks
    # Workflow will be initialized when first needed by get_content_creation_workflow()
    
    print("Agent & Workflow system is ready. Type your requests or 'quit' to exit.")
    print("Example prompts:")
    print("  - \"What are people saying on Twitter about #opensource AI?\" (Uses Orchestrator Agent)")
    print("  - \"create post about: benefits of dark mode for productivity\" (Uses Content Creation Workflow)")
    print("  - \"Get the main content from https://blog.agno.com/ and tell me about it.\" (Uses Orchestrator Agent)")
    print("-" * 30)

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                print("Exiting agent interaction.")
                break
            if not user_input.strip():
                continue

            print("\nSystem thinking...")
            
            response_content = "No response generated."
            response_source = "System"

            create_post_command = "create post about:"
            if user_input.lower().startswith(create_post_command):
                topic = user_input[len(create_post_command):].strip()
                if topic:
                    print(f"Initiating Content Creation Workflow for topic: '{topic}'")
                    workflow = get_content_creation_workflow()
                    # You might want to specify platform and research_depth or parse from user_input too
                    workflow_response = workflow.run(topic=topic, platform="Twitter", research_depth=2)
                    response_content = workflow_response.content
                    response_source = "Content Creation Workflow"
                else:
                    response_content = "Please specify a topic after 'create post about:'"
            else:
                # Default to OrchestratorAgent for other queries
                orchestrator_response = orchestrator.run(user_input)
                if hasattr(orchestrator_response, 'content') and orchestrator_response.content:
                    response_content = orchestrator_response.content
                response_source = "Orchestrator Agent"
            
            print(f"\n{response_source}:")
            print(response_content)
            
            print("\n" + "-" * 30)

        except Exception as e:
            print(f"An error occurred: {e}")
            # Optionally, decide if you want to break the loop on error
            # break
        except KeyboardInterrupt:
            print("\nExiting agent interaction due to KeyboardInterrupt.")
            break

def main():
    # Ensure an event loop is available if any part of Agno or its tools
    # (even if run synchronously via asyncio.run) needs it.
    # For simple synchronous `agent.run()` where tools manage their own async,
    # this might not be strictly necessary, but it's safer.
    try:
        asyncio.get_running_loop()
    except RuntimeError:  # No event loop running
        asyncio.set_event_loop(asyncio.new_event_loop())
    
    run_chat_loop()

if __name__ == "__main__":
    main() 