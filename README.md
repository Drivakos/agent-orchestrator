# CrewAI Agent Orchestrator

An interactive CLI tool that orchestrates a team of AI agents (Product Manager, Developer, QA, Architect) using [CrewAI](https://crewai.com) to plan, code, and test features based on user stories.

## Features

- **Project Management**: Create new projects or continue working on existing ones.
- **Git Integration**: 
  - **Auto-Init**: Option to initialize a Git repository for new projects.
  - **Version Control**: Automatically tracks version and branch in `project_metadata.json`.
  - **Auto-Commit**: Automatically commits changes (with version increment) upon successful feature implementation.
  - **Auto-Push**: Automatically pushes changes to `origin` if a remote is configured for the project.
- **Context Awareness**: 
  - **Memory**: Tracks implemented features.
  - **File Structure**: Agents receive a real-time tree view of the project's files, ensuring they know exactly where code resides.
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
2.  **Git Setup**: 
    - **New Projects**: You will be asked if you want to initialize a git repository.
    - **Existing Projects**: You can add a Remote URL if one isn't configured, or initialize git if missing.
3.  Enter a "User Story" or feature description when prompted.
    - **Example Question:** "How do we handle Redis in this project?" (PM answers)
    - **Example Task:** "Implement a Redis caching layer for the user API." (Crew executes & Commits)
4.  The agent crew will analyze, plan, implement, and test the feature.
5.  Generated files will be saved in `projects/<your_project>/code`.
