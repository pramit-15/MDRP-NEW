import os
import time
import uuid
from flask import Flask, g, request
from flasgger import Swagger
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load .env if present (for local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from backend.app.config import Config
from backend.utils.logger import get_logger
from backend.database import init_db
from backend.services.model_loader import model_loader

logger = get_logger("factory")

# Global dict to store app state (useful for health checks)
app_state = {
    "start_time": time.time(),
    "models_loaded": False,
    "version": Config.VERSION
}

def create_app(config_class=Config):
    config_class.validate()
    app = Flask(__name__, static_folder=config_class.STATIC_DIR, template_folder=config_class.TEMPLATES_DIR)
    app.config.from_object(config_class)
    
    # Initialize Security Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # Customize origins in production
    # Talisman: disable force_https in dev/testing so local http:// calls work
    is_prod = os.environ.get("FLASK_ENV", "development").lower() == "production"
    Talisman(app, content_security_policy=None, force_https=is_prod)
    
    # Rate Limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # Initialize Database engine and session factory
    init_db(config_class.DATABASE_URL)
    
    # Auto-create tables if they don't exist (dev-friendly; Alembic handles production)
    try:
        from backend.database.base import Base
        from backend.database import models  # noqa: F401 — imports all model classes
        from backend.database.database import get_engine
        eng = get_engine()
        if eng is not None:
            Base.metadata.create_all(bind=eng)
            logger.info("Database tables verified/created.")
    except Exception as e:
        logger.error(f"Database table creation failed: {e}")
    
    # Initialize Swagger
    app.config['SWAGGER'] = {
        'title': 'MDRP API',
        'uiversion': 3,
        'openapi': '3.0.0',
        'version': config_class.VERSION,
        'components': {
            'securitySchemes': {
                'BearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT'
                }
            }
        }
    }
    Swagger(app)

    # Initialize models
    try:
        model_loader.load_all()
        app_state["models_loaded"] = True
        logger.info("All models loaded successfully during startup.")
    except Exception as e:
        logger.error(f"Failed to load models during startup: {e}")
        app_state["models_loaded"] = False

    # Request ID injection and Logging
    @app.before_request
    def before_request():
        g.start_time = time.time()
        
        # Use existing X-Request-ID if provided by proxy/gateway, else generate one
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
        g.request_id = request_id
        
        # Run Clerk authentication middleware
        from backend.auth.middleware import clerk_middleware
        clerk_middleware()

    @app.after_request
    def after_request(response):
        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id
            
        if hasattr(g, "start_time"):
            duration_ms = (time.time() - g.start_time) * 1000
            
            # Safely capture request input
            req_body = ""
            if request.content_length and request.content_length < 50000: # Don't log massive files
                try:
                    req_body = request.get_data(as_text=True)
                    if len(req_body) > 1000:
                        req_body = req_body[:1000] + "... [truncated]"
                except Exception:
                    req_body = "[Unparseable request body]"

            # Safely capture response output
            res_body = ""
            if response.content_type and "application/json" in response.content_type:
                try:
                    res_body = response.get_data(as_text=True)
                    if len(res_body) > 1000:
                        res_body = res_body[:1000] + "... [truncated]"
                except Exception:
                    res_body = "[Unparseable response body]"

            # Log the request details
            logger.info(
                f"{request.method} {request.path} - {response.status_code} - {duration_ms:.2f}ms",
                extra={
                    "http_method": request.method,
                    "http_path": request.path,
                    "http_status": response.status_code,
                    "duration_ms": duration_ms,
                    "client_ip": request.remote_addr,
                    "request_body": req_body,
                    "response_body": res_body
                }
            )
            
        return response

    @app.teardown_appcontext
    def remove_session(exception=None):
        from backend.database.database import SessionLocal
        try:
            if SessionLocal:
                SessionLocal.remove()
        except RuntimeError:
            pass

    # Register Blueprints
    from backend.api.routes import api_bp, root_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(root_bp)
    
    return app
