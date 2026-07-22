import pytest
import io
from api import app as flask_app
from backend.app.config import Config

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def sample_patient_data():
    """Basic valid patient data for API testing."""
    return {
        "age": 45,
        "gender": 1,
        "bmi": 25.5,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "glucose": 95,
        "cholesterol": 180,
        "hdl": 50,
        "ldl": 100,
        "triglycerides": 120,
        "bgr": 130,
        "bu": 15.0,
        "sc": 1.0,
        "sod": 140,
        "pot": 4.5,
        "hemo": 15.0,
        "pcv": 45,
        "wc": 8000,
        "rc": 5.0
    }

@pytest.fixture
def sample_pdf_file():
    """Mock a PDF file upload."""
    return (io.BytesIO(b"%PDF-1.4 sample PDF content"), "test_report.pdf")
