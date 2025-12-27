from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
import unittest

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.server import app

class TestServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('src.server.CrewEngine')
    def test_message_endpoint(self, MockEngine):
        # Setup Mock
        mock_instance = MockEngine.return_value
        mock_instance.process_message.return_value = "Hello form Agent"
        
        response = self.client.post("/message", json={
            "project_name": "test_proj",
            "message": "Hello"
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "response": "Hello form Agent",
            "project": "test_proj"
        })
        
        mock_instance.process_message.assert_called_once_with("Hello")

    @patch('src.server.CrewEngine')
    def test_run_endpoint(self, MockEngine):
        # Setup Mock
        mock_instance = MockEngine.return_value
        mock_instance.run.return_value = "Task Done"
        
        response = self.client.post("/run", json={
            "project_name": "test_proj",
            "user_story": "Do task"
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "result": "Task Done",
            "project": "test_proj"
        })

    @patch('os.listdir')
    @patch('os.path.exists')
    @patch('os.path.isdir')
    def test_list_projects(self, mock_isdir, mock_exists, mock_listdir):
        mock_exists.return_value = True
        mock_listdir.return_value = ["proj1", "proj2"]
        mock_isdir.return_value = True
        
        response = self.client.get("/projects")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"projects": ["proj1", "proj2"]})

    @patch('src.server.CrewEngine')
    def test_create_project(self, MockEngine):
        response = self.client.post("/projects", json={
            "project_name": "new_proj",
            "init_git": True
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], "success")
        MockEngine.assert_called_with(project_name="new_proj", init_git=True, remote_url=None)

if __name__ == '__main__':
    unittest.main()
