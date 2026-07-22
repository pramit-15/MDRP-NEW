import pytest
import numpy as np
import pandas as pd
from datetime import datetime
from backend.utils.serialization import make_json_safe
from backend.services.explainability_service import explainability_service

def test_numpy_serialization():
    # Test numpy types
    data = {
        "int_val": np.int64(42),
        "float_val": np.float64(3.14),
        "array_val": np.array([1, 2, 3]),
        "nested": {
            "val": np.int32(10)
        },
        "time": datetime(2023, 1, 1)
    }
    
    safe_data = make_json_safe(data)
    
    assert isinstance(safe_data["int_val"], int)
    assert isinstance(safe_data["float_val"], float)
    assert isinstance(safe_data["array_val"], list)
    assert isinstance(safe_data["nested"]["val"], int)

def test_create_summary():
    shap_results = {
        "feature_importance": [{"feature": "glucose", "contribution": 0.5}],
        "positive_contributors": [
            {"feature": "glucose", "value": 150.0, "contribution": 0.5},
            {"feature": "bmi", "value": 30.0, "contribution": 0.2}
        ],
        "negative_contributors": [
            {"feature": "hdl", "value": 60.0, "contribution": -0.1}
        ]
    }
    
    summary = explainability_service.create_summary("diabetes", shap_results)
    assert "Your diabetes risk is influenced by several factors" in summary
    assert "glucose (150.0)" in summary
    assert "hdl (60.0)" in summary
