import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine import CrewEngine

class TestCrewEngineUnit(unittest.TestCase):
    def setUp(self):
        # We need to mock os.makedirs and other file system operations in __init__
        with patch('os.makedirs'), \
             patch('src.engine.LLM'), \
             patch('src.engine.FileWriterTool'), \
             patch('src.engine.FileReadTool'), \
             patch('src.engine.SerperDevTool'), \
             patch('src.engine.CodeExecutionTool'), \
             patch('src.engine.SyntaxCheckTool'):
            self.engine = CrewEngine(project_name="test_proj")

    @patch('src.engine.SerperDevTool')
    @patch('os.getenv')
    @patch('os.makedirs')
    @patch('src.engine.LLM')
    def test_search_tool_initialization(self, mock_llm, mock_makedirs, mock_getenv, MockSerper):
        # Setup: SERPER_API_KEY is present
        def getenv_side_effect(key, default=None):
            if key == "SERPER_API_KEY": return "dummy_key"
            if key == "OPENAI_API_KEY": return "dummy_key"
            return default
        mock_getenv.side_effect = getenv_side_effect
        
        with patch('src.engine.FileWriterTool'), patch('src.engine.FileReadTool'):
             engine = CrewEngine(project_name="test_proj")
        
        self.assertIsNotNone(engine.search_tool)
        MockSerper.assert_called_once()

    @patch('os.walk')
    def test_get_file_tree(self, mock_walk):
        # Mocking os.walk to return a predictable structure
        # Use os.path.join to be platform agnostic
        base = os.path.join('projects', 'test_proj')
        mock_walk.return_value = [
            (base, ['code', '__pycache__'], ['memory.md']),
            (os.path.join(base, 'code'), [], ['main.py']),
        ]
        
        self.engine.base_dir = base
        
        tree = self.engine._get_file_tree()
        
        self.assertIn('memory.md', tree)
        self.assertIn('code/', tree)
        self.assertIn('main.py', tree)
        self.assertNotIn('__pycache__', tree)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"version": "0.1.0"}')
    def test_get_project_metadata(self, mock_file, mock_exists):
        mock_exists.return_value = True
        metadata = self.engine.get_project_metadata()
        self.assertEqual(metadata['version'], '0.1.0')

    @patch('re.finditer')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_files_from_output(self, mock_file, mock_makedirs, mock_finditer):
        # Mock a task with output
        mock_task = MagicMock()
        mock_task.output = "### test.py\n```python\nprint('hello')\n```"
        
        mock_crew = MagicMock()
        mock_crew.tasks = [mock_task]
        
        # Mock re.finditer to return a match
        mock_match = MagicMock()
        mock_match.group.side_effect = lambda i: {1: 'test.py', 2: "print('hello')"}[i]
        mock_finditer.return_value = [mock_match]
        
        self.engine._save_files_from_output(mock_crew)
        
        # Verify file was "written"
        # The file path will be os.path.join(self.engine.output_dir, 'test.py')
        mock_file().write.assert_called_with("print('hello')")

    @patch('src.engine.Agent')
    @patch('src.engine.Crew')
    @patch('src.engine.Task')
    def test_classify_intent_chat(self, MockTask, MockCrew, MockAgent):
        mock_crew_instance = MockCrew.return_value
        mock_crew_instance.kickoff.return_value = "CHAT"
        
        intent = self.engine._classify_intent("How are you?")
        self.assertEqual(intent, "CHAT")

    @patch('src.engine.Agent')
    @patch('src.engine.Crew')
    @patch('src.engine.Task')
    def test_classify_intent_task(self, MockTask, MockCrew, MockAgent):
        mock_crew_instance = MockCrew.return_value
        mock_crew_instance.kickoff.return_value = "TASK"
        
        intent = self.engine._classify_intent("Add a new button")
        self.assertEqual(intent, "TASK")

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_initialize_git_repo(self, mock_file, mock_exists, mock_run):
        # Setup: Repo does NOT exist
        mock_exists.return_value = False
        
        self.engine._initialize_git_repo(remote_url="https://github.com/user/repo")
        
        # Check if git init was called
        # mock_run is called multiple times: git init, git add, git commit, git branch, git remote, git remote add, git push
        calls = [call.args[0] for call in mock_run.call_args_list]
        self.assertIn(["git", "init"], calls)
        self.assertIn(["git", "add", "."], calls)
        self.assertIn(["git", "branch", "-m", "main"], calls)
        
        # Check if metadata file was created
        mock_file.assert_any_call(self.engine.metadata_file, 'w')

    @patch('builtins.open', new_callable=mock_open)
    def test_update_memory(self, mock_file):
        self.engine._update_memory("Add login", "Result OK")
        
        mock_file.assert_called_with(self.engine.memory_file, 'a', encoding='utf-8')
        mock_file().write.assert_called()
        # Verify content written contains the user story
        args, _ = mock_file().write.call_args
        self.assertIn("Add login", args[0])

    @patch('src.engine.CrewEngine._chat_with_pm')
    @patch('src.engine.CrewEngine.run')
    @patch('src.engine.CrewEngine._classify_intent')
    def test_process_message_chat(self, mock_classify, mock_run, mock_chat):
        mock_classify.return_value = "CHAT"
        self.engine.process_message("Hi")
        
        mock_chat.assert_called_once_with("Hi")
        mock_run.assert_not_called()

    @patch('src.engine.CrewEngine._chat_with_pm')
    @patch('src.engine.CrewEngine.run')
    @patch('src.engine.CrewEngine._classify_intent')
    def test_process_message_task(self, mock_classify, mock_run, mock_chat):
        mock_classify.return_value = "TASK"
        self.engine.process_message("Do work")
        
        mock_run.assert_called_once_with("Do work")
        mock_chat.assert_not_called()

    @patch('src.engine.Agent')
    @patch('src.engine.Crew')
    @patch('src.engine.Task')
    @patch('src.engine.CrewEngine._get_memory_context')
    def test_chat_with_pm(self, mock_context, MockTask, MockCrew, MockAgent):
        mock_context.return_value = "Context"
        mock_crew = MockCrew.return_value
        mock_crew.kickoff.return_value = "Hello user"
        
        response = self.engine._chat_with_pm("Hi")
        
        self.assertEqual(response, "Hello user")
        # Ensure context was fetched
        mock_context.assert_called_once()

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('json.dump')
    @patch('src.engine.CrewEngine.get_project_metadata')
    @patch('builtins.open', new_callable=mock_open)
    def test_commit_changes(self, mock_file, mock_get_meta, mock_json_dump, mock_exists, mock_run):
        # Setup: .git exists, metadata returns version 0.1.0
        mock_exists.return_value = True
        mock_get_meta.return_value = {"version": "0.1.0"}
        
        self.engine._commit_changes("New Feature")
        
        # Verify version incremented to 0.1.1
        # json.dump should be called with updated metadata
        args, _ = mock_json_dump.call_args
        self.assertEqual(args[0]['version'], "0.1.1")
        
        # Verify git commit called
        calls = [call.args[0] for call in mock_run.call_args_list]
        self.assertTrue(any("commit" in cmd for cmd in calls))

if __name__ == '__main__':
    unittest.main()
