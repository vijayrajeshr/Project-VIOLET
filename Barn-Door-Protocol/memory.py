import sqlite3
import json
from datetime import datetime

class VioletMemory:
    def __init__(self, db_path="violet_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    role TEXT,
                    content TEXT
                )
            """)
            conn.commit()

    def add_message(self, role, content):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))
            conn.commit()

    def get_history(self, limit=20):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, content FROM history ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            # Reverse to get chronological order
            return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

    def clear_memory(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history")
            conn.commit()

if __name__ == "__main__":
    memory = VioletMemory()
    memory.add_message("user", "Hello VIOLET")
    print(memory.get_history())
