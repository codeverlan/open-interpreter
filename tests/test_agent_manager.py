import unittest
from unittest.mock import patch, MagicMock
from interpreter.core.core import OpenInterpreter, AgentModel, Project, db, app
from interpreter.core.task_assignment import TaskAssignmentSystem
from interpreter.core.agent import Agent
import json

class TestAgentManager(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.interpreter = OpenInterpreter()
        self.interpreter.openrouter_client = MagicMock()
        self.interpreter.current_project = MagicMock()
        self.interpreter.current_project.id = "test_project_id"
        self.interpreter.task_assignment_system = MagicMock()

    def tearDown(self):
        self.app_context.pop()

    @patch('interpreter.core.core.db.session')
    @patch('interpreter.core.core.AgentModel')
    def test_create_agent(self, mock_agent_model, mock_db_session):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_agent = MagicMock()
        mock_agent.to_dict.return_value = {
            'id': 'test_id',
            'name': 'Test Agent',
            'description': 'A test agent',
            'project_id': 'test_project_id',
            'created_at': '2023-01-01T00:00:00',
            'assigned_model': 'gpt-3.5-turbo',
            'capabilities': ['test'],
            'role': 'general',
            'knowledge_base': {},
            'status': 'idle',
            'current_task': None
        }
        mock_agent_model.return_value = mock_agent

        data = {
            "name": "Test Agent",
            "description": "A test agent",
            "assigned_model": "gpt-3.5-turbo",
            "role": "general",
            "capabilities": ["test"]
        }

        result = self.interpreter.create_agent(data)

        self.assertTrue(result['success'])
        self.assertEqual(result['agent']['name'], "Test Agent")
        self.assertEqual(result['agent']['role'], "general")
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch('interpreter.core.core.AgentModel.query')
    @patch('interpreter.core.core.db.session')
    def test_update_agent(self, mock_db_session, mock_query):
        mock_agent = MagicMock()
        mock_agent.capabilities = '[]'
        mock_agent.knowledge_base = '{}'
        mock_query.get.return_value = mock_agent
        mock_db_session.commit = MagicMock()

        data = {
            "name": "Updated Agent",
            "description": "An updated test agent",
            "assigned_model": "gpt-4",
            "role": "specialized",
            "status": "idle"
        }

        result = self.interpreter.update_agent("test_agent_id", data)

        self.assertTrue(result['success'])
        self.assertEqual(mock_agent.name, "Updated Agent")
        self.assertEqual(mock_agent.role, "specialized")
        mock_db_session.commit.assert_called_once()

    @patch('interpreter.core.core.AgentModel.query')
    @patch('interpreter.core.core.db.session')
    def test_delete_agent(self, mock_db_session, mock_query):
        mock_agent = MagicMock()
        mock_query.get.return_value = mock_agent
        mock_db_session.delete = MagicMock()
        mock_db_session.commit = MagicMock()

        result = self.interpreter.delete_agent("test_agent_id")

        self.assertTrue(result['success'])
        self.assertEqual(result['message'], "Agent deleted successfully")
        mock_db_session.delete.assert_called_once_with(mock_agent)
        mock_db_session.commit.assert_called_once()

    def test_assign_task(self):
        self.interpreter.task_assignment_system.execute_task.return_value = "Task completed successfully"
        self.interpreter.task_assignment_system.task_progress = {'task1': {}}

        task_data = {
            "description": "Test task",
            "iterations": 3
        }

        result = self.interpreter.assign_task(task_data)

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], "Task completed successfully")
        self.interpreter.task_assignment_system.execute_task.assert_called_once_with(task_data, iterations=3)

    def test_get_task_progress(self):
        self.interpreter.task_assignment_system.get_task_progress.return_value = {
            "status": "in_progress",
            "current_iteration": 2,
            "total_iterations": 3
        }

        result = self.interpreter.get_task_progress("test_task_id")

        self.assertTrue(result['success'])
        self.assertEqual(result['progress']['status'], "in_progress")
        self.assertEqual(result['progress']['current_iteration'], 2)
        self.interpreter.task_assignment_system.get_task_progress.assert_called_once_with("test_task_id")

    def test_get_next_steps(self):
        self.interpreter.task_assignment_system.suggest_next_steps.return_value = "Suggested next steps for the task"

        result = self.interpreter.get_next_steps("test_task_id")

        self.assertTrue(result['success'])
        self.assertEqual(result['next_steps'], "Suggested next steps for the task")
        self.interpreter.task_assignment_system.suggest_next_steps.assert_called_once_with("test_task_id")

if __name__ == '__main__':
    unittest.main()