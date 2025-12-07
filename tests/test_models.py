from datetime import datetime, timedelta

from models import event as event_model
from models import reward as reward_model


def test_create_and_get_event():
    # Arrange
    starts_at = datetime.utcnow()
    ends_at = starts_at + timedelta(hours=2)

    # Act
    new_id = event_model.create_event(
        title="Test Event",
        description="Some description",
        event_type="Seasonal",
        starts_at=starts_at,
        ends_at=ends_at,
        is_active=True,
    )

    ev = event_model.get_event_by_id(new_id)

    # Assert
    assert ev is not None
    assert ev["title"] == "Test Event"
    assert ev["event_type"] == "Seasonal"
    assert ev["is_active"] is True


def test_get_active_events_filters_by_time_and_flag():
    now = datetime.utcnow()

    # Ивент, который активен сейчас
    active_id = event_model.create_event(
        title="Active",
        description="",
        event_type="Daily",
        starts_at=now - timedelta(hours=1),
        ends_at=now + timedelta(hours=1),
        is_active=True,
    )

    # Ивент в будущем — не должен попасть
    future_id = event_model.create_event(
        title="Future",
        description="",
        event_type="Daily",
        starts_at=now + timedelta(hours=2),
        ends_at=now + timedelta(hours=3),
        is_active=True,
    )

    # Ивент с выключенным флагом — тоже не должен попасть
    inactive_id = event_model.create_event(
        title="Inactive",
        description="",
        event_type="Daily",
        starts_at=now - timedelta(hours=1),
        ends_at=now + timedelta(hours=1),
        is_active=False,
    )

    active_events = event_model.get_active_events(now)

    ids = {e["id"] for e in active_events}

    assert active_id in ids
    assert future_id not in ids
    assert inactive_id not in ids


def test_rewards_add_and_get():
    # Сначала создадим ивент
    starts_at = datetime.utcnow()
    ends_at = starts_at + timedelta(hours=1)

    event_id = event_model.create_event(
        title="Event with rewards",
        description="",
        event_type="Quest",
        starts_at=starts_at,
        ends_at=ends_at,
        is_active=True,
    )

    # Добавляем две награды
    reward_model.add_reward(event_id, "Gold", 1000, "1000 золота")
    reward_model.add_reward(event_id, "XP", 500, "500 опыта")

    rewards = reward_model.get_rewards_for_event(event_id)

    assert len(rewards) == 2
    types = {r["reward_type"] for r in rewards}
    assert "Gold" in types
    assert "XP" in types
