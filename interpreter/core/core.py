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
from flask_sqlalchemy import SQLAlchemy
import logging
import sys
import subprocess
import uuid

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
from interpreter.core.agent import Agent
from interpreter.core.environment import Environment
from interpreter.core.skill import TEMPERATURE_CONTROL, HUMIDITY_CONTROL

# Update the static_folder to point to the correct build directory
app = Flask(__name__, static_folder='/root/open/interpreter/frontend/build', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////root/open/interpreter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the Project model
class Project(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    directory = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    agents = db.relationship('AgentModel', backref='project', lazy=True)
    docs = db.relationship('Document', backref='project', lazy=True)
    outlines = db.relationship('Outline', backref='project', lazy=True)
    prompts = db.relationship('Prompt', backref='project', lazy=True)
    terminal_outputs = db.relationship('TerminalOutput', backref='project', lazy=True)
    settings = db.relationship('Setting', backref='project', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'directory': self.directory,
            'created_at': self.created_at.isoformat()
        }

class AgentModel(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat()
        }

class Document(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat()
        }

class Outline(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat()
        }

class Prompt(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat()
        }

class TerminalOutput(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat()
        }

class Setting(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat()
        }

class OpenInterpreter:
    def __init__(self):
        self.config = {}  # Initialize config as an empty dictionary
        self.agent = None
        self.environment = None
        self.projects_dir = '/root/open/projects'  # Directory to store project folders

    def start_server(self, host='0.0.0.0', port=5159):
        """
        Starts the Flask server to serve the React front-end and handle API requests.
        """
        with app.app_context():
            # Create the database tables
            db.create_all()

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
                return jsonify({"success": True, "message": "Log received"})
            except Exception as e:
                logger.error(f"Error in log_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/get_settings', methods=['GET'])
        def get_settings_api():
            try:
                logger.info("Received get_settings request")
                project_id = request.args.get('project_id')
                if not project_id:
                    return jsonify({"success": False, "error": "Project ID is required"}), 400
                settings = Setting.query.filter_by(project_id=project_id).all()
                return jsonify({"success": True, "settings": {s.key: s.value for s in settings}})
            except Exception as e:
                logger.error(f"Error in get_settings_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/get_projects', methods=['GET'])
        def get_projects_api():
            try:
                logger.info("Received get_projects request")
                projects = Project.query.all()
                return jsonify({"success": True, "projects": [project.to_dict() for project in projects]})
            except Exception as e:
                logger.error(f"Error in get_projects_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/create_project', methods=['POST'])
        def create_project_api():
            try:
                logger.info("Received create_project request")
                data = request.json
                project_name = data.get('name')
                if not project_name:
                    return jsonify({"success": False, "error": "Project name is required"}), 400

                # Create a safe directory name
                safe_dir_name = "".join([c for c in project_name if c.isalnum() or c in (' ', '-', '_')]).rstrip()
                project_dir = os.path.join(self.projects_dir, safe_dir_name)

                # Check if the project directory already exists
                if os.path.exists(project_dir):
                    return jsonify({"success": False, "error": "A project with this name already exists"}), 400

                # Create the project directory
                os.makedirs(project_dir)

                # Create a new Project instance
                new_project = Project(
                    name=project_name,
                    directory=project_dir
                )

                # Add the new project to the database
                db.session.add(new_project)
                db.session.commit()

                return jsonify({"success": True, "project": new_project.to_dict()})
            except Exception as e:
                logger.error(f"Error in create_project_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/list_files', methods=['GET'])
        def list_files_api():
            try:
                logger.info("Received list_files request")
                project_id = request.args.get('project_id')
                if not project_id:
                    return jsonify({"success": False, "error": "Project ID is required"}), 400
                
                project = Project.query.get(project_id)
                if not project:
                    return jsonify({"success": False, "error": "Project not found"}), 404

                path = request.args.get('path', '/')
                full_path = os.path.join(project.directory, path.lstrip('/'))
                
                if not os.path.exists(full_path):
                    return jsonify({"success": False, "error": "Path not found"}), 404

                files = []
                for item in os.listdir(full_path):
                    item_path = os.path.join(full_path, item)
                    files.append({
                        "name": item,
                        "type": "directory" if os.path.isdir(item_path) else "file"
                    })

                return jsonify({"success": True, "files": files})
            except Exception as e:
                logger.error(f"Error in list_files_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/get_project_documentation', methods=['GET'])
        def get_project_documentation_api():
            try:
                logger.info("Received get_project_documentation request")
                project_id = request.args.get('project_id')
                if not project_id:
                    return jsonify({"success": False, "error": "Project ID is required"}), 400
                
                docs = Document.query.filter_by(project_id=project_id).all()
                return jsonify({"success": True, "documentation": [doc.to_dict() for doc in docs]})
            except Exception as e:
                logger.error(f"Error in get_project_documentation_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/get_project_outline', methods=['GET'])
        def get_project_outline_api():
            try:
                logger.info("Received get_project_outline request")
                project_id = request.args.get('project_id')
                if not project_id:
                    return jsonify({"success": False, "error": "Project ID is required"}), 400
                
                outline = Outline.query.filter_by(project_id=project_id).first()
                if not outline:
                    return jsonify({"success": False, "error": "Outline not found"}), 404
                
                return jsonify({"success": True, "outline": outline.to_dict()})
            except Exception as e:
                logger.error(f"Error in get_project_outline_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/update_project_outline', methods=['POST'])
        def update_project_outline_api():
            try:
                logger.info("Received update_project_outline request")
                data = request.json
                project_id = data.get('project_id')
                outline_content = data.get('outline')
                if not project_id or not outline_content:
                    return jsonify({"success": False, "error": "Missing project_id or outline"}), 400
                
                outline = Outline.query.filter_by(project_id=project_id).first()
                if outline:
                    outline.content = outline_content
                else:
                    outline = Outline(project_id=project_id, content=outline_content)
                    db.session.add(outline)
                
                db.session.commit()
                return jsonify({"success": True, "message": "Project outline updated successfully"})
            except Exception as e:
                logger.error(f"Error in update_project_outline_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/get_logs', methods=['GET'])
        def get_logs_api():
            try:
                logger.info("Received get_logs request")
                project_id = request.args.get('project_id')
                if not project_id:
                    return jsonify({"success": False, "error": "Project ID is required"}), 400
                
                logs = TerminalOutput.query.filter_by(project_id=project_id).order_by(TerminalOutput.created_at.desc()).all()
                return jsonify({"success": True, "logs": [log.to_dict() for log in logs]})
            except Exception as e:
                logger.error(f"Error in get_logs_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/execute_command', methods=['POST'])
        def execute_command_api():
            try:
                logger.info("Received execute_command request")
                data = request.json
                project_id = data.get('project_id')
                command = data.get('command')
                if not project_id or not command:
                    return jsonify({"success": False, "error": "Missing project_id or command"}), 400
                
                project = Project.query.get(project_id)
                if not project:
                    return jsonify({"success": False, "error": "Project not found"}), 404
                
                # Execute the command and capture the output
                result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=project.directory)
                
                # Save the output to the database
                output = TerminalOutput(project_id=project_id, content=result.stdout + result.stderr)
                db.session.add(output)
                db.session.commit()
                
                return jsonify({
                    "success": True,
                    "output": result.stdout,
                    "error": result.stderr,
                    "returncode": result.returncode
                })
            except Exception as e:
                logger.error(f"Error in execute_command_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/agents', methods=['GET'])
        def get_agents_api():
            try:
                logger.info("Received get_agents request")
                project_id = request.args.get('project_id')
                if not project_id:
                    return jsonify({"success": False, "error": "Project ID is required"}), 400
                
                agents = AgentModel.query.filter_by(project_id=project_id).all()
                return jsonify({"success": True, "agents": [agent.to_dict() for agent in agents]})
            except Exception as e:
                logger.error(f"Error in get_agents_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/agents', methods=['POST'])
        def create_agent_api():
            try:
                logger.info("Received create_agent request")
                data = request.json
                project_id = data.get('project_id')
                name = data.get('name')
                description = data.get('description')
                if not project_id or not name:
                    return jsonify({"success": False, "error": "Missing project_id or name"}), 400
                
                new_agent = AgentModel(project_id=project_id, name=name, description=description)
                db.session.add(new_agent)
                db.session.commit()
                return jsonify({"success": True, "agent": new_agent.to_dict()})
            except Exception as e:
                logger.error(f"Error in create_agent_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/agents/<agent_id>', methods=['PUT'])
        def update_agent_api(agent_id):
            try:
                logger.info(f"Received update_agent request for agent {agent_id}")
                data = request.json
                agent = AgentModel.query.get(agent_id)
                if not agent:
                    return jsonify({"success": False, "error": "Agent not found"}), 404
                
                agent.name = data.get('name', agent.name)
                agent.description = data.get('description', agent.description)
                db.session.commit()
                return jsonify({"success": True, "agent": agent.to_dict()})
            except Exception as e:
                logger.error(f"Error in update_agent_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/agents/<agent_id>', methods=['DELETE'])
        def delete_agent_api(agent_id):
            try:
                logger.info(f"Received delete_agent request for agent {agent_id}")
                agent = AgentModel.query.get(agent_id)
                if not agent:
                    return jsonify({"success": False, "error": "Agent not found"}), 404
                
                db.session.delete(agent)
                db.session.commit()
                return jsonify({"success": True, "message": "Agent deleted successfully"})
            except Exception as e:
                logger.error(f"Error in delete_agent_api: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        logger.info(f"Starting server on http://{host}:{port}")
        app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    interpreter = OpenInterpreter()
    interpreter.start_server()
