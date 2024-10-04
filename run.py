import os
import subprocess
from interpreter.extended_interpreter import ExtendedInterpreter
from interpreter.server.api import start_server

def build_react_app():
    os.chdir('interpreter/frontend')
    subprocess.run(['npm', 'install'], check=True)
    subprocess.run(['npm', 'run', 'build'], check=True)
    os.chdir('../..')

def main():
    # Build the React app
    build_react_app()

    # Initialize the ExtendedInterpreter
    interpreter = ExtendedInterpreter(server_port=5000)
    interpreter.load_frontend_config('frontend_config.yaml')  # You can create this file for frontend-specific settings

    # Start the server
    start_server(interpreter, port=interpreter.server_port)

if __name__ == "__main__":
    main()