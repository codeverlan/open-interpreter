import os
import sqlite3
import json
from threading import local
from datetime import datetime
from interpreter.core.models.prompt import Prompt
from interpreter.core.agent import Agent
from interpreter.core.default_system_message import default_system_message

class Database:
    _thread_local = local()

    def __init__(self):
        self.db_path = os.environ.get('OPEN_INTERPRETER_DB_PATH')
        if not self.db_path:
            raise ValueError("OPEN_INTERPRETER_DB_PATH environment variable is not set")
        
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        self.get_connection()
        self.create_tables()

    def get_connection(self):
        if not hasattr(self._thread_local, "connection"):
            self._thread_local.connection = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            self._thread_local.connection.row_factory = sqlite3.Row
            self._thread_local.cursor = self._thread_local.connection.cursor()
        return self._thread_local.connection, self._thread_local.cursor

    def create_tables(self):
        conn, cursor = self.get_connection()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                is_default_system_message BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                prompt TEXT NOT NULL,
                ai_model TEXT NOT NULL,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Check if the is_default_system_message column exists, if not, add it
        cursor.execute("PRAGMA table_info(prompts)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'is_default_system_message' not in columns:
            cursor.execute('ALTER TABLE prompts ADD COLUMN is_default_system_message BOOLEAN NOT NULL DEFAULT 0')
        
        # Check if the updated_at column exists in agents table, if not, add it
        cursor.execute("PRAGMA table_info(agents)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'updated_at' not in columns:
            cursor.execute('ALTER TABLE agents ADD COLUMN updated_at TIMESTAMP')
            # Update existing rows with current timestamp
            cursor.execute('UPDATE agents SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL')
        
        conn.commit()

    def add_agent(self, agent):
        conn, cursor = self.get_connection()
        cursor.execute('''
            INSERT INTO agents (id, name, description, prompt, ai_model, feedback, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (agent.id, agent.name, agent.description, agent.prompt, agent.ai_model, json.dumps(agent.feedback), datetime.now()))
        conn.commit()
        return agent.id

    def get_agent(self, agent_id):
        conn, cursor = self.get_connection()
        cursor.execute('SELECT * FROM agents WHERE id = ?', (agent_id,))
        row = cursor.fetchone()
        if row:
            return Agent(
                name=row['name'],
                description=row['description'],
                prompt=row['prompt'],
                ai_model=row['ai_model'],
                id=row['id'],
                feedback=json.loads(row['feedback']) if row['feedback'] else []
            )
        return None

    def update_agent(self, agent):
        conn, cursor = self.get_connection()
        cursor.execute('''
            UPDATE agents
            SET name = ?, description = ?, prompt = ?, ai_model = ?, feedback = ?, updated_at = ?
            WHERE id = ?
        ''', (agent.name, agent.description, agent.prompt, agent.ai_model, json.dumps(agent.feedback), datetime.now(), agent.id))
        conn.commit()

    def delete_agent(self, agent_id):
        conn, cursor = self.get_connection()
        cursor.execute('DELETE FROM agents WHERE id = ?', (agent_id,))
        conn.commit()

    def get_all_agents(self):
        conn, cursor = self.get_connection()
        cursor.execute('SELECT * FROM agents')
        rows = cursor.fetchall()
        return [Agent(
            name=row['name'],
            description=row['description'],
            prompt=row['prompt'],
            ai_model=row['ai_model'],
            id=row['id'],
            feedback=json.loads(row['feedback']) if row['feedback'] else []
        ) for row in rows]

    def add_feedback_to_agent(self, agent_id, feedback_content):
        agent = self.get_agent(agent_id)
        if agent:
            agent.add_feedback(feedback_content)
            self.update_agent(agent)
        else:
            raise ValueError(f"Agent with id {agent_id} not found")

    def close(self):
        if hasattr(self._thread_local, "connection"):
            self._thread_local.connection.close()
            del self._thread_local.connection
            del self._thread_local.cursor

    # Existing methods (add_prompt, get_prompt, get_prompts_for_project, update_prompt, delete_prompt, get_all_project_ids, get_or_create_default_system_message)
    # ... (keep all the existing methods as they were)