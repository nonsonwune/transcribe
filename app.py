from flask import Flask, session
from config import Config
from routes import main_bp
import logging
from utils import setup_directories
from celery_app import celery  # Import the celery instance

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_app():
    app = Flask(__name__)
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
