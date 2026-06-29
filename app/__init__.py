from flask import Flask
from .config import config


def create_app(config_name="default"):
    """
    Application factory pattern.
    Keeps the app testable and config-swappable without circular imports.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Load config object
    app.config.from_object(config[config_name])

    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register custom Jinja2 filters
    from .filters import register_filters
    register_filters(app)

    return app
