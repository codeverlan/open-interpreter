```python
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

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s')
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
        logger.info(f"Requested path: {path}")
        log_handler.add_log(f"[INFO] [API] Requested path: {path}")
        if path.startswith('api/'):
            return handle_api_request(path)
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            logger.info(f"Serving file: {os.path.join(app.static_folder, path)}")
            return send_from_directory(app.static_folder, path)
        else:
            logger.info(f"Serving index.html")
            return send_from_directory(app.static_folder, 'index.html')

    @app.route('/api/log', methods=['POST'])
    def log_api():
        log_data = request.json
        logger.info(f"Received log: {log_data}")
        log_handler.add_log(f"[INFO] [API] Received log: {json.dumps(log_data)}")
        return jsonify({"success": True, "message": "Log received"})

    @app.route('/api/get_logs', methods=['GET'])
    def get_logs():
        level = request.args.get('level')
        module = request.args.get('module')
        keyword = request.args.get('keyword')

        if level:
            logs = log_handler.get_logs_by_level(level)
        elif module:
            logs = log_handler.get_logs_by_module(module)
        elif keyword:
            logs = log_handler.search_logs(keyword)
        else:
            logs = log_handler.get_recent_logs()

        return jsonify({"success": True, "logs": logs})

    # Agent-related endpoints
    @app.route('/api/agents', methods=['POST'])
    def create_agent():
        data = request.json
        new_agent = Agent(
            name=data['name'],
            description=data.get('description', ''),
            prompt=data.get('prompt', ''),
            ai_model=data.get('ai_model', ''),
            skills=data.get('skills', [])
        )
        agent_id = db.add_agent(new_agent)
        new_agent.id = agent_id  # Assign the ID returned from the database
        logger.info(f"Created new agent with ID {agent_id}")
        log_handler.add_log(f"[INFO] [API] Created new agent with ID {agent_id}")
        return jsonify({"success": True, "agent_id": agent_id})

    @app.route('/api/agents', methods=['GET'])
    def get_agents():
        agents = db.get_all_agents()
        agent_list = [agent.to_dict() for agent in agents]
        logger.info(f"Retrieved list of agents")
        log_handler.add_log(f"[INFO] [API] Retrieved list of agents")
        return jsonify({"success": True, "agents": agent_list})

    @app.route('/api/agents/<int:agent_id>', methods=['GET'])
    def get_agent(agent_id):
        agent = db.get_agent(agent_id)
        if agent:
            logger.info(f"Retrieved agent with ID {agent_id}")
            log_handler.add_log(f"[INFO] [API] Retrieved agent with ID {agent_id}")
            return jsonify({"success": True, "agent": agent.to_dict()})
        else:
            logger.warning(f"Agent with ID {agent_id} not found")
            log_handler.add_log(f"[WARNING] [API] Agent with ID {agent_id} not found")
            return jsonify({"success": False, "error": "Agent not found"}), 404

    @app.route('/api/agents/<int:agent_id>', methods=['PUT'])
    def update_agent(agent_id):
        data = request.json
        agent = db.get_agent(agent_id)
        if agent:
            agent.name = data.get('name', agent.name)
            agent.description = data.get('description', agent.description)
            agent.prompt = data.get('prompt', agent.prompt)
            agent.ai_model = data.get('ai_model', agent.ai_model)
            agent.skills = data.get('skills', agent.skills)
            db.update_agent(agent)
            logger.info(f"Updated agent with ID {agent_id}")
            log_handler.add_log(f"[INFO] [API] Updated agent with ID {agent_id}")
            return jsonify({"success": True, "agent": agent.to_dict()})
        else:
            logger.warning(f"Agent with ID {agent_id} not found")
            log_handler.add_log(f"[WARNING] [API] Agent with ID {agent_id} not found")
            return jsonify({"success": False, "error": "Agent not found"}), 404

    @app.route('/api/agents/<int:agent_id>', methods=['DELETE'])
    def delete_agent(agent_id):
        agent = db.get_agent(agent_id)
        if agent:
            db.delete_agent(agent_id)
            logger.info(f"Deleted agent with ID {agent_id}")
            log_handler.add_log(f"[INFO] [API] Deleted agent with ID {agent_id}")
            return jsonify({"success": True, "message": f"Agent {agent_id} deleted"})
        else:
            logger.warning(f"Agent with ID {agent_id} not found")
            log_handler.add_log(f"[WARNING] [API] Agent with ID {agent_id} not found")
            return jsonify({"success": False, "error": "Agent not found"}), 404

    @app.route('/api/agents/<int:agent_id>/feedback', methods=['POST'])
    def submit_feedback(agent_id):
        feedback_data = request.json
        agent = db.get_agent(agent_id)
        if agent:
            # Assume there's a method to handle feedback
            db.add_feedback_to_agent(agent_id, feedback_data['content'])
            logger.info(f"Feedback submitted for agent with ID {agent_id}")
            log_handler.add_log(f"[INFO] [API] Feedback submitted for agent with ID {agent_id}")
            return jsonify({"success": True, "message": "Feedback submitted successfully"})
        else:
            logger.warning(f"Agent with ID {agent_id} not found")
            log_handler.add_log(f"[WARNING] [API] Agent with ID {agent_id} not found")
            return jsonify({"success": False, "error": "Agent not found"}), 404

    # Additional endpoints...

    def handle_api_request(path):
        # Implementation for handling other API requests
        pass

    return app

def start_server(port=5159):
    app = create_app()
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    logger.info(f"Static folder: {app.static_folder}")
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

if __name__ == '__main__':
    start_server()
```