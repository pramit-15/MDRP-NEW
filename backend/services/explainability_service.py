import shap
import pandas as pd
import numpy as np
import time
from backend.utils.logger import get_logger
from backend.services.model_loader import model_loader
from backend.utils.serialization import make_json_safe

class ExplainabilityService:
    def __init__(self):
        self.logger = get_logger("ExplainabilityService")
        self._explainers = {}

    def _get_explainer(self, model_name: str, model, X: pd.DataFrame):
        """ Get or create an explainer for a given model. """
        if model_name in self._explainers:
            return self._explainers[model_name]

        start_time = time.time()
        explainer = None
        
        try:
            # TreeExplainer is best for XGBoost/RandomForest
            # XGBoost models usually have a booster or predict method that TreeExplainer likes
            if hasattr(model, 'get_booster') or type(model).__name__ in ['XGBClassifier', 'XGBRegressor', 'RandomForestClassifier']:
                explainer = shap.TreeExplainer(model)
            elif hasattr(model, 'coef_'):
                # For linear models
                explainer = shap.LinearExplainer(model, X)
            else:
                # Fallback to KernelExplainer (can be slow)
                # Sample background data for KernelExplainer
                background = shap.kmeans(X, 10) if len(X) > 10 else X
                explainer = shap.KernelExplainer(model.predict_proba, background)
            
            self._explainers[model_name] = explainer
            self.logger.info(f"Initialized {type(explainer).__name__} for {model_name} in {(time.time() - start_time)*1000:.0f} ms")
        except Exception as e:
            self.logger.exception(f"Failed to initialize explainer for {model_name}")
            raise e
            
        return explainer

    def compute_shap_values(self, model_name: str, X: pd.DataFrame) -> dict:
        """ Compute SHAP values for a single prediction and return a structured dictionary. """
        model = model_loader.get_model(model_name)
        if model is None:
            return {}

        try:
            explainer = self._get_explainer(model_name, model, X)
            
            start_time = time.time()
            shap_values_obj = explainer(X)
            self.logger.info(f"Computed SHAP values for {model_name} in {(time.time() - start_time)*1000:.0f} ms")
            
            # Extract data
            if hasattr(shap_values_obj, "values") and len(shap_values_obj.values.shape) > 1:
                # TreeExplainer for classification often returns values of shape (samples, features, classes)
                # We usually want the positive class (index 1)
                if len(shap_values_obj.values.shape) == 3:
                    values = shap_values_obj.values[0, :, 1]
                    base_val = shap_values_obj.base_values[0, 1] if hasattr(shap_values_obj.base_values, '__len__') and isinstance(shap_values_obj.base_values[0], (list, np.ndarray)) else shap_values_obj.base_values[0]
                else:
                    values = shap_values_obj.values[0]
                    base_val = shap_values_obj.base_values[0]
            else:
                # Fallback for old SHAP versions or KernelExplainer
                shap_values_raw = explainer.shap_values(X)
                if isinstance(shap_values_raw, list):
                    values = shap_values_raw[1][0]
                    base_val = explainer.expected_value[1]
                else:
                    values = shap_values_raw[0]
                    base_val = explainer.expected_value
                    
                if isinstance(base_val, (list, np.ndarray)):
                    base_val = base_val[0]

            expected_value = base_val
            feature_names = X.columns.tolist()
            
            contributions = []
            for i, name in enumerate(feature_names):
                contributions.append({
                    "feature": name,
                    "value": float(X.iloc[0, i]),
                    "contribution": float(values[i])
                })
                
            # Sort by absolute contribution to get feature importance
            contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
            
            positive_contributors = [c for c in contributions if c["contribution"] > 0]
            negative_contributors = [c for c in contributions if c["contribution"] < 0]
            
            return {
                "base_value": float(expected_value),
                "expected_value": float(expected_value + sum(values)),
                "feature_importance": contributions,
                "top_features": contributions[:5],
                "positive_contributors": positive_contributors,
                "negative_contributors": negative_contributors,
                "shap_values": [float(v) for v in values]
            }
            
        except Exception as e:
            self.logger.exception(f"Error computing SHAP values for {model_name}")
            return {}

    def create_summary(self, disease_name: str, shap_results: dict) -> str:
        """ Generate a natural language summary from SHAP results. """
        if not shap_results or not shap_results.get("feature_importance"):
            return "No explanation available."
            
        top_pos = [f"{c['feature']} ({c['value']})" for c in shap_results["positive_contributors"][:3]]
        top_neg = [f"{c['feature']} ({c['value']})" for c in shap_results["negative_contributors"][:3]]
        
        summary = f"Your {disease_name} risk is influenced by several factors. "
        
        if top_pos:
            summary += f"Factors increasing your risk include {', '.join(top_pos)}. "
        if top_neg:
            summary += f"Factors decreasing your risk include {', '.join(top_neg)}."
            
        return summary

    def generate_explanation(self, model_name: str, features: list, input_data: dict, scaled_data: np.ndarray) -> dict:
        """
        Orchestrator to generate full explanation for a specific model.
        """
        X_df = pd.DataFrame(scaled_data, columns=features)
        
        results = self.compute_shap_values(model_name, X_df)
        if results:
            results["explanation_summary"] = self.create_summary(model_name, results)
        
        return make_json_safe(results)

explainability_service = ExplainabilityService()
