from functools import wraps
from flask import g, jsonify
from backend.utils.logger import get_logger

logger = get_logger("auth_decorators")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(g, 'user', None) or not g.user.is_authenticated:
            logger.warning("Authorization Failure: Unauthenticated request to protected endpoint")
            return jsonify({
                "success": False,
                "error": {
                    "type": "AuthenticationError",
                    "message": "Missing or invalid authentication token"
                }
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*required_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not getattr(g, 'user', None) or not g.user.is_authenticated:
                logger.warning("Authorization Failure: Unauthenticated request to roles-protected endpoint")
                return jsonify({
                    "success": False,
                    "error": {
                        "type": "AuthenticationError",
                        "message": "Missing or invalid authentication token"
                    }
                }), 401
                
            user_roles = g.user.roles
            for role in required_roles:
                if role not in user_roles:
                    logger.warning(f"Authorization Failure: User {g.user.user_id} lacks required role '{role}'")
                    return jsonify({
                        "success": False,
                        "error": {
                            "type": "AuthorizationError",
                            "message": "Insufficient permissions"
                        }
                    }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
