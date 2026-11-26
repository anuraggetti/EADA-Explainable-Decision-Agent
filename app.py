"""
E.A.D.A Flask Application
-------------------------
Main application entry point.
"""

from flask import Flask

from config import DevelopmentConfig

from routes.analytics import analytics_bp
from routes.decision import decision_bp
from routes.home import home_bp
from routes.train import train_bp
from routes.history import history_bp


def create_app(
    config_class=DevelopmentConfig
) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_class:
            Configuration class used to initialize Flask.

    Returns:
        Configured Flask application.
    """

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    app.config.from_object(config_class)

    config_class.create_required_directories()

    register_blueprints(app)

    return app


def register_blueprints(app: Flask) -> None:
    """
    Register all currently available application blueprints.
    """

    app.register_blueprint(home_bp)
    app.register_blueprint(decision_bp)
    app.register_blueprint(train_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(history_bp)


app = create_app()


if __name__ == "__main__":
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
        use_reloader=app.config["USE_RELOADER"]
    )