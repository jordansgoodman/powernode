import sqlite3
import os
from datetime import datetime
import json

DB_PATH = os.path.abspath(
    os.path .join(os.path.dirname(__file__), "..", "data", "log.db")
)

def init_action_log():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS action_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp   TEXT NOT NULL,
        workflow    TEXT,
        action      TEXT NOT NULL,
        payload     TEXT
    )
    """)
    conn.commit()
    conn.close()

def register_action(action: str, workflow: str = None, payload: dict = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO action_log (timestamp, workflow, action, payload) VALUES (?, ?, ?, ?)",
        (
            datetime.utcnow().isoformat(),
            workflow,
            action,
            json.dumps(payload) if payload is not None else None
        )
    )
    conn.commit()
    conn.close()
