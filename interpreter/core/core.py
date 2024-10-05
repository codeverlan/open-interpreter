"""
This file defines the Interpreter class and includes a Flask server to serve the React front-end.
"""
import json
import os
import threading
import time
from datetime import datetime
import yaml
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import logging
import sys

# Add the project root to the Python path
sys.path.append('/root/open')

from interpreter.terminal_interface.local_setup import local_setup
from interpreter.terminal_interface.terminal_interface import terminal_interface
from interpreter.terminal_interface.utils.display_markdown_message import display_markdown_message
from interpreter.terminal_interface.utils.local_storage_path import get_storage_path
from interpreter.terminal_interface.utils.oi_dir import oi_dir
from interpreter.core.computer.computer import Computer
from interpreter.core.default_system_message import default_system_message
from interpreter.core.llm.llm import Llm
from interpreter.core.respond import respond
from interpreter.core.utils.telemetry import send_telemetry
from interpreter.core.utils.truncate_output import truncate_output

# Update the static_folder to point to the correct build directory
app = Flask(__name__, static_folder='/root/open/interpreter/frontend/build', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for client logs
client_logs = []

class OpenInterpreter:
    def __init__(self):
        self.config = {}  # Initialize config as an empty dictionary

    def start_server(self, host='0.0.0.0', port=5159):
        """
        Starts the Flask server to serve the React front-end and handle API requests.
        """
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve(path):
            if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            else:
                return send_from_directory(app.static_folder, 'index.html')

        @app.route('/api/log', methods=['POST'])
        def log_api():
            try:
                log_data = request.json
                logger.info(f"Received client log: {log_data}")
                client_logs.append(log_data)
                return jsonify({"success": True, "message": "Log received"})
            except Exception as e:
                logger.error(f"Error in log_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/get_settings', methods=['GET'])
        def get_settings_api():
            try:
                logger.info("Received get_settings request")
                return jsonify({"success": True, "settings": self.config})
            except Exception as e:
                logger.error(f"Error in get_settings_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/get_projects', methods=['GET'])
        def get_projects_api():
            try:
                logger.info("Received get_projects request")
                # Implement the logic to get projects here
                # For now, we'll return a dummy list
                projects = ["Project 1", "Project 2", "Project 3"]
                return jsonify({"success": True, "projects": projects})
            except Exception as e:
                logger.error(f"Error in get_projects_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/list_files', methods=['GET'])
        def list_files_api():
            try:
                logger.info("Received list_files request")
                path = request.args.get('path', '/')
                # Implement the logic to list files here
                # For now, we'll return a dummy list
                files = [
                    {"name": "file1.txt", "type": "file"},
                    {"name": "file2.txt", "type": "file"},
                    {"name": "folder1", "type": "directory"}
                ]
                return jsonify({"success": True, "files": files})
            except Exception as e:
                logger.error(f"Error in list_files_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/get_project_documentation', methods=['GET'])
        def get_project_documentation_api():
            try:
                logger.info("Received get_project_documentation request")
                project = request.args.get('project')
                # Implement the logic to get project documentation here
                # For now, we'll return a dummy response
                documentation = f"This is the documentation for {project}"
                return jsonify({"success": True, "documentation": documentation})
            except Exception as e:
                logger.error(f"Error in get_project_documentation_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/get_documentation_file_list', methods=['GET'])
        def get_documentation_file_list_api():
            try:
                logger.info("Received get_documentation_file_list request")
                project = request.args.get('project')
                # Implement the logic to get documentation file list here
                # For now, we'll return a dummy list
                file_list = [
                    "README.md",
                    "API.md",
                    "CONTRIBUTING.md"
                ]
                return jsonify({"success": True, "files": file_list})
            except Exception as e:
                logger.error(f"Error in get_documentation_file_list_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        logger.info(f"Starting server on http://{host}:{port}")
        app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    interpreter = OpenInterpreter()
    interpreter.start_server()
