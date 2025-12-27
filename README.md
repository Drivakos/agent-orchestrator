# CrewAI Agent Orchestrator (v2)

An advanced interactive CLI tool that orchestrates a specialized team of AI agents to plan, develop, test, and document software features. Optimized for local models (via Ollama) with a focus on reliability, verification, and automated workflows.

## New in v2: Advanced Agentic Workflow

- **Iterative Feedback Loop**: If the **Chief Architect** finds bugs, missing tests, or incomplete work, the task is automatically routed back to the Developer for a "Fix Round" (up to 3 iterations).
- **Sandboxed Code Execution**: A **DevOps Engineer** agent executes generated code and tests in real-time using a safe local runner, reporting logs back to the team.
- **Web Search Capabilities**: Agents can use **SerperDevTool** to research documentation, verify library versions, and find solutions to errors on the fly.
- **Local Model Optimizations**:
  - **Brainstorming**: Product Managers generate and compare multiple approaches before selecting the best implementation path.
  - **Self-Critique**: Developers perform a "Self-Critique" pass on their code to catch logical errors before submission.
  - **Automated Linting**: Integrated **Syntax Checker (flake8)** to catch indentation and syntax errors automatically.
- **Documentation Specialist**: A dedicated agent ensures `README.md` and project docs are updated alongside code changes.

## Core Features

- **Project Management**: Create new projects or continue working on existing ones with persistent memory.
- **Git Integration**: 
  - **Auto-Init**: Option to initialize a Git repository for new projects.
  - **Version Control**: Automatically tracks version and branch in `project_metadata.json`.
  - **Auto-Commit**: Automatically commits changes (with version increment) upon successful feature implementation.
  - **Auto-Push**: Automatically pushes changes to `origin` if a remote is configured.
- **Context Awareness**: 
  - **Memory**: Persistent tracking of implemented features in `memory.md`.
  - **File Structure**: Agents receive a real-time tree view of the project's files.
- **Role-Based Workflow**:
  - **Product Manager**: Brainstorms and plans features.
  - **Senior Developer**: Writes code with self-critique pass.
  - **QA Engineer**: Writes unit tests.
  - **DevOps Engineer**: Executes code/tests and checks syntax.
  - **Docs Specialist**: Updates project documentation.
  - **Chief Architect**: Final review and "APPROVED/REJECTED" verdict.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Drivakos/agent-orchestrator.git
    cd agent-orchestrator
    ```

2.  **Activate virtual environment & Install dependencies:**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    Copy `.env.example` to `.env` and configure your LLM (Ollama/OpenAI) and Serper API key.
    ```bash
    cp .env.example .env
    ```

## Usage

Run the orchestrator:
```bash
python main.py
```

### Running the Orchestrator's Own Tests
We maintain high code coverage for the orchestrator itself. To run our unit and integration tests:
```bash
# Run all tests
venv\Scripts\python -m unittest discover tests
```

## How it works (The "Fix" Cycle)
1. **User Story** is entered.
2. **PM** plans, **Dev** codes, **QA** tests, **DevOps** runs the code.
3. **Architect** reviews the combined output and logs.
4. **If REJECTED**: The loop restarts from the Developer with the Architect's feedback.
5. **If APPROVED**: Files are saved, docs are updated, and changes are committed to Git.