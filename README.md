# Open Interpreter with React Front-end

This project extends the Open Interpreter with a React front-end, providing a user-friendly interface for interacting with the interpreter.

## Features

- Chat interface for communicating with the AI
- Code editor for writing and executing code
- File browser for navigating the file system
- Settings panel for configuring the interpreter
- Agent Manager for creating, updating, and deleting AI agents
- Modular architecture for easier maintenance and updates

## Prerequisites

- Python 3.7+
- Node.js and npm

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/open-interpreter.git
   cd open-interpreter
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies:
   ```
   cd interpreter/frontend
   npm install
   cd ../..
   ```

## Running the Application

1. From the project root directory, run:
   ```
   python run.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`

## Development

The project is structured to be modular and easy to maintain:

- `extended_interpreter.py`: Extends the original OpenInterpreter class with additional functionality.
- `server/api.py`: Contains the Flask server and API endpoints.
- `frontend_config.yaml`: Configuration file for frontend-specific settings.
- `frontend/src/`: React components for the user interface.
- `docs/`: Contains documentation for various features, including the AgentManager.

To modify the API endpoints, update the routes in `interpreter/server/api.py`.
To change the front-end components, edit the files in `interpreter/frontend/src`.

## Handling Updates to the Original Open Interpreter

When the original Open Interpreter is updated:

1. Update the core Open Interpreter files in the `interpreter/core/` directory.
2. Review the changes and update `extended_interpreter.py` if necessary to maintain compatibility.
3. If there are new features or settings, update the `frontend_config.yaml` and relevant React components to incorporate these changes.

## Configuration

- `sample_config.yaml`: Contains the main configuration for the interpreter.
- `frontend_config.yaml`: Contains frontend-specific settings and API endpoint configurations.

## Documentation

Detailed documentation for specific features can be found in the `docs/` directory. For information about the Agent Manager, refer to `docs/AgentManager.md`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
