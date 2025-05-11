from agno.workflow import Workflow, RunResponse, RunEvent
from agno.agent import Agent
from textwrap import dedent

from auto_sns_agent.agents.orchestrator import get_orchestrator_agent
from auto_sns_agent.agents.content_generator import get_content_generator_agent

class ContentCreationWorkflow(Workflow):
    """Workflow to research a topic and generate a draft social media post."""

    description: str = dedent("""
        Orchestrates research on a given topic and then generates a draft social media post
        based on that research.
    """)

    orchestrator_agent: Agent
    content_generator_agent: Agent

    def __init__(self, **data):
        super().__init__(**data)
        self.orchestrator_agent = get_orchestrator_agent()
        self.content_generator_agent = get_content_generator_agent()

    def run(self, topic: str, platform: str = "Twitter", research_depth: int = 3) -> RunResponse:
        """
        Args:
            topic (str): The topic to research and generate a post about.
            platform (str): The social media platform to target for research (default: "Twitter").
            research_depth (int): The number of posts to retrieve during research (default: 3).
        """
        print(f"Workflow starting for topic: {topic} on {platform} with research depth: {research_depth}")

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
            return RunResponse(
                content=f"Failed to get research from OrchestratorAgent for topic: {topic}", 
                event=RunEvent.workflow_completed  # Workflow completed, but with an error message in content
            )
        
        research_summary = orchestrator_response.content
        print(f"OrchestratorAgent research summary: {research_summary[:500]}...") # Print a snippet

        # Step 2: Generate content using the ContentGeneratorAgent
        # The generator agent is tool-less and takes the research summary as input.
        generation_prompt = (
            f"You are a helpful and creative social media assistant. Based on the following research summary, "
            f"draft a concise, engaging, and informative social media post for {platform} about '{topic}'. "
            f"The post should be original and capture the essence of the research. "
            f"Please include 2-3 relevant hashtags. "
            f"Research Summary:\n---\n{research_summary}\n---"
        )
        print(f"Running ContentGeneratorAgent with prompt based on research.")
        generator_response = self.content_generator_agent.run(generation_prompt)

        if not generator_response or not generator_response.content:
            return RunResponse(
                content=f"Failed to generate content from ContentGeneratorAgent for topic: {topic}",
                event=RunEvent.workflow_completed  # Workflow completed, but with an error message in content
            )

        draft_post = generator_response.content
        print(f"ContentGeneratorAgent draft post: {draft_post}")

        return RunResponse(content=draft_post, event=RunEvent.workflow_completed)

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
    print(f"Event: {response.event}")
    print(f"Content: {response.content}") 