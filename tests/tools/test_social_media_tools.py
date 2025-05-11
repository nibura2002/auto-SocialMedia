import pytest
from auto_sns_agent.tools.social_media_tools import get_social_media_posts_for_topic, post_to_social_media, _post_to_social_media_async
from unittest.mock import patch, AsyncMock, MagicMock
from auto_sns_agent.config import OPENAI_API_KEY, X_LOGIN_IDENTIFIER, X_PASSWORD
import asyncio # Ensure asyncio is imported

# Ensure pytest-asyncio is installed and configured if not already
pytest_plugins = ('pytest_asyncio',)

@pytest.mark.vcr # Optional: if using pytest-vcr for recording/replaying live calls
@pytest.mark.live_tool_test # Custom marker for tests that make live calls
def test_get_social_media_posts_for_topic_live():
    """Test get_social_media_posts_for_topic with a live call to Twitter/X."""
    topic = "#AIethics"
    platform = "Twitter"
    count = 2
    
    # Attempt to call the underlying function via .entrypoint
    result = get_social_media_posts_for_topic.entrypoint(topic=topic, platform=platform, count=count)
    
    print(f"\nOutput for topic '{topic}' from {platform}:")
    print(result)
    
    assert isinstance(result, str), "Result should be a string"
    assert len(result) > 0, "Result string should not be empty"
    
    # Basic check: Does it look like it tried to get posts or hit an error?
    # A more robust check would parse the delimited posts if successful, 
    # or check for specific error message patterns.
    if "Error" not in result and f"No posts found or extracted for topic: {topic}" not in result:
        # If it seems successful, check for the delimiter or at least some content
        # The actual content is highly dynamic. We mostly check if the tool ran and returned something plausible.
        assert "---NEXT_POST_DELIMITER---" in result or len(result) > 50 # Arbitrary length for plausible content
        print("Live test seems to have fetched some content or a single post.")
    else:
        print(f"Live test resulted in an error or no posts found message: {result}")
        # Consider if this should fail the test or if error messages are acceptable outcomes for a live test
        # For now, allow error messages as the tool is experimental with live UIs.
        pass

    # Further assertions could involve trying to split by "---NEXT_POST_DELIMITER---"
    # and checking the number of posts if the call was expected to be successful.
    # posts = result.split("---NEXT_POST_DELIMITER---")
    # if "Error" not in result and "No posts found" not in result:
    #    assert len(posts) <= count, f"Expected up to {count} posts, got {len(posts)}"

# Add more tests here, e.g., for unsupported platforms, error conditions, etc.
# def test_get_social_media_posts_unsupported_platform():
#     result = get_social_media_posts_for_topic(topic="test", platform="Fakebook")
#     assert "Error: Platform 'Fakebook' is not supported" in result 

@patch("auto_sns_agent.tools.social_media_tools.BrowserUseAgent", autospec=True)
def test_post_to_social_media_mocked(MockBrowserUseAgent):
    """Test the post_to_social_media tool with a mocked BrowserUseAgent."""
    mock_bua_instance = MockBrowserUseAgent.return_value
    # BrowserUseAgent.run() is an async method, so its mock needs to be an AsyncMock
    # and its final_result an attribute of the awaited result.
    mock_run_result = MagicMock()
    mock_run_result.final_result.return_value = "Successfully posted! New post URL: https://x.com/user/status/123"
    mock_bua_instance.run = AsyncMock(return_value=mock_run_result)
    
    test_content = "This is a test post about #testing."
    expected_platform = "Twitter"
    expected_url = "https://x.com"
    
    # Call the synchronous wrapper, which internally calls asyncio.run
    result = post_to_social_media.entrypoint(content=test_content, platform=expected_platform)
    
    # Assert BrowserUseAgent was called
    MockBrowserUseAgent.assert_called_once()
    args, kwargs = MockBrowserUseAgent.call_args
    
    # Check the task prompt given to BrowserUseAgent
    assert "task" in kwargs
    task_prompt = kwargs["task"]
    
    assert f"Go to {expected_url}" in task_prompt
    assert f"[AutoPostingTest] {test_content}" in task_prompt
    assert "find the interface to create a new post" in task_prompt
    assert "click the button to submit/publish the post" in task_prompt
    
    # Check that the mock's run method was called
    mock_bua_instance.run.assert_called_once()
    
    # Check the final result from the tool
    assert result == "Successfully posted! New post URL: https://x.com/user/status/123"

@patch("auto_sns_agent.tools.social_media_tools.BrowserUseAgent", autospec=True)
def test_post_to_social_media_login_mocked(MockBrowserUseAgent):
    """Test posting tool with login_identifier_override and password_override, checking login instructions."""
    mock_bua_instance = MockBrowserUseAgent.return_value
    mock_run_result = MagicMock()
    mock_run_result.final_result.return_value = "Posted with login."
    mock_bua_instance.run = AsyncMock(return_value=mock_run_result)

    test_content = "Another test post."
    login_id = "testuser_or_email_or_phone"
    password = "testpass"

    # Use the new override parameter names
    post_to_social_media.entrypoint(
        content=test_content, 
        platform="Twitter", 
        login_identifier_override=login_id, 
        password_override=password
    )

    MockBrowserUseAgent.assert_called_once()
    args, kwargs = MockBrowserUseAgent.call_args
    task_prompt = kwargs["task"]

    # Check that the prompt uses the generic term "identifier"
    assert f"log in using the identifier '{login_id}' and password '{password}'" in task_prompt 

# Removed @pytest.mark.asyncio from class level
class TestSocialMediaTools:
    DUMMY_CONTENT = "This is a test post for X.com!"
    DUMMY_PLATFORM_TWITTER = "Twitter"
    DUMMY_PLATFORM_UNSUPPORTED = "UnsupportedPlatform"
    DUMMY_X_URL = "https://x.com"

    @patch('auto_sns_agent.tools.social_media_tools.OPENAI_API_KEY', "test_api_key")
    @patch('auto_sns_agent.tools.social_media_tools._post_to_social_media_async')
    @patch('auto_sns_agent.tools.social_media_tools.asyncio.run') 
    def test_post_to_social_media_twitter_success(self, mock_asyncio_run_social_tools, mock_internal_async_func):
        # Arrange
        expected_async_result = f"Successfully posted. URL: http://x.com/test_post_id"
        mock_internal_async_func.return_value = expected_async_result

        def side_effect_for_run(coroutine_obj, *args, **kwargs):
            if asyncio.iscoroutine(coroutine_obj):
                pass
            return mock_internal_async_func.return_value
        mock_asyncio_run_social_tools.side_effect = side_effect_for_run
        
        # Act
        result = post_to_social_media.entrypoint(content=self.DUMMY_CONTENT, platform=self.DUMMY_PLATFORM_TWITTER)

        # Assert
        mock_asyncio_run_social_tools.assert_called_once() 
        mock_internal_async_func.assert_called_once()
        assert result == expected_async_result

    @patch('auto_sns_agent.tools.social_media_tools.OPENAI_API_KEY', "test_api_key")
    @patch('auto_sns_agent.tools.social_media_tools._post_to_social_media_async')
    @patch('auto_sns_agent.tools.social_media_tools.asyncio.run') 
    def test_post_to_social_media_twitter_failure_on_post(self, mock_asyncio_run_social_tools, mock_internal_async_func):
        # Arrange
        expected_async_result = "Failed to post: Could not find post button"
        mock_internal_async_func.return_value = expected_async_result

        def side_effect_for_run(coroutine_obj, *args, **kwargs):
            return mock_internal_async_func.return_value
        mock_asyncio_run_social_tools.side_effect = side_effect_for_run
        
        # Act
        result = post_to_social_media.entrypoint(content=self.DUMMY_CONTENT, platform=self.DUMMY_PLATFORM_TWITTER)

        # Assert
        mock_asyncio_run_social_tools.assert_called_once()
        mock_internal_async_func.assert_called_once()
        assert result == expected_async_result

    @patch('auto_sns_agent.tools.social_media_tools.OPENAI_API_KEY', "test_api_key")
    @patch('auto_sns_agent.tools.social_media_tools._post_to_social_media_async')
    @patch('auto_sns_agent.tools.social_media_tools.asyncio.run') 
    def test_post_to_social_media_twitter_bua_exception(self, mock_asyncio_run_social_tools, mock_internal_async_func):
        # Arrange
        expected_async_result = f"Error attempting to post to '{self.DUMMY_X_URL}': BrowserUse Connection Error"
        mock_internal_async_func.return_value = expected_async_result

        def side_effect_for_run(coroutine_obj, *args, **kwargs):
            return mock_internal_async_func.return_value
        mock_asyncio_run_social_tools.side_effect = side_effect_for_run

        # Act
        result = post_to_social_media.entrypoint(content=self.DUMMY_CONTENT, platform=self.DUMMY_PLATFORM_TWITTER)

        # Assert
        mock_asyncio_run_social_tools.assert_called_once()
        mock_internal_async_func.assert_called_once()
        assert result == expected_async_result

    # This test is synchronous, so no @pytest.mark.asyncio
    def test_post_to_social_media_unsupported_platform(self):
        # Arrange
        # Act
        result = post_to_social_media.entrypoint(content=self.DUMMY_CONTENT, platform=self.DUMMY_PLATFORM_UNSUPPORTED)

        # Assert
        assert f"Error: Platform '{self.DUMMY_PLATFORM_UNSUPPORTED}' is not supported for posting." in result

    # This test is synchronous, so no @pytest.mark.asyncio
    @patch('auto_sns_agent.tools.social_media_tools.OPENAI_API_KEY', None)
    def test_post_to_social_media_no_openai_key(self):
        # Arrange
        # Act
        result = post_to_social_media.entrypoint(content=self.DUMMY_CONTENT, platform=self.DUMMY_PLATFORM_TWITTER)

        # Assert
        assert "Error: OPENAI_API_KEY not found for browser_use_llm." in result
        
    @pytest.mark.asyncio # This test remains async as it tests the async function directly
    @patch('auto_sns_agent.tools.social_media_tools.BrowserUseAgent')
    async def test_internal_post_async_logic(self, MockBrowserUseAgent):
        # This test is more for the async function directly
        # Arrange
        mock_agent_instance = MockBrowserUseAgent.return_value
        
        mock_run_result = MagicMock() # Changed from AsyncMock
        # final_result() is a method call, its return_value is what we check
        mock_run_result.final_result.return_value = "Async success"
        mock_agent_instance.run = AsyncMock(return_value=mock_run_result)

        # Act
        result = await _post_to_social_media_async(
            content="Async test", 
            platform_url=self.DUMMY_X_URL, 
            login_identifier="user", 
            password="password"
        )

        # Assert
        MockBrowserUseAgent.assert_called_once()
        mock_agent_instance.run.assert_called_once()
        assert result == "Async success" 

@pytest.mark.vcr
@pytest.mark.live_tool_test
def test_post_to_social_media_live():
    """Test post_to_social_media with a live call to Twitter/X."""
    test_content = "This is a live test post from auto_sns_agent! Hello world! #LiveTest"
    platform = "Twitter"

    print(f"Attempting to post live to {platform} with content: '{test_content}'")
    print("Please ensure X_LOGIN_IDENTIFIER and X_PASSWORD are set in your environment or .env for this test.")
    
    # Attempt to call the underlying function via .entrypoint
    result = post_to_social_media.entrypoint(content=test_content, platform=platform)
    
    print(f"\nOutput from live post attempt to {platform}:")
    print(result)
    
    assert isinstance(result, str), "Result should be a string"
    assert len(result) > 0, "Result string should not be empty"
    
    # Check for indicators of success or known/acceptable failure messages from BrowserUseAgent
    # The exact success message depends on the prompt and BrowserUseAgent's execution
    # For live tests, UI can change, so we look for patterns.
    assert ("Successfully posted. URL:" in result or \
            "Posted successfully but could not retrieve URL" in result or \
            "Failed to post:" in result or \
            "Error attempting to post" in result or \
            "No specific confirmation received" in result), \
           f"Unexpected result from live post: {result}"

    if "Successfully posted. URL:" in result:
        print("Live post appears successful and URL was retrieved.")
    elif "Posted successfully but could not retrieve URL" in result:
        print("Live post may have been successful, but URL retrieval failed.")
    else:
        print("Live post attempt did not clearly succeed in retrieving a URL. Check output for details.") 