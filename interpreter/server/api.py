from flask import Flask, send_from_directory, jsonify, request, Response
import os
import json

from interpreter.exceptions import InterpreterError, ConfigurationError, FileOperationError, ExecutionError
from interpreter.core.models.prompt import Prompt
from interpreter.core.database import Database

def create_app(interpreter):
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build'))
    app = Flask(__name__, static_folder=static_folder)
    db = Database()

    @app.errorhandler(InterpreterError)
    def handle_interpreter_error(error):
        response = jsonify({
            'success': False,
            'error': str(error),
            'error_type': error.__class__.__name__
        })
        response.status_code = 400
        return response

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        print(f"Requested path: {path}")
        if path.startswith('api/'):
            return handle_api_request(path)
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            print(f"Serving file: {os.path.join(app.static_folder, path)}")
            return send_from_directory(app.static_folder, path)
        else:
            print(f"Serving index.html")
            return send_from_directory(app.static_folder, 'index.html')

    @app.route('/api/log', methods=['POST'])
    def log_api():
        log_data = request.json
        print(f"Received log: {log_data}")
        return jsonify({"success": True, "message": "Log received"})

    def handle_api_request(path):
        if path == 'api/get_projects':
            response = interpreter.get_projects()
            print(f"API response for get_projects: {json.dumps(response, indent=2)}")
            return jsonify(response)
        elif path == 'api/get_settings':
            response = interpreter.get_settings()
            print(f"API response for get_settings: {json.dumps(response, indent=2)}")
            return jsonify(response)
        elif path == 'api/list_files':
            path = request.args.get('path', '/')
            try:
                files = os.listdir(path)
                response = {
                    'success': True,
                    'files': files
                }
                print(f"API response for list_files: {json.dumps(response, indent=2)}")
                return jsonify(response)
            except Exception as e:
                response = {
                    'success': False,
                    'error': str(e)
                }
                print(f"API error for list_files: {json.dumps(response, indent=2)}")
                return jsonify(response), 400
        elif path.startswith('api/projects/'):
            return handle_prompt_request(path)
        else:
            return jsonify({'error': 'Invalid API endpoint'}), 404

    def handle_prompt_request(path):
        parts = path.split('/')
        if len(parts) < 4:
            return jsonify({'error': 'Invalid API endpoint'}), 404

        project_id = parts[3]
        
        if len(parts) == 4 and request.method == 'GET':
            # GET /api/projects/<project_id>/prompts
            prompts = db.get_prompts_for_project(project_id)
            return jsonify({'success': True, 'prompts': [p.to_dict() for p in prompts]})
        
        elif len(parts) == 4 and request.method == 'POST':
            # POST /api/projects/<project_id>/prompts
            data = request.json
            new_prompt = Prompt(id=None, project_id=project_id, name=data['name'], content=data['content'])
            prompt_id = db.add_prompt(new_prompt)
            return jsonify({'success': True, 'prompt_id': prompt_id})
        
        elif len(parts) == 5:
            prompt_id = int(parts[4])
            
            if request.method == 'GET':
                # GET /api/projects/<project_id>/prompts/<prompt_id>
                prompt = db.get_prompt(prompt_id)
                if prompt and prompt.project_id == project_id:
                    return jsonify({'success': True, 'prompt': prompt.to_dict()})
                else:
                    return jsonify({'error': 'Prompt not found'}), 404
            
            elif request.method == 'PUT':
                # PUT /api/projects/<project_id>/prompts/<prompt_id>
                data = request.json
                prompt = db.get_prompt(prompt_id)
                if prompt and prompt.project_id == project_id:
                    prompt.name = data['name']
                    prompt.content = data['content']
                    db.update_prompt(prompt)
                    return jsonify({'success': True})
                else:
                    return jsonify({'error': 'Prompt not found'}), 404
            
            elif request.method == 'DELETE':
                # DELETE /api/projects/<project_id>/prompts/<prompt_id>
                prompt = db.get_prompt(prompt_id)
                if prompt and prompt.project_id == project_id:
                    db.delete_prompt(prompt_id)
                    return jsonify({'success': True})
                else:
                    return jsonify({'error': 'Prompt not found'}), 404

        return jsonify({'error': 'Invalid API endpoint'}), 404

    return app

def start_server(interpreter, port=5159):
    app = create_app(interpreter)
    print(f"Starting server on http://0.0.0.0:{port}")
    print(f"Static folder: {app.static_folder}")
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
            # Assuming we have a method to get all unique project IDs
            project_ids = self.db.get_all_project_ids()
            projects = [{"id": pid, "name": f"Project {pid}"} for pid in project_ids]
            return {"success": True, "projects": projects}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_settings(self):
        return {"success": True, "settings": self.settings}

if __name__ == '__main__':
    interpreter = OpenInterpreter()
    start_server(interpreter)