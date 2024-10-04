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

from ..terminal_interface.local_setup import local_setup
from ..terminal_interface.terminal_interface import terminal_interface
from ..terminal_interface.utils.display_markdown_message import display_markdown_message
from ..terminal_interface.utils.local_storage_path import get_storage_path
from ..terminal_interface.utils.oi_dir import oi_dir
from .computer.computer import Computer
from .default_system_message import default_system_message
from .llm.llm import Llm
from .respond import respond
from .utils.telemetry import send_telemetry
from .utils.truncate_output import truncate_output

app = Flask(__name__, static_folder='../frontend/build')

class OpenInterpreter:
    # ... [previous OpenInterpreter code remains unchanged]

    def start_server(self, port=5000):
        """
        Starts the Flask server to serve the React front-end and handle API requests.
        """
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve(path):
            if path != "" and os.path.exists(app.static_folder + '/' + path):
                return send_from_directory(app.static_folder, path)
            else:
                return send_from_directory(app.static_folder, 'index.html')

        @app.route('/api/chat', methods=['POST'])
        def chat_api():
            message = request.json.get('message')
            response = self.chat(message, display=False, stream=False)
            return jsonify(response)

        @app.route('/api/run_code', methods=['POST'])
        def run_code_api():
            code = request.json.get('code')
            language = request.json.get('language', 'python')
            result = self.computer.run(language, code)
            return jsonify(result)

        @app.route('/api/get_files', methods=['GET'])
        def get_files_api():
            path = request.args.get('path', '/')
            files = self.computer.files.search(path)
            return jsonify(files)

        @app.route('/api/get_settings', methods=['GET'])
        def get_settings_api():
            return jsonify(self.config)

        @app.route('/api/update_settings', methods=['POST'])
        def update_settings_api():
            new_settings = request.json
            self.config.update(new_settings)
            return jsonify({"status": "success"})

        print(f"Starting server on http://localhost:{port}")
        app.run(port=port)

# ... [rest of the file remains unchanged]
