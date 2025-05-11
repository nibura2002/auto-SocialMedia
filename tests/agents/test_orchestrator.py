import pytest
from agno.agent import Agent
# Correct import for RunResponse if needed for type hinting response object itself
# from agno.types import RunResponse 
# For now, we are checking the type of response.content, so direct import might not be strictly necessary
# if we only assert on response.content existing.

from auto_sns_agent.agents.orchestrator import get_orchestrator_agent
from unittest.mock import patch, MagicMock
# Assuming browser_tools will now have get_webpage_main_content
from auto_sns_agent.tools.browser_tools import get_webpage_main_content 
from auto_sns_agent.tools.social_media_tools import get_social_media_posts_for_topic


def test_get_orchestrator_agent_initialization():
    """Test that the orchestrator agent can be initialized."""
    agent = get_orchestrator_agent()
    assert isinstance(agent, Agent), "Should be an instance of Agno Agent"
    # Check if tools are registered - now expecting 3 tools
    assert len(agent.tools) == 3 
    tool_names = [t.name for t in agent.tools] # t.name is the string name of the Agno tool
    # Check against the expected string names of the tools
    assert "get_webpage_main_content" in tool_names
    assert "get_social_media_posts_for_topic" in tool_names


def test_orchestrator_agent_simple_run():
    """Test a simple run of the orchestrator agent without using tools."""
    agent = get_orchestrator_agent()
    prompt = "Hello, what are your main capabilities?"
    response = agent.run(prompt)
    assert hasattr(response, 'content') and response.content is not None
    assert isinstance(response.content, str) and len(response.content.strip()) > 0
    print(f"Agent simple response: {response.content}") 


@pytest.mark.live_tool_test 
def test_orchestrator_can_get_webpage_content_live(capsys):
    """Test that the orchestrator agent uses get_webpage_main_content tool (live)."""
    url_to_test = "https://blog.agno.com/introducing-agno-llm-developer-platform/" # A blog post
    expected_content_fragment = "Agno LLM Developer Platform" # Something likely in that blog post

    agent = get_orchestrator_agent()
    # Prompt designed to trigger the get_webpage_main_content tool
    prompt = f"Please get the main content from the webpage at {url_to_test} and tell me what it says about Agno."
    response = agent.run(prompt)
    
    print(f"Agent raw response content (webpage content live): {response.content}")
    assert response.content is not None
    # The agent's final response should reflect the content found by the tool.
    assert expected_content_fragment in response.content, \
        f"Expected fragment '{expected_content_fragment}' not found in agent response."
    # We also expect the tool to have been called. Agno's `show_tool_calls=True` in agent prints this.
    # Capturing stdout can verify this implicitly if the test passes based on content from the tool.


@patch('auto_sns_agent.tools.social_media_tools.get_social_media_posts_for_topic.entrypoint', new_callable=MagicMock)
def test_orchestrator_uses_social_media_research_tool_mocked(mock_tool_entrypoint):
    """Test orchestrator using mocked get_social_media_posts_for_topic tool's entrypoint."""
    
    mock_topic = "AI in art"
    mock_platform = "Twitter"
    mock_social_posts_output = (
        f"Post 1 about {mock_topic}: AI is revolutionizing digital art. #AIArt ---NEXT_POST_DELIMITER---"
        f"Post 2 about {mock_topic}: Check out these amazing GAN creations! #GenerativeAI"
    )
    mock_tool_entrypoint.return_value = mock_social_posts_output

    agent = get_orchestrator_agent()
    prompt = f"What are people saying about '{mock_topic}' on {mock_platform}? Summarize the findings."
    response = agent.run(prompt)

    print(f"Agent raw response (mocked social research): {response.content}")

    mock_tool_entrypoint.assert_called_once()
    called_args, called_kwargs = mock_tool_entrypoint.call_args
    assert called_kwargs.get('topic') == mock_topic
    
    # Allow for a flexible count chosen by the LLM, e.g., between 1 and 10 inclusive
    # The orchestrator prompt gives it leeway: "default to a reasonable number like 5-10 if not specified by the user, but use your judgment"
    actual_count = called_kwargs.get('count')
    assert isinstance(actual_count, int) and 1 <= actual_count <= 10, \
        f"Expected count to be an int between 1 and 10, but got {actual_count}"

    # Allow platform to be case-insensitive or default if not explicitly provided by LLM
    # ... (rest of test if platform assertion needs adjustment - currently it's fine)


@patch('auto_sns_agent.tools.browser_tools.get_webpage_main_content.entrypoint', new_callable=MagicMock)
def test_orchestrator_uses_webpage_content_tool_mocked(mock_tool_entrypoint):
    """Test orchestrator using mocked get_webpage_main_content tool's entrypoint."""
    
    mock_url = "https://example.com/my-article"
    mock_article_content = "Successfully extracted main content from https://example.com/my-article:\nThis is a detailed article about the wonders of LLMs and their impact on modern technology. LLMs are cool."
    mock_tool_entrypoint.return_value = mock_article_content

    agent = get_orchestrator_agent()
    prompt = f"Please read the article at {mock_url} and summarize its key points regarding LLMs."
    response = agent.run(prompt)

    print(f"Agent raw response (mocked web content): {response.content}")

    mock_tool_entrypoint.assert_called_once_with(url=mock_url)
    assert response.content is not None
    assert "LLMs are cool" in response.content or "wonders of LLMs" in response.content
    assert "detailed article" in response.content

# Removed old test_orchestrator_agent_uses_navigation_tool_live as it was for H1 and is superseded by get_webpage_main_content logic
# Removed old test_orchestrator_can_get_first_h1_live as it's renamed to test_orchestrator_can_get_webpage_content_live and updated.