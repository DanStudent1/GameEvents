from datetime import datetime, timedelta

from models import event as event_model


def _dt_to_html(dt: datetime) -> str:
    """
    Вспомогательная функция: datetime -> формат для input[type=datetime-local].
    """
    return dt.strftime("%Y-%m-%dT%H:%M")


def test_index_page_empty(client):
    resp = client.get("/")
    assert resp.status_code == 200
    text = resp.data.decode("utf-8")
    assert "Список ивентов" in text
    assert "Ивентов пока нет. Создайте первый." in text


def test_create_event_via_form_and_view_it(client):
    starts_at = datetime.utcnow()
    ends_at = starts_at + timedelta(hours=2)

    form_data = {
        "title": "Form Event",
        "event_type": "PvP",
        "starts_at": _dt_to_html(starts_at),
        "ends_at": _dt_to_html(ends_at),
        "description": "Создан через форму",
        "is_active": "on",
    }

    # Отправляем POST на создание, следуем за редиректом
    resp = client.post(
        "/events/new",
        data=form_data,
        follow_redirects=True,
    )
    assert resp.status_code == 200
    text = resp.data.decode("utf-8")
    # На детальной странице должен быть заголовок и текст
    assert "Ивент: Form Event" in text
    assert "Создан через форму" in text

    # Проверим, что на главной странице ивент тоже отображается
    resp_index = client.get("/")
    text_index = resp_index.data.decode("utf-8")
    assert "Form Event" in text_index


def test_api_events_and_active(client):
    # Для начала — БД пустая (фикстура db_clean уже всё очистила).

    now = datetime.utcnow()

    # Создадим активный ивент
    active_id = event_model.create_event(
        title="API Active",
        description="",
        event_type="Daily",
        starts_at=now - timedelta(minutes=30),
        ends_at=now + timedelta(minutes=30),
        is_active=True,
    )

    # И неактивный
    inactive_id = event_model.create_event(
        title="API Inactive",
        description="",
        event_type="Daily",
        starts_at=now - timedelta(minutes=30),
        ends_at=now + timedelta(minutes=30),
        is_active=False,
    )

    # /api/events — должны прийти оба
    resp_all = client.get("/api/events")
    assert resp_all.status_code == 200
    data_all = resp_all.get_json()
    ids_all = {e["id"] for e in data_all}
    assert active_id in ids_all
    assert inactive_id in ids_all

    # /api/events/active — только активный
    resp_active = client.get("/api/events/active")
    assert resp_active.status_code == 200
    data_active = resp_active.get_json()
    ids_active = {e["id"] for e in data_active}
    assert active_id in ids_active
    assert inactive_id not in ids_active
