import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main

class TestMain(unittest.TestCase):
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('os.listdir')
    @patch('builtins.input')
    def test_get_project_selection_existing(self, mock_input, mock_listdir, mock_makedirs, mock_exists):
        # Setup: Project "existing_proj" exists, but .git does NOT
        def exists_side_effect(path):
            if path == "projects": return True
            if "existing_proj" in path and ".git" not in path: return True
            return False
            
        mock_exists.side_effect = exists_side_effect
        mock_listdir.return_value = ["existing_proj"]
        
        # User selects "1" (existing_proj)
        # User says "n" to git init
        mock_input.side_effect = ["1", "n"]
        
        with patch('os.path.isdir', return_value=True):
            project_name, init_git, remote = main.get_project_selection()
        
        self.assertEqual(project_name, "existing_proj")
        self.assertFalse(init_git)
        self.assertIsNone(remote)

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('os.listdir')
    @patch('builtins.input')
    def test_get_project_selection_new(self, mock_input, mock_listdir, mock_makedirs, mock_exists):
        # Setup: No projects
        mock_exists.return_value = False
        mock_listdir.return_value = []
        
        # User types "new_proj"
        # User says "y" to git init
        # User enters "https://github.com/user/repo" for remote
        mock_input.side_effect = ["new_proj", "y", "https://github.com/user/repo"]
        
        project_name, init_git, remote = main.get_project_selection()
        
        self.assertEqual(project_name, "new_proj")
        self.assertTrue(init_git)
        self.assertEqual(remote, "https://github.com/user/repo")

if __name__ == '__main__':
    unittest.main()
