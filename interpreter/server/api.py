from flask import Flask, send_from_directory, jsonify, request
import os

def create_app(interpreter):
    app = Flask(__name__, static_folder='../../frontend/build')

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
        response = interpreter.chat(message, display=False, stream=False)
        return jsonify(response)

    @app.route('/api/run_code', methods=['POST'])
    def run_code_api():
        code = request.json.get('code')
        language = request.json.get('language', 'python')
        result = interpreter.computer.run(language, code)
        return jsonify(result)

    @app.route('/api/get_files', methods=['GET'])
    def get_files_api():
        path = request.args.get('path', '/')
        files = interpreter.computer.files.search(path)
        return jsonify(files)

    @app.route('/api/get_settings', methods=['GET'])
    def get_settings_api():
        return jsonify({
            'interpreter_config': interpreter.config,
            'frontend_config': interpreter.get_frontend_config()
        })

    @app.route('/api/update_settings', methods=['POST'])
    def update_settings_api():
        new_settings = request.json
        interpreter.config.update(new_settings.get('interpreter_config', {}))
        # You might want to add logic here to update frontend_config if needed
        return jsonify({"status": "success"})

    return app

def start_server(interpreter, port=5000):
    app = create_app(interpreter)
    print(f"Starting server on http://localhost:{port}")
    app.run(port=port)