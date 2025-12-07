from datetime import datetime

from flask import Blueprint, jsonify

from models import event as event_model
from models import reward as reward_model

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/events")
def api_events():
    """Все ивенты (для интеграции с внешними клиентами)."""
    events = event_model.get_all_events()
    return jsonify(events)


@api_bp.get("/events/active")
def api_active_events():
    """Активные ивенты на текущий момент."""
    now = datetime.utcnow()
    events = event_model.get_active_events(now)
    return jsonify(events)


@api_bp.get("/events/<int:event_id>")
def api_event_detail(event_id: int):
    """Информация об одном ивенте."""
    ev = event_model.get_event_by_id(event_id)
    if ev is None:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(ev)


@api_bp.get("/events/<int:event_id>/rewards")
def api_event_rewards(event_id: int):
    """Награды для ивента."""
    rewards = reward_model.get_rewards_for_event(event_id)
    return jsonify(rewards)
