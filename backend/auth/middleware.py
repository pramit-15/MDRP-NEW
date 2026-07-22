from flask import request, g
from backend.auth.auth_service import ClerkAuthService
from backend.utils.logger import get_logger

logger = get_logger("clerk_middleware")

def clerk_middleware():
    """
    Middleware to intercept request and verify Clerk JWT if provided.
    Populates g.user with CurrentUser.
    """
    auth_header = request.headers.get("Authorization")
    
    g.user = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            user = ClerkAuthService.verify_token(token)
            g.user = user
            logger.info(f"Authentication Success: User {user.user_id}")
        except Exception as e:
            # We don't fail the request here. The @login_required decorator will handle missing/invalid auth.
            logger.debug(f"Middleware JWT verification failed: {e}")
