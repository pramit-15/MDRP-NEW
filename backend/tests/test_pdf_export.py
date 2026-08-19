import pytest
import io
from backend.services.pdf_export_service import pdf_export_service

def test_generate_prediction_pdf():
    sample_prediction = {
        "id": "pred_test_12345678",
        "heart_risk": 45.2,
        "diabetes_risk": 18.7,
        "kidney_risk": 12.0,
        "scores_detail": {
            "heart": {"ml": 50.0, "clinical": 40.0},
            "diabetes": {"ml": 20.0, "clinical": 17.0},
            "kidney": {"ml": 10.0, "clinical": 15.0}
        },
        "inputs_used": {
            "age": 52,
            "bmi": 28.4,
            "blood_pressure": 135,
            "cholesterol": 210,
            "glucose": 105
        },
        "ai_suggestions": {
            "summary": "Patient exhibits moderate cardiovascular risk driven by elevated blood pressure and total cholesterol.",
            "top_priority": "Initiate daily aerobic exercise and reduce dietary sodium.",
            "lifestyle_suggestions": [
                {
                    "category": "Diet & Nutrition",
                    "title": "Low Sodium DASH Diet",
                    "priority": "High",
                    "advice": "Limit sodium to under 2,000 mg daily.",
                    "action_items": ["Replace processed snacks with fresh fruit", "Check nutrition labels"]
                }
            ]
        }
    }

    pdf_buffer = pdf_export_service.generate_prediction_pdf(sample_prediction)
    assert isinstance(pdf_buffer, io.BytesIO)
    content = pdf_buffer.getvalue()
    # Check PDF header magic bytes %PDF-
    assert content.startswith(b"%PDF-")
    assert len(content) > 1000 # Formatted multi-page PDF has substantial byte content
