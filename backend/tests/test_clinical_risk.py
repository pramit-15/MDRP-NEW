import pytest
from backend.services.clinical_risk import calculate_heart_risk, calculate_diabetes_risk, calculate_kidney_risk

def test_heart_risk_normal():
    row = {
        "ldl": 100,
        "hdl": 60,
        "trestbps": 115,
        "age": 30,
        "hba1c": 5.0,
        "chol": 150,
        "triglycerides": 100,
        "bmi": 22
    }
    score = calculate_heart_risk(row)
    assert score == 0.0

def test_heart_risk_high():
    row = {
        "ldl": 150,
        "hdl": 40,  # ratio 3.75 -> 25
        "trestbps": 170, # -> 20
        "age": 70, # -> 15
        "hba1c": 8.0, # -> 10
        "chol": 250, # -> 10
        "triglycerides": 550, # -> 10
        "bmi": 36 # -> 10
    }
    score = calculate_heart_risk(row)
    assert score == 100.0

def test_diabetes_risk_normal():
    row = {
        "hba1c": 5.0,
        "glucose": 90,
        "bgr": 100,
        "bmi": 20,
        "age": 30,
        "triglycerides": 100
    }
    score = calculate_diabetes_risk(row)
    assert score == 0.0

def test_kidney_risk_normal():
    row = {
        "egfr": 95,
        "sc": 0.8,
        "bu": 15,
        "trestbps": 120,
        "glucose": 90
    }
    score = calculate_kidney_risk(row)
    assert score == 0.0
