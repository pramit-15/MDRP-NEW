"""
predict.py  —  v4 (Service Layer Entrypoint)
=======================================================
This module now serves as a lightweight entrypoint for CLI testing.
All business logic, model loading, and prediction orchestration
have been moved to the Service Layer (`app.services.prediction_service`).
"""

from backend.services.prediction_service import prediction_service

def predict_all(patient_data: dict) -> dict:
    """
    Predicts the risk of heart disease, diabetes, and kidney disease.
    Delegates to PredictionService.
    """
    return prediction_service.predict_all(patient_data)

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = {
        "age": 35, "sex": 1, "trestbps": 120, "bloodpressure": 74,
        "bmi": 24.5, "glucose": 102.9, "bgr": 157.1, "hba1c": 5.6,
        "chol": 139.3, "ldl": 75.97, "hdl": 37.2, "triglycerides": 130.65,
        "sc": 0.41, "bu": 14.32, "egfr": 159.0, "preg": 0,
    }

    results = predict_all(sample)
    print("\n── MDRP v3 Prediction Results ───────────────────────────────────")
    print(f"  Heart Disease Risk : {results['heart']}%")
    print(f"  Diabetes Risk      : {results['diabetes']}%")
    print(f"  Kidney Disease Risk: {results['kidney']}%")
    for disease, detail in results["scores_detail"].items():
        print(f"  {disease.capitalize():<10}: ML={detail['ml']}%  Clinical Score={detail['clinical']}/100")
