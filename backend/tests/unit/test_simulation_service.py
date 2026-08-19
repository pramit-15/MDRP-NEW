import pytest
from backend.services.simulation_service import simulation_service

def test_simulate_risk_reduction_lifestyle(sample_patient_data):
    # Baseline patient with elevated BP, BMI, and glucose
    base_data = sample_patient_data.copy()
    base_data.update({
        "height_cm": 175,
        "weight_kg": 90.0, # BMI ~ 29.4
        "systolic_bp": 145,
        "diastolic_bp": 92,
        "glucose": 130,
        "hba1c": 6.8,
        "chol": 230
    })

    # Patient simulates: losing 8kg, lowering systolic BP to 120, dropping HbA1c to 5.4, lowering chol
    modifications = {
        "weight_kg": 82.0, # BMI ~ 26.8
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "glucose": 95,
        "hba1c": 5.4,
        "chol": 185
    }

    result = simulation_service.simulate_risk_reduction(base_data, modifications)
    
    assert result["success"] is True
    assert "baseline" in result
    assert "simulated" in result
    assert "deltas" in result
    assert "percentage_reductions" in result
    
    # Risk should be lower in simulated state
    assert result["simulated"]["heart"] <= result["baseline"]["heart"]
    assert result["simulated"]["diabetes"] <= result["baseline"]["diabetes"]
    assert result["deltas"]["composite"] <= 0
    assert result["percentage_reductions"]["composite"] >= 0

def test_simulate_bmi_recalculation(sample_patient_data):
    base_data = sample_patient_data.copy()
    base_data.update({
        "height_cm": 180,
        "weight_kg": 100.0 # Initial BMI = 30.86
    })

    modifications = {
        "weight_kg": 80.0 # New BMI should be 80 / (1.8^2) = 24.69
    }

    result = simulation_service.simulate_risk_reduction(base_data, modifications)
    assert result["simulated"]["bmi_used"] == pytest.approx(24.7, 0.1)
