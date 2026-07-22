"""
api.py  —  v4.1
===============
Flask REST API backend.
Refactored to use Application Factory pattern for production readiness.
"""
from backend.app.factory import create_app
from backend.app.config import Config
from backend.utils.logger import get_logger

logger = get_logger("main")

# Initialize the global app object for Gunicorn/WSGI
app = create_app()

if __name__ == "__main__":
    logger.info(f"Application starting up on port {Config.PORT}...")
    app.run(debug=Config.MDRP_DEBUG, host="0.0.0.0", port=Config.PORT)
