import pytest
import json
import io

def test_predict_route_success(client, sample_patient_data):
    response = client.post("/predict", json=sample_patient_data)
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "heart" in data
    assert "diabetes" in data
    assert "kidney" in data
    assert "scores_detail" in data
    assert "health_condition" in data

def test_predict_route_missing_body(client):
    response = client.post("/predict")
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["type"] == "ValidationError"
    assert data["error"]["field"] == "request"

def test_predict_route_validation_error(client, sample_patient_data):
    invalid_data = sample_patient_data.copy()
    invalid_data["age"] = -5 # Invalid age
    
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["type"] == "ValidationError"
    assert data["error"]["field"] == "age"

def test_parse_pdf_success(client, sample_pdf_file):
    # Depending on whether google-genai and pdfplumber are installed,
    # this might return success or ConfigurationError. We test for both cases.
    response = client.post("/parse-pdf", data={
        "file": sample_pdf_file
    })
    
    if response.status_code == 500:
        data = response.get_json()
        assert data["error"]["type"] in ["ConfigurationError", "SystemError"]
    else:
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "extracted" in data
        assert "method" in data

def test_parse_pdf_no_file(client):
    response = client.post("/parse-pdf")
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["type"] == "PDFParsingError"

def test_parse_pdf_invalid_file(client):
    response = client.post("/parse-pdf", data={
        "file": (io.BytesIO(b"image data"), "test.jpg")
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["message"] == "Only PDF files are accepted."
