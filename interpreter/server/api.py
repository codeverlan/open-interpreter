from flask import Flask, send_from_directory, jsonify, request, Response
import os
import json

from ..exceptions import InterpreterError, ConfigurationError, FileOperationError, ExecutionError

def create_app(interpreter):
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build'))
    app = Flask(__name__, static_folder=static_folder)

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
        else:
            return jsonify({'error': 'Invalid API endpoint'}), 404

    return app

def start_server(interpreter, port=5159):
    app = create_app(interpreter)
    print(f"Starting server on http://0.0.0.0:{port}")
    print(f"Static folder: {app.static_folder}")
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)