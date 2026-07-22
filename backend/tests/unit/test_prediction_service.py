import pytest
from unittest.mock import patch, MagicMock
from backend.services.prediction_service import PredictionService
from backend.utils.exceptions import PredictionError
from backend.app.constants import RISK_THRESHOLD

@pytest.fixture
def prediction_service():
    return PredictionService()

@patch('app.services.prediction_service.model_loader')
def test_predict_ml_model_not_found(mock_loader, prediction_service):
    mock_loader.get_model.return_value = None
    # Should return fallback RISK_THRESHOLD
    result = prediction_service._predict_ml("heart", {})
    assert result == RISK_THRESHOLD

@patch('app.services.prediction_service.model_loader')
def test_predict_ml_success(mock_loader, prediction_service):
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.2, 0.8]]
    
    mock_loader.get_model.return_value = mock_model
    mock_loader.get_features.return_value = ["age", "bmi"]
    mock_loader.get_scaler.return_value = None # No scaler
    
    result = prediction_service._predict_ml("diabetes", {"age": 45, "bmi": 25})
    
    assert result == 0.8
    mock_model.predict_proba.assert_called_once()

@patch('app.services.prediction_service.model_loader')
def test_predict_ml_exception(mock_loader, prediction_service):
    mock_model = MagicMock()
    mock_model.predict_proba.side_effect = Exception("Incompatible shape")
    mock_loader.get_model.return_value = mock_model
    mock_loader.get_features.return_value = ["age"]
    
    with pytest.raises(PredictionError):
        prediction_service._predict_ml("heart", {"age": 45})

@patch('app.services.prediction_service.model_loader')
def test_classify_health_condition(mock_loader, prediction_service):
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.1, 0.9]]
    
    mock_loader.get_model.return_value = mock_model
    mock_loader.get_features.return_value = ["glucose"]
    mock_loader.get_classes.return_value = ["Healthy", "Condition"]
    
    result = prediction_service._classify_health_condition({"glucose": 150})
    
    assert "Healthy" in result
    assert "Condition" in result
    assert result["Healthy"] == 10.0
    assert result["Condition"] == 90.0

@patch.object(PredictionService, '_predict_ml')
@patch.object(PredictionService, '_classify_health_condition')
def test_predict_all_integration(mock_hm, mock_ml, prediction_service, sample_patient_data):
    mock_ml.return_value = 0.5 # 50% probability from ML
    mock_hm.return_value = {"Healthy": 100.0}
    
    results = prediction_service.predict_all(sample_patient_data)
    
    assert "heart" in results
    assert "diabetes" in results
    assert "kidney" in results
    assert "scores_detail" in results
    assert "health_condition" in results
    assert "used_defaults" in results
    
    assert mock_ml.call_count == 3
    assert mock_hm.call_count == 1
