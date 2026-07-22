"""
Auth module for Clerk integration.
"""
from .user_context import CurrentUser
from .auth_service import ClerkAuthService
from .decorators import login_required, roles_required
