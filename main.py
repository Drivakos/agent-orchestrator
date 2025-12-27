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
    
    should_init_git = False
    remote_url = None
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(projects):
            project_name = projects[idx]
            project_path = os.path.join(projects_dir, project_name)
            has_git = os.path.exists(os.path.join(project_path, ".git"))
            
            if not has_git:
                git_choice = input(f"Initialize a git repository for '{project_name}'? (y/n): ").strip().lower()
                should_init_git = git_choice == 'y'
            else:
                should_init_git = True # Set True so we can check/add remote in engine
            
            if should_init_git:
                 remote_url = input("Enter Remote Repository URL (optional, press Enter to skip/keep existing): ").strip()
                 if not remote_url:
                    remote_url = None
            
            return project_name, should_init_git, remote_url
        else:
            print("Invalid selection. Creating new project with that name.")
            project_name = choice
    else:
        project_name = choice
        
    # Ask for git initialization
    if project_name not in projects:
        git_choice = input(f"Initialize a git repository for '{project_name}'? (y/n): ").strip().lower()
        should_init_git = git_choice == 'y'
        
        if should_init_git:
            remote_url = input("Enter Remote Repository URL (optional, press Enter to skip): ").strip()
            if not remote_url:
                remote_url = None
        
    return project_name, should_init_git, remote_url

if __name__ == "__main__":
    print("## Welcome to the CrewAI Agent Orchestrator (v2) ##")
    print("----------------------------------------------------")
    
    project_name, should_init_git, remote_url = get_project_selection()
    if not project_name:
        project_name = "default_project"
        
    engine = CrewEngine(project_name=project_name, init_git=should_init_git, remote_url=remote_url)
    
    print(f"\n[System] Loaded project '{project_name}'.")
    
    # Display Project Metadata
    meta = engine.get_project_metadata()
    if meta:
        print(f"[System] Version: {meta.get('version', 'unknown')} | Branch: {meta.get('branch', 'unknown')}")
    
    while True:
        user_story = input("\nEnter User Story (or 'exit'): ").strip()
        if user_story.lower() == 'exit' or not user_story:
            break
            
        print(f"\n[System] Processing: {user_story}...")
        result = engine.process_message(user_story)
        
        print("\n--- Result ---")
        print(result)
        print("--------------")