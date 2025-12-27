from crewai.tools import BaseTool
from pydantic import Field
import subprocess
import os

class CodeExecutionTool(BaseTool):
    name: str = "Code Executor"
    description: str = "Executes shell commands (like 'pytest test_file.py' or 'python main.py'). PREFER running files over complex one-liners. Input is the command string."
    working_dir: str = Field(..., description="The directory where the command should be executed.")

    def _run(self, command: str) -> str:
        try:
            # Basic validation to ensure we are running python/pytest
            cmd_clean = command.strip()
            if not (cmd_clean.startswith("python") or cmd_clean.startswith("pytest") or cmd_clean.startswith("pip")):
                 return "Error: Only 'python', 'pytest', or 'pip' commands are allowed for safety. Please write code to a file first if it's complex."

            # Warn against long -c commands if they look too complex
            if "python -c" in cmd_clean and len(cmd_clean) > 200:
                return "Error: The 'python -c' command is too long and complex. Please write the code to a .py file using FileWriterTool and then run it using 'python <filename>'."

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

