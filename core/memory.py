import sqlite3
import os
from datetime import datetime

class VioletMemory:
    def __init__(self, db_path="violet_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite database schema for memory."""
        try:
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
        except Exception as e:
            print(f"[MEMORY ERROR] Failed to initialize SQLite database: {e}")

    def add_message(self, role, content):
        """Appends a dialogue turn to the session history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))
                conn.commit()
        except Exception as e:
            print(f"[MEMORY ERROR] Failed to append message to history: {e}")

    def get_history(self, limit=6):
        """Fetches the last N messages formatted for chat templates in chronological order."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT role, content FROM history ORDER BY timestamp DESC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                # Reverse to sort chronologically (oldest to newest)
                return [{"role": row[0], "content": row[1]} for row in reversed(rows)]
        except Exception as e:
            print(f"[MEMORY ERROR] Failed to retrieve message history: {e}")
            return []

    def clear_memory(self):
        """Wipes the database history clean."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history")
                conn.commit()
        except Exception as e:
            print(f"[MEMORY ERROR] Failed to clear history: {e}")

if __name__ == "__main__":
    memory = VioletMemory("test_memory.db")
    memory.add_message("user", "System diagnostics, VIOLET.")
    memory.add_message("assistant", "Operational, Vijay.")
    print("History retrieved:", memory.get_history())
    memory.clear_memory()
    if os.path.exists("test_memory.db"):
        os.remove("test_memory.db")
