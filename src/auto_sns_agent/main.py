import asyncio
from auto_sns_agent.agents.orchestrator import get_orchestrator_agent
from auto_sns_agent.config import OPENAI_API_KEY # To check if API key is loaded

def run_chat_loop():
    """Runs a chat loop to interact with the OrchestratorAgent."""
    print("Initializing Social Media Creation Agent (Orchestrator)...")
    
    if not OPENAI_API_KEY:
        print("\nERROR: OPENAI_API_KEY is not set. Please ensure it's in your .env file and accessible.")
        print("The agent cannot function without the API key.")
        return

    orchestrator = get_orchestrator_agent()
    print("Orchestrator Agent is ready. Type your requests or 'quit' to exit.")
    print("Example prompts:")
    print("  - \"What are people saying on Twitter about #opensource AI?\"")
    print("  - \"Get the main content from https://blog.agno.com/ and tell me about it.\"")
    print("  - \"Based on current discussions on Twitter about 'sustainable fashion', give me a concept for a post.\"")
    print("-" * 30)

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                print("Exiting agent interaction.")
                break
            if not user_input.strip():
                continue

            print("\nAgent thinking...")
            # For Agno agents, agent.run() is synchronous by default if the underlying model/tools are.
            # If you had async tools that weren't run with asyncio.run() inside,
            # you might need to handle agent.run() in an async context.
            # Our current browser tools use asyncio.run() internally, so this should be fine.
            response = orchestrator.run(user_input)
            
            print("\nOrchestrator:")
            if hasattr(response, 'content') and response.content:
                # The response.content should be markdown if markdown=True was set for the agent
                print(response.content)
            else:
                print("No textual content in response or response format unexpected.")
            
            # If you want to see tool calls (if show_tool_calls=True on agent):
            # Agno usually prints these to stdout during the run if they occur.
            # If response object has tool_calls attribute:
            # if hasattr(response, 'tool_calls') and response.tool_calls:
            #     print("\n--- Tool Calls Made ---")
            #     for tc in response.tool_calls:
            #         print(f"Tool: {tc.tool_name}, Input: {tc.tool_input}, Output: {tc.tool_output}")
            # else:
            #     print("(No direct tool calls reported in final response object)")

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