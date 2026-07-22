import pytest
from backend.services.clinical_risk import (
    calculate_heart_risk, 
    calculate_diabetes_risk, 
    calculate_kidney_risk, 
    calculate_all_risks,
    _get
)

def test_get_helper():
    row = {"age": 45.0, "invalid": "not a number", "missing": None}
    assert _get(row, "age") == 45.0
    # Should fallback to defaults
    assert _get(row, "invalid") >= 0.0
    assert _get(row, "missing") >= 0.0

def test_calculate_heart_risk():
    # Ideal patient
    ideal = {"ldl": 80, "hdl": 60, "trestbps": 110, "age": 30, "hba1c": 5.0, "chol": 150, "triglycerides": 100, "bmi": 22}
    assert calculate_heart_risk(ideal) == 0.0
    
    # High risk patient
    high_risk = {"ldl": 160, "hdl": 40, "trestbps": 150, "age": 60, "hba1c": 7.0, "chol": 250, "triglycerides": 250, "bmi": 32}
    score = calculate_heart_risk(high_risk)
    assert score > 50.0

def test_calculate_diabetes_risk():
    # Ideal patient
    ideal = {"hba1c": 5.0, "glucose": 90, "bgr": 100, "bmi": 22, "age": 30, "triglycerides": 100}
    assert calculate_diabetes_risk(ideal) == 0.0
    
    # High risk patient
    high_risk = {"hba1c": 8.0, "glucose": 130, "bgr": 210, "bmi": 32, "age": 55, "triglycerides": 300}
    score = calculate_diabetes_risk(high_risk)
    assert score > 60.0

def test_calculate_kidney_risk():
    # Ideal patient
    ideal = {"egfr": 100, "sc": 0.8, "bu": 15, "trestbps": 120, "glucose": 90}
    assert calculate_kidney_risk(ideal) == 0.0
    
    # High risk patient
    high_risk = {"egfr": 40, "sc": 1.5, "bu": 50, "trestbps": 150, "glucose": 130}
    score = calculate_kidney_risk(high_risk)
    assert score > 50.0

def test_calculate_all_risks():
    patient = {"age": 60, "glucose": 150, "egfr": 50, "sc": 1.5, "hba1c": 7.5}
    risks = calculate_all_risks(patient)
    assert "diabetes_clinical" in risks
    assert "heart_clinical" in risks
    assert "kidney_clinical" in risks
    
    for key, value in risks.items():
        assert isinstance(value, float)
        assert 0.0 <= value <= 100.0
