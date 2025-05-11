import pytest
from unittest.mock import MagicMock, patch

from agno.workflow import RunResponse, RunEvent

# For patching, use the path to where the functions are *looked up*, not where they are defined.
# In this case, the workflow module imports and uses them.
ORCHESTRATOR_GETTER_PATH = "auto_sns_agent.workflows.content_creation_workflow.get_orchestrator_agent"
GENERATOR_GETTER_PATH = "auto_sns_agent.workflows.content_creation_workflow.get_content_generator_agent"

@pytest.fixture
def mock_orchestrator_agent():
    agent = MagicMock()
    agent.run.return_value = RunResponse(content="Mocked research summary about topic X.", event=RunEvent.run_completed)
    return agent

@pytest.fixture
def mock_content_generator_agent():
    agent = MagicMock()
    agent.run.return_value = RunResponse(content="Mocked draft post about topic X: Be productive!", event=RunEvent.run_completed)
    return agent


@patch(ORCHESTRATOR_GETTER_PATH)
@patch(GENERATOR_GETTER_PATH)
def test_content_creation_workflow_run_successful(mock_get_generator, mock_get_orchestrator, mock_orchestrator_agent, mock_content_generator_agent):
    """Test the workflow's run method with mocked agents for a successful scenario."""
    # Setup mocks: the @patch decorators pass the MagicMock for the *getter functions*
    # We then set the return_value of these getter functions to be our *mocked agent instances*
    mock_get_orchestrator.return_value = mock_orchestrator_agent
    mock_get_generator.return_value = mock_content_generator_agent

    # Dynamically import the workflow class *after* patches are applied
    from auto_sns_agent.workflows.content_creation_workflow import ContentCreationWorkflow
    workflow = ContentCreationWorkflow()

    test_topic = "topic X"
    response = workflow.run(topic=test_topic, platform="Twitter", research_depth=2)

    assert response.event == RunEvent.workflow_completed
    assert "Mocked draft post about topic X" in response.content

    # Verify orchestrator agent was called correctly
    mock_orchestrator_agent.run.assert_called_once()
    orchestrator_call_args = mock_orchestrator_agent.run.call_args[0][0] # Get the first positional argument
    assert f"Gather information and key discussion points about '{test_topic}'" in orchestrator_call_args
    assert "Twitter" in orchestrator_call_args
    assert "2" in orchestrator_call_args # research_depth

    # Verify content generator agent was called correctly with the output of the orchestrator
    mock_content_generator_agent.run.assert_called_once()
    generator_call_args = mock_content_generator_agent.run.call_args[0][0]
    assert "Mocked research summary about topic X." in generator_call_args
    assert f"draft a concise and engaging social media post for Twitter about '{test_topic}'" in generator_call_args

@patch(ORCHESTRATOR_GETTER_PATH)
@patch(GENERATOR_GETTER_PATH)
def test_content_creation_workflow_orchestrator_fails(mock_get_generator, mock_get_orchestrator, mock_orchestrator_agent, mock_content_generator_agent):
    """Test workflow handling when orchestrator agent fails to return content."""
    mock_get_orchestrator.return_value = mock_orchestrator_agent
    mock_get_generator.return_value = mock_content_generator_agent
    
    # Simulate orchestrator failure: ran but produced no content
    mock_orchestrator_agent.run.return_value = RunResponse(content=None, event=RunEvent.run_completed)

    from auto_sns_agent.workflows.content_creation_workflow import ContentCreationWorkflow
    workflow = ContentCreationWorkflow()

    test_topic = "failing topic"
    response = workflow.run(topic=test_topic)

    assert response.event == RunEvent.workflow_completed # Workflow completed, but outcome is failure
    assert f"Failed to get research from OrchestratorAgent for topic: {test_topic}" in response.content
    mock_content_generator_agent.run.assert_not_called() # Generator should not be called

@patch(ORCHESTRATOR_GETTER_PATH)
@patch(GENERATOR_GETTER_PATH)
def test_content_creation_workflow_generator_fails(mock_get_generator, mock_get_orchestrator, mock_orchestrator_agent, mock_content_generator_agent):
    """Test workflow handling when content generator agent fails to return content."""
    mock_get_orchestrator.return_value = mock_orchestrator_agent
    mock_get_generator.return_value = mock_content_generator_agent

    # Simulate generator failure: ran but produced no content
    mock_content_generator_agent.run.return_value = RunResponse(content=None, event=RunEvent.run_completed)

    from auto_sns_agent.workflows.content_creation_workflow import ContentCreationWorkflow
    workflow = ContentCreationWorkflow()

    test_topic = "another topic"
    response = workflow.run(topic=test_topic)

    assert response.event == RunEvent.workflow_completed # Workflow completed, but outcome is failure
    assert f"Failed to generate content from ContentGeneratorAgent for topic: {test_topic}" in response.content 