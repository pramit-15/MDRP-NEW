import pytest
import json
from unittest.mock import patch
from flask import g
from backend.auth.user_context import CurrentUser

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_valid_token"}

def test_missing_token(client):
    """Test accessing protected route without a token."""
    response = client.post('/api/v1/predict', json={})
    assert response.status_code == 401
    assert "error" in response.json
    assert response.json["error"]["type"] == "AuthenticationError"

def test_invalid_token(client):
    """Test accessing protected route with invalid token."""
    with patch('app.auth.auth_service.ClerkAuthService.verify_token') as mock_verify:
        mock_verify.side_effect = ValueError("Invalid token")
        
        response = client.post('/api/v1/predict', headers={"Authorization": "Bearer invalid_token"}, json={})
        assert response.status_code == 401
        assert "error" in response.json

def test_expired_token(client):
    """Test accessing protected route with expired token."""
    with patch('app.auth.auth_service.ClerkAuthService.verify_token') as mock_verify:
        mock_verify.side_effect = ValueError("Token has expired")
        
        response = client.post('/api/v1/predict', headers={"Authorization": "Bearer expired_token"}, json={})
        assert response.status_code == 401

def test_valid_token_protected_route(client, auth_headers):
    """Test accessing protected route with valid token. Should pass auth and hit validation."""
    with patch('app.auth.auth_service.ClerkAuthService.verify_token') as mock_verify:
        mock_verify.return_value = CurrentUser(user_id="user_123", session_id="sess_123")
        
        # We send invalid body just to trigger 400 validation error (which means auth passed)
        response = client.post('/api/v1/predict', headers=auth_headers, json={})
        assert response.status_code == 400
        assert response.json["error"]["type"] == "ValidationError"

def test_public_routes(client):
    """Test that public routes remain accessible without auth."""
    response_health = client.get('/api/v1/health')
    assert response_health.status_code == 200
    
    response_ready = client.get('/api/v1/ready')
    # Can be 200 or 503 depending on model loading, but shouldn't be 401
    assert response_ready.status_code in (200, 503)

    response_apidocs = client.get('/apidocs/')
    # Swagger UI usually returns 200, if not configured at /apidocs/ maybe 404, but not 401
    assert response_apidocs.status_code != 401
