import os
import sqlite3
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:  # pragma: no cover - only happens before dependencies are installed
    psycopg2 = None
    RealDictCursor = None


DB_PATH = Path("data") / "sentimentcloud.db"


def get_database_url() -> str:
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    try:
        import streamlit as st

        secret_keys = (
            "DATABASE_URL",
            "SUPABASE_DATABASE_URL",
            "SUPABASE_DB_URL",
            "POSTGRES_URL",
            "POSTGRESQL_URL",
        )
        for key in secret_keys:
            value = st.secrets.get(key, "")
            if value:
                return str(value)

        connections = st.secrets.get("connections", {})
        if isinstance(connections, dict):
            for config in connections.values():
                if isinstance(config, dict):
                    for key in ("url", "uri", "database_url", "DATABASE_URL"):
                        value = config.get(key, "")
                        if value:
                            return str(value)
    except Exception:
        return ""
    return ""


def using_postgres() -> bool:
    database_url = get_database_url()
    return database_url.startswith(("postgres://", "postgresql://"))


def get_database_status() -> dict[str, str]:
    database_url = get_database_url()
    if not database_url:
        return {
            "mode": "SQLite Lokal",
            "detail": str(DB_PATH),
            "host": "local",
        }

    parsed = urlparse(database_url)
    if parsed.scheme in ("postgres", "postgresql"):
        return {
            "mode": "PostgreSQL Cloud",
            "detail": "DATABASE_URL aktif",
            "host": parsed.hostname or "unknown-host",
        }

    return {
        "mode": "Konfigurasi database tidak valid",
        "detail": "DATABASE_URL harus diawali postgres:// atau postgresql://",
        "host": parsed.hostname or "unknown-host",
    }


def get_connection():
    database_url = get_database_url()
    if database_url:
        if psycopg2 is None:
            raise RuntimeError("psycopg2-binary belum terpasang. Jalankan pip install -r requirements.txt.")
        return psycopg2.connect(database_url, sslmode="require")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    if using_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS analysis_history (
                        id BIGSERIAL PRIMARY KEY,
                        topic TEXT NOT NULL,
                        analysis_date TEXT NOT NULL,
                        total_comments INTEGER NOT NULL,
                        positive_count INTEGER NOT NULL,
                        negative_count INTEGER NOT NULL,
                        neutral_count INTEGER NOT NULL
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS uploaded_csv_files (
                        id BIGSERIAL PRIMARY KEY,
                        analysis_id BIGINT NOT NULL REFERENCES analysis_history(id) ON DELETE CASCADE,
                        file_name TEXT NOT NULL,
                        row_count INTEGER NOT NULL,
                        column_count INTEGER NOT NULL,
                        csv_content TEXT NOT NULL,
                        uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sentiment_results (
                        id BIGSERIAL PRIMARY KEY,
                        analysis_id BIGINT NOT NULL REFERENCES analysis_history(id) ON DELETE CASCADE,
                        row_number INTEGER NOT NULL,
                        username TEXT,
                        comment TEXT NOT NULL,
                        processed_comment TEXT NOT NULL,
                        positive_score INTEGER NOT NULL,
                        negative_score INTEGER NOT NULL,
                        sentiment TEXT NOT NULL,
                        created_at TEXT,
                        analyzed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
        return

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                analysis_date TEXT NOT NULL,
                total_comments INTEGER NOT NULL,
                positive_count INTEGER NOT NULL,
                negative_count INTEGER NOT NULL,
                neutral_count INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS uploaded_csv_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                column_count INTEGER NOT NULL,
                csv_content TEXT NOT NULL,
                uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sentiment_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                row_number INTEGER NOT NULL,
                username TEXT,
                comment TEXT NOT NULL,
                processed_comment TEXT NOT NULL,
                positive_score INTEGER NOT NULL,
                negative_score INTEGER NOT NULL,
                sentiment TEXT NOT NULL,
                created_at TEXT,
                analyzed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE CASCADE
            )
            """
        )


def save_history(
    topic: str,
    analysis_date: str,
    total_comments: int,
    positive_count: int,
    negative_count: int,
    neutral_count: int,
) -> int:
    if using_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO analysis_history (
                        topic,
                        analysis_date,
                        total_comments,
                        positive_count,
                        negative_count,
                        neutral_count
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        topic,
                        analysis_date,
                        total_comments,
                        positive_count,
                        negative_count,
                        neutral_count,
                    ),
                )
                history_id = cur.fetchone()[0]
                return int(history_id)
        return

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analysis_history (
                topic,
                analysis_date,
                total_comments,
                positive_count,
                negative_count,
                neutral_count
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                topic,
                analysis_date,
                total_comments,
                positive_count,
                negative_count,
                neutral_count,
            ),
        )
        return int(cursor.lastrowid)


def save_uploaded_csv(
    analysis_id: int,
    file_name: str,
    row_count: int,
    column_count: int,
    csv_content: str,
) -> None:
    if using_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO uploaded_csv_files (
                        analysis_id,
                        file_name,
                        row_count,
                        column_count,
                        csv_content
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (analysis_id, file_name, row_count, column_count, csv_content),
                )
        return

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO uploaded_csv_files (
                analysis_id,
                file_name,
                row_count,
                column_count,
                csv_content
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (analysis_id, file_name, row_count, column_count, csv_content),
        )


def save_sentiment_results(analysis_id: int, rows: list[dict[str, object]]) -> None:
    if not rows:
        return

    values = [
        (
            analysis_id,
            int(row.get("row_number", 0)),
            _optional_text(row.get("username")),
            str(row.get("comment", "")),
            str(row.get("processed_comment", "")),
            int(row.get("positive_score", 0)),
            int(row.get("negative_score", 0)),
            str(row.get("sentiment", "")),
            _optional_text(row.get("created_at")),
        )
        for row in rows
    ]

    if using_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO sentiment_results (
                        analysis_id,
                        row_number,
                        username,
                        comment,
                        processed_comment,
                        positive_score,
                        negative_score,
                        sentiment,
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    values,
                )
        return

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO sentiment_results (
                analysis_id,
                row_number,
                username,
                comment,
                processed_comment,
                positive_score,
                negative_score,
                sentiment,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )


def fetch_history():
    if using_postgres():
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        id,
                        topic,
                        analysis_date,
                        total_comments,
                        positive_count,
                        negative_count,
                        neutral_count
                    FROM analysis_history
                    ORDER BY id DESC
                    """
                )
                return [dict(row) for row in cur.fetchall()]

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                id,
                topic,
                analysis_date,
                total_comments,
                positive_count,
                negative_count,
                neutral_count
            FROM analysis_history
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_analysis_detail(history_id: int) -> tuple[Optional[dict[str, object]], list[dict[str, object]]]:
    if using_postgres():
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        id,
                        topic,
                        analysis_date,
                        total_comments,
                        positive_count,
                        negative_count,
                        neutral_count
                    FROM analysis_history
                    WHERE id = %s
                    """,
                    (history_id,),
                )
                history = cur.fetchone()
                cur.execute(
                    """
                    SELECT
                        row_number,
                        username,
                        comment,
                        created_at,
                        processed_comment,
                        positive_score,
                        negative_score,
                        sentiment
                    FROM sentiment_results
                    WHERE analysis_id = %s
                    ORDER BY row_number ASC
                    """,
                    (history_id,),
                )
                results = cur.fetchall()
                return (dict(history) if history else None, [dict(row) for row in results])

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        history_row = conn.execute(
            """
            SELECT
                id,
                topic,
                analysis_date,
                total_comments,
                positive_count,
                negative_count,
                neutral_count
            FROM analysis_history
            WHERE id = ?
            """,
            (history_id,),
        ).fetchone()
        result_rows = conn.execute(
            """
            SELECT
                row_number,
                username,
                comment,
                created_at,
                processed_comment,
                positive_score,
                negative_score,
                sentiment
            FROM sentiment_results
            WHERE analysis_id = ?
            ORDER BY row_number ASC
            """,
            (history_id,),
        ).fetchall()
    return (
        dict(history_row) if history_row else None,
        [dict(row) for row in result_rows],
    )


def delete_history(history_id: int) -> None:
    if using_postgres():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM analysis_history WHERE id = %s", (history_id,))
        return

    with get_connection() as conn:
        conn.execute("DELETE FROM analysis_history WHERE id = ?", (history_id,))


def _optional_text(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value)
    return text if text.strip() else None
