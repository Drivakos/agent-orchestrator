import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.engine import CrewEngine

# Suppress Litellm logs
logging.getLogger('litellm').setLevel(logging.CRITICAL)

app = FastAPI(title="Ollama Agent Orchestrator API")

class TaskRequest(BaseModel):
    project_name: str
    user_story: str

@app.post("/run")
async def run_task(request: TaskRequest):
    """
    Runs the agent crew for a specific project and user story.
    If the project doesn't exist, it creates it.
    """
    try:
        engine = CrewEngine(project_name=request.project_name)
        result = engine.run(request.user_story)
        return {"status": "success", "result": result, "project": request.project_name}
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
