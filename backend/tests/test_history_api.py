import pytest
from backend.app.factory import create_app
from backend.database import Base, init_db, get_session

@pytest.fixture(scope="module")
def app():
    # Ensure config has testing setup
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE_URL": "sqlite:///:memory:"
    })
    
    with app.app_context():
        init_db("sqlite:///:memory:")
        engine = get_session().get_bind()
        Base.metadata.create_all(engine)
        yield app
        Base.metadata.drop_all(engine)

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

from unittest.mock import patch
from backend.auth.user_context import CurrentUser
from backend.services.history_service import history_service

def test_history_unauthorized(client):
    response = client.get("/api/v1/history")
    assert response.status_code == 401

def test_history_and_export_pdf_authorized(client):
    clerk_id = "user_test_export_999"
    
    # Save a prediction in DB
    pred_id = history_service.save_prediction_result(
        clerk_id=clerk_id,
        results={"heart": 35.0, "diabetes": 20.0, "kidney": 15.0, "scores_detail": {}},
        patient_data={"age": 45, "bmi": 24.5}
    )
    
    with patch('backend.auth.auth_service.ClerkAuthService.verify_token') as mock_verify:
        mock_verify.return_value = CurrentUser(user_id=clerk_id, session_id="sess_123")
        headers = {"Authorization": "Bearer valid_test_token"}

        # 1. Test history list
        resp = client.get("/api/v1/history", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] >= 1

        # 2. Test history detail
        resp_detail = client.get(f"/api/v1/history/{pred_id}", headers=headers)
        assert resp_detail.status_code == 200

        # 3. Test export PDF
        resp_pdf = client.get(f"/api/v1/history/{pred_id}/export-pdf", headers=headers)
        assert resp_pdf.status_code == 200
        assert resp_pdf.mimetype == "application/pdf"
        assert resp_pdf.data.startswith(b"%PDF-")

        # 4. Test notifications endpoint
        resp_notif = client.get("/api/v1/notifications", headers=headers)
        assert resp_notif.status_code == 200
        assert "items" in resp_notif.get_json()
