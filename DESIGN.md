# Design Document: Social Media Creation Agent

## 1. Overview

The Social Media Creation Agent automates the process of social media content creation and posting. It will leverage Agno for orchestrating tasks like information gathering and content generation, and Browser Use for interacting with social media web interfaces for data extraction and posting.

The primary goal is to create an agent that can:
- Research topics based on user prompts.
- Generate engaging social media posts (text and potentially image suggestions).
- Post the generated content to specified social media platforms (initially Twitter).
- Optionally, monitor social media for mentions and summarize findings.

This project aims to study the innovative combination of Agno and Browser Use.

## 2. Architecture

The system will consist of the following main components:

### 2.1. Agno Orchestrator Agent
- **Purpose**: Acts as the main controller and brain of the system.
- **Responsibilities**:
    - Receives user prompts (e.g., "Create a viral tweet about the latest AI trends").
    - Defines and manages the workflow (e.g., research -> content generation -> posting).
    - Delegates tasks to specialized sub-agents or directly uses tools.
    - Processes information from research and generates final content.
    - Manages interaction with Browser Use for web automation.
- **Tools**:
    - Potentially other Agno agents (Research Agent, Content Generation Agent).
    - Browser Use tool (for web interaction).
    - Search tools (e.g., DuckDuckGo via Agno tools).
    - Potentially image generation API tools (e.g., wrapped Stable Diffusion).

### 2.2. Browser Use Interaction Module
- **Purpose**: Handles all direct browser interactions.
- **Responsibilities**:
    - Logging into social media platforms.
    - Searching for information on social media sites.
    - Extracting text and other data from web pages.
    - Automating the posting process (filling forms, clicking buttons, uploading media).
- **Integration**: Called as a tool by the Agno Orchestrator Agent. The Agno agent will provide high-level instructions (e.g., "Post this tweet: '...' with this image: '...'") which Browser Use translates into browser actions.

### 2.3. (Optional) Specialized Agno Agents
- **Research Agent**:
    - **Purpose**: Focuses on gathering information from various sources (web search, specific social media feeds via Browser Use).
    - **Output**: A collection of relevant articles, posts, and data points.
- **Content Generation Agent**:
    - **Purpose**: Takes researched information and generates social media content (text, image prompts).
    - **Output**: Draft posts, image descriptions.

## 3. Core Functionalities & Workflow

### 3.1. Scenario 1: Content Creation and Posting

1.  **User Input**: User provides a topic and target social media platform (e.g., "Create a Twitter post about the benefits of remote work, include a relevant hashtag").
2.  **Agno Orchestrator - Research Phase**:
    *   Uses search tools (e.g., DuckDuckGo) to find recent articles/discussions on the topic.
    *   Optionally, uses Browser Use to search the target social media platform for trending posts or related content on the topic.
3.  **Agno Orchestrator - Content Generation Phase**:
    *   Analyzes the gathered information.
    *   Generates a draft post (text) suitable for the target platform.
    *   Suggests relevant hashtags.
    *   (Future) Generates a prompt for an image if requested.
4.  **Agno Orchestrator - Posting Phase**:
    *   Instructs Browser Use to:
        *   Navigate to the social media platform.
        *   Log in (if necessary and credentials are securely managed).
        *   Open the "new post" dialog.
        *   Input the generated text and hashtags.
        *   (Future) Upload an image if provided.
        *   Click the "post" button.
5.  **Feedback**: Agent reports success or failure of the posting attempt, potentially with a link to the post.

### 3.2. Scenario 2: Social Listening & Reporting (Future Enhancement)

1.  **User Input**: User provides keywords/topics and social media platforms to monitor (e.g., "Summarize mentions of 'OurCompanyName' on Twitter and Reddit this week").
2.  **Agno Orchestrator - Data Collection**:
    *   Instructs Browser Use to search specified platforms for mentions.
    *   Collects relevant posts and comments.
3.  **Agno Orchestrator - Analysis & Summarization**:
    *   Processes collected text data.
    *   Identifies key themes, sentiment, and important mentions.
    *   Generates a summary report.
4.  **Output**: Presents the report to the user.

## 4. Technologies

- **Orchestration**: Agno SDK
- **Browser Automation**: Browser Use SDK
- **Language Model**: GPT-4o or similar (as supported by Agno)
- **Programming Language**: Python
- **Dependency Management**: uv
- **Version Control**: Git & GitHub

## 5. Project Structure (Initial src-layout)

```
auto-SocialMedia/
├── .git/
├── .venv/
├── src/
│   └── auto_sns_agent/
│       ├── __init__.py
│       ├── main.py             # Main script to run the agent
│       ├── agents/             # Agno agent definitions
│       │   ├── __init__.py
│       │   └── orchestrator.py
│       │   └── (optional_research_agent.py)
│       │   └── (optional_content_agent.py)
│       ├── tools/              # Custom tools, wrappers for Browser Use
│       │   ├── __init__.py
│       │   └── browser_tools.py
│       └── config.py           # Configuration (API keys, etc.)
├── tests/
│   └── ...
├── pyproject.toml
├── README.md
└── DESIGN.md
```

## 6. Key Success Metrics

- **Working Demo**: Successfully post content to at least one social media platform (e.g., Twitter) based on a user prompt.
- **Innovative Use of Agno & Browser Use**: Clear demonstration of how Agno orchestrates tasks and Browser Use interacts with web UIs.
- **Code Quality**: Clean, well-structured, and commented code.
- **Comprehensive README**: Clear setup instructions, explanation of functionality, and demo video link.

## 7. Potential Challenges & Mitigations

- **Dynamic Web UIs**: Social media UIs change. Browser Use needs to be robust.
    - **Mitigation**: Use stable selectors, build in some flexibility, rely on Browser Use's AI capabilities to adapt.
- **Login/Authentication**: Securely handling credentials for social media.
    - **Mitigation**: Initially, might require manual login in a browser session that Browser Use attaches to, or use environment variables for credentials (with clear security warnings). Avoid storing credentials in code.
- **Rate Limiting/CAPTCHAs**: Automated interactions can be flagged.
    - **Mitigation**: Implement respectful interaction speeds, handle common CAPTCHAs if Browser Use supports it, or focus on platforms with more lenient automation policies for the demo.
- **Scope Creep**: Trying to support too many platforms or features.
    - **Mitigation**: Focus on a core use case (e.g., Twitter posting).

## 8. Next Steps (Implementation Plan Outline)

1.  **Setup Basic Agno Agent**: Create the `OrchestratorAgent` with a simple instruction.
2.  **Integrate Browser Use**:
    *   Develop a basic Browser Use script to open a specific URL (e.g., Twitter).
    *   Wrap this script as an Agno tool.
    *   Have the `OrchestratorAgent` call this tool.
3.  **Implement Twitter Posting Logic**:
    *   Extend Browser Use tool to log in (manually or via config).
    *   Implement steps to navigate to the tweet composition box, enter text, and post.
4.  **Implement Research Logic**:
    *   Integrate a web search tool (e.g., `DuckDuckGoTools` from Agno) into the `OrchestratorAgent`.
5.  **Implement Content Generation**:
    *   Prompt the LLM (via Agno) to generate tweet text based on research results.
6.  **Refine and Test**: Thoroughly test the end-to-end flow.
7.  **Documentation**: Update README, record demo video. 