from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from models import event as event_model
from models import reward as reward_model

events_bp = Blueprint("events", __name__)


@events_bp.route("/")
def index():
    """Список всех ивентов."""
    events = event_model.get_all_events()
    return render_template("events_list.html", events=events)


@events_bp.route("/events/new", methods=["GET", "POST"])
def create_event():
    """Создание нового ивента."""
    if request.method == "POST":
        form = request.form

        title = form.get("title", "").strip()
        description = form.get("description", "").strip()
        event_type = form.get("event_type", "").strip()
        starts_at_str = form.get("starts_at", "").strip()
        ends_at_str = form.get("ends_at", "").strip()
        is_active_str = form.get("is_active")

        if not title or not event_type or not starts_at_str or not ends_at_str:
            flash("Пожалуйста, заполните все обязательные поля.")
            return render_template("event_form.html", form=form)

        try:
            starts_at = datetime.strptime(starts_at_str, "%Y-%m-%dT%H:%M")
            ends_at = datetime.strptime(ends_at_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Некорректный формат даты/времени.")
            return render_template("event_form.html", form=form)

        is_active = is_active_str == "on"

        new_id = event_model.create_event(
            title=title,
            description=description,
            event_type=event_type,
            starts_at=starts_at,
            ends_at=ends_at,
            is_active=is_active,
        )

        flash("Ивент успешно создан.")
        return redirect(url_for("events.view_event", event_id=new_id))

    return render_template("event_form.html", form=None)


@events_bp.route("/events/<int:event_id>")
def view_event(event_id: int):
    """Просмотр ивента + список наград."""
    ev = event_model.get_event_by_id(event_id)
    if ev is None:
        flash("Ивент не найден.")
        return redirect(url_for("events.index"))

    rewards = reward_model.get_rewards_for_event(event_id)
    return render_template("event_detail.html", event=ev, rewards=rewards)


@events_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
def edit_event(event_id: int):
    """Редактирование ивента."""
    ev = event_model.get_event_by_id(event_id)
    if ev is None:
        flash("Ивент не найден.")
        return redirect(url_for("events.index"))

    if request.method == "POST":
        form = request.form

        title = form.get("title", "").strip()
        description = form.get("description", "").strip()
        event_type = form.get("event_type", "").strip()
        starts_at_str = form.get("starts_at", "").strip()
        ends_at_str = form.get("ends_at", "").strip()
        is_active_str = form.get("is_active")

        if not title or not event_type or not starts_at_str or not ends_at_str:
            flash("Пожалуйста, заполните все обязательные поля.")
            return render_template("event_form.html", form=form, event_id=event_id, is_edit=True)

        try:
            starts_at = datetime.strptime(starts_at_str, "%Y-%m-%dT%H:%M")
            ends_at = datetime.strptime(ends_at_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Некорректный формат даты/времени.")
            return render_template("event_form.html", form=form, event_id=event_id, is_edit=True)

        is_active = is_active_str == "on"

        event_model.update_event(
            event_id=event_id,
            title=title,
            description=description,
            event_type=event_type,
            starts_at=starts_at,
            ends_at=ends_at,
            is_active=is_active,
        )

        flash("Ивент обновлён.")
        return redirect(url_for("events.view_event", event_id=event_id))

    ev_form = {
        "title": ev["title"],
        "description": ev["description"] or "",
        "event_type": ev["event_type"],
        "starts_at": ev["starts_at"].strftime("%Y-%m-%dT%H:%M"),
        "ends_at": ev["ends_at"].strftime("%Y-%m-%dT%H:%M"),
        "is_active": "on" if ev["is_active"] else "",
    }

    return render_template("event_form.html", form=ev_form, event_id=event_id, is_edit=True)


@events_bp.route("/events/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id: int):
    """Удаление ивента."""
    event_model.delete_event(event_id)
    flash("Ивент удалён.")
    return redirect(url_for("events.index"))


@events_bp.route("/events/<int:event_id>/rewards/add", methods=["POST"])
def add_reward(event_id: int):
    """Добавление награды к ивенту."""
    ev = event_model.get_event_by_id(event_id)
    if ev is None:
        flash("Ивент не найден.")
        return redirect(url_for("events.index"))

    form = request.form
    reward_type = form.get("reward_type", "").strip()
    amount_str = form.get("amount", "").strip()
    description = form.get("description", "").strip()

    amount = int(amount_str) if amount_str else None

    if not reward_type:
        flash("Тип награды обязателен.")
        return redirect(url_for("events.view_event", event_id=event_id))

    reward_model.add_reward(event_id, reward_type, amount, description)
    flash("Награда добавлена.")
    return redirect(url_for("events.view_event", event_id=event_id))
