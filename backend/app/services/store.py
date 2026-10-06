import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parents[2] / "plate_x.db"

def connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            registration TEXT,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS evidence (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            source TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id)
        )""")
        conn.commit()

def insert(table: str, values: dict[str, Any]):
    columns = ", ".join(values)
    placeholders = ", ".join("?" for _ in values)
    with connection() as conn:
        conn.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
            tuple(values.values()),
        )
        conn.commit()

def rows(table: str):
    with connection() as conn:
        return [dict(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY created_at DESC")]

def row(table: str, item_id: str):
    with connection() as conn:
        result = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone()
        return dict(result) if result else None
