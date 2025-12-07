from typing import Any

from .database import fetch_all, execute, execute_returning_id


def add_reward(
    event_id: int,
    reward_type: str,
    amount: int | None,
    description: str,
) -> int:
    """Добавляем награду к ивенту, возвращаем id награды."""
    query = """
        INSERT INTO rewards (event_id, reward_type, amount, description)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    return execute_returning_id(query, (event_id, reward_type, amount, description))


def get_rewards_for_event(event_id: int) -> list[dict[str, Any]]:
    """Список наград для указанного ивента."""
    query = """
        SELECT id, reward_type, amount, description
        FROM rewards
        WHERE event_id = %s
        ORDER BY id;
    """
    return fetch_all(query, (event_id,))


def delete_rewards_for_event(event_id: int) -> None:
    """Удаляем все награды ивента (обычно не нужно, т.к. CASCADE)."""
    query = "DELETE FROM rewards WHERE event_id = %s;"
    execute(query, (event_id,))
