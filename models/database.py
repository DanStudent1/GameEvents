import os
import time
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://gameuser:gamepass@db:5432/gameevents",
)


def get_connection() -> psycopg2.extensions.connection:
    """Создаём новое соединение с базой данных."""
    return psycopg2.connect(DATABASE_URL)


def init_db(retries: int = 5, delay: int = 2) -> None:
    """
    Инициализация БД: пытаемся подключиться несколько раз
    и создаём таблицы, если их ещё нет.
    """
    for attempt in range(1, retries + 1):
        try:
            print(f"[DB] Попытка подключения #{attempt}")
            conn = get_connection()
            cur = conn.cursor()

            # Таблица ивентов
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    description TEXT,
                    event_type VARCHAR(50) NOT NULL,
                    starts_at TIMESTAMPTZ NOT NULL,
                    ends_at TIMESTAMPTZ NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE
                );
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS rewards (
                    id SERIAL PRIMARY KEY,
                    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                    reward_type VARCHAR(50) NOT NULL,
                    amount INTEGER,
                    description TEXT
                );
                """
            )

            conn.commit()
            cur.close()
            conn.close()
            print("[DB] Инициализация завершена успешно")
            break

        except psycopg2.OperationalError as exc:
            print(f"[DB] Ошибка подключения: {exc}")
            if attempt == retries:
                print("[DB] Не удалось подключиться к БД после нескольких попыток")
                raise
            time.sleep(delay)


def fetch_all(query: str, params: tuple | None = None) -> list[dict[str, Any]]:
    """Утилита: выполняем SELECT и возвращаем список словарей."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, params or ())
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return list(rows)


def fetch_one(query: str, params: tuple | None = None) -> dict[str, Any] | None:
    """Утилита: выполняем SELECT и возвращаем один словарь или None."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, params or ())
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row is not None else None


def execute(query: str, params: tuple | None = None) -> None:
    """Утилита: выполняем INSERT/UPDATE/DELETE без возврата результата."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    cur.close()
    conn.close()


def execute_returning_id(query: str, params: tuple | None = None) -> int:
    """INSERT ... RETURNING id — создаём запись и возвращаем её id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params or ())
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return int(new_id)
