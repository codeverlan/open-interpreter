import os
import subprocess
from interpreter.extended_interpreter import ExtendedInterpreter

def build_react_app():
    os.chdir('interpreter/frontend')
    subprocess.run(['npm', 'install'], check=True)
    subprocess.run(['npm', 'run', 'build'], check=True)
    os.chdir('../..')

def main():
    # Build the React app
    build_react_app()

    # Initialize and start the ExtendedInterpreter
    interpreter = ExtendedInterpreter(server_port=5000)
    interpreter.load_frontend_config('frontend_config.yaml')  # You can create this file for frontend-specific settings
    interpreter.start_server()

if __name__ == "__main__":
    main()