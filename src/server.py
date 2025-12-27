import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.engine import CrewEngine

# Suppress Litellm logs
logging.getLogger('litellm').setLevel(logging.CRITICAL)

app = FastAPI(title="Ollama Agent Orchestrator API")

# Allow CORS for local UI development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    project_name: str
    user_story: str

class MessageRequest(BaseModel):
    project_name: str
    message: str

class CreateProjectRequest(BaseModel):
    project_name: str
    init_git: bool = False
    remote_url: str = None

@app.get("/projects")
async def list_projects():
    """List all available projects."""
    projects_dir = "projects"
    if not os.path.exists(projects_dir):
        return {"projects": []}
    
    projects = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]
    return {"projects": projects}

@app.post("/projects")
async def create_project(request: CreateProjectRequest):
    """Create a new project with optional Git initialization."""
    try:
        engine = CrewEngine(
            project_name=request.project_name, 
            init_git=request.init_git, 
            remote_url=request.remote_url
        )
        return {"status": "success", "project": request.project_name, "message": f"Project '{request.project_name}' initialized."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run")
async def run_task(request: TaskRequest):
    """
    Directly runs a task. Useful for specific triggers.
    """
    try:
        engine = CrewEngine(project_name=request.project_name, init_git=False)
        result = engine.run(request.user_story)
        return {"status": "success", "result": result, "project": request.project_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/message")
async def process_message(request: MessageRequest):
    """
    Unified endpoint for Chat or Task execution.
    The engine determines intent (CHAT vs TASK).
    """
    try:
        engine = CrewEngine(project_name=request.project_name, init_git=False)
        result = engine.process_message(request.message)
        return {"status": "success", "response": result, "project": request.project_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_name}/memory")
async def get_memory(project_name: str):
    """
    Returns the memory context (history) for a project.
    """
    engine = CrewEngine(project_name=project_name)
    return {"memory": engine._get_memory_context()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
