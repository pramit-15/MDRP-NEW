import pytest
import numpy as np
import pandas as pd
from backend.utils.input_mapper import normalize_key, _estimate_egfr, compute_smart_defaults, map_input, map_input_df
from backend.app.constants import SAFE_DEFAULTS

def test_normalize_key():
    assert normalize_key("Fasting Blood Sugar") == "glucose"
    assert normalize_key(" FBS ") == "glucose"
    assert normalize_key("systolic bp") == "trestbps"
    assert normalize_key("random key") == "random key" # Unmapped returns self

def test_estimate_egfr():
    # Example values
    egfr_male = _estimate_egfr(sc=1.2, age=50, sex_male=True)
    assert isinstance(egfr_male, float)
    assert egfr_male > 0
    
    egfr_female = _estimate_egfr(sc=1.2, age=50, sex_male=False)
    assert isinstance(egfr_female, float)
    assert egfr_female > 0
    
    assert _estimate_egfr(-1, 50, True) == 95.0

def test_compute_smart_defaults():
    defaults = compute_smart_defaults(age=50, glucose=130, sex_male=True, systolic_bp=145, bgr=150, sc=1.0)
    
    assert defaults["fbs"] == 1 # glucose > 120
    assert defaults["htn"] == 1 # systolic_bp >= 140
    assert defaults["dm"] == 1
    assert defaults["dm"] == 1
    
    assert "thalach" in defaults
    assert defaults["thalach"] == max(int(208 - 0.7 * 50), 90)

def test_map_input():
    user_input = {"Age": 45, "Fasting Blood Sugar": 110, "Unknown": 999}
    required_features = ["age", "glucose", "bmi"]
    
    result = map_input(user_input, required_features)
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 3)
    
    assert result[0][0] == 45.0 # age
    assert result[0][1] == 110.0 # glucose
    assert result[0][2] == SAFE_DEFAULTS.get("bmi", 0.0) # filled by default

def test_map_input_df():
    user_input = {"Age": 45, "Fasting Blood Sugar": 110}
    required_features = ["age", "glucose", "bmi"]
    
    df = map_input_df(user_input, required_features)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1, 3)
    assert df.iloc[0]["age"] == 45.0
    assert df.iloc[0]["glucose"] == 110.0
    assert df.iloc[0]["bmi"] == SAFE_DEFAULTS.get("bmi", 0.0)
