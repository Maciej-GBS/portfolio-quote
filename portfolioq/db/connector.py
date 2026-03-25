import sqlite3
from pathlib import Path

class Connector:
    """
    This simple Connector wraps sqlite3 with context management
    for transaction handling.
    """
    DB_PATH = Path("sample_data", "data.db")

    def __init__(self):
        self.conn = sqlite3.connect(self.DB_PATH)
        self.cursor = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type or exc_value or traceback:
            self.rollback()
        else:
            self.commit()

    def get_cursor(self) -> sqlite3.Cursor:
        if not self.cursor:
            self.cursor = self.conn.cursor()
        return self.cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.cursor = None
        self.conn.close()
        self.conn = None

def get_connector() -> Connector:
    return Connector()
