import json
import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / "ev_memory.db"

DEFAULT_HISTORY_LIMIT = 20
MAX_HISTORY_LIMIT = 100


def _connect():
    connection = sqlite3.connect(
        DATABASE_PATH
    )
    connection.row_factory = sqlite3.Row
    return connection


def initialize_task_history():
    """
    Create EV's task-history table in the existing local
    SQLite database.
    """

    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                request TEXT NOT NULL,
                goal TEXT NOT NULL,
                status TEXT NOT NULL,
                actions_json TEXT NOT NULL,
                error TEXT
            )
            """
        )


def _normalize_actions(actions):
    """
    Save only action names. Generated Notepad text and full
    executor payloads are not stored in task history.
    """

    normalized = []

    for item in actions or []:
        if isinstance(
            item,
            str,
        ):
            action = (
                item
                .strip()
                .lower()
            )

        elif isinstance(
            item,
            dict,
        ):
            action = str(
                item.get(
                    "action",
                    "",
                )
            ).strip().lower()

        else:
            continue

        if (
            action
            and action not in normalized
        ):
            normalized.append(
                action
            )

    return normalized


def save_task_history(
    request,
    goal,
    status,
    actions=None,
    error=None,
):
    request = str(
        request
    ).strip()

    goal = (
        str(
            goal
        ).strip()
        or "Unknown goal"
    )

    status = (
        str(
            status
        )
        .strip()
        .lower()
    )

    if not request:
        raise ValueError(
            "Task history request cannot be empty."
        )

    allowed_statuses = {
        "previewed",
        "executed",
        "refused",
        "failed",
    }

    if status not in allowed_statuses:
        raise ValueError(
            f"Unsupported task history status "
            f"'{status}'."
        )

    created_at = (
        datetime.now()
        .astimezone()
        .isoformat(
            timespec="seconds"
        )
    )

    normalized_actions = _normalize_actions(
        actions
    )

    error_text = None

    if error:
        error_text = (
            str(
                error
            )
            .strip()
        )

        if len(error_text) > 1000:
            error_text = error_text[
                :1000
            ].rstrip()

    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO task_history (
                created_at,
                request,
                goal,
                status,
                actions_json,
                error
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                request,
                goal,
                status,
                json.dumps(
                    normalized_actions
                ),
                error_text,
            ),
        )

        return cursor.lastrowid


def load_task_history(
    limit=DEFAULT_HISTORY_LIMIT,
):
    try:
        limit = int(
            limit
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "History limit must be a number."
        ) from exc

    if limit < 1:
        raise ValueError(
            "History limit must be at least 1."
        )

    limit = min(
        limit,
        MAX_HISTORY_LIMIT,
    )

    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                created_at,
                request,
                goal,
                status,
                actions_json,
                error
            FROM task_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                limit,
            ),
        ).fetchall()

    history = []

    for row in rows:
        try:
            actions = json.loads(
                row[
                    "actions_json"
                ]
            )

        except json.JSONDecodeError:
            actions = []

        history.append(
            {
                "id": row[
                    "id"
                ],
                "created_at": row[
                    "created_at"
                ],
                "request": row[
                    "request"
                ],
                "goal": row[
                    "goal"
                ],
                "status": row[
                    "status"
                ],
                "actions": actions,
                "error": row[
                    "error"
                ],
            }
        )

    return history


def clear_task_history():
    with _connect() as connection:
        connection.execute(
            """
            DELETE FROM task_history
            """
        )


def format_task_history(history):
    if not history:
        return (
            "No task history recorded yet."
        )

    blocks = []

    for item in history:
        actions = item.get(
            "actions",
            [],
        )

        action_text = (
            ", ".join(
                actions
            )
            if actions
            else "none"
        )

        lines = [
            (
                f"#{item['id']} "
                f"[{item['status'].upper()}] "
                f"{item['created_at']}"
            ),
            (
                f"Request: "
                f"{item['request']}"
            ),
            (
                f"Goal: "
                f"{item['goal']}"
            ),
            (
                f"Actions: "
                f"{action_text}"
            ),
        ]

        if item.get(
            "error"
        ):
            lines.append(
                f"Error: "
                f"{item['error']}"
            )

        blocks.append(
            "\n".join(
                lines
            )
        )

    return (
        "\n\n".join(
            blocks
        )
    )


if __name__ == "__main__":
    initialize_task_history()

    print(
        "EV v0.9 Task History"
    )

    print(
        format_task_history(
            load_task_history(
                limit=5
            )
        )
    )
