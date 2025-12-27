import os
import sys
from src.engine import CrewEngine

def get_project_selection():
    """Lists existing projects and lets the user select one or create new."""
    projects_dir = "projects"
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)
    
    # Get list of directories
    projects = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]
    
    print("\n--- Available Projects ---")
    if not projects:
        print("(No projects found)")
    else:
        for i, p in enumerate(projects):
            print(f"{i + 1}. {p}")
    
    print("--------------------------")
    choice = input("Select a number or type a NEW project name: ").strip()
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(projects):
            return projects[idx]
        else:
            print("Invalid selection. Creating new project with that name.")
            return choice
    return choice

if __name__ == "__main__":
    print("## Welcome to the CrewAI Agent Orchestrator (v2) ##")
    print("----------------------------------------------------")
    
    project_name = get_project_selection()
    if not project_name:
        project_name = "default_project"
        
    engine = CrewEngine(project_name=project_name)
    
    print(f"\n[System] Loaded project '{project_name}'.")
    # Show last few lines of memory for context
    mem_context = engine._get_memory_context()
    print(f"[System] Memory Context (preview):\n...{mem_context[-200:] if len(mem_context) > 200 else mem_context}\n")
    
    while True:
        user_story = input("\nEnter User Story (or 'exit'): ").strip()
        if user_story.lower() == 'exit' or not user_story:
            break
            
        print(f"\n[System] Running Crew for: {user_story}...")
        result = engine.run(user_story)
        
        print("\n########################")
        print("##  CYCLE COMPLETED   ##")
        print("########################\n")
        print(result)
        
        print("\n[System] Checking for unwritten files...")
        # Since we are using engine.run, the saving happens inside the engine class now.
        # But we can keep a secondary check if needed, though engine._save_files_from_output handles it.