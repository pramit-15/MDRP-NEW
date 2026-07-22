import pytest
import pandas as pd
import os
from ml_pipeline.preprocessing.feature_engineering import load_features

def test_load_features(tmp_path):
    # Create a temporary CSV file
    csv_file = tmp_path / "test_data.csv"
    
    df = pd.DataFrame({
        "feature1": [1, 2, 3],
        "feature2": [4, 5, 6],
        "target_col": [0, 1, 0]
    })
    df.to_csv(csv_file, index=False)
    
    # Test successful load
    X, y = load_features(str(csv_file), "target_col")
    assert "target_col" not in X.columns
    assert "feature1" in X.columns
    assert len(X) == 3
    assert len(y) == 3
    assert y.name == "target_col"

def test_load_features_missing_target(tmp_path):
    csv_file = tmp_path / "test_data_no_target.csv"
    
    df = pd.DataFrame({
        "feature1": [1, 2, 3]
    })
    df.to_csv(csv_file, index=False)
    
    with pytest.raises(ValueError) as exc:
        load_features(str(csv_file), "missing_target")
    
    assert "Target column 'missing_target' not found" in str(exc.value)
