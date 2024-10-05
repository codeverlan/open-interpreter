import sqlite3
import os
from threading import local
from datetime import datetime
from interpreter.core.models.prompt import Prompt
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
        
        # Check if the is_default_system_message column exists, if not, add it
        cursor.execute("PRAGMA table_info(prompts)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'is_default_system_message' not in columns:
            cursor.execute('ALTER TABLE prompts ADD COLUMN is_default_system_message BOOLEAN NOT NULL DEFAULT 0')
        
        conn.commit()

    def add_prompt(self, prompt):
        conn, cursor = self.get_connection()
        cursor.execute('''
            INSERT INTO prompts (project_id, name, content, is_default_system_message, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (prompt.project_id, prompt.name, prompt.content, prompt.is_default_system_message, 
              prompt.created_at, prompt.updated_at))
        conn.commit()
        return cursor.lastrowid

    def get_prompt(self, prompt_id):
        conn, cursor = self.get_connection()
        cursor.execute('SELECT * FROM prompts WHERE id = ?', (prompt_id,))
        row = cursor.fetchone()
        if row:
            return Prompt(
                id=row['id'],
                project_id=row['project_id'],
                name=row['name'],
                content=row['content'],
                is_default_system_message=bool(row['is_default_system_message']),
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        return None

    def get_prompts_for_project(self, project_id):
        conn, cursor = self.get_connection()
        cursor.execute('SELECT * FROM prompts WHERE project_id = ?', (project_id,))
        rows = cursor.fetchall()
        return [Prompt(
            id=row['id'],
            project_id=row['project_id'],
            name=row['name'],
            content=row['content'],
            is_default_system_message=bool(row['is_default_system_message']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        ) for row in rows]

    def update_prompt(self, prompt):
        conn, cursor = self.get_connection()
        cursor.execute('''
            UPDATE prompts
            SET name = ?, content = ?, is_default_system_message = ?, updated_at = ?
            WHERE id = ?
        ''', (prompt.name, prompt.content, prompt.is_default_system_message, datetime.now(), prompt.id))
        conn.commit()

    def delete_prompt(self, prompt_id):
        conn, cursor = self.get_connection()
        cursor.execute('DELETE FROM prompts WHERE id = ?', (prompt_id,))
        conn.commit()

    def get_all_project_ids(self):
        conn, cursor = self.get_connection()
        cursor.execute('SELECT DISTINCT project_id FROM prompts')
        rows = cursor.fetchall()
        return [row['project_id'] for row in rows]

    def get_or_create_default_system_message(self, project_id):
        conn, cursor = self.get_connection()
        cursor.execute('SELECT * FROM prompts WHERE project_id = ? AND is_default_system_message = 1', (project_id,))
        row = cursor.fetchone()
        if row:
            return Prompt(
                id=row['id'],
                project_id=row['project_id'],
                name=row['name'],
                content=row['content'],
                is_default_system_message=bool(row['is_default_system_message']),
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        else:
            new_prompt = Prompt(
                id=None,
                project_id=project_id,
                name="Default System Message",
                content=default_system_message,
                is_default_system_message=True
            )
            new_id = self.add_prompt(new_prompt)
            return self.get_prompt(new_id)

    def close(self):
        if hasattr(self._thread_local, "connection"):
            self._thread_local.connection.close()
            del self._thread_local.connection
            del self._thread_local.cursor