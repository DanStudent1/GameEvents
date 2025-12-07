from flask import Flask
from models.database import init_db
from controllers.events_controller import events_bp
from controllers.api_controller import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "super-secret-key-for-dev"

    init_db()

    app.register_blueprint(events_bp)
    app.register_blueprint(api_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
