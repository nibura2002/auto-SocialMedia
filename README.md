# Social Media Creation Agent (auto-sns)

This project, developed for the Global Agent Hackathon May 2025, is a Python-based agent designed to automate aspects of social media content creation and research. It leverages the Agno framework for agent orchestration and Browser Use for web interactions.

## Goal

The primary goal is to create an intelligent agent that can:
1.  **Research Topics**: Gather information and existing posts from social media platforms (initially X.com/Twitter) based on user prompts.
2.  **Generate Content Concepts**: Based on the research, propose ideas or concepts for new social media posts.
3.  **(Future) Draft Posts**: Generate full draft posts for review.
4.  **(Future) Post to Platforms**: Automate the posting of approved content.
5.  **(Future) Social Listening**: Monitor social media for mentions, trends, or sentiment related to specified topics.

## Architecture

-   **`Agno OrchestratorAgent` (`src/auto_sns_agent/agents/orchestrator.py`)**: The main controller that manages the workflow. It interprets user requests and delegates tasks to other components or tools.
-   **`BrowserUse Interaction Module` (via `src/auto_sns_agent/tools/browser_tools.py` and `social_media_tools.py`)**: Handles all browser-based interactions, such as logging into platforms, performing searches, extracting content, and (eventually) posting. This is implemented as Agno-compatible tools that use the `browser-use` library.
-   **`ContentGeneratorAgent` (`src/auto_sns_agent/agents/content_generator.py`)**: A specialized agent responsible for taking research findings or briefs and generating creative social media post content.
-   **(Future) Specialized Agents**: More agents might be added for specific tasks like in-depth analysis or image/video generation.

## Core Functionalities Implemented

-   User interaction via a command-line chat loop (`src/auto_sns_agent/main.py`).
-   Tool for fetching general webpage content using `BrowserUseAgent`.
-   Tool for searching X.com (Twitter) for posts on a given topic, including login capability, and extracting their text using `BrowserUseAgent`.
-   Orchestrator agent that can use these tools to perform research.
-   Separate content generator agent (basic, awaiting workflow integration).

## Technologies

-   **Python**: Core programming language.
-   **Agno**: Framework for building and orchestrating AI agents.
-   **Browser Use**: Library for controlling and interacting with web browsers for automation tasks.
-   **OpenAI GPT models** (e.g., `gpt-4o-mini`, `gpt-4o`): Used by Agno agents for decision-making and by Browser Use for interpreting web pages.
-   **uv**: For Python packaging and virtual environment management.
-   **pytest**: For testing.

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
    └── workflows/   # (Planned for content creation workflow)
        └── __init__.py
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
    X_USERNAME="your_x_username_or_email"
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
-   "Based on current discussions on Twitter about 'sustainable fashion', give me a concept for a post."

Type `quit` to exit the agent.

## How to Run Tests

To run the test suite (make sure your environment is activated and dependencies, including dev dependencies, are installed):

```bash
uv run pytest
```

## Next Steps (Planned)

-   Implement the "Content Creation Workflow" (`src/auto_sns_agent/workflows/content_creation_workflow.py`) where the `OrchestratorAgent` passes research findings to the `ContentGeneratorAgent` to produce a draft post.
-   Refine `BrowserUseAgent` prompts for more robust interactions, especially around handling different website structures and potential errors.
-   Add functionality for the agent to post content (requires careful handling of authentication and platform APIs/interactions).
-   Expand social listening capabilities.
-   Improve error handling and logging throughout the application.
