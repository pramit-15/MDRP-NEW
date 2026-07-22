import time
import numpy as np
from backend.services.model_loader import model_loader
from backend.utils.logger import get_logger
from backend.utils.input_mapper import map_input, compute_smart_defaults, SAFE_DEFAULTS
from backend.services.clinical_risk import calculate_all_risks
from backend.app.constants import W_ML, W_CLINICAL, RISK_THRESHOLD
from backend.utils.exceptions import PredictionError, ModelLoadingError

class PredictionService:
    def __init__(self):
        self.logger = get_logger("PredictionService")

    def predict_all(self, patient_data: dict) -> dict:
        self.logger.info("Prediction request received in PredictionService")
        start_time = time.time()
        
        full_input, used_defaults = self._prepare_input(patient_data)
        clinical = self._calculate_clinical_scores(full_input)
        
        heart_ml = self._predict_ml("heart", full_input)
        diabetes_ml = self._predict_ml("diabetes", full_input)
        kidney_ml = self._predict_ml("kidney", full_input)
        
        heart_risk = self._combine_scores(heart_ml, clinical["heart_clinical"])
        diabetes_risk = self._combine_scores(diabetes_ml, clinical["diabetes_clinical"])
        kidney_risk = self._combine_scores(kidney_ml, clinical["kidney_clinical"])
        
        health_condition = self._classify_health_condition(full_input)
        
        # Explainability
        try:
            explainability = self._generate_explanations(full_input)
        except Exception as e:
            self.logger.exception(f"Explainability failed: {e}")
            explainability = {}
        
        duration_ms = (time.time() - start_time) * 1000
        self.logger.info(f"Prediction logic completed in {duration_ms:.0f} ms")
        
        response = self._build_response(
            heart_risk, diabetes_risk, kidney_risk,
            heart_ml, diabetes_ml, kidney_ml,
            clinical, health_condition, used_defaults
        )
        response["explainability"] = explainability
        return response

    def _prepare_input(self, patient_data: dict):
        age = float(patient_data.get("age", SAFE_DEFAULTS["age"]))
        glucose = float(patient_data.get("glucose", SAFE_DEFAULTS["glucose"]))
        sex_male = int(patient_data.get("sex", 1)) == 1

        smart = compute_smart_defaults(
            age=age,
            glucose=glucose,
            sex_male=sex_male,
            systolic_bp=float(patient_data.get("trestbps", 118.0)),
            bgr=patient_data.get("bgr"),
            sc=patient_data.get("sc"),
        )

        full_input = {**smart, **patient_data}

        if "bloodpressure" in full_input and "bp" not in full_input:
            full_input["bp"] = full_input["bloodpressure"]

        provided = set(patient_data.keys())
        all_features = set(
            model_loader.get_features("heart") + 
            model_loader.get_features("diabetes") + 
            model_loader.get_features("kidney")
        )
        used_defaults = sorted(
            f for f in all_features
            if f not in provided and f not in smart
        )
        
        return full_input, used_defaults

    def _calculate_clinical_scores(self, full_input: dict):
        return calculate_all_risks(full_input)

    def _apply_scaler(self, X, name: str):
        scaler = model_loader.get_scaler(name)
        if scaler is not None:
            return scaler.transform(X)
        return X

    def _predict_ml(self, name: str, full_input: dict) -> float:
        model = model_loader.get_model(name)
        if model is None:
            # We maintain the RISK_THRESHOLD fallback to preserve existing behavior,
            # but we could raise ModelLoadingError here if strict failure is desired.
            return RISK_THRESHOLD
        
        features = model_loader.get_features(name)
        X = map_input(full_input, features)
        X = self._apply_scaler(X, name)
        
        try:
            return float(model.predict_proba(X)[0][1])
        except Exception as e:
            self.logger.exception(f"Prediction failed for {name}")
            raise PredictionError(f"Prediction failed for {name}: {str(e)}")

    def _classify_health_condition(self, full_input: dict) -> dict:
        model = model_loader.get_model("hm")
        if model is None:
            return {}

        features = model_loader.get_features("hm")
        X_hm = map_input(full_input, features)
        X_hm = self._apply_scaler(X_hm, "hm")

        try:
            probs = model.predict_proba(X_hm)[0]
            classes = model_loader.get_classes("hm")
            if classes is None:
                classes = [str(i) for i in range(len(probs))]
            return {cls: round(float(p) * 100, 1) for cls, p in zip(classes, probs)}
        except Exception as e:
            self.logger.exception("Health condition classification failed")
            raise PredictionError(f"Health condition classification failed: {str(e)}")

    def _combine_scores(self, ml_prob: float, clinical_score: float) -> float:
        blended = W_ML * ml_prob + W_CLINICAL * (clinical_score / 100.0)
        return round(float(np.clip(blended, 0.0, 1.0)) * 100.0, 2)

    def _build_response(self, heart_risk, diabetes_risk, kidney_risk, 
                        heart_ml, diabetes_ml, kidney_ml, 
                        clinical, health_condition, used_defaults):
        return {
            "heart": heart_risk,
            "diabetes": diabetes_risk,
            "kidney": kidney_risk,
            "clinical_scores": {
                "diabetes_clinical": clinical["diabetes_clinical"],
                "heart_clinical": clinical["heart_clinical"],
                "kidney_clinical": clinical["kidney_clinical"],
            },
            "scores_detail": {
                "heart": {"ml": round(heart_ml * 100, 2), "clinical": clinical["heart_clinical"]},
                "diabetes": {"ml": round(diabetes_ml * 100, 2), "clinical": clinical["diabetes_clinical"]},
                "kidney": {"ml": round(kidney_ml * 100, 2), "clinical": clinical["kidney_clinical"]},
            },
            "health_condition": health_condition,
            "used_defaults": used_defaults,
        }

    def _generate_explanations(self, full_input: dict) -> dict:
        from backend.services.explainability_service import explainability_service
        explainability = {
            "shap_values": {},
            "feature_importance": {},
            "top_features": {},
            "explanation_summary": {},
            "positive_contributors": {},
            "negative_contributors": {},
            "expected_value": {},
            "base_value": {}
        }
        
        for name in ["heart", "diabetes", "kidney"]:
            features = model_loader.get_features(name)
            X_mapped = map_input(full_input, features)
            X_scaled = self._apply_scaler(X_mapped, name)
            
            res = explainability_service.generate_explanation(name, features, full_input, X_scaled)
            if res:
                for key in explainability.keys():
                    if key in res:
                        explainability[key][name] = res[key]
                        
        return explainability

prediction_service = PredictionService()
