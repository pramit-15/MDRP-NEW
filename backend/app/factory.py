import time
import uuid
from flask import Flask, g, request
from flasgger import Swagger
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from backend.app.config import Config
from backend.utils.logger import get_logger
from backend.database import init_db
from backend.services.model_loader import model_loader
from backend.utils.exceptions import ModelLoadingError

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
    Talisman(app, content_security_policy=None) # CSP can be strict, setting to None for API mostly, or customize
    
    # Rate Limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # Initialize Database engine and session factory
    init_db(config_class.DATABASE_URL)
    
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

    # Request ID injection
    @app.before_request
    def before_request():
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
