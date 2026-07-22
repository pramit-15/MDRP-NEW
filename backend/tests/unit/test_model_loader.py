import pytest
import os
from unittest.mock import patch, MagicMock
from backend.services.model_loader import ModelLoader

@pytest.fixture
def mock_loader():
    loader = ModelLoader()
    # Reset internal state to avoid bleeding between tests
    loader._loaded = False
    loader._models = {}
    loader._scalers = {}
    loader._features = {}
    loader._classes = {}
    return loader

@patch('app.services.model_loader.os.path.exists')
@patch('app.services.model_loader.joblib.load')
def test_load_all_success(mock_joblib_load, mock_exists, mock_loader):
    mock_exists.return_value = True
    mock_joblib_load.return_value = MagicMock()
    
    mock_loader.load_all()
    
    assert mock_loader._loaded is True
    assert mock_loader.get_model("heart") is not None
    assert mock_loader.get_scaler("diabetes") is not None
    assert mock_loader.get_features("heart") == mock_loader.HEART_FEATURES
    assert mock_loader.get_features("diabetes") == mock_loader.DIABETES_FEATURES
    
    # joblib.load should be called for models, scalers, classes and features
    assert mock_joblib_load.call_count >= 10

@patch('app.services.model_loader.os.path.exists')
@patch('app.services.model_loader.joblib.load')
def test_load_all_missing_files(mock_joblib_load, mock_exists, mock_loader):
    mock_exists.return_value = False
    
    mock_loader.load_all()
    
    assert mock_loader._loaded is True
    assert mock_loader.get_model("heart") is None
    assert mock_loader.get_scaler("kidney") is None
    # Features should still fallback to defaults
    assert mock_loader.get_features("heart") == mock_loader.HEART_FEATURES
    
    # Not called because files don't exist
    mock_joblib_load.assert_not_called()

@patch('app.services.model_loader.os.path.exists')
@patch('app.services.model_loader.joblib.load')
def test_safe_load_exception(mock_joblib_load, mock_exists, mock_loader):
    mock_exists.return_value = True
    mock_joblib_load.side_effect = Exception("Corrupt file")
    
    result = mock_loader._safe_load("dummy_path", "Dummy Model")
    assert result is None
    # Ensure no exception propagates
