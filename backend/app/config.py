import os

class ConfigError(Exception):
    pass

class BaseConfig:
    # Base Directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

    # App Settings
    VERSION = "1.0.0"
    PORT = int(os.environ.get("PORT", 5000))
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB

    # Model paths - strictly from env variables or fallback to a known models directory
    MODELS_DIR = os.environ.get("MODELS_DIR", os.path.join(os.path.dirname(BASE_DIR), "models"))
    
    HEART_MODEL_PATH = os.environ.get("HEART_MODEL_PATH", os.path.join(MODELS_DIR, "heart_model.pkl"))
    DIABETES_MODEL_PATH = os.environ.get("DIABETES_MODEL_PATH", os.path.join(MODELS_DIR, "diabetes_model.pkl"))
    KIDNEY_MODEL_PATH = os.environ.get("KIDNEY_MODEL_PATH", os.path.join(MODELS_DIR, "kidney_model.pkl"))
    HM_MODEL_PATH = os.environ.get("HM_MODEL_PATH", os.path.join(MODELS_DIR, "hm_model.pkl"))
    
    HEART_SCALER_PATH = os.environ.get("HEART_SCALER_PATH", os.path.join(MODELS_DIR, "heart_scaler.pkl"))
    DIABETES_SCALER_PATH = os.environ.get("DIABETES_SCALER_PATH", os.path.join(MODELS_DIR, "diabetes_scaler.pkl"))
    KIDNEY_SCALER_PATH = os.environ.get("KIDNEY_SCALER_PATH", os.path.join(MODELS_DIR, "kidney_scaler.pkl"))
    HM_SCALER_PATH = os.environ.get("HM_SCALER_PATH", os.path.join(MODELS_DIR, "hm_scaler.pkl"))
    
    HM_CLASSES_PATH = os.environ.get("HM_CLASSES_PATH", os.path.join(MODELS_DIR, "hm_classes.pkl"))
    HM_FEATURES_PATH = os.environ.get("HM_FEATURES_PATH", os.path.join(MODELS_DIR, "hm_features.pkl"))
    KIDNEY_FEATURES_PATH = os.environ.get("KIDNEY_FEATURES_PATH", os.path.join(MODELS_DIR, "kidney_features.pkl"))

    # Required API Keys & Secrets
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY")
    CLERK_PUBLISHABLE_KEY = os.environ.get("CLERK_PUBLISHABLE_KEY")
    CLERK_JWT_ISSUER = os.environ.get("CLERK_JWT_ISSUER")
    CLERK_FRONTEND_API = os.environ.get("CLERK_FRONTEND_API")

    @classmethod
    def validate(cls):
        required_vars = [
            "GOOGLE_API_KEY",
            "CLERK_SECRET_KEY", 
            "CLERK_PUBLISHABLE_KEY",
            "CLERK_JWT_ISSUER",
            "CLERK_FRONTEND_API",
            "DATABASE_URL"
        ]
        missing = [v for v in required_vars if not getattr(cls, v, None)]
        if missing:
            raise ConfigError(f"Missing required environment variables: {', '.join(missing)}")


class DevelopmentConfig(BaseConfig):
    MDRP_DEBUG = True
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://user:pass@localhost:5432/mdrp_dev")
    
    @classmethod
    def validate(cls):
        # In development we might bypass strict checks for Clerk/Gemini if not testing auth/LLM
        pass


class TestingConfig(BaseConfig):
    TESTING = True
    MDRP_DEBUG = True
    DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    # Mock secrets for testing
    GOOGLE_API_KEY = "mock_key"
    CLERK_SECRET_KEY = "mock_key"
    CLERK_PUBLISHABLE_KEY = "mock_key"
    CLERK_JWT_ISSUER = "mock_key"
    CLERK_FRONTEND_API = "mock_key"
    
    @classmethod
    def validate(cls):
        pass


class ProductionConfig(BaseConfig):
    MDRP_DEBUG = False
    DATABASE_URL = os.environ.get("DATABASE_URL")

    @classmethod
    def validate(cls):
        super().validate()


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    return DevelopmentConfig

Config = get_config()
