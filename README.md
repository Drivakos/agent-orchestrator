# CrewAI Agent Orchestrator

An interactive CLI tool that orchestrates a team of AI agents (Product Manager, Developer, QA, Architect) using [CrewAI](https://crewai.com) to plan, code, and test features based on user stories.

## Features

- **Project Management**: Create new projects or continue working on existing ones.
- **Persistent Memory**: Maintains a memory of implemented features (`memory.md`) to provide context for future tasks.
- **Role-Based Workflow**:
  - **Product Manager**: Plans the feature implementation.
  - **Senior Developer**: Writes the code.
  - **QA Engineer**: Writes unit tests.
  - **Chief Architect**: Reviews and approves the work.
- **Automated Output**: Automatically saves generated code and tests to the `projects/<project_name>/code` directory.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Drivakos/agent-orchestrator.git
    cd agent-orchestrator
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**
    Copy `.env.example` to `.env` and add your API keys (e.g., OpenAI, Ollama URL).
    ```bash
    cp .env.example .env
    ```
    *Note: The `.env` file is git-ignored to prevent sensitive data leaks.*

## Usage

Run the main application:

```bash
python main.py
```

1.  Select an existing project or enter a name for a new one.
2.  Enter a "User Story" or feature description when prompted.
3.  The agent crew will analyze, plan, implement, and test the feature.
4.  Generated files will be saved in `projects/<your_project>/code`.
