import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine import CrewEngine

class TestFeedbackLoop(unittest.TestCase):
    @patch('src.engine.Crew')
    @patch('src.engine.Agent')
    @patch('src.engine.Task')
    @patch('src.engine.LLM')
    def test_feedback_loop(self, MockLLM, MockTask, MockAgent, MockCrew):
        # Setup Mock Crew to return REJECTED then APPROVED
        mock_crew_instance = MockCrew.return_value
        
        # We expect kickoff to be called:
        # 1. Initial run -> REJECTED
        # 2. Fix run -> APPROVED
        
        # side_effect for kickoff
        mock_crew_instance.kickoff.side_effect = [
            "REJECTED: The code is missing comments.",  # 1st run result
            "APPROVED: Looks good now."                # 2nd run result (fix)
        ]

        engine = CrewEngine(project_name="test_project", init_git=False)
        
        # Mock file operations to avoid side effects
        engine._save_files_from_output = MagicMock()
        engine._update_memory = MagicMock()
        engine._commit_changes = MagicMock()
        engine._get_memory_context = MagicMock(return_value="Context")
        
        print("\nStarting test run...")
        result = engine.run("Implement a hello world script")
        
        # Verification
        self.assertIn("APPROVED", result)
        self.assertEqual(mock_crew_instance.kickoff.call_count, 2)
        print("\nTest passed: Loop executed 2 times (Reject -> Approve)")

if __name__ == '__main__':
    unittest.main()
