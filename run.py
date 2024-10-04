import os
import subprocess
import sys
from interpreter.extended_interpreter import ExtendedInterpreter
from interpreter.server.api import start_server

def install_python_dependencies():
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def build_react_app():
    os.chdir('interpreter/frontend')
    subprocess.run(['npm', 'install'], check=True)
    subprocess.run(['npm', 'run', 'build'], check=True)
    os.chdir('../..')

def main():
    # Store the original directory
    original_dir = os.getcwd()

    # Change to the 'open' directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    try:
        # Install Python dependencies
        install_python_dependencies()

        # Build the React app
        build_react_app()

        # Initialize the ExtendedInterpreter
        interpreter = ExtendedInterpreter(server_port=5159)

        # Start the server
        start_server(interpreter, port=5159)
    finally:
        # Change back to the original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    main()