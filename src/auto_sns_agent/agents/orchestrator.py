from agno.agent import Agent
from agno.models.openai import OpenAIChat

from auto_sns_agent.config import OPENAI_API_KEY
from auto_sns_agent.tools.browser_tools import get_webpage_main_content
from auto_sns_agent.tools.social_media_tools import get_social_media_posts_for_topic, post_to_social_media


def get_orchestrator_agent() -> Agent:
    """
    Initializes and returns the orchestrator agent. 
    This agent can research topics on the general web or social media, 
    and then conceptualize content based on that research.
    """
    llm = OpenAIChat(api_key=OPENAI_API_KEY, id="gpt-4o")
    
    tools = [
        get_webpage_main_content,
        get_social_media_posts_for_topic,
        post_to_social_media
    ]

    agent = Agent(
        model=llm,
        tools=tools,
        description=(
            "An AI agent that orchestrates tasks for social media content creation. "
            "It can research topics on the web or social media, and then use that info "
            "to plan content (actual content generation is by other specialized agents/workflows)."
        ),
        instructions=[
            "You are the central orchestrator for a social media automation system.",
            "Your primary goal is to gather information and then plan social media content.",
            "If asked to create content about a topic for social media:",
            "  1. Decide if you need to research general web articles or recent social media posts.",
            "     - Use the 'get_webpage_main_content' tool if you need to understand a topic from a detailed article or blog post.",
            "     - Use the 'get_social_media_posts_for_topic' tool if you need to find existing social media discussions or recent posts on a topic (e.g., on Twitter/X).",
            "  2. After gathering information with the appropriate tool, state what information you found.",
            "  3. Then, based on the gathered information, briefly outline or conceptualize the social media post that should be created.",
            "     (You are not writing the final post yourself; you are providing the gathered info and a concept to a specialist content generator).",
            "If a specific research source (general web vs. social media) is implied by the request, prioritize that.",
            "You also have a tool to post content to social media. If asked to post provided content, use the 'post_to_social_media' tool.",
            "Always clearly state which tool you are using and for what purpose if you decide to use one."
        ],
        show_tool_calls=True,
        markdown=True,
    )
    return agent 