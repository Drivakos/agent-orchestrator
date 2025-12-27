import unittest
from unittest.mock import patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools import CodeExecutionTool

class TestCodeExecutionTool(unittest.TestCase):
    def setUp(self):
        self.tool = CodeExecutionTool(working_dir=".")

    @patch('subprocess.run')
    def test_run_pytest(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Tests passed"
        mock_run.return_value.stderr = ""
        
        output = self.tool._run("pytest")
        
        self.assertIn("Exit Code: 0", output)
        self.assertIn("STDOUT:\nTests passed", output)
        
        mock_run.assert_called_once()
        args = mock_run.call_args
        self.assertEqual(args[0][0], "pytest")

    @patch('subprocess.run')
    def test_run_blocked_command(self, mock_run):
        output = self.tool._run("rm -rf /")
        self.assertIn("Error: Only 'python', 'pytest', or 'pip' commands are allowed", output)
        mock_run.assert_not_called()

    @patch('subprocess.run')
    def test_run_error(self, mock_run):
        mock_run.side_effect = Exception("Boom")
        output = self.tool._run("python script.py")
        self.assertIn("Execution Execution Error: Boom", output)

if __name__ == '__main__':
    unittest.main()
