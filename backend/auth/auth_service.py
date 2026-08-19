import jwt
import requests
from jwt.algorithms import RSAAlgorithm
from flask import current_app

from backend.utils.logger import get_logger
from backend.auth.user_context import CurrentUser

logger = get_logger("auth_service")

class ClerkAuthService:
    _jwks_cache = None

    @classmethod
    def get_jwks(cls):
        if cls._jwks_cache is None:
            clerk_frontend = current_app.config.get("CLERK_FRONTEND_API", "").strip().strip("/")
            if not clerk_frontend:
                raise ValueError("CLERK_FRONTEND_API is not configured")

            # Strip any existing protocol prefix — we always add https://
            for prefix in ("https://", "http://"):
                if clerk_frontend.startswith(prefix):
                    clerk_frontend = clerk_frontend[len(prefix):]

            jwks_url = f"https://{clerk_frontend}/.well-known/jwks.json"
            logger.info(f"Fetching JWKS from: {jwks_url}")

            try:
                response = requests.get(jwks_url, timeout=10)
                response.raise_for_status()
                cls._jwks_cache = response.json()
            except Exception as e:
                logger.error(f"Failed to fetch JWKS: {e}")
                raise

        return cls._jwks_cache

    @classmethod
    def clear_jwks_cache(cls):
        """Clear cached JWKS (e.g. after key rotation)."""
        cls._jwks_cache = None

    @classmethod
    def verify_token(cls, token: str) -> CurrentUser:
        try:
            jwks = cls.get_jwks()
            public_keys = {}
            for jwk in jwks['keys']:
                kid = jwk['kid']
                public_keys[kid] = RSAAlgorithm.from_jwk(jwk)

            kid = jwt.get_unverified_header(token)['kid']
            key = public_keys.get(kid)

            if not key:
                raise ValueError("Public key not found in JWKS")

            payload = jwt.decode(
                token,
                key=key,
                algorithms=['RS256'],
                options={"verify_aud": False, "verify_iss": False}
            )

            user_id = payload.get("sub")
            session_id = payload.get("sid", "")
            roles = payload.get("roles", [])
            metadata = payload.get("metadata", {})

            logger.info(f"JWT verified successfully for user: {user_id}")
            return CurrentUser(
                user_id=user_id,
                session_id=session_id,
                roles=roles,
                metadata=metadata
            )

        except jwt.ExpiredSignatureError:
            logger.warning("Authentication Failure: Token expired")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Authentication Failure: Invalid token ({str(e)})")
            raise ValueError(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Authentication Failure: Unexpected error verifying token ({str(e)})")
            raise ValueError("Token verification failed")
