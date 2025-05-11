import asyncio
from typing import List, Dict, Any

from agno.tools import tool
from browser_use import Agent as BrowserUseAgent
from langchain_openai import ChatOpenAI

from auto_sns_agent.config import OPENAI_API_KEY, X_LOGIN_IDENTIFIER, X_PASSWORD

# Consider centralizing this if used by multiple browser tool files
browser_use_llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)

async def _get_social_media_posts_async(topic: str, platform_url: str, count: int, login_identifier: str | None, password: str | None) -> str:
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
    if login_identifier and password and "x.com" in platform_url: # Specific instructions for X.com
        login_instructions = (
            f"If you encounter a login page, try to log in using the identifier '{login_identifier}' and password '{password}'. "
            f"For X.com login, follow these exact steps: "
            f"1. Click the 'ログイン' button on the homepage if present. "
            f"2. On the login form, type '{login_identifier}' in the username/email field. "
            f"3. Click '次へ' (Next) button. "
            f"4. On the password screen, type '{password}' carefully. "
            f"5. Click 'ログイン' button or press Enter to submit. "
            f"6. If login fails the first time, try again following the same steps. "
            f"7. If repeated login attempts fail, try to continue without logging in (search for the topic as a guest). "
            f"8. If the site requests a 2-Factor Authentication (2FA) code, you won't be able to proceed - report this as an error. "
        )

    task_prompt = (
        f"Go to {platform_url}. {login_instructions}"
        f"In the search bar, search for content related to the topic: '{topic}'. "
        f"If you cannot find a search bar directly, try to navigate to a state where searching is possible. "
        f"Identify approximately {count} distinct posts from the search results. "
        f"For each of these posts, extract its main textual content. "
        f"Return all extracted post texts as a single string, with each post separated by '---NEXT_POST_DELIMITER---'."
    )
    
    agent = None  # Define outside try block to access in finally
    
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
    finally:
        # Attempt to explicitly clean up browser resources
        if agent and hasattr(agent, 'controller') and agent.controller:
            try:
                await agent.controller.close_all()
                print(f"Successfully closed browser resources for search operation on {platform_url}")
            except Exception as cleanup_error:
                print(f"Warning: Error during browser cleanup after search: {cleanup_error}")

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

    return asyncio.run(_get_social_media_posts_async(topic, actual_platform_url, count, X_LOGIN_IDENTIFIER, X_PASSWORD))

async def _post_to_social_media_async(content: str, platform_url: str, login_identifier: str | None, password: str | None) -> str:
    """(Async) Uses BrowserUseAgent to post content to a social media platform."""
    
    login_instructions = ""
    if login_identifier and password and "x.com" in platform_url: # Specific instructions for X.com
        login_instructions = (
            f"If you encounter a login page, try to log in using the identifier '{login_identifier}' and password '{password}'. "
            f"For X.com login, follow these exact steps: "
            f"1. Click the 'ログイン' button on the homepage if present. "
            f"2. On the login form, type '{login_identifier}' in the username/email field. "
            f"3. Click '次へ' (Next) button. "
            f"4. On the password screen, type '{password}' carefully. "
            f"5. Click 'ログイン' button or press Enter to submit. "
            f"6. If login fails the first time, try again following the same steps. "
            f"7. If repeated login attempts fail, try to continue without logging in (search for the topic as a guest). "
            f"8. If the site requests a 2-Factor Authentication (2FA) code, you won't be able to proceed - report this as an error. "
        )

    post_content_with_tag = f"[AutoPostingTest] {content}"

    task_prompt = (
        f"Go to {platform_url}. {login_instructions} "
        f"Once logged in (or if already logged in), find the interface to create a new post (e.g., a 'Post', 'Tweet', or '+' button). "
        f"In the main content area for the new post, enter the following text exactly: '{post_content_with_tag}'. "
        f"Then, wait for 2 seconds to ensure the post button becomes enabled after text entry. "
        f"To click the post button, use this exact approach in order: "
        f"1. Try to click the button with data-testid=\"tweetButtonInline\" which contains the text 'ポストする' or 'Post'. "
        f"2. If that doesn't work, try clicking by CSS selector 'button[data-testid=\"tweetButtonInline\"]'. "
        f"3. If that doesn't work, try to find a blue-colored button that says '投稿する', 'ポストする', or contains role='button'. "
        f"4. If the button still appears disabled, try explicitly sending keyboard shortcut Ctrl+Enter (or Command+Enter on Mac). "
        f"5. Finally, try clicking any button-like element that appears enabled after text entry with a blue background. "
        f"Be aware that the post button is initially disabled (has attributes aria-disabled='true' and disabled='') but becomes enabled after text is entered. "
        f"After clicking the post button, wait a few seconds for the page to update. Look for a success notification (e.g., 'Your post was sent', 'Tweet sent'). "
        f"Posting might fail if the text is too long or if the post button is not found. Check if there are any notification or error message. "
        f"Try posting again if you still see the posting modal or posting page unchanged. "
        f"To confirm the post and get its URL: "
        f"1. If a success message with a 'View post' link appears, click it and get the current URL. "
        f"2. If not, try to navigate to your profile page (usually by clicking a 'Profile' link or your avatar/icon). "
        f"3. On your profile page, identify the most recent post you just submitted. "
        f"4. Extract the direct URL of this most recent post. This might involve clicking on the post's timestamp to go to its individual page, or finding a 'share' or 'copy link' option associated with it. "
        f"If you successfully retrieve the post URL, return 'Successfully posted. URL: [retrieved URL]'. "
        f"If you believe the post was successful but cannot retrieve the URL, return 'Posted successfully but could not retrieve URL'. "
        f"If posting fails, describe the reason (e.g., 'Failed to post: Could not find post button', 'Failed to post: Error message encountered: [error message]')."
    )
    
    agent = None  # Define outside try block to access in finally
    
    try:
        agent = BrowserUseAgent(
            task=task_prompt,
            llm=browser_use_llm,
        )
        bua_result_history = await agent.run()
        
        post_result_str = bua_result_history.final_result() if hasattr(bua_result_history, 'final_result') else str(bua_result_history)
        
        return post_result_str if post_result_str else f"No specific confirmation received after attempting to post to {platform_url}."

    except Exception as e:
        return f"Error attempting to post to '{platform_url}': {str(e)}"
    finally:
        # Attempt to explicitly clean up browser resources
        if agent and hasattr(agent, 'controller') and agent.controller:
            try:
                await agent.controller.close_all()
                print(f"Successfully closed browser resources for posting operation on {platform_url}")
            except Exception as cleanup_error:
                print(f"Warning: Error during browser cleanup after posting: {cleanup_error}")

@tool(show_result=True)
def post_to_social_media(content: str, platform: str = "Twitter", login_identifier_override: str | None = None, password_override: str | None = None) -> str:
    """
    Posts the given content to a specified social media platform.
    Prepends "[AutoPostingTest]" to the content before posting.

    Args:
        content (str): The text content to post.
        platform (str): The social media platform to post to (default: "Twitter").
                        Currently, only "Twitter" (which navigates to x.com) is explicitly handled.
        login_identifier_override (str, optional): Override the login identifier from config.
        password_override (str, optional): Override the password from config.

    Returns:
        str: A message indicating the outcome of the posting attempt (e.g., success with URL, or an error).
    """
    platform_url_map = {
        "Twitter": "https://x.com"
        # Add other platforms here if needed
    }
    
    actual_platform_url = platform_url_map.get(platform)
    
    if not actual_platform_url:
        return f"Error: Platform '{platform}' is not supported for posting. Supported platforms: {list(platform_url_map.keys())}"
        
    print(f"Tool 'post_to_social_media' called for platform: '{platform}', url: '{actual_platform_url}'")
    
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY not found for browser_use_llm."
    
    # Check character limits for Twitter
    if platform.lower() in ["twitter", "x", "x.com"]:
        # Account for the "[AutoPostingTest] " prefix (17 chars) that will be added
        effective_length = len(content) + 17
        if effective_length >= 280:
            return f"Error: Content exceeds Twitter's 280 character limit. Current length with prefix: {effective_length} characters. Please shorten your content to less than {280-17} characters."

    # Use overrides if provided, otherwise use resolved values from config
    current_login_identifier = login_identifier_override if login_identifier_override is not None else X_LOGIN_IDENTIFIER
    current_password = password_override if password_override is not None else X_PASSWORD
    
    return asyncio.run(_post_to_social_media_async(content, actual_platform_url, current_login_identifier, current_password))

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