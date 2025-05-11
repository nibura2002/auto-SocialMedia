import pytest
from agno.agent import Agent

from auto_sns_agent.agents.content_generator import get_content_generator_agent

def test_get_content_generator_agent_initialization():
    """Test that the content generator agent can be initialized."""
    agent = get_content_generator_agent()
    assert isinstance(agent, Agent), "Should be an instance of Agno Agent"

def test_content_generator_agent_simple_run():
    """Test a simple run of the content generator agent with sample input."""
    agent = get_content_generator_agent()
    sample_h1_text = "First H1 text from https://docs.agno.com: The text content of the first <h1> element found is: 'What is Agno'."
    
    prompt = sample_h1_text # The agent is designed to take the text directly
    response = agent.run(prompt)
    
    assert hasattr(response, 'content'), "Response object should have a content attribute"
    assert response.content is not None, "Response content should not be None"
    assert isinstance(response.content, str), "Response content should be a string"
    assert len(response.content.strip()) > 0, "Response content should not be empty"
    
    print(f"Input to ContentGeneratorAgent: {sample_h1_text}")
    print(f"ContentGeneratorAgent response: {response.content}")
    
    # Check for some expected characteristics of a social media post
    assert "#" in response.content, "Response should contain a hashtag"
    assert "Agno" in response.content, "Response should mention 'Agno' given the input" 