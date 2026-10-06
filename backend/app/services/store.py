import os
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("PLATE_X_DB_PATH", Path(__file__).resolve().parents[2] / "plate_x.db"))

def connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT, registration TEXT,
            status TEXT NOT NULL DEFAULT 'open', created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS evidence (
            id TEXT PRIMARY KEY, case_id TEXT NOT NULL, filename TEXT NOT NULL, sha256 TEXT NOT NULL,
            source TEXT NOT NULL, notes TEXT, created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id)
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS audit_events (
            id TEXT PRIMARY KEY, username TEXT NOT NULL, role TEXT NOT NULL, action TEXT NOT NULL,
            resource TEXT NOT NULL, resource_id TEXT, metadata TEXT NOT NULL, created_at TEXT NOT NULL
        )""")
        conn.commit()

def insert(table: str, values: dict[str, Any]):
    allowed = {"cases", "evidence", "audit_events"}
    if table not in allowed:
        raise ValueError("Unsupported table")
    columns = ", ".join(values)
    placeholders = ", ".join("?" for _ in values)
    with connection() as conn:
        conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(values.values()))
        conn.commit()

def rows(table: str):
    allowed = {"cases", "evidence", "audit_events"}
    if table not in allowed:
        raise ValueError("Unsupported table")
    with connection() as conn:
        return [dict(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY created_at DESC")]

def row(table: str, item_id: str):
    allowed = {"cases", "evidence"}
    if table not in allowed:
        raise ValueError("Unsupported table")
    with connection() as conn:
        result = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone()
        return dict(result) if result else None

def get_user(username: str):
    with connection() as conn:
        result = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(result) if result else None

def create_user(username: str, password_hash: str, role: str):
    from datetime import datetime, timezone
    with connection() as conn:
        conn.execute("INSERT INTO users (username,password_hash,role,active,created_at) VALUES (?,?,?,?,?)",
                     (username, password_hash, role, 1, datetime.now(timezone.utc).isoformat()))
        conn.commit()

def list_users():
    with connection() as conn:
        return [dict(row) for row in conn.execute("SELECT username, role, active, created_at FROM users ORDER BY username")]
