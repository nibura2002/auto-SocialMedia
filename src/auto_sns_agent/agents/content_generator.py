from agno.agent import Agent
from agno.models.openai import OpenAIChat

from auto_sns_agent.config import OPENAI_API_KEY

def get_content_generator_agent() -> Agent:
    """
    Initializes and returns the Content Generator agent.
    This agent takes text input and generates a short social media post.
    """
    llm = OpenAIChat(api_key=OPENAI_API_KEY, id="gpt-4o-mini") # Using gpt-4o-mini for cost/speed
    
    agent = Agent(
        model=llm,
        tools=[], # No tools for this agent initially
        description="An AI agent that generates creative social media content from input text.",
        instructions=[
            "You are a creative assistant specializing in social media content.",
            "Given an input text (like a main heading or a summary of an article), generate a short, engaging social media post (e.g., for Twitter/X or LinkedIn).",
            "The post should be concise, attention-grabbing, and relevant to the input text.",
            "Include 1-3 relevant hashtags.",
            "Do not make up external URLs or facts not present in the input text.",
        ],
        show_tool_calls=False, # Not using tools yet
        markdown=True,
    )
    return agent

if __name__ == '__main__':
    # Example usage for direct testing of this module
    print("Testing ContentGeneratorAgent directly...")
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY not found. Exiting.")
        exit(1)

    generator_agent = get_content_generator_agent()
    sample_input_text = "First H1 text from https://docs.agno.com: The text content of the first <h1> element found is: 'What is Agno'."
    
    print(f"\nSending to ContentGeneratorAgent:\n'''{sample_input_text}'''")
    response = generator_agent.run(sample_input_text)
    
    if response and response.content:
        print("\nContentGeneratorAgent Output:")
        print(response.content)
    else:
        print("No response or content from ContentGeneratorAgent.") 