from flask import Flask, send_from_directory, jsonify, request, Response
import os
from ..exceptions import InterpreterError, ConfigurationError, FileOperationError, ExecutionError

def create_app(interpreter):
    app = Flask(__name__, static_folder='../../frontend/build')

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
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    @app.route('/api/chat', methods=['POST'])
    def chat_api():
        message = request.json.get('message')
        def generate():
            try:
                for token in interpreter.stream_chat(message):
                    yield f"data: {token}\n\n"
            except ExecutionError as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        return Response(generate(), mimetype='text/event-stream')

    @app.route('/api/run_code', methods=['POST'])
    def run_code_api():
        code = request.json.get('code')
        language = request.json.get('language', 'python')
        result = interpreter.execute_code(code, language)
        return jsonify(result)

    @app.route('/api/list_files', methods=['GET'])
    def list_files_api():
        path = request.args.get('path', '/')
        result = interpreter.list_files(path)
        return jsonify(result)

    @app.route('/api/read_file', methods=['GET'])
    def read_file_api():
        path = request.args.get('path')
        result = interpreter.read_file(path)
        return jsonify(result)

    @app.route('/api/write_file', methods=['POST'])
    def write_file_api():
        path = request.json.get('path')
        content = request.json.get('content')
        result = interpreter.write_file(path, content)
        return jsonify(result)

    @app.route('/api/delete_file', methods=['POST'])
    def delete_file_api():
        path = request.json.get('path')
        result = interpreter.delete_file(path)
        return jsonify(result)

    @app.route('/api/create_directory', methods=['POST'])
    def create_directory_api():
        path = request.json.get('path')
        result = interpreter.create_directory(path)
        return jsonify(result)

    @app.route('/api/get_settings', methods=['GET'])
    def get_settings_api():
        interpreter_settings = interpreter.get_settings()
        frontend_config = interpreter.get_frontend_config()
        return jsonify({
            'success': True,
            'interpreter_settings': interpreter_settings.get('settings', {}),
            'frontend_config': frontend_config
        })

    @app.route('/api/update_settings', methods=['POST'])
    def update_settings_api():
        new_settings = request.json
        result = interpreter.update_settings(new_settings)
        return jsonify(result)

    @app.route('/api/analyze_project', methods=['POST'])
    def analyze_project_api():
        project_name = request.json.get('project_name')
        result = interpreter.analyze_project(project_name)
        return jsonify(result)

    @app.route('/api/set_current_directory', methods=['POST'])
    def set_current_directory_api():
        path = request.json.get('path')
        result = interpreter.set_current_directory(path)
        return jsonify(result)

    @app.route('/api/get_current_directory', methods=['GET'])
    def get_current_directory_api():
        result = interpreter.get_current_directory()
        return jsonify(result)

    @app.route('/api/get_projects', methods=['GET'])
    def get_projects_api():
        result = interpreter.get_projects()
        return jsonify(result)

    @app.route('/api/create_project', methods=['POST'])
    def create_project_api():
        project_name = request.json.get('project_name')
        result = interpreter.set_current_project(project_name)
        return jsonify(result)

    @app.route('/api/delete_project', methods=['POST'])
    def delete_project_api():
        project_name = request.json.get('project_name')
        result = interpreter.delete_project(project_name)
        return jsonify(result)

    @app.route('/api/get_project_settings', methods=['GET'])
    def get_project_settings_api():
        project_name = request.args.get('project')
        result = interpreter.get_project_settings(project_name)
        return jsonify(result)

    @app.route('/api/update_project_settings', methods=['POST'])
    def update_project_settings_api():
        project_name = request.json.get('project')
        new_settings = request.json.get('settings')
        result = interpreter.update_project_settings(project_name, new_settings)
        return jsonify(result)

    @app.route('/api/get_project_prompts', methods=['GET'])
    def get_project_prompts_api():
        project_name = request.args.get('project')
        result = interpreter.get_project_prompts(project_name)
        return jsonify(result)

    @app.route('/api/update_project_prompts', methods=['POST'])
    def update_project_prompts_api():
        project_name = request.json.get('project')
        new_prompts = request.json.get('prompts')
        result = interpreter.update_project_prompts(project_name, new_prompts)
        return jsonify(result)

    return app

def start_server(interpreter, port=5159):
    app = create_app(interpreter)
    print(f"Starting server on http://localhost:{port}")
    app.run(port=port, debug=True, threaded=True)