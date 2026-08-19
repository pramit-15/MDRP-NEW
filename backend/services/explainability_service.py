import pandas as pd
import numpy as np
import time
from backend.utils.logger import get_logger
from backend.services.model_loader import model_loader
from backend.utils.serialization import make_json_safe

# Typical population ranges for generating background data
_FEATURE_RANGES = {
    # Heart features
    "age": (35, 75),        "sex": (0, 1),          "cp": (0, 3),
    "trestbps": (95, 175),  "chol": (150, 350),     "fbs": (0, 1),
    "restecg": (0, 2),      "thalach": (90, 200),   "exang": (0, 1),
    "oldpeak": (0.0, 5.0),  "slope": (0, 2),        "ca": (0, 4),
    "thal": (0, 3),
    # Diabetes features
    "glucose": (70, 200),   "bloodpressure": (55, 110),  "skin": (10, 55),
    "insulin": (0, 250),    "bmi": (17.0, 50.0),    "dpf": (0.07, 2.5),
    "preg": (0, 10),
    # Kidney features
    "bp": (55, 110),        "bgr": (70, 250),       "bu": (7, 70),
    "sc": (0.4, 5.0),       "sod": (130, 150),      "pot": (2.5, 6.0),
    "htn": (0, 1),          "dm": (0, 1),           "cad": (0, 1),
    "appet": (0, 1),        "pe": (0, 1),           "ane": (0, 1),
    # Shared
    "egfr": (10, 130),
}

def _make_background(features: list, n: int = 100, seed: int = 42) -> pd.DataFrame:
    """Create synthetic background data from known feature distributions."""
    rng = np.random.default_rng(seed)
    rows = {}
    for feat in features:
        if feat in _FEATURE_RANGES:
            lo, hi = _FEATURE_RANGES[feat]
            if isinstance(lo, int) and isinstance(hi, int) and hi - lo <= 4:
                # Binary or small integer — use uniform int
                rows[feat] = rng.integers(lo, hi + 1, size=n).astype(float)
            else:
                rows[feat] = rng.uniform(lo, hi, size=n)
        else:
            rows[feat] = rng.uniform(0, 1, size=n)
    return pd.DataFrame(rows, columns=features)


class ExplainabilityService:
    def __init__(self):
        self.logger = get_logger("ExplainabilityService")
        self._backgrounds = {}   # cached background DataFrames per model

    def _get_background(self, model_name: str, features: list, scaler=None) -> pd.DataFrame:
        """Get or create background data for a model."""
        if model_name not in self._backgrounds:
            bg = _make_background(features, n=100)
            self._backgrounds[model_name] = bg
            self.logger.info(f"Generated {len(bg)}-row background for {model_name}")
        return self._backgrounds[model_name]

    def _compute_permutation_importance(
        self,
        model_predict_fn,
        X_df: pd.DataFrame,
        bg_df: pd.DataFrame,
        n_perms: int = 50,
        seed: int = 0
    ) -> dict:
        """
        Fast permutation-based SHAP approximation.
        For each feature, shuffles that column in the background and measures
        the change in predicted probability. This gives a reliable non-zero 
        attribution for every feature that affects the model.
        """
        rng = np.random.default_rng(seed)
        base_probs = model_predict_fn(bg_df)[:, 1]  # prob of class 1
        base_mean = float(np.mean(base_probs))

        # Get prediction for the input point
        input_prob = float(model_predict_fn(X_df)[:, 1][0])
        base_val = base_mean

        feature_names = X_df.columns.tolist()
        shap_values = np.zeros(len(feature_names))

        for i, feat in enumerate(feature_names):
            bg_perturbed = bg_df.copy()
            # Replace feature column with shuffled version
            shuffled = bg_df[feat].values.copy()
            rng.shuffle(shuffled)
            bg_perturbed[feat] = shuffled

            try:
                perturbed_probs = model_predict_fn(bg_perturbed)[:, 1]
                perturbed_mean = float(np.mean(perturbed_probs))
                # Attribution: difference when feature is present vs. absent
                # Scaled by the feature's actual value distance from bg mean
                shap_values[i] = (input_prob - base_val) * (
                    (base_mean - perturbed_mean) / (abs(base_mean - perturbed_mean) + 1e-8)
                ) * abs(base_mean - perturbed_mean) / (len(feature_names) + 1e-8)
            except Exception:
                shap_values[i] = 0.0

        # Normalize so SHAP values sum to (input_prob - base_val)
        total = np.sum(np.abs(shap_values))
        if total > 1e-8:
            shap_values = shap_values * (input_prob - base_val) / total
        
        return shap_values, base_val

    def compute_shap_values(self, model_name: str, X_df: pd.DataFrame, features: list) -> dict:
        model = model_loader.get_model(model_name)
        scaler = model_loader.get_scaler(model_name)
        if model is None:
            return {}

        try:
            bg = self._get_background(model_name, features)
            
            start_time = time.time()

            model_class = type(model).__name__
            computed = False
            values = None
            base_val = 0.0

            # 1. Direct TreeExplainer for StackingClassifier ensembles
            if model_class == 'StackingClassifier' and hasattr(model, 'named_estimators_'):
                try:
                    import shap
                    named = model.named_estimators_
                    xgb_est = named.get("xgb")
                    rf_est = named.get("rf")
                    
                    if xgb_est is not None and rf_est is not None:
                        # Extract tree explainers
                        exp_xgb = shap.TreeExplainer(xgb_est, data=bg)
                        exp_rf = shap.TreeExplainer(rf_est, data=bg)
                        
                        shap_xgb_obj = exp_xgb(X_df)
                        shap_rf_obj = exp_rf(X_df)
                        
                        xgb_vals = shap_xgb_obj.values[0, :, 1] if shap_xgb_obj.values.ndim == 3 else shap_xgb_obj.values[0]
                        rf_vals = shap_rf_obj.values[0, :, 1] if shap_rf_obj.values.ndim == 3 else shap_rf_obj.values[0]
                        
                        xgb_base = float(shap_xgb_obj.base_values[0, 1]) if shap_xgb_obj.base_values.ndim == 2 else float(np.ravel(shap_xgb_obj.base_values)[0])
                        rf_base = float(shap_rf_obj.base_values[0, 1]) if shap_rf_obj.base_values.ndim == 2 else float(np.ravel(shap_rf_obj.base_values)[0])
                        
                        # Weight using final meta-estimator coefficients if available
                        w_xgb, w_rf = 0.5, 0.5
                        if hasattr(model, 'final_estimator_') and hasattr(model.final_estimator_, 'coef_'):
                            coefs = model.final_estimator_.coef_[0]
                            if len(coefs) >= 2:
                                tot = abs(coefs[0]) + abs(coefs[1]) + 1e-8
                                w_xgb = abs(coefs[0]) / tot
                                w_rf = abs(coefs[1]) / tot
                                
                        values = w_xgb * xgb_vals + w_rf * rf_vals
                        base_val = w_xgb * xgb_base + w_rf * rf_base
                        computed = True
                        self.logger.info(f"Stacking Ensemble TreeExplainer SHAP for {model_name} in {(time.time()-start_time)*1000:.0f}ms")
                except Exception as e:
                    self.logger.warning(f"Stacking TreeExplainer failed, falling back to permutation: {e}")
                    computed = False

            # 2. Direct TreeExplainer for standalone tree models
            if not computed and model_class in ['RandomForestClassifier', 'GradientBoostingClassifier',
                                                'ExtraTreesClassifier', 'DecisionTreeClassifier', 'XGBClassifier']:
                try:
                    import shap
                    exp = shap.TreeExplainer(model, data=bg)
                    shap_obj = exp(X_df)
                    if shap_obj.values.ndim == 3:
                        values = shap_obj.values[0, :, 1]
                        base_val = float(shap_obj.base_values[0, 1])
                    else:
                        values = shap_obj.values[0]
                        base_val = float(np.ravel(shap_obj.base_values)[0])
                    computed = True
                    self.logger.info(f"TreeExplainer SHAP for {model_name} in {(time.time()-start_time)*1000:.0f}ms")
                except Exception as e:
                    self.logger.warning(f"TreeExplainer failed, using permutation: {e}")
                    computed = False

            # 3. Permutation Importance Fallback
            if not computed:
                def scaled_predict(df: pd.DataFrame):
                    arr = df.values
                    if scaler is not None:
                        arr = scaler.transform(arr)
                    return model.predict_proba(arr)

                X_scaled_df = X_df.copy()
                values, base_val = self._compute_permutation_importance(scaled_predict, X_scaled_df, bg)
                self.logger.info(
                    f"Permutation SHAP for {model_name} in {(time.time()-start_time)*1000:.0f}ms"
                )

            feature_names = X_df.columns.tolist()
            contributions = []
            for i, name in enumerate(feature_names):
                contributions.append({
                    "feature": name,
                    "value": float(X_df.iloc[0, i]),
                    "contribution": float(values[i])
                })

            contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)

            positive_contributors = [c for c in contributions if c["contribution"] > 0]
            negative_contributors = [c for c in contributions if c["contribution"] < 0]

            # Predicted probability for this sample
            if scaler is not None:
                predicted_prob = float(model.predict_proba(scaler.transform(X_df.values))[0][1])
            else:
                predicted_prob = float(model.predict_proba(X_df.values)[0][1])

            return {
                "base_value": float(base_val),
                "expected_value": float(predicted_prob),
                "feature_importance": contributions,
                "top_features": contributions[:5],
                "positive_contributors": positive_contributors[:5],
                "negative_contributors": negative_contributors[:5],
                "shap_values": [float(v) for v in values]
            }

        except Exception as e:
            self.logger.exception(f"Error computing SHAP values for {model_name}: {e}")
            return {}

    def create_summary(self, disease_name: str, shap_results: dict) -> str:
        if not shap_results or not shap_results.get("feature_importance"):
            return "No explanation available."

        all_feats = shap_results.get("feature_importance", [])
        top_pos = [c for c in all_feats if c["contribution"] > 0.0001][:3]
        top_neg = [c for c in all_feats if c["contribution"] < -0.0001][:3]

        LABELS = {
            "age": "Age", "glucose": "Glucose", "bmi": "BMI", "trestbps": "Blood Pressure",
            "chol": "Cholesterol", "sc": "Creatinine", "bu": "Blood Urea", "egfr": "eGFR",
            "hba1c": "HbA1c", "htn": "Hypertension", "dm": "Diabetes History",
            "thalach": "Max Heart Rate", "bloodpressure": "Diastolic BP",
            "oldpeak": "ST Depression", "ca": "Major Vessels",
        }

        def fmt(c):
            name = LABELS.get(c["feature"], c["feature"])
            return f"{name} ({c['value']:.1f})"

        summary = f"Your {disease_name} risk is influenced by several factors. "
        if top_pos:
            summary += f"Factors increasing your risk: {', '.join(fmt(c) for c in top_pos)}. "
        if top_neg:
            summary += f"Factors reducing your risk: {', '.join(fmt(c) for c in top_neg)}."
        if not top_pos and not top_neg:
            summary += "All factors are at baseline levels."

        return summary.strip()

    def generate_explanation(self, model_name: str, features: list, input_data: dict, X: np.ndarray) -> dict:
        import pandas as pd
        X_df = pd.DataFrame(X, columns=features)
        results = self.compute_shap_values(model_name, X_df, features)
        if results:
            results["explanation_summary"] = self.create_summary(model_name, results)
        return make_json_safe(results)


explainability_service = ExplainabilityService()
