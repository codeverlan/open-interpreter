import yaml
from .core.core import OpenInterpreter
from .server.api import start_server

class ExtendedInterpreter(OpenInterpreter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server_port = kwargs.get('server_port', 5000)
        self.frontend_config = {}

    def start_server(self):
        start_server(self, port=self.server_port)

    def load_frontend_config(self, config_path):
        try:
            with open(config_path, 'r') as config_file:
                self.frontend_config = yaml.safe_load(config_file)
        except Exception as e:
            print(f"Error loading frontend configuration: {e}")

    def get_frontend_config(self):
        return self.frontend_config

    # Add any other methods specific to the extended functionality