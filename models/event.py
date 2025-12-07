from datetime import datetime
from typing import Any

from .database import fetch_all, fetch_one, execute, execute_returning_id


def create_event(
    title: str,
    description: str,
    event_type: str,
    starts_at: datetime,
    ends_at: datetime,
    is_active: bool = True,
) -> int:
    """Создаём новый ивент и возвращаем его id."""
    query = """
        INSERT INTO events (title, description, event_type, starts_at, ends_at, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    return execute_returning_id(
        query,
        (title, description, event_type, starts_at, ends_at, is_active),
    )


def get_all_events() -> list[dict[str, Any]]:
    """Возвращаем все ивенты (для списка)."""
    query = """
        SELECT id, title, event_type, starts_at, ends_at, is_active
        FROM events
        ORDER BY starts_at DESC;
    """
    return fetch_all(query)


def get_event_by_id(event_id: int) -> dict[str, Any] | None:
    """Возвращаем один ивент по id."""
    query = """
        SELECT id, title, description, event_type, starts_at, ends_at, is_active
        FROM events
        WHERE id = %s;
    """
    return fetch_one(query, (event_id,))


def get_active_events(now: datetime | None = None) -> list[dict[str, Any]]:
    """Ивенты, активные в данный момент (по времени и флагу is_active)."""
    now = now or datetime.utcnow()
    query = """
        SELECT id, title, event_type, starts_at, ends_at
        FROM events
        WHERE is_active = TRUE
          AND starts_at <= %s
          AND ends_at >= %s
        ORDER BY ends_at;
    """
    return fetch_all(query, (now, now))


def update_event(
    event_id: int,
    title: str,
    description: str,
    event_type: str,
    starts_at: datetime,
    ends_at: datetime,
    is_active: bool,
) -> None:
    """Обновляем данные ивента."""
    query = """
        UPDATE events
        SET title = %s,
            description = %s,
            event_type = %s,
            starts_at = %s,
            ends_at = %s,
            is_active = %s
        WHERE id = %s;
    """
    execute(
        query,
        (title, description, event_type, starts_at, ends_at, is_active, event_id),
    )


def delete_event(event_id: int) -> None:
    """Удаляем ивент (награды удалятся каскадно)."""
    query = "DELETE FROM events WHERE id = %s;"
    execute(query, (event_id,))
