import sqlite3
import os
from typing import Optional
from backend.services.auth_service import AuthService

class AdminService:
    def __init__(self, db_path: str = "backend/data/admin.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create admins table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create users table for regular users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_username TEXT,
                action TEXT,
                sql_query TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                prompt TEXT NOT NULL,
                response_json TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if default admin exists
        cursor.execute("SELECT COUNT(*) FROM admins WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            default_pass = AuthService.get_password_hash("admin123")
            cursor.execute("INSERT INTO admins (username, hashed_password) VALUES (?, ?)", ("admin", default_pass))
        
        conn.commit()
        conn.close()

    def get_user(self, username: str) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def get_regular_user(self, username: str) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def register_user(self, username: str, hashed_password: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, hashed_password, status) VALUES (?, ?, 'PENDING')", 
                           (username, hashed_password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, status, created_at FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_user_status(self, username: str, status: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET status = ? WHERE username = ?", (status, username))
        conn.commit()
        conn.close()

    def log_action(self, username: str, action: str, sql_query: Optional[str] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO admin_logs (admin_username, action, sql_query) VALUES (?, ?, ?)", 
                       (username, action, sql_query))
        conn.commit()
        conn.close()

    def save_chat(self, username: str, prompt: str, response_json: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_history (username, prompt, response_json) VALUES (?, ?, ?)", 
                       (username, prompt, response_json))
        conn.commit()
        conn.close()

    def get_chat_history(self, username: str):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_history WHERE username = ? ORDER BY timestamp DESC LIMIT 50", (username,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def clear_chat_history(self, username: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE username = ?", (username,))
        conn.commit()
        conn.close()

    def delete_chat_item(self, username: str, chat_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE id = ? AND username = ?", (chat_id, username))
        conn.commit()
        conn.close()
