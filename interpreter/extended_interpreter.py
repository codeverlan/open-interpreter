import yaml
import os
import json
import shutil
from .core.core import OpenInterpreter
from .project_analyzer import ProjectAnalyzer
from .exceptions import InterpreterError, ConfigurationError, FileOperationError, ExecutionError

class ExtendedInterpreter(OpenInterpreter):
    def __init__(self, **kwargs):
        super().__init__()  # Call the parent's __init__ without arguments
        self.server_port = kwargs.get('server_port', 5159)
        self.frontend_config = {}
        self.current_directory = '/'
        self.current_project = None
        self.project_settings = {}
        self.projects_directory = os.path.join(self.current_directory, 'projects')
        if not os.path.exists(self.projects_directory):
            os.makedirs(self.projects_directory)
        self.default_prompts = {
            'system_message': "You are an AI assistant with expertise in programming and software development. Stick to best practices and avoid creative solutions.",
            'code_execution': "Please execute the following code and provide the output:",
            'error_handling': "An error occurred. Please provide more information about the error and suggest possible solutions based on best practices:",
            'documentation_request': "Please provide documentation or explanation for the following, focusing on standard practices and conventions:",
        }
        # Set environment variables for non-user-facing settings
        os.environ['TEMPERATURE'] = '0.2'  # Lower temperature for less randomness
        os.environ['TOP_P'] = '0.1'  # Lower top_p for more focused sampling
        self.max_tokens = 2048  # Reduced max tokens to limit response length

    def get_projects(self):
        try:
            projects = [d for d in os.listdir(self.projects_directory) 
                        if os.path.isdir(os.path.join(self.projects_directory, d))]
            return {'success': True, 'projects': projects}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_settings(self):
        try:
            return {
                'success': True,
                'settings': {
                    'max_tokens': self.max_tokens,
                    'temperature': os.environ.get('TEMPERATURE'),
                    'top_p': os.environ.get('TOP_P'),
                    'server_port': self.server_port,
                    # Add any other relevant settings here
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ... [rest of the methods remain unchanged]

# Add any other methods specific to the extended functionality