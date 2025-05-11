import asyncio
from typing import Dict, Any # Removed Type as it wasn't used

from browser_use import Agent as BrowserUseAgent
from langchain_openai import ChatOpenAI
from agno.tools import tool # Import the decorator

from auto_sns_agent.config import OPENAI_API_KEY

# Initialize the LLM for BrowserUseAgent (as per browser-use documentation)
# This LLM is used by BrowserUseAgent internally to understand tasks.
browser_use_llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)

async def _get_webpage_main_content_async(url: str) -> str:
    """(Async) Uses BrowserUseAgent to navigate to a URL and get its main textual content."""
    try:
        # This prompt asks for main content, trying to avoid boilerplate.
        # Effectiveness will depend on BrowserUseAgent's interpretation and the website structure.
        task_prompt = (
            f"Go to {url}. Extract the main textual content of the article or page. "
            f"Focus on the primary body of text, and try to exclude headers, footers, navigation menus, sidebars, and advertisements. "
            f"Return the extracted clean text."
        )
        agent = BrowserUseAgent(
            task=task_prompt,
            llm=browser_use_llm,
        )
        bua_result_history = await agent.run()
        final_text_result = bua_result_history.final_result() if hasattr(bua_result_history, 'final_result') else str(bua_result_history)
        
        # Return a more descriptive success message including the URL for clarity
        return f"Successfully extracted main content from {url}:\n{final_text_result}" if final_text_result else f"No main content extracted or found at {url}"
    except Exception as e:
        return f"Error extracting main content from {url}: {str(e)}"

@tool(show_result=True) # Add the Agno tool decorator with show_result=True
def get_webpage_main_content(url: str) -> str:
    """ 
    Navigates to a specified URL using BrowserUseAgent and returns the main textual content 
    of the page, attempting to exclude boilerplate like headers, footers, and ads.
    Use this tool to get the substance of an article or blog post.

    Args:
        url (str): The URL to navigate to and extract content from.
    """
    print(f"Tool 'get_webpage_main_content' called with URL: {url}")
    return asyncio.run(_get_webpage_main_content_async(url=url))

# For direct testing of this module
if __name__ == '__main__':
    # This section is for direct testing of this module
    # Note: direct execution might have PYTHONPATH issues for imports like auto_sns_agent.config
    # Prefer testing with `PYTHONPATH=src uv run python -m auto_sns_agent.tools.browser_tools`
    
    print("Attempting to run browser_tools.py (get_webpage_main_content) directly...")
    
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY not found. Please set it in .env or environment.")
        exit(1)

    import agno # Keep for version check, though it might not be strictly needed here
    if hasattr(agno, '__version__'):
        print(f"Using Agno version: {agno.__version__}")
    else:
        print("Agno version attribute not found.")

    test_url = "https://blog.agno.com/introducing-agno-llm-developer-platform/" # Example, replace if needed
    # test_url = "https://news.ycombinator.com/item?id=40300667" # For a different structure
    print(f"Attempting to get main content from: {test_url}")
    
    try:
        output = get_webpage_main_content(test_url)
        print("\nTool Output (from get_webpage_main_content):")
        print(output)
    except Exception as e:
        print(f"Error during direct test run: {e}") 