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
    outlines = db.relationship('Outline', backref='project', lazy=True)
    prompts = db.relationship('Prompt', backref='project', lazy=True)
    terminal_outputs = db.relationship('TerminalOutput', backref='project', lazy=True)
    settings = db.relationship('Setting', backref='project', lazy=True)
    project_info = db.Column(db.Text)  # New field for storing project-specific information

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'directory': self.directory,
            'created_at': self.created_at.isoformat(),
            'project_info': json.loads(self.project_info) if self.project_info else {}
        }

class AgentModel(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    assigned_model = db.Column(db.String(100))
    capabilities = db.Column(db.Text)  # Store capabilities as a JSON string
    role = db.Column(db.String(20), default='general')  # 'lead', 'general', or 'specialized'
    knowledge_base = db.Column(db.Text)  # Store knowledge base as a JSON string
    persistent_knowledge_base = db.Column(db.Text)  # Store persistent knowledge base as a JSON string
    status = db.Column(db.String(20), default='idle')  # 'idle', 'working', 'completed'
    current_task = db.Column(db.Text)  # Store current task as a JSON string
    task_history = db.Column(db.Text)  # Store task history as a JSON string
    user_feedback = db.Column(db.Text)  # Store user feedback as a JSON string
    preferences = db.Column(db.Text)  # Store preferences as a JSON string
    self_critiques = db.Column(db.Text)  # Store self-critiques as a JSON string
    agent_evaluations = db.Column(db.Text)  # Store agent evaluations as a JSON string

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat(),
            'assigned_model': self.assigned_model,
            'capabilities': json.loads(self.capabilities) if self.capabilities else [],
            'role': self.role,
            'knowledge_base': json.loads(self.knowledge_base) if self.knowledge_base else {},
            'persistent_knowledge_base': json.loads(self.persistent_knowledge_base) if self.persistent_knowledge_base else {},
            'status': self.status,
            'current_task': json.loads(self.current_task) if self.current_task else None,
            'task_history': json.loads(self.task_history) if self.task_history else [],
            'user_feedback': json.loads(self.user_feedback) if self.user_feedback else [],
            'preferences': json.loads(self.preferences) if self.preferences else {},
            'self_critiques': json.loads(self.self_critiques) if self.self_critiques else [],
            'agent_evaluations': json.loads(self.agent_evaluations) if self.agent_evaluations else {}
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
        self.current_project = None

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
            lead_agent_model = AgentModel.query.filter_by(role='lead', project_id=self.current_project.id).first()
            if not lead_agent_model:
                # Create a new lead agent if one doesn't exist for the current project
                lead_agent_model = AgentModel(
                    name="Lead Agent",
                    description="Lead agent for task assignment",
                    project_id=self.current_project.id,
                    assigned_model="openai/gpt-3.5-turbo",
                    capabilities=json.dumps(["task_delegation"]),
                    role='lead'
                )
                db.session.add(lead_agent_model)
                db.session.commit()

            self.lead_agent = Agent.from_dict(lead_agent_model.to_dict())
            self.lead_agent.set_role('lead')

            other_agents = AgentModel.query.filter(AgentModel.role != 'lead', AgentModel.project_id == self.current_project.id).all()
            for agent_model in other_agents:
                agent = Agent.from_dict(agent_model.to_dict())
                self.lead_agent.add_managed_agent(agent)

            self.task_assignment_system = TaskAssignmentSystem(self.lead_agent, self.openrouter_client)

    def set_current_project(self, project_id):
        with app.app_context():
            project = Project.query.get(project_id)
            if project:
                self.current_project = project
                self.initialize_task_assignment_system()
            else:
                raise ValueError(f"Project with id {project_id} not found")

    def create_agent(self, data):
        try:
            new_agent = AgentModel(
                name=data['name'],
                description=data.get('description', ''),
                project_id=self.current_project.id,
                assigned_model=data.get('assigned_model'),
                capabilities=json.dumps(data.get('capabilities', [])),
                role=data.get('role', 'general'),
                knowledge_base=json.dumps(data.get('knowledge_base', {})),
                persistent_knowledge_base=json.dumps(data.get('persistent_knowledge_base', {})),
                task_history=json.dumps([]),
                user_feedback=json.dumps([]),
                preferences=json.dumps({}),
                self_critiques=json.dumps([]),
                agent_evaluations=json.dumps({})
            )
            db.session.add(new_agent)
            db.session.commit()
            self.initialize_task_assignment_system()  # Reinitialize with new agent
            return {"success": True, "agent": new_agent.to_dict()}
        except Exception as e:
            logger.error(f"Error in create_agent: {str(e)}")
            return {"success": False, "error": str(e)}

    def update_agent(self, agent_id, data):
        try:
            agent = AgentModel.query.get(agent_id)
            if not agent:
                return {"success": False, "error": "Agent not found"}
            
            agent.name = data.get('name', agent.name)
            agent.description = data.get('description', agent.description)
            agent.assigned_model = data.get('assigned_model', agent.assigned_model)
            agent.capabilities = json.dumps(data.get('capabilities', json.loads(agent.capabilities)))
            agent.role = data.get('role', agent.role)
            agent.knowledge_base = json.dumps(data.get('knowledge_base', json.loads(agent.knowledge_base)))
            agent.persistent_knowledge_base = json.dumps(data.get('persistent_knowledge_base', json.loads(agent.persistent_knowledge_base)))
            agent.status = data.get('status', agent.status)
            agent.current_task = json.dumps(data.get('current_task')) if data.get('current_task') else None
            agent.task_history = json.dumps(data.get('task_history', json.loads(agent.task_history)))
            agent.user_feedback = json.dumps(data.get('user_feedback', json.loads(agent.user_feedback)))
            agent.preferences = json.dumps(data.get('preferences', json.loads(agent.preferences)))
            agent.self_critiques = json.dumps(data.get('self_critiques', json.loads(agent.self_critiques)))
            agent.agent_evaluations = json.dumps(data.get('agent_evaluations', json.loads(agent.agent_evaluations)))
            
            db.session.commit()
            self.initialize_task_assignment_system()  # Reinitialize with updated agent
            return {"success": True, "agent": agent.to_dict()}
        except Exception as e:
            logger.error(f"Error in update_agent: {str(e)}")
            return {"success": False, "error": str(e)}

    def delete_agent(self, agent_id):
        try:
            agent = AgentModel.query.get(agent_id)
            if not agent:
                return {"success": False, "error": "Agent not found"}
            
            db.session.delete(agent)
            db.session.commit()
            self.initialize_task_assignment_system()  # Reinitialize without deleted agent
            return {"success": True, "message": "Agent deleted successfully"}
        except Exception as e:
            logger.error(f"Error in delete_agent: {str(e)}")
            return {"success": False, "error": str(e)}

    def assign_task(self, task_data):
        try:
            iterations = task_data.get('iterations', 1)
            result = self.task_assignment_system.execute_task(task_data, iterations=iterations)
            return {"success": True, "result": result, "task_id": list(self.task_assignment_system.task_progress.keys())[-1]}
        except Exception as e:
            logger.error(f"Error in assign_task: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_task_progress(self, task_id):
        try:
            progress = self.task_assignment_system.get_task_progress(task_id)
            return {"success": True, "progress": progress}
        except Exception as e:
            logger.error(f"Error in get_task_progress: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_next_steps(self, task_id):
        try:
            next_steps = self.task_assignment_system.suggest_next_steps(task_id)
            return {"success": True, "next_steps": next_steps}
        except Exception as e:
            logger.error(f"Error in get_next_steps: {str(e)}")
            return {"success": False, "error": str(e)}

    def add_user_feedback(self, agent_id, feedback, task_id=None):
        try:
            agent = AgentModel.query.get(agent_id)
            if not agent:
                return {"success": False, "error": "Agent not found"}
            
            user_feedback = json.loads(agent.user_feedback)
            user_feedback.append({
                'feedback': feedback,
                'task_id': task_id,
                'timestamp': time.time()
            })
            agent.user_feedback = json.dumps(user_feedback)
            
            db.session.commit()
            return {"success": True, "message": "User feedback added successfully"}
        except Exception as e:
            logger.error(f"Error in add_user_feedback: {str(e)}")
            return {"success": False, "error": str(e)}

    def set_agent_preference(self, agent_id, key, value):
        try:
            agent = AgentModel.query.get(agent_id)
            if not agent:
                return {"success": False, "error": "Agent not found"}
            
            preferences = json.loads(agent.preferences)
            preferences[key] = value
            agent.preferences = json.dumps(preferences)
            
            db.session.commit()
            return {"success": True, "message": "Agent preference set successfully"}
        except Exception as e:
            logger.error(f"Error in set_agent_preference: {str(e)}")
            return {"success": False, "error": str(e)}

    def update_project_info(self, project_id, info):
        try:
            project = Project.query.get(project_id)
            if not project:
                return {"success": False, "error": "Project not found"}
            
            project.project_info = json.dumps(info)
            db.session.commit()
            return {"success": True, "message": "Project information updated successfully"}
        except Exception as e:
            logger.error(f"Error in update_project_info: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_project_info(self, project_id):
        try:
            project = Project.query.get(project_id)
            if not project:
                return {"success": False, "error": "Project not found"}
            
            return {"success": True, "project_info": json.loads(project.project_info) if project.project_info else {}}
        except Exception as e:
            logger.error(f"Error in get_project_info: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_agent_self_critiques(self, agent_id):
        try:
            agent = AgentModel.query.get(agent_id)
            if not agent:
                return {"success": False, "error": "Agent not found"}
            
            return {"success": True, "self_critiques": json.loads(agent.self_critiques) if agent.self_critiques else []}
        except Exception as e:
            logger.error(f"Error in get_agent_self_critiques: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_agent_evaluations(self, agent_id):
        try:
            agent = AgentModel.query.get(agent_id)
            if not agent:
                return {"success": False, "error": "Agent not found"}
            
            return {"success": True, "agent_evaluations": json.loads(agent.agent_evaluations) if agent.agent_evaluations else {}}
        except Exception as e:
            logger.error(f"Error in get_agent_evaluations: {str(e)}")
            return {"success": False, "error": str(e)}

    def start_server(self, host='0.0.0.0', port=5159):
        """
        Starts the Flask server to serve the React front-end and handle API requests.
        """
        with app.app_context():
            # Create the database tables
            db.create_all()
            
        # Initialize OpenRouter client
        self.initialize_openrouter_client()

        @app.route('/api/projects/<project_id>/info', methods=['GET', 'PUT'])
        def project_info(project_id):
            if request.method == 'GET':
                return jsonify(self.get_project_info(project_id))
            elif request.method == 'PUT':
                data = request.json
                return jsonify(self.update_project_info(project_id, data))

        @app.route('/api/agents/<agent_id>/knowledge', methods=['GET', 'PUT'])
        def agent_knowledge(agent_id):
            agent = AgentModel.query.get(agent_id)
            if not agent:
                return jsonify({"success": False, "error": "Agent not found"}), 404

            if request.method == 'GET':
                return jsonify({
                    "success": True,
                    "knowledge_base": json.loads(agent.knowledge_base),
                    "persistent_knowledge_base": json.loads(agent.persistent_knowledge_base)
                })
            elif request.method == 'PUT':
                data = request.json
                agent.knowledge_base = json.dumps(data.get('knowledge_base', {}))
                agent.persistent_knowledge_base = json.dumps(data.get('persistent_knowledge_base', {}))
                db.session.commit()
                return jsonify({"success": True, "message": "Agent knowledge updated successfully"})

        @app.route('/api/agents/<agent_id>/self_critiques', methods=['GET'])
        def agent_self_critiques(agent_id):
            return jsonify(self.get_agent_self_critiques(agent_id))

        @app.route('/api/agents/<agent_id>/evaluations', methods=['GET'])
        def agent_evaluations(agent_id):
            return jsonify(self.get_agent_evaluations(agent_id))

        @app.route('/api/tasks', methods=['POST'])
        def create_task():
            data = request.json
            return jsonify(self.assign_task(data))

        @app.route('/api/tasks/<task_id>/progress', methods=['GET'])
        def task_progress(task_id):
            return jsonify(self.get_task_progress(task_id))

        @app.route('/api/tasks/<task_id>/next_steps', methods=['GET'])
        def task_next_steps(task_id):
            return jsonify(self.get_next_steps(task_id))

        # ... (rest of the server setup code)

        logger.info(f"Starting server on http://{host}:{port}")
        app.run(host=host, port=port, debug=True)

interpreter = OpenInterpreter()

if __name__ == '__main__':
    interpreter.start_server()
