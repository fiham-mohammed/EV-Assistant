import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "ev_memory.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_memory():
    with get_connection() as conn:

        # Short-term conversation history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Long-term structured memory
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                memory_key TEXT NOT NULL,
                memory_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, memory_key)
            )
        """)


# =====================================================
# Conversation memory
# =====================================================

def save_message(role, content):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            (role, content)
        )


def load_recent_messages(limit=30):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM messages
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    rows.reverse()

    return [
        {
            "role": role,
            "content": content
        }
        for role, content in rows
    ]


def clear_conversation_memory():
    with get_connection() as conn:
        conn.execute("DELETE FROM messages")


# =====================================================
# Long-term memory
# =====================================================

def save_memory(category, memory_key, memory_value):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO memories (
                category,
                memory_key,
                memory_value
            )
            VALUES (?, ?, ?)

            ON CONFLICT(category, memory_key)
            DO UPDATE SET
                memory_value = excluded.memory_value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                category,
                memory_key,
                memory_value
            )
        )


def load_all_memories():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT category, memory_key, memory_value
            FROM memories
            ORDER BY updated_at DESC
            """
        ).fetchall()

    return [
        {
            "category": category,
            "key": memory_key,
            "value": memory_value
        }
        for category, memory_key, memory_value in rows
    ]


def delete_memory(category, memory_key):
    with get_connection() as conn:
        conn.execute(
            """
            DELETE FROM memories
            WHERE category = ?
            AND memory_key = ?
            """,
            (
                category,
                memory_key
            )
        )


def clear_long_term_memory():
    with get_connection() as conn:
        conn.execute("DELETE FROM memories")


def clear_all_memory():
    with get_connection() as conn:
        conn.execute("DELETE FROM messages")
        conn.execute("DELETE FROM memories")