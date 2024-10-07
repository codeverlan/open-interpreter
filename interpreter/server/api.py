# /root/open/interpreter/server/api.py

import logging
from flask import Flask, send_from_directory, jsonify, request, Response
import os
import json
from dotenv import load_dotenv

from interpreter.exceptions import InterpreterError
from interpreter.core.models.prompt import Prompt
from interpreter.core.database import Database
from interpreter.core.log_handler import LogHandler
from interpreter.core.agent import Agent
from interpreter.core.anthropic_client import anthropic_client
from interpreter.core.openrouter_client import openrouter_client

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build'))
    app = Flask(__name__, static_folder=static_folder)
    db = Database()
    log_handler = LogHandler()

    # Get the log file path from environment variable or use a default
    log_file_path = os.getenv('OPEN_INTERPRETER_LOG_PATH', '/root/open/data/api_logs.txt')

    # Write logs to a file
    with open(log_file_path, 'w') as f:
        f.write(f"Current logs: {json.dumps(log_handler.logs, indent=2)}\n")

    @app.errorhandler(InterpreterError)
    def handle_interpreter_error(error):
        response = jsonify({
            'success': False,
            'error': str(error),
            'error_type': error.__class__.__name__
        })
        response.status_code = 400
        logger.error(f"InterpreterError: {str(error)}")
        log_handler.add_log(f"[ERROR] [API] InterpreterError: {str(error)}")
        return response

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        logger.debug(f"Requested path: {path}")
        logger.debug(f"Static folder: {app.static_folder}")
        log_handler.add_log(f"[DEBUG] [API] Requested path: {path}")
        
        if path.startswith('api/'):
            logger.debug(f"Handling API request: {path}")
            return handle_api_request(path)
        
        file_path = os.path.join(app.static_folder, path)
        logger.debug(f"Checking file path: {file_path}")
        
        if path != "" and os.path.exists(file_path):
            logger.debug(f"Serving file: {file_path}")
            return send_from_directory(app.static_folder, path)
        else:
            index_path = os.path.join(app.static_folder, 'index.html')
            logger.debug(f"Serving index.html: {index_path}")
            if os.path.exists(index_path):
                return send_from_directory(app.static_folder, 'index.html')
            else:
                logger.error(f"index.html not found at {index_path}")
                return "index.html not found", 404

    @app.route('/api/log', methods=['POST'])
    def log_api():
        log_data = request.json
        logger.info(f"Received log: {log_data}")
        log_handler.add_log(f"[INFO] [API] Received log: {json.dumps(log_data)}")
        return jsonify({"success": True, "message": "Log received"})

    @app.route('/api/get_settings', methods=['GET'])
    def get_settings():
        # Implement get_settings logic here
        return jsonify({"success": True, "settings": {}})

    @app.route('/api/get_projects', methods=['GET'])
    def get_projects():
        # Implement get_projects logic here
        return jsonify({"success": True, "projects": []})

    @app.route('/api/ai_models', methods=['GET'])
    def get_ai_models():
        # Implement get_ai_models logic here
        return jsonify({"success": True, "models": []})

    @app.route('/api/test_anthropic', methods=['GET'])
    def test_anthropic():
        success, message = anthropic_client.test_api()
        logger.info(f"Anthropic API test result: success={success}, message={message}")
        return jsonify({"success": success, "message": message})

    @app.route('/api/test_openrouter', methods=['GET'])
    def test_openrouter():
        success, message = openrouter_client.test_api()
        logger.info(f"OpenRouter API test result: success={success}, message={message}")
        return jsonify({"success": success, "message": message})

    def handle_api_request(path):
        # This function should handle all API requests
        # You can add more specific handling based on the path
        return jsonify({"error": "Not implemented"}), 501

    return app

def start_server(port=5159):
    app = create_app()
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    logger.info(f"Static folder: {app.static_folder}")
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

if __name__ == '__main__':
    start_server()