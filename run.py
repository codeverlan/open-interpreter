import os
import subprocess
import sys
from dotenv import load_dotenv
from interpreter.extended_interpreter import ExtendedInterpreter
from interpreter.server.api import start_server

# Load environment variables
load_dotenv()

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

        # Get the port number from the environment variable, with a default of 5159
        port = int(os.getenv('SERVER_PORT', 5159))

        # Initialize the ExtendedInterpreter
        interpreter = ExtendedInterpreter(server_port=port)

        # Start the server
        start_server(port=port)
    finally:
        # Change back to the original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    main()