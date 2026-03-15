import sqlite3
import os
from config import DB_PATH

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

CREATE_OFFERS_TABLE = """
CREATE TABLE IF NOT EXISTS offers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    company     TEXT,
    location    TEXT,
    url         TEXT    UNIQUE NOT NULL,
    source      TEXT,
    score       INTEGER DEFAULT 0,
    status      TEXT    DEFAULT 'new',  -- new | seen | applied | rejected
    posted_at   TEXT,
    scraped_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    notified    INTEGER DEFAULT 0       -- 0 = pas encore envoyé sur Telegram
);
"""

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute(CREATE_OFFERS_TABLE)
        conn.commit()
