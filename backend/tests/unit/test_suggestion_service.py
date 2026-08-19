import pytest
from backend.services.suggestion_service import SuggestionService

def test_suggestion_service_fallback_generation():
    service = SuggestionService()
    
    mock_results = {
        "heart": 45.5,
        "diabetes": 58.2,
        "kidney": 15.0,
        "scores_detail": {
            "heart": {"ml": 40.0, "clinical": 50.0},
            "diabetes": {"ml": 60.0, "clinical": 55.0},
            "kidney": {"ml": 10.0, "clinical": 20.0},
        },
        "clinical_scores": {
            "heart_clinical": 50.0,
            "diabetes_clinical": 55.0,
            "kidney_clinical": 20.0
        },
        "health_condition": {"Pre-Diabetic": 65.0, "Healthy": 35.0}
    }
    
    mock_patient_data = {
        "age": 52,
        "sex": 1,
        "bmi": 28.4,
        "glucose": 118,
        "hba1c": 6.1,
        "trestbps": 138,
        "bloodpressure": 88,
        "chol": 215,
        "ldl": 130,
        "sc": 0.9,
        "egfr": 92
    }
    
    mock_explainability = {
        "top_features": {
            "diabetes": [{"feature": "glucose", "contribution": 0.08}],
            "heart": [{"feature": "trestbps", "contribution": 0.05}]
        }
    }
    
    suggestions = service.generate_suggestions(mock_results, mock_patient_data, mock_explainability)
    
    assert isinstance(suggestions, dict)
    assert "summary" in suggestions
    assert len(suggestions["summary"]) > 20
    assert "risk_breakdown" in suggestions
    assert "heart" in suggestions["risk_breakdown"]
    assert "diabetes" in suggestions["risk_breakdown"]
    assert "kidney" in suggestions["risk_breakdown"]
    
    assert "lifestyle_suggestions" in suggestions
    assert len(suggestions["lifestyle_suggestions"]) >= 3
    
    for item in suggestions["lifestyle_suggestions"]:
        assert "category" in item
        assert "title" in item
        assert "advice" in item
        assert "action_items" in item
        assert len(item["action_items"]) > 0
        
    assert "top_priority" in suggestions
    assert len(suggestions["top_priority"]) > 10
    assert "disclaimer" in suggestions
    assert suggestions["generated_by"] in ["gemini_ai", "clinical_rules"]

def test_suggestion_service_low_risk_profile():
    service = SuggestionService()
    
    low_risk_results = {
        "heart": 12.0,
        "diabetes": 8.5,
        "kidney": 5.0,
        "scores_detail": {
            "heart": {"ml": 10.0, "clinical": 14.0},
            "diabetes": {"ml": 8.0, "clinical": 9.0},
            "kidney": {"ml": 5.0, "clinical": 5.0},
        },
        "clinical_scores": {
            "heart_clinical": 14.0,
            "diabetes_clinical": 9.0,
            "kidney_clinical": 5.0
        },
        "health_condition": {"Optimal Health": 90.0}
    }
    
    low_risk_patient = {
        "age": 28,
        "sex": 0,
        "bmi": 21.5,
        "glucose": 88,
        "hba1c": 5.1,
        "trestbps": 112,
        "bloodpressure": 72,
        "chol": 160,
        "ldl": 80,
        "sc": 0.7,
        "egfr": 110
    }
    
    suggestions = service.generate_suggestions(low_risk_results, low_risk_patient)
    assert isinstance(suggestions, dict)
    assert "summary" in suggestions
    assert "lifestyle_suggestions" in suggestions
    assert len(suggestions["lifestyle_suggestions"]) >= 3
