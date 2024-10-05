import logging
from flask import Flask, send_from_directory, jsonify, request, Response
import os
import json
from dotenv import load_dotenv

from interpreter.exceptions import InterpreterError, ConfigurationError, FileOperationError, ExecutionError
from interpreter.core.models.prompt import Prompt
from interpreter.core.database import Database
from interpreter.core.log_handler import LogHandler
from interpreter.core.agent import Agent

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s')
logger = logging.getLogger(__name__)

def create_app(interpreter):
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
        
        with open(log_file_path, 'a') as f:
            f.write(f"Current logs before filtering: {json.dumps(log_handler.logs, indent=2)}\n")
        
        if level:
            logs = log_handler.get_logs_by_level(level)
        elif module:
            logs = log_handler.get_logs_by_module(module)
        elif keyword:
            logs = log_handler.search_logs(keyword)
        else:
            logs = log_handler.get_recent_logs()
        
        with open(log_file_path, 'a') as f:
            f.write(f"Filtered logs ({level=}, {module=}, {keyword=}): {json.dumps(logs, indent=2)}\n")
        
        return jsonify({"success": True, "logs": logs})

    @app.route('/api/agents', methods=['POST'])
    def create_agent():
        data = request.json
        new_agent = Agent(
            name=data['name'],
            description=data['description'],
            prompt=data['prompt'],
            ai_model=data['ai_model']
        )
        agent_id = db.add_agent(new_agent)
        return jsonify({"success": True, "agent_id": agent_id})

    @app.route('/api/agents', methods=['GET'])
    def get_agents():
        agents = db.get_all_agents()
        return jsonify({"success": True, "agents": [agent.to_dict() for agent in agents]})

    @app.route('/api/agents/<agent_id>', methods=['GET'])
    def get_agent(agent_id):
        agent = db.get_agent(agent_id)
        if agent:
            return jsonify({"success": True, "agent": agent.to_dict()})
        else:
            return jsonify({"success": False, "error": "Agent not found"}), 404

    @app.route('/api/agents/<agent_id>', methods=['PUT'])
    def update_agent(agent_id):
        data = request.json
        agent = db.get_agent(agent_id)
        if agent:
            agent.name = data.get('name', agent.name)
            agent.description = data.get('description', agent.description)
            agent.prompt = data.get('prompt', agent.prompt)
            agent.ai_model = data.get('ai_model', agent.ai_model)
            db.update_agent(agent)
            return jsonify({"success": True, "agent": agent.to_dict()})
        else:
            return jsonify({"success": False, "error": "Agent not found"}), 404

    @app.route('/api/agents/<agent_id>', methods=['DELETE'])
    def delete_agent(agent_id):
        if db.get_agent(agent_id):
            db.delete_agent(agent_id)
            return jsonify({"success": True, "message": f"Agent {agent_id} deleted"})
        else:
            return jsonify({"success": False, "error": "Agent not found"}), 404

    @app.route('/api/agents/<agent_id>/feedback', methods=['POST'])
    def submit_feedback(agent_id):
        feedback_data = request.json
        try:
            db.add_feedback_to_agent(agent_id, feedback_data['content'])
            return jsonify({"success": True, "message": "Feedback submitted successfully"})
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 404

    @app.route('/api/project_status', methods=['GET'])
    def get_project_status():
        try:
            with open('/root/open/project_status.md', 'r') as f:
                status = f.read()
            return jsonify({"success": True, "status": status})
        except FileNotFoundError:
            return jsonify({"success": False, "error": "Project status file not found"}), 404
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/project_status', methods=['POST'])
    def update_project_status():
        data = request.json
        try:
            with open('/root/open/project_status.md', 'w') as f:
                f.write(data['status'])
            return jsonify({"success": True, "message": "Project status updated successfully"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    def handle_api_request(path):
        if path == 'api/get_projects':
            response = interpreter.get_projects()
            logger.info(f"API response for get_projects: {json.dumps(response, indent=2)}")
            log_handler.add_log(f"[INFO] [API] API response for get_projects: {json.dumps(response, indent=2)}")
            return jsonify(response)
        elif path == 'api/get_settings':
            response = interpreter.get_settings()
            logger.info(f"API response for get_settings: {json.dumps(response, indent=2)}")
            log_handler.add_log(f"[INFO] [API] API response for get_settings: {json.dumps(response, indent=2)}")
            return jsonify(response)
        elif path == 'api/list_files':
            path = request.args.get('path', '/')
            try:
                files = os.listdir(path)
                response = {
                    'success': True,
                    'files': files
                }
                logger.info(f"API response for list_files: {json.dumps(response, indent=2)}")
                log_handler.add_log(f"[INFO] [API] API response for list_files: {json.dumps(response, indent=2)}")
                return jsonify(response)
            except Exception as e:
                response = {
                    'success': False,
                    'error': str(e)
                }
                logger.error(f"API error for list_files: {json.dumps(response, indent=2)}")
                log_handler.add_log(f"[ERROR] [API] API error for list_files: {json.dumps(response, indent=2)}")
                return jsonify(response), 400
        elif path.startswith('api/projects/'):
            return handle_prompt_request(path)
        else:
            logger.warning(f"Invalid API endpoint: {path}")
            log_handler.add_log(f"[WARNING] [API] Invalid API endpoint: {path}")
            return jsonify({'error': 'Invalid API endpoint'}), 404

    def handle_prompt_request(path):
        parts = path.split('/')
        if len(parts) < 4:
            logger.warning(f"Invalid API endpoint: {path}")
            log_handler.add_log(f"[WARNING] [API] Invalid API endpoint: {path}")
            return jsonify({'error': 'Invalid API endpoint'}), 404

        project_id = parts[3]
        
        if len(parts) == 4 and request.method == 'GET':
            # GET /api/projects/<project_id>/prompts
            prompts = db.get_prompts_for_project(project_id)
            logger.info(f"Fetched prompts for project {project_id}")
            log_handler.add_log(f"[INFO] [API] Fetched prompts for project {project_id}")
            return jsonify({'success': True, 'prompts': [p.to_dict() for p in prompts]})
        
        elif len(parts) == 4 and request.method == 'POST':
            # POST /api/projects/<project_id>/prompts
            data = request.json
            new_prompt = Prompt(id=None, project_id=project_id, name=data['name'], content=data['content'],
                                is_default_system_message=data.get('is_default_system_message', False))
            prompt_id = db.add_prompt(new_prompt)
            logger.info(f"Created new prompt {prompt_id} for project {project_id}")
            log_handler.add_log(f"[INFO] [API] Created new prompt {prompt_id} for project {project_id}")
            return jsonify({'success': True, 'prompt_id': prompt_id})
        
        elif len(parts) == 5:
            if parts[4] == 'default_system_message':
                if request.method == 'GET':
                    # GET /api/projects/<project_id>/prompts/default_system_message
                    default_prompt = db.get_or_create_default_system_message(project_id)
                    logger.info(f"Fetched default system message for project {project_id}")
                    log_handler.add_log(f"[INFO] [API] Fetched default system message for project {project_id}")
                    return jsonify({'success': True, 'prompt': default_prompt.to_dict()})
                
                elif request.method == 'PUT':
                    # PUT /api/projects/<project_id>/prompts/default_system_message
                    data = request.json
                    default_prompt = db.get_or_create_default_system_message(project_id)
                    default_prompt.content = data['content']
                    db.update_prompt(default_prompt)
                    logger.info(f"Updated default system message for project {project_id}")
                    log_handler.add_log(f"[INFO] [API] Updated default system message for project {project_id}")
                    return jsonify({'success': True, 'message': 'Default system message updated successfully'})
            else:
                prompt_id = int(parts[4])
                
                if request.method == 'GET':
                    # GET /api/projects/<project_id>/prompts/<prompt_id>
                    prompt = db.get_prompt(prompt_id)
                    if prompt and prompt.project_id == project_id:
                        logger.info(f"Fetched prompt {prompt_id} for project {project_id}")
                        log_handler.add_log(f"[INFO] [API] Fetched prompt {prompt_id} for project {project_id}")
                        return jsonify({'success': True, 'prompt': prompt.to_dict()})
                    else:
                        logger.warning(f"Prompt {prompt_id} not found for project {project_id}")
                        log_handler.add_log(f"[WARNING] [API] Prompt {prompt_id} not found for project {project_id}")
                        return jsonify({'error': 'Prompt not found'}), 404
                
                elif request.method == 'PUT':
                    # PUT /api/projects/<project_id>/prompts/<prompt_id>
                    data = request.json
                    prompt = db.get_prompt(prompt_id)
                    if prompt and prompt.project_id == project_id:
                        prompt.name = data['name']
                        prompt.content = data['content']
                        prompt.is_default_system_message = data.get('is_default_system_message', prompt.is_default_system_message)
                        db.update_prompt(prompt)
                        logger.info(f"Updated prompt {prompt_id} for project {project_id}")
                        log_handler.add_log(f"[INFO] [API] Updated prompt {prompt_id} for project {project_id}")
                        return jsonify({'success': True})
                    else:
                        logger.warning(f"Prompt {prompt_id} not found for project {project_id}")
                        log_handler.add_log(f"[WARNING] [API] Prompt {prompt_id} not found for project {project_id}")
                        return jsonify({'error': 'Prompt not found'}), 404
                
                elif request.method == 'DELETE':
                    # DELETE /api/projects/<project_id>/prompts/<prompt_id>
                    prompt = db.get_prompt(prompt_id)
                    if prompt and prompt.project_id == project_id:
                        if prompt.is_default_system_message:
                            logger.warning(f"Attempted to delete default system message {prompt_id} for project {project_id}")
                            log_handler.add_log(f"[WARNING] [API] Attempted to delete default system message {prompt_id} for project {project_id}")
                            return jsonify({'error': 'Cannot delete default system message'}), 400
                        db.delete_prompt(prompt_id)
                        logger.info(f"Deleted prompt {prompt_id} for project {project_id}")
                        log_handler.add_log(f"[INFO] [API] Deleted prompt {prompt_id} for project {project_id}")
                        return jsonify({'success': True})
                    else:
                        logger.warning(f"Prompt {prompt_id} not found for project {project_id}")
                        log_handler.add_log(f"[WARNING] [API] Prompt {prompt_id} not found for project {project_id}")
                        return jsonify({'error': 'Prompt not found'}), 404

        logger.warning(f"Invalid API endpoint: {path}")
        log_handler.add_log(f"[WARNING] [API] Invalid API endpoint: {path}")
        return jsonify({'error': 'Invalid API endpoint'}), 404

    return app

def start_server(interpreter, port=5159):
    app = create_app(interpreter)
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    logger.info(f"Static folder: {app.static_folder}")
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

class OpenInterpreter:
    def __init__(self):
        self.db = Database()
        self.settings = self.load_settings()

    def load_settings(self):
        # TODO: Implement loading settings from a file or database
        return {
            "theme": "light",
            "language": "en",
            "auto_save": True
        }

    def get_projects(self):
        try:
            project_ids = self.db.get_all_project_ids()
            projects = [{"id": pid, "name": f"Project {pid}"} for pid in project_ids]
            return {"success": True, "projects": projects}
        except Exception as e:
            logger.error(f"Error in get_projects: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_settings(self):
        return {"success": True, "settings": self.settings}

if __name__ == '__main__':
    interpreter = OpenInterpreter()
    start_server(interpreter)