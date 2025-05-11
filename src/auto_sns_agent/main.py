import asyncio
from auto_sns_agent.agents.orchestrator import get_orchestrator_agent
from auto_sns_agent.config import OPENAI_API_KEY # To check if API key is loaded
from auto_sns_agent.workflows.content_creation_workflow import ContentCreationWorkflow

from agno.workflow import RunEvent # Removed UserInput import attempt

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
                    
                    # Workflow can now be a generator due to human_intervention_required
                    flow_generator = workflow.run(topic=topic, platform="Twitter", research_depth=2)
                    
                    last_response = None
                    user_input_for_send = None
                    try:
                        while True:
                            if user_input_for_send is None:
                                current_yielded_response = next(flow_generator)
                            else:
                                # Before sending, if the workflow is expecting a confirmation, set it.
                                # We infer this by checking the content of the last yielded response.
                                if last_response and last_response.event == RunEvent.run_response and \
                                   ("Do you want to post this to" in last_response.content or \
                                    "Do you want to post this to {platform}? (yes/no)" in last_response.content): # Check both old and new prompt format
                                    print(f"MAIN: Setting workflow.user_provided_confirmation = '{user_input_for_send}'")
                                    workflow.user_provided_confirmation = user_input_for_send
                                
                                current_yielded_response = flow_generator.send(user_input_for_send)
                            
                            last_response = current_yielded_response
                            user_input_for_send = None # Reset for next iteration

                            if current_yielded_response.event == RunEvent.run_response: # Your event for human input
                                print(f"\nWorkflow requires input:")
                                print(current_yielded_response.content) 
                                user_input_for_send = input("Your response: ")
                                print("\nSystem thinking after human input...")
                            elif current_yielded_response.event == RunEvent.workflow_completed:
                                response_content = current_yielded_response.content
                                response_source = "Content Creation Workflow (Completed via Yield)"
                                break # Exit the while loop, workflow is done
                            else:
                                # Handle other intermediate events if necessary or treat as final if loop breaks
                                response_content = f"Workflow intermediate: {current_yielded_response.content}"
                                response_source = f"Content Creation Workflow ({current_yielded_response.event})"
                                # Potentially break or continue depending on how other events should be handled

                    except StopIteration:
                        response_source = "Content Creation Workflow (Finished)"
                        if last_response and last_response.event == RunEvent.workflow_completed:
                            response_content = last_response.content
                        elif last_response: # Some other state was the last thing yielded
                            response_content = f"Workflow ended after: {last_response.content}"
                        else:
                            response_content = "Workflow completed with no specific final content."
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