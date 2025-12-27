import os
import json
import re
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import FileReadTool, FileWriterTool

load_dotenv()

# --- Configuration ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://llm.drivakosv.gr/v1")
MODEL_NAME = "openai/qwen3:8b" 
API_KEY = os.getenv("OPENAI_API_KEY")

class CrewEngine:
    def __init__(self, project_name="default_project"):
        self.project_name = project_name
        self.base_dir = os.path.join("projects", project_name)
        self.output_dir = os.path.join(self.base_dir, "code")
        self.memory_file = os.path.join(self.base_dir, "memory.md")
        
        # Ensure directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Tools
        self.file_writer = FileWriterTool()
        self.file_reader = FileReadTool()
        
        # Initialize LLM
        self.llm = LLM(
            model=MODEL_NAME,
            base_url=OLLAMA_BASE_URL,
            api_key=API_KEY,
            extra_headers={
                "User-Agent": "Mozilla/5.0",
                "Authorization": f"Bearer {API_KEY}"
            }
        )

    def _get_memory_context(self):
        """Reads the memory file to provide context to the agent."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return f.read()
        return "No previous features implemented yet."

    def _update_memory(self, user_story, result):
        """Appends the new feature to the memory file."""
        entry = f"\n## Implemented Feature: {user_story}\n\n**Result Summary:**\n{result}\n\n---\n"
        with open(self.memory_file, 'a', encoding='utf-8') as f:
            f.write(entry)

    def run(self, user_story):
        """Executes the Crew for a specific user story with memory context."""
        
        memory_context = self._get_memory_context()
        
        # --- Agents ---
        pm_agent = Agent(
            role='Product Manager',
            goal=f'Plan features for the project "{self.project_name}".',
            backstory=f"""You are the Technical PM for "{self.project_name}".
            
            **Current Project Status (Memory):**
            {memory_context}
            
            Your job is to plan the implementation of: '{user_story}'
            Ensure it integrates with existing features.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        dev_agent = Agent(
            role='Senior Developer',
            goal='Write code and output it in Markdown blocks.',
            backstory=f"""You are the Lead Dev. 
            Output files using this format:
            ### filename
            ```language
            code
            ```
            Relative paths should be based on the project root.
            """,
            verbose=True,
            allow_delegation=False,
            tools=[self.file_writer],
            llm=self.llm
        )

        qa_agent = Agent(
            role='QA Engineer',
            goal='Write unit tests.',
            backstory="You are the QA. Write tests for the new code.",
            verbose=True,
            allow_delegation=False,
            tools=[self.file_writer],
            llm=self.llm
        )

        reviewer_agent = Agent(
            role='Chief Architect',
            goal='Review and Approval.',
            backstory="Review the work. Ensure it matches the memory and requirements.",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )

        # --- Tasks ---
        task_plan = Task(
            description=f"Plan the feature: '{user_story}'. Consider the existing memory: {memory_context}.",
            expected_output="Implementation plan.",
            agent=pm_agent
        )

        task_dev = Task(
            description="Write the code. Use '### filename' format.",
            expected_output="Source code in markdown.",
            agent=dev_agent,
            context=[task_plan]
        )

        task_qa = Task(
            description="Write tests.",
            expected_output="Test code in markdown.",
            agent=qa_agent,
            context=[task_dev]
        )

        task_review = Task(
            description="Final review.",
            expected_output="Verdict.",
            agent=reviewer_agent,
            context=[task_plan, task_dev, task_qa]
        )

        crew = Crew(
            agents=[pm_agent, dev_agent, qa_agent, reviewer_agent],
            tasks=[task_plan, task_dev, task_qa, task_review],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        
        # Save files and update memory
        self._save_files_from_output(crew)
        self._update_memory(user_story, str(result))
        
        return str(result)

    def _save_files_from_output(self, crew):
        """Parses output from all tasks and saves files to the project code directory."""
        print(f"\n[Engine] Saving files to: {self.output_dir}")
        for task in crew.tasks:
            if not task.output: continue
            
            # Markdown Parsing
            pattern = r'###\s+([^\n]+)\s+```[^\n]*\n(.*?)\n```'
            matches = re.finditer(pattern, str(task.output), re.DOTALL)
            
            for match in matches:
                filename = match.group(1).strip()
                content = match.group(2)
                
                # Remove redundant paths if agent added them
                clean_filename = filename.replace('output/', '').replace('code/', '')
                full_path = os.path.join(self.output_dir, clean_filename)
                
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  - Saved: {clean_filename}")
