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
from flask_migrate import Migrate
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
from interpreter.core.openrouter_client import OpenRouterClient
from interpreter.core.task_assignment import TaskAssignmentSystem

# Update the static_folder to point to the correct build directory
app = Flask(__name__, static_folder='/root/open/interpreter/frontend/build', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////root/open/interpreter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

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
    assigned_model = db.Column(db.String(100))
    capabilities = db.Column(db.Text)  # Store capabilities as a JSON string
    is_lead_agent = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat(),
            'assigned_model': self.assigned_model,
            'capabilities': json.loads(self.capabilities) if self.capabilities else [],
            'is_lead_agent': self.is_lead_agent
        }

# ... (keep other model definitions)

class OpenInterpreter:
    def __init__(self):
        self.config = {}  # Initialize config as an empty dictionary
        self.agent = None
        self.environment = None
        self.projects_dir = '/root/open/projects'  # Directory to store project folders
        self.openrouter_client = None
        self.task_assignment_system = None
        self.lead_agent = None

    def initialize_openrouter_client(self):
        with app.app_context():
            api_key_setting = Setting.query.filter_by(key='openrouter_api_key').first()
            if api_key_setting:
                self.openrouter_client = OpenRouterClient()
                self.openrouter_client.set_api_key(api_key_setting.value)
            else:
                logger.warning("OpenRouter API key not found in settings")

    def initialize_task_assignment_system(self):
        with app.app_context():
            lead_agent_model = AgentModel.query.filter_by(is_lead_agent=True).first()
            if not lead_agent_model:
                # Create a new lead agent if one doesn't exist
                lead_agent_model = AgentModel(
                    name="Lead Agent",
                    description="Lead agent for task assignment",
                    project_id=Project.query.first().id,  # Assign to the first project for now
                    assigned_model="openai/gpt-3.5-turbo",
                    capabilities=json.dumps(["task_delegation"]),
                    is_lead_agent=True
                )
                db.session.add(lead_agent_model)
                db.session.commit()

            self.lead_agent = Agent.from_dict(lead_agent_model.to_dict())
            self.lead_agent.set_as_lead_agent()

            other_agents = AgentModel.query.filter_by(is_lead_agent=False).all()
            for agent_model in other_agents:
                agent = Agent.from_dict(agent_model.to_dict())
                self.lead_agent.add_managed_agent(agent)

            self.task_assignment_system = TaskAssignmentSystem(self.lead_agent)

    def start_server(self, host='0.0.0.0', port=5159):
        """
        Starts the Flask server to serve the React front-end and handle API requests.
        """
        with app.app_context():
            # Create the database tables
            db.create_all()
            
        # Initialize OpenRouter client
        self.initialize_openrouter_client()

        # Initialize Task Assignment System
        self.initialize_task_assignment_system()

        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve(path):
            if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            else:
                return send_from_directory(app.static_folder, 'index.html')

        # ... (keep all other route definitions)

        @app.route('/api/agents', methods=['POST'])
        def create_agent():
            try:
                data = request.json
                new_agent = AgentModel(
                    name=data['name'],
                    description=data.get('description', ''),
                    project_id=data['project_id'],
                    assigned_model=data.get('assigned_model'),
                    capabilities=json.dumps(data.get('capabilities', [])),
                    is_lead_agent=data.get('is_lead_agent', False)
                )
                db.session.add(new_agent)
                db.session.commit()
                self.initialize_task_assignment_system()  # Reinitialize with new agent
                return jsonify({"success": True, "agent": new_agent.to_dict()})
            except Exception as e:
                logger.error(f"Error in create_agent: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/agents/<agent_id>', methods=['PUT'])
        def update_agent(agent_id):
            try:
                agent = AgentModel.query.get(agent_id)
                if not agent:
                    return jsonify({"success": False, "error": "Agent not found"}), 404
                
                data = request.json
                agent.name = data.get('name', agent.name)
                agent.description = data.get('description', agent.description)
                agent.assigned_model = data.get('assigned_model', agent.assigned_model)
                agent.capabilities = json.dumps(data.get('capabilities', []))
                agent.is_lead_agent = data.get('is_lead_agent', agent.is_lead_agent)
                
                db.session.commit()
                self.initialize_task_assignment_system()  # Reinitialize with updated agent
                return jsonify({"success": True, "agent": agent.to_dict()})
            except Exception as e:
                logger.error(f"Error in update_agent: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        @app.route('/api/tasks', methods=['POST'])
        def assign_task():
            try:
                task_data = request.json
                result = self.task_assignment_system.execute_task(task_data)
                return jsonify({"success": True, "result": result})
            except Exception as e:
                logger.error(f"Error in assign_task: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

        logger.info(f"Starting server on http://{host}:{port}")
        app.run(host=host, port=port, debug=True)

interpreter = OpenInterpreter()

if __name__ == '__main__':
    interpreter.start_server()
