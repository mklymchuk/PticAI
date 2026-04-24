import sqlite3
import json

class BotDatabase:
    def __init__(self, db_path="ptic_data.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Таблиця для профілів (RAG)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id TEXT PRIMARY KEY,
                    first_name TEXT,
                    bio TEXT,
                    interests TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Таблиця для історії
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def update_profile(self, user_id, bio=None, interests=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO profiles (user_id, bio, interests)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                bio = COALESCE(?, bio),
                interests = COALESCE(?, interests),
                last_updated = CURRENT_TIMESTAMP
            ''', (str(user_id), bio, interests, bio, interests))
            conn.commit()

    def get_profile(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT bio, interests FROM profiles WHERE user_id = ?', (str(user_id),))
            return cursor.fetchone()

    def add_to_history(self, user_id, role, content):
        """Зберігає нове повідомлення в базу."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)', 
                           (str(user_id), role, content))
            conn.commit()

    def get_recent_history(self, user_id, limit=8):
        """Отримує останні N повідомлень і форматує їх для Ollama."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content FROM (
                    SELECT role, content, id FROM history 
                    WHERE user_id = ? 
                    ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
            ''', (str(user_id), limit))
            rows = cursor.fetchall()
            
            formatted_history = []
            temp_user = None
            for role, content in rows:
                if role == "user":
                    temp_user = content
                elif role == "assistant" and temp_user:
                    formatted_history.append({"user": temp_user, "bot": content})
                    temp_user = None
            return formatted_history

    def get_history_count(self, user_id):
        """Рахує кількість повідомлень користувача для тригера аналізатора."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM history WHERE user_id = ?', (str(user_id),))
            result = cursor.fetchone()
            return result[0] if result else 0