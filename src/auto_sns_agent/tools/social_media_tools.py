import asyncio
from typing import List, Dict, Any

from agno.tools import tool
from browser_use import Agent as BrowserUseAgent
from langchain_openai import ChatOpenAI

from auto_sns_agent.config import OPENAI_API_KEY, X_USERNAME, X_PASSWORD

# Consider centralizing this if used by multiple browser tool files
browser_use_llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)

async def _get_social_media_posts_async(topic: str, platform_url: str, count: int, username: str | None, password: str | None) -> str:
    """(Async) Uses BrowserUseAgent to search a platform for posts on a topic and extract text."""
    # This prompt needs to be carefully crafted and tested.
    # It should guide BrowserUseAgent to:
    # 1. Navigate to the platform_url.
    # 2. If login is required and credentials are provided, attempt to log in.
    # 3. Find and use the search bar for the 'topic'.
    # 4. Identify 'count' number of posts (e.g., top, recent).
    # 5. Extract the main text content of each post.
    # 6. Return the texts, ideally in a structured way or clearly delimited.
    
    login_instructions = ""
    if username and password and "x.com" in platform_url: # Specific instructions for X.com
        login_instructions = (
            f"If you encounter a login page, try to log in using the username '{username}' and password '{password}'. "
            f"Look for username/email and password input fields, and a login button. After logging in, proceed with the search. "
            f"If login fails or is not possible, try to proceed without logging in if the site allows. "
        )

    task_prompt = (
        f"Go to {platform_url}. {login_instructions}"
        f"In the search bar, search for content related to the topic: '{topic}'. "
        f"If you cannot find a search bar directly, try to navigate to a state where searching is possible. "
        f"Identify approximately {count} distinct posts from the search results. "
        f"For each of these posts, extract its main textual content. "
        f"Return all extracted post texts as a single string, with each post separated by '---NEXT_POST_DELIMITER---'."
    )
    
    try:
        agent = BrowserUseAgent(
            task=task_prompt,
            llm=browser_use_llm,
            # Might need to adjust viewport, wait times, or other BrowserUseAgent params
        )
        bua_result_history = await agent.run()
        
        # Process bua_result_history to get the desired string
        # final_result() should give the text BrowserUseAgent was instructed to return.
        extracted_posts_str = bua_result_history.final_result() if hasattr(bua_result_history, 'final_result') else str(bua_result_history)
        
        if "---NEXT_POST_DELIMITER---" not in extracted_posts_str and extracted_posts_str:
             # If delimiter is missing but we have content, it might be a single post or an error message from BUA.
             # For now, we'll assume it's a valid (single) extraction if it's not an obvious error pattern.
             # More robust error handling or specific BUA error parsing can be added.
             print(f"Warning: Delimiter '---NEXT_POST_DELIMITER---' not found in BrowserUseAgent output for topic '{topic}'. Output: {extracted_posts_str[:200]}...") # Log a snippet
        
        return extracted_posts_str if extracted_posts_str else f"No posts found or extracted for topic: {topic} on {platform_url}"

    except Exception as e:
        return f"Error searching social media for '{topic}' on '{platform_url}': {str(e)}"

@tool(show_result=True)
def get_social_media_posts_for_topic(topic: str, platform: str = "Twitter", count: int = 3) -> str:
    """
    Searches a social media platform for posts related to a given topic and extracts their text.

    Args:
        topic (str): The topic or keywords to search for.
        platform (str): The social media platform to search (default: "Twitter"). 
                        Currently, only "Twitter" (which navigates to x.com) is explicitly handled.
        count (int): The approximate number of recent posts to try and retrieve.

    Returns:
        str: A string containing the text of the found posts, separated by 
             '---NEXT_POST_DELIMITER---', or an error/status message.
    """
    platform_url_map = {
        "Twitter": "https://x.com"
        # Add other platforms here if needed, e.g., "Reddit": "https://www.reddit.com"
    }
    
    actual_platform_url = platform_url_map.get(platform)
    
    if not actual_platform_url:
        return f"Error: Platform '{platform}' is not supported. Supported platforms: {list(platform_url_map.keys())}"
        
    print(f"Tool 'get_social_media_posts_for_topic' called with: topic='{topic}', platform='{platform}', count={count}, url='{actual_platform_url}'")
    
    # Ensure OPENAI_API_KEY is available (could also be checked at app startup)
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY not found for browser_use_llm."

    return asyncio.run(_get_social_media_posts_async(topic, actual_platform_url, count, X_USERNAME, X_PASSWORD))

if __name__ == '__main__':
    # Example for direct testing
    print("Testing social_media_tools.py directly...")
    test_topic = "AI in healthcare"
    print(f"Attempting to get social media posts for topic: '{test_topic}' from Twitter")
    
    output = get_social_media_posts_for_topic(topic=test_topic, platform="Twitter", count=2)
    
    print("\nTool Output:")
    if output:
        posts = output.split("---NEXT_POST_DELIMITER---")
        for i, post_text in enumerate(posts):
            print(f"Post {i+1}:")
            print(post_text.strip())
            print("-" * 20)
    else:
        print("No output or empty output from tool.") 