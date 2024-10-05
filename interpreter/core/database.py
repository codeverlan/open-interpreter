import sqlite3
import os
from interpreter.core.models.prompt import Prompt

class Database:
    def __init__(self):
        db_path = os.environ.get('OPEN_INTERPRETER_DB_PATH')
        if not db_path:
            raise ValueError("OPEN_INTERPRETER_DB_PATH environment variable is not set")
        
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_prompt(self, prompt):
        self.cursor.execute('''
            INSERT INTO prompts (project_id, name, content)
            VALUES (?, ?, ?)
        ''', (prompt.project_id, prompt.name, prompt.content))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_prompt(self, prompt_id):
        self.cursor.execute('SELECT * FROM prompts WHERE id = ?', (prompt_id,))
        row = self.cursor.fetchone()
        if row:
            return Prompt(id=row[0], project_id=row[1], name=row[2], content=row[3],
                          created_at=row[4], updated_at=row[5])
        return None

    def get_prompts_for_project(self, project_id):
        self.cursor.execute('SELECT * FROM prompts WHERE project_id = ?', (project_id,))
        rows = self.cursor.fetchall()
        return [Prompt(id=row[0], project_id=row[1], name=row[2], content=row[3],
                       created_at=row[4], updated_at=row[5]) for row in rows]

    def update_prompt(self, prompt):
        self.cursor.execute('''
            UPDATE prompts
            SET name = ?, content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (prompt.name, prompt.content, prompt.id))
        self.conn.commit()

    def delete_prompt(self, prompt_id):
        self.cursor.execute('DELETE FROM prompts WHERE id = ?', (prompt_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()