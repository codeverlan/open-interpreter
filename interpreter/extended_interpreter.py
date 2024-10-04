import yaml
import os
import json
import shutil
from .core.core import OpenInterpreter
from .project_analyzer import ProjectAnalyzer
from .exceptions import InterpreterError, ConfigurationError, FileOperationError, ExecutionError

class ExtendedInterpreter(OpenInterpreter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def load_frontend_config(self, config_path):
        try:
            with open(config_path, 'r') as config_file:
                self.frontend_config = yaml.safe_load(config_file)
        except Exception as e:
            raise ConfigurationError(f"Error loading frontend configuration: {str(e)}")

    def get_frontend_config(self):
        return self.frontend_config

    def execute_code(self, code, language):
        try:
            prompt = self.get_prompt('code_execution')
            result = self.chat(f"{prompt}\n```{language}\n{code}\n```")
            return {'success': True, 'result': result}
        except Exception as e:
            error_prompt = self.get_prompt('error_handling')
            error_response = self.chat(f"{error_prompt}\n{str(e)}")
            raise ExecutionError(f"Error executing code: {error_response}")

    def list_files(self, path):
        full_path = os.path.join(self.current_directory, path)
        try:
            files = [{'name': f, 'type': 'directory' if os.path.isdir(os.path.join(full_path, f)) else 'file'}
                     for f in os.listdir(full_path)]
            return {'success': True, 'files': files}
        except Exception as e:
            raise FileOperationError(f"Error listing files: {str(e)}")

    def read_file(self, path):
        full_path = os.path.join(self.current_directory, path)
        try:
            with open(full_path, 'r') as file:
                content = file.read()
            return {'success': True, 'content': content}
        except Exception as e:
            raise FileOperationError(f"Error reading file: {str(e)}")

    def write_file(self, path, content):
        full_path = os.path.join(self.current_directory, path)
        try:
            with open(full_path, 'w') as file:
                file.write(content)
            return {'success': True}
        except Exception as e:
            raise FileOperationError(f"Error writing file: {str(e)}")

    def delete_file(self, path):
        full_path = os.path.join(self.current_directory, path)
        try:
            if os.path.isdir(full_path):
                os.rmdir(full_path)
            else:
                os.remove(full_path)
            return {'success': True}
        except Exception as e:
            raise FileOperationError(f"Error deleting file: {str(e)}")

    def create_directory(self, path):
        full_path = os.path.join(self.current_directory, path)
        try:
            os.makedirs(full_path, exist_ok=True)
            return {'success': True}
        except Exception as e:
            raise FileOperationError(f"Error creating directory: {str(e)}")

    def update_settings(self, new_settings):
        try:
            for key, value in new_settings.items():
                if hasattr(self, key) and key not in ['temperature', 'top_p']:
                    setattr(self, key, value)
                else:
                    raise ConfigurationError(f"Unknown or restricted setting: {key}")
            return {'success': True}
        except Exception as e:
            raise ConfigurationError(f"Error updating settings: {str(e)}")

    def get_settings(self):
        try:
            return {
                'success': True,
                'settings': {
                    'max_tokens': self.max_tokens,
                    # Add any other relevant user-facing settings
                }
            }
        except Exception as e:
            raise ConfigurationError(f"Error retrieving settings: {str(e)}")

    def analyze_project(self, project_name):
        try:
            project_path = os.path.join(self.projects_directory, project_name)
            if not os.path.exists(project_path):
                raise FileOperationError(f"Project {project_name} does not exist")
            
            analyzer = ProjectAnalyzer(project_path)
            report = analyzer.generate_report()
            return {'success': True, 'report': json.loads(report)}
        except Exception as e:
            raise ExecutionError(f"Error analyzing project: {str(e)}")

    def stream_chat(self, message):
        try:
            for token in self.chat(message, stream=True):
                yield token
        except Exception as e:
            raise ExecutionError(f"Error in chat stream: {str(e)}")

    def set_current_directory(self, path):
        full_path = os.path.abspath(path)
        if os.path.isdir(full_path):
            self.current_directory = full_path
            return {'success': True, 'path': full_path}
        else:
            raise FileOperationError(f"Invalid directory path: {path}")

    def get_current_directory(self):
        return {'success': True, 'path': self.current_directory}

    def get_projects(self):
        try:
            projects = [d for d in os.listdir(self.projects_directory) 
                        if os.path.isdir(os.path.join(self.projects_directory, d))]
            return {'success': True, 'projects': projects}
        except Exception as e:
            raise FileOperationError(f"Error getting projects: {str(e)}")

    def set_current_project(self, project_name):
        try:
            project_dir = os.path.join(self.projects_directory, project_name)
            if not os.path.isdir(project_dir):
                os.makedirs(project_dir)
            self.current_project = project_name
            self.load_project_settings()
            return {'success': True, 'project': project_name}
        except Exception as e:
            raise ConfigurationError(f"Error setting current project: {str(e)}")

    def get_current_project(self):
        return {'success': True, 'project': self.current_project}

    def delete_project(self, project_name):
        try:
            project_dir = os.path.join(self.projects_directory, project_name)
            if os.path.isdir(project_dir):
                shutil.rmtree(project_dir)
            if self.current_project == project_name:
                self.current_project = None
                self.project_settings = {}
            return {'success': True}
        except Exception as e:
            raise FileOperationError(f"Error deleting project: {str(e)}")

    def load_project_settings(self):
        if not self.current_project:
            raise ConfigurationError("No project is currently set")
        try:
            settings_path = os.path.join(self.projects_directory, self.current_project, 'project_settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    self.project_settings = json.load(f)
            else:
                self.project_settings = {}
            return {'success': True, 'settings': self.project_settings}
        except Exception as e:
            raise ConfigurationError(f"Error loading project settings: {str(e)}")

    def save_project_settings(self):
        if not self.current_project:
            raise ConfigurationError("No project is currently set")
        try:
            settings_path = os.path.join(self.projects_directory, self.current_project, 'project_settings.json')
            with open(settings_path, 'w') as f:
                json.dump(self.project_settings, f, indent=2)
            return {'success': True}
        except Exception as e:
            raise ConfigurationError(f"Error saving project settings: {str(e)}")

    def update_project_settings(self, project_name, new_settings):
        try:
            self.set_current_project(project_name)
            self.project_settings.update(new_settings)
            self.save_project_settings()
            return {'success': True, 'settings': self.project_settings}
        except Exception as e:
            raise ConfigurationError(f"Error updating project settings: {str(e)}")

    def get_project_settings(self, project_name):
        try:
            self.set_current_project(project_name)
            return {'success': True, 'settings': self.project_settings}
        except Exception as e:
            raise ConfigurationError(f"Error getting project settings: {str(e)}")

    def get_project_prompts(self, project_name):
        try:
            self.set_current_project(project_name)
            prompts_path = os.path.join(self.projects_directory, project_name, 'prompts.json')
            if os.path.exists(prompts_path):
                with open(prompts_path, 'r') as f:
                    prompts = json.load(f)
            else:
                prompts = self.default_prompts.copy()
            return {'success': True, 'prompts': prompts}
        except Exception as e:
            raise ConfigurationError(f"Error getting project prompts: {str(e)}")

    def update_project_prompts(self, project_name, new_prompts):
        try:
            self.set_current_project(project_name)
            prompts_path = os.path.join(self.projects_directory, project_name, 'prompts.json')
            current_prompts = self.default_prompts.copy()
            if os.path.exists(prompts_path):
                with open(prompts_path, 'r') as f:
                    current_prompts.update(json.load(f))
            current_prompts.update(new_prompts)
            with open(prompts_path, 'w') as f:
                json.dump(current_prompts, f, indent=2)
            return {'success': True, 'prompts': current_prompts}
        except Exception as e:
            raise ConfigurationError(f"Error updating project prompts: {str(e)}")

    def get_prompt(self, prompt_key):
        if not self.current_project:
            return self.default_prompts.get(prompt_key, "")
        prompts_path = os.path.join(self.projects_directory, self.current_project, 'prompts.json')
        if os.path.exists(prompts_path):
            with open(prompts_path, 'r') as f:
                prompts = json.load(f)
            return prompts.get(prompt_key, self.default_prompts.get(prompt_key, ""))
        return self.default_prompts.get(prompt_key, "")

    def chat(self, message, stream=False):
        system_message = self.get_prompt('system_message')
        # Use environment variables for temperature and top_p
        temperature = float(os.environ.get('TEMPERATURE', 0.2))
        top_p = float(os.environ.get('TOP_P', 0.1))
        return super().chat(f"{system_message}\n\nUser: {message}", stream=stream, temperature=temperature, top_p=top_p)

# Add any other methods specific to the extended functionality