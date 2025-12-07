import pytest

from app import create_app
from models.database import execute


@pytest.fixture(scope="session")
def app():
    """
    Создаём Flask-приложение один раз на всю сессию тестов.
    create_app() внутри уже вызывает init_db().
    """
    app = create_app()
    # Для тестов выключим режим отладки Werkzeug
    app.config.update({"TESTING": True})
    return app


@pytest.fixture()
def client(app):
    """
    Тестовый клиент Flask — через него будем делать запросы к роутам.
    """
    return app.test_client()


@pytest.fixture(autouse=True)
def db_clean():
    """
    Перед КАЖДЫМ тестом очищаем таблицы, чтобы тесты не мешали друг другу.
    """
    # Сначала дочерние таблицы (rewards), затем events
    execute("DELETE FROM rewards;")
    execute("DELETE FROM events;")
    yield
    # На всякий случай ещё раз почистим после теста
    execute("DELETE FROM rewards;")
    execute("DELETE FROM events;")
