import logging
from flask import Flask, session
from config import Config
from routes import main_bp
from celery_app import celery, create_app_with_celery
from utils import setup_directories

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_app():
    app, _ = (
        create_app_with_celery()
    )  # Use create_app_with_celery instead of create_flask_app
    app.config.from_object(Config)

    # Ensure necessary directories exist
    with app.app_context():
        setup_directories(app)

    # Register blueprint
    app.register_blueprint(main_bp)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
