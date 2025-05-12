import time
from agno.workflow import Workflow, RunResponse, RunEvent
from agno.agent import Agent
from textwrap import dedent
from typing import Generator
import subprocess
import json
import sys
import os

from auto_sns_agent.agents.orchestrator import get_orchestrator_agent
from auto_sns_agent.agents.content_generator import get_content_generator_agent

# Length of the prefix added by the posting tool (e.g., "[AutoPostingTest] " is 18 chars)
POSTING_PREFIX_LENGTH = 18
TWITTER_CHAR_LIMIT = 280
# Max length for the content itself, to ensure (content + prefix) < TWITTER_CHAR_LIMIT
# So, len(content) <= TWITTER_CHAR_LIMIT - 1 - POSTING_PREFIX_LENGTH
MAX_CONTENT_LENGTH_FOR_TWITTER_POST = TWITTER_CHAR_LIMIT - 1 - POSTING_PREFIX_LENGTH # 279 - 18 = 261

class ContentCreationWorkflow(Workflow):
    """Workflow to research a topic and generate a draft social media post."""

    description: str = dedent("""
        Orchestrates research on a given topic and then generates a draft social media post
        based on that research.
    """)

    orchestrator_agent: Agent
    content_generator_agent: Agent
    user_provided_confirmation: str | None = None # Attribute to store user's decision

    def __init__(self, **data):
        super().__init__(**data)
        self.orchestrator_agent = get_orchestrator_agent()
        self.content_generator_agent = get_content_generator_agent()

    def run(self, topic: str, platform: str = "Twitter", research_depth: int = 3) -> Generator[RunResponse, str, RunResponse]:
        """
        Args:
            topic (str): The topic to research and generate a post about.
            platform (str): The social media platform to target for research (default: "Twitter").
            research_depth (int): The number of posts to retrieve during research (default: 3).
        """
        print(f"Workflow starting for topic: {topic} on {platform} with research depth: {research_depth}")

        # Original logic (simplified path has been removed)
        # Step 1: Research the topic using the OrchestratorAgent
        # We'll construct a prompt for the orchestrator similar to how a user might ask.
        # The orchestrator's tools should handle the actual research (e.g., get_social_media_posts_for_topic)
        research_prompt = (
            f"Please research the topic '{topic}' on {platform}. "
            f"Focus on approximately {research_depth} key posts or pieces of information. "
            f"Provide a concise summary of the findings, highlighting key discussion points, sentiment, and any actionable insights suitable for creating a new social media post."
        )
        print(f"Running OrchestratorAgent with prompt: {research_prompt}")
        orchestrator_response = self.orchestrator_agent.run(research_prompt)

        if not orchestrator_response or not orchestrator_response.content:
            yield RunResponse(
                content=f"Failed to get research from OrchestratorAgent for topic: {topic}", 
                event=RunEvent.workflow_completed  # Workflow completed, but with an error message in content
            )
            return
        
        research_summary = orchestrator_response.content
        print(f"OrchestratorAgent research summary: {research_summary[:500]}...") # Print a snippet

        # Step 2: Generate content using the ContentGeneratorAgent
        # The generator agent is tool-less and takes the research summary as input.
        # Add platform-specific constraints to the prompt
        character_limit_instruction = ""
        if platform.lower() in ["twitter", "x", "x.com"]:
            character_limit_instruction = "IMPORTANT: The post must be strictly less than 280 characters in total, including hashtags, to comply with X.com/Twitter's character limit. "
        
        generation_prompt = (
            f"You are a helpful and creative social media assistant. Based on the following research summary, "
            f"draft a concise, engaging, and informative social media post for {platform} about '{topic}'. "
            f"{character_limit_instruction}"
            f"The post should be original and capture the essence of the research. "
            f"Please include 2-3 relevant hashtags. "
            f"Research Summary:\n---\n{research_summary}\n---"
        )
        print(f"Running ContentGeneratorAgent with prompt based on research.")
        generator_response = self.content_generator_agent.run(generation_prompt)

        if not generator_response or not generator_response.content:
            yield RunResponse(
                content=f"Failed to generate content from ContentGeneratorAgent for topic: {topic}",
                event=RunEvent.workflow_completed  # Workflow completed, but with an error message in content
            )
            return

        draft_post = generator_response.content
        print(f"ContentGeneratorAgent draft post: {draft_post}")
        
        # Add character limit validation for Twitter/X posts
        if platform.lower() in ["twitter", "x", "x.com"]:
            if len(draft_post) > MAX_CONTENT_LENGTH_FOR_TWITTER_POST:
                print(f"Warning: Generated post (length {len(draft_post)}) exceeds effective Twitter limit of {MAX_CONTENT_LENGTH_FOR_TWITTER_POST} (to allow for prefix). Truncating...")
                # Truncate the post to fit within Twitter's character limit while preserving hashtags
                if "#" in draft_post:
                    hashtag_position = draft_post.rfind("#") # Find last hashtag to keep more text
                    # Ensure hashtags are at the end or reasonably close
                    if len(draft_post) - hashtag_position < 80: # Heuristic: hashtags are likely at the end
                        hashtags = draft_post[hashtag_position:]
                        main_text = draft_post[:hashtag_position].strip()
                        # Calculate available space for main text, aiming for MAX_CONTENT_LENGTH_FOR_TWITTER_POST
                        # Ellipsis takes 3 chars, space before hashtags takes 1.
                        available_space = MAX_CONTENT_LENGTH_FOR_TWITTER_POST - len(hashtags) - 4 
                        if available_space > 20:  # Ensure we have reasonable space for main text
                            draft_post = main_text[:available_space] + "... " + hashtags
                        else:
                            # Not enough space for both; prioritize main content with minimal hashtags, truncate harder
                            draft_post = draft_post[:(MAX_CONTENT_LENGTH_FOR_TWITTER_POST - 3)] + "..."
                    else: # Hashtags are too early, simple truncation
                         draft_post = draft_post[:(MAX_CONTENT_LENGTH_FOR_TWITTER_POST - 3)] + "..."
                else:
                    # No hashtags, simply truncate with ellipsis
                    draft_post = draft_post[:(MAX_CONTENT_LENGTH_FOR_TWITTER_POST - 3)] + "..."
                
                # Ensure it doesn't exceed by any chance after manipulations
                if len(draft_post) > MAX_CONTENT_LENGTH_FOR_TWITTER_POST:
                    draft_post = draft_post[:MAX_CONTENT_LENGTH_FOR_TWITTER_POST]

                print(f"Post truncated. New content length: {len(draft_post)} characters")
                print(f"Truncated post: {draft_post}")

        # Step 3: Ask for user confirmation and get their response
        # Update confirmation prompt to show character count for Twitter/X posts
        confirmation_prompt_content = (
            f"Draft post generated for '{topic}' on {platform}:\n\n"
            f"---S\n{draft_post}\n---S\n\n"
        )
        
        if platform.lower() in ["twitter", "x", "x.com"]:
            final_post_length_with_prefix = len(draft_post) + POSTING_PREFIX_LENGTH
            confirmation_prompt_content += f"Character count (including prefix): {final_post_length_with_prefix}/{TWITTER_CHAR_LIMIT}\n\n"
            
        confirmation_prompt_content += f"Do you want to post this to {platform}? (yes/no)"
        
        print("Workflow: About to yield for user confirmation...")
        # The yield expression itself will evaluate to what is .send() into the generator
        user_confirmation_content: str = yield RunResponse(content=confirmation_prompt_content, event=RunEvent.run_response)
        print(f"Workflow: Resumed. Value of self.user_provided_confirmation: '{self.user_provided_confirmation}'")
        
        if not self.user_provided_confirmation or self.user_provided_confirmation.lower() != "yes":
            print(f"Workflow: User confirmation is not 'yes' (got: {self.user_provided_confirmation}). Cancelling posting.")
            self.user_provided_confirmation = None # Reset after use
            yield RunResponse(
                content="Posting cancelled by user.", 
                event=RunEvent.workflow_completed
            )
            return

        print(f"Workflow: User confirmed 'yes' via self.user_provided_confirmation. Proceeding to post.")
        self.user_provided_confirmation = None # Reset after use
        
        # Add a delay before posting to allow browser resources to clean up
        print("Workflow: Pausing for 3 seconds before posting attempt...")
        time.sleep(3)  # Short pause before subprocess call
        
        # Create a temporary script to perform the posting in a separate process
        print("Workflow: Starting posting in separate process...")
        temp_script_path = "temp_posting_script.py"
        with open(temp_script_path, "w") as f:
            f.write("""
import sys
import json
import asyncio
from auto_sns_agent.tools.social_media_tools import post_to_social_media

def main():
    try:
        # Get arguments from command line
        post_content = sys.argv[1]
        platform = sys.argv[2]
        
        # Clear marker to separate logs from actual result
        print("==LOGS_START==") # Everything before this will be ignored for JSON parsing
        
        # Call the posting function using entrypoint - the proper way to call a tool
        result = post_to_social_media.entrypoint(
            content=post_content,
            platform=platform
        )
        
        # Output a clear separator to identify where logs end and result begins
        print("==LOGS_END==")
        
        # Return result as JSON to stdout
        print(json.dumps({"success": True, "result": result}))
        return 0
    except Exception as e:
        # Output a clear separator
        print("==LOGS_END==")
        # Return error as JSON to stdout 
        print(json.dumps({"success": False, "error": str(e)}))
        return 1

if __name__ == "__main__":
    sys.exit(main())
""")
        
        # Run the temporary script in a separate process
        final_post_content = draft_post  # No need for [AutoPostingTest] here since it's added in social_media_tools.py
        try:
            print(f"Running posting in separate process: {sys.executable} {temp_script_path} '{final_post_content}' {platform}")
            
            # Use subprocess.check_output to capture the output from the script
            result = subprocess.check_output(
                [sys.executable, temp_script_path, final_post_content, platform],
                text=True,
                env=dict(os.environ, PYTHONPATH="src")  # Ensure PYTHONPATH includes src
            )
            
            # Parse the JSON result
            try:
                # Look for the JSON output after ==LOGS_END==
                if "==LOGS_END==" in result:
                    json_str = result.split("==LOGS_END==")[-1].strip()
                    parsed_result = json.loads(json_str)
                    if parsed_result["success"]:
                        post_result = parsed_result["result"]
                    else:
                        post_result = f"Error in posting subprocess: {parsed_result.get('error', 'Unknown error')}"
                else:
                    post_result = f"Failed to parse result: separator '==LOGS_END==' not found in output. Raw output: {result[:300]}..."
            except json.JSONDecodeError:
                post_result = f"Failed to parse JSON from subprocess output. Raw output after separator: {result.split('==LOGS_END==')[-1][:300] if '==LOGS_END==' in result else 'No separator found'}"
                
            print(f"Posting subprocess completed with result: {post_result}")
        except subprocess.CalledProcessError as e:
            post_result = f"Subprocess error (exit code {e.returncode}): {e.output}"
        except Exception as e:
            post_result = f"Error running posting subprocess: {str(e)}"
        finally:
            # Clean up the temporary script
            try:
                os.remove(temp_script_path)
                print(f"Removed temporary script {temp_script_path}")
            except:
                print(f"Failed to remove temporary script {temp_script_path}")
        
        # Assume post_result contains the outcome message (URL or error)
        yield RunResponse(
            content=f"Posting attempt result: {post_result}",
            event=RunEvent.workflow_completed
        )
        return

if __name__ == '__main__':
    import asyncio
    # Ensure an event loop is available for any async operations within agents/tools
    try:
        asyncio.get_running_loop()
    except RuntimeError:  # No event loop running
        asyncio.set_event_loop(asyncio.new_event_loop())

    print("Testing ContentCreationWorkflow directly...")
    workflow = ContentCreationWorkflow()
    
    # Example topic
    test_topic = "benefits of remote work"
    print(f"Running workflow for topic: '{test_topic}'")
    
    # Note: This direct run will use live API calls for OpenAI and BrowserUse (X.com)
    # Ensure .env is set up with OPENAI_API_KEY, X_USERNAME, X_PASSWORD
    response = workflow.run(topic=test_topic, platform="Twitter", research_depth=2)
    
    print("\nWorkflow Output:")
    # Handle potential generator output
    if isinstance(response, RunResponse): # Should not happen now, run is always a generator
        print(f"Event: {response.event}")
        print(f"Content: {response.content}")
    else: # It's a generator
        flow_generator = response
        last_response = None
        user_input_for_send = None
        try:
            while True:
                if user_input_for_send is None:
                    current_yielded_response = next(flow_generator)
                else:
                    current_yielded_response = flow_generator.send(user_input_for_send)
                
                last_response = current_yielded_response
                user_input_for_send = None # Reset for next iteration

                print(f"Event: {current_yielded_response.event}")
                print(f"Content: {current_yielded_response.content}")

                if current_yielded_response.event == RunEvent.run_response: # Check for human input needed event
                    user_input_for_send = input("Your response (yes/no): ")
                    print(f"Workflow preparing to send: {user_input_for_send}") # For debugging
                elif current_yielded_response.event == RunEvent.workflow_completed:
                    print("Workflow signaled completion via yield.")
                    break # Exit while loop
        except StopIteration:
            print("Workflow ended (StopIteration).")
            if last_response:
                 print(f"Last yielded event: {last_response.event}")
                 print(f"Last yielded content: {last_response.content}")
            # No e.value to check here since we are yielding final responses 