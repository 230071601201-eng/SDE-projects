"""
config/database.py
------------------
SQLite database - zero configuration, works instantly on Windows.
No password, no connection issues, no external services needed.
"""
import sqlite3
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# SQLite file stored in backend folder
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "escrow.db")

def dict_factory(cursor, row):
    """Return rows as dictionaries."""
    return {col[0]: val for col, val in zip(cursor.description, row)}

def init_db():
    """Create all tables if they don't exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = dict_factory
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('customer','seller')),
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                customer_id TEXT NOT NULL REFERENCES users(id),
                seller_id TEXT NOT NULL REFERENCES users(id),
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending','in_escrow','delivered','completed','disputed')),
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS escrow (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                order_id TEXT UNIQUE NOT NULL REFERENCES orders(id),
                amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'held'
                    CHECK(status IN ('held','released','refunded')),
                held_at TEXT DEFAULT (datetime('now')),
                released_at TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                order_id TEXT NOT NULL REFERENCES orders(id),
                type TEXT NOT NULL CHECK(type IN ('deposit','release','refund')),
                amount REAL NOT NULL,
                note TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
        conn.close()
        logger.info("✅ Database ready! (SQLite)")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        raise

def close_db():
    pass

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
