# Social Media Creation Agent (auto-sns)

This project, developed for the Global Agent Hackathon May 2025, is a Python-based agent designed to automate aspects of social media content creation and research. It leverages the Agno framework for agent orchestration and Browser Use for web interactions.

## Goal

The primary goal is to create an intelligent agent that can:
1.  **Research Topics**: Gather information and existing posts from social media platforms (initially X.com/Twitter) based on user prompts.
2.  **Generate Content Concepts**: Based on the research, propose ideas or concepts for new social media posts.
3.  **Draft Posts**: Generate full draft posts for review.
4.  **Post to Platforms**: Automate the posting of approved content to Twitter/X.com.
5.  **(Future) Social Listening**: Monitor social media for mentions, trends, or sentiment related to specified topics.

## Architecture

-   **`Agno OrchestratorAgent` (`src/auto_sns_agent/agents/orchestrator.py`)**: The main controller that manages the workflow. It interprets user requests and delegates tasks to other components or tools.
-   **`BrowserUse Interaction Module` (via `src/auto_sns_agent/tools/browser_tools.py` and `social_media_tools.py`)**: Handles all browser-based interactions, such as logging into platforms, performing searches, extracting content, and posting. This is implemented as Agno-compatible tools that use the `browser-use` library.
-   **`ContentGeneratorAgent` (`src/auto_sns_agent/agents/content_generator.py`)**: A specialized agent responsible for taking research findings or briefs and generating creative social media post content.
-   **`ContentCreationWorkflow` (`src/auto_sns_agent/workflows/content_creation_workflow.py`)**: Orchestrates the entire process from research to content generation to post submission with user approval.
-   **(Future) Specialized Agents**: More agents might be added for specific tasks like in-depth analysis or image/video generation.

## Core Functionalities Implemented

-   User interaction via a command-line chat loop (`src/auto_sns_agent/main.py`).
-   Tool for fetching general webpage content using `BrowserUseAgent`.
-   Tool for searching X.com (Twitter) for posts on a given topic, including login capability, and extracting their text using `BrowserUseAgent`.
-   Orchestrator agent that can use these tools to perform research.
-   Content generator agent that creates draft posts based on research.
-   Social media posting tool that can post content to X.com/Twitter with user approval.
-   Workflow that integrates research, content generation, and posting with human-in-the-loop confirmation.
-   Character limit enforcement for X.com/Twitter posts (strictly less than 280 characters).

## Technologies

-   **Python**: Core programming language.
-   **Agno**: Framework for building and orchestrating AI agents.
-   **Browser Use**: Library for controlling and interacting with web browsers for automation tasks.
-   **OpenAI GPT models** (e.g., `gpt-4o-mini`, `gpt-4o`): Used by Agno agents for decision-making and by Browser Use for interpreting web pages.
-   **uv**: For Python packaging and virtual environment management.
-   **pytest**: For testing, including `pytest-asyncio` for testing async code.

## Project Structure

```
.gitignore
.env.example       # Template for environment variables
DESIGN.md          # Initial design document
README.md          # This file
pyproject.toml     # Project metadata and dependencies
src/
└── auto_sns_agent/
    ├── __init__.py
    ├── agents/
    │   ├── __init__.py
    │   ├── content_generator.py
    │   └── orchestrator.py
    ├── tools/
    │   ├── __init__.py
    │   ├── browser_tools.py
    │   └── social_media_tools.py
    ├── config.py
    ├── main.py      # Main entry point to run the agent
    └── workflows/   # Content creation workflow
        ├── __init__.py
        └── content_creation_workflow.py
tests/
├── __init__.py
├── agents/
│   ├── __init__.py
│   ├── test_content_generator.py
│   └── test_orchestrator.py
└── tools/
    ├── __init__.py
    └── test_social_media_tools.py
```

## Setup Instructions

1.  **Clone the repository (if applicable)**:
    ```bash
    # git clone <repository_url>
    # cd auto-sns
    ```

2.  **Create and activate a virtual environment using `uv`**:
    ```bash
    uv venv
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate    # On Windows
    ```

3.  **Install dependencies and the project in editable mode**:
    This command will install all dependencies listed in `pyproject.toml` and make your `auto-sns` script available.
    ```bash
    uv sync
    ```

4.  **Install Playwright browsers**:
    Browser Use relies on Playwright.
    ```bash
    playwright install
    ```

5.  **Set up environment variables**:
    Copy the `.env.example` file to `.env` and fill in your actual credentials:
    ```bash
    cp .env.example .env
    ```
    Now, edit `.env` with your details:
    ```
    OPENAI_API_KEY="sk-YOUR_OPENAI_API_KEY_HERE"
    X_LOGIN_IDENTIFIER="your_x_username_or_email"
    X_PASSWORD="your_x_password"
    ```
    Ensure your `.env` file is listed in `.gitignore` (it is by default with the provided one).

## How to Run

Once the setup is complete, you can run the Social Media Creation Agent using the command defined in `pyproject.toml`:

```bash
uv run auto-sns
```

This will start an interactive chat loop where you can provide prompts to the agent.

**Example Prompts:**

-   "What are people saying on Twitter about #opensource AI?"
-   "Get the main content from https://blog.agno.com/ and tell me about it."
-   "Research and create a post about sustainable fashion."
-   "Create a Twitter post about the latest AI developments."

Type `quit` to exit the agent.

## How to Run Tests

To run the test suite (make sure your environment is activated and dependencies, including dev dependencies, are installed):

```bash
uv run pytest
```

To run specific tests, like the social media posting tests:

```bash
uv run pytest tests/tools/test_social_media_tools.py
```

## Implementation Notes

### Social Media Posting

The social media posting functionality uses the `BrowserUseAgent` to post content to X.com/Twitter. Key implementation details:

- A separate process is used for posting to avoid potential browser resource conflicts.
- The `gpt-4o` model is used for more reliable interaction with the Twitter interface.
- The posting process includes detailed instructions for finding and interacting with the posting interface.
- User confirmation is required before posts are submitted, following a human-in-the-loop approach.
- Posts for X.com/Twitter are strictly enforced to be less than 280 characters (including the "[AutoPostingTest]" prefix).
- For X.com posts that exceed the limit, automatic truncation is applied while attempting to preserve hashtags.
- The user is shown the character count when confirming Twitter posts.

## Next Steps (Planned)

-   Expand social listening capabilities.
-   Add support for more social media platforms (e.g., LinkedIn, Instagram).
-   Implement media attachment functionality (images, videos).
-   Add scheduling capabilities for posts.
-   Improve error handling and logging throughout the application.
