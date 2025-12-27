from crewai.tools import BaseTool
from pydantic import Field
import subprocess
import os

class CodeExecutionTool(BaseTool):
    name: str = "Code Executor"
    description: str = "Executes shell commands (like 'pytest' or 'python main.py') to run code and tests. Input is the command string."
    working_dir: str = Field(..., description="The directory where the command should be executed.")

    def _run(self, command: str) -> str:
        try:
            # Basic validation to ensure we are running python/pytest
            if not (command.strip().startswith("python") or command.strip().startswith("pytest") or command.strip().startswith("pip")):
                 return "Error: Only 'python', 'pytest', or 'pip' commands are allowed for safety."

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.working_dir
            )
            
            output = f"Exit Code: {result.returncode}\n"
            output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
                
            return output
        except Exception as e:
            return f"Execution Execution Error: {str(e)}"

