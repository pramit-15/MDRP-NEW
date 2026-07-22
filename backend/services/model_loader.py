import time
import joblib
import os
from backend.app.config import Config
from backend.utils.logger import get_logger

class ModelLoader:
    def __init__(self):
        self.logger = get_logger("ModelLoader")
        self._models = {}
        self._scalers = {}
        self._features = {}
        self._classes = {}
        self._loaded = False

        self.HEART_FEATURES = [
            "age", "sex", "cp", "trestbps", "chol",
            "fbs", "restecg", "thalach", "exang",
            "oldpeak", "slope", "ca", "thal",
        ]

        self.DIABETES_FEATURES = [
            "preg", "glucose", "bloodpressure", "skin",
            "insulin", "bmi", "dpf", "age",
        ]

        self._KIDNEY_FEATURES_DEFAULT = [
            "age", "bp", "bgr", "bu", "sc", "sod", "pot",
            "htn", "dm", "cad", "appet", "pe", "ane",
        ]

        self.HM_FEATURES = [
            "glucose", "hba1c", "trestbps", "bloodpressure",
            "ldl", "hdl", "triglycerides",
        ]

    def _safe_load(self, path: str, name: str = ""):
        if os.path.exists(path):
            try:
                obj = joblib.load(path)
                self.logger.info(f"Loaded {name} successfully from {path}")
                return obj
            except Exception as e:
                self.logger.exception(f"Failed to load {name} from {path}: {e}")
                return None
        self.logger.warning(f"{name} not found at {path}")
        return None

    def load_all(self):
        if self._loaded:
            return

        self.logger.info("Starting model loading sequence")
        start_time = time.time()

        self._models["heart"] = self._safe_load(Config.HEART_MODEL_PATH, "Heart Model")
        self._models["diabetes"] = self._safe_load(Config.DIABETES_MODEL_PATH, "Diabetes Model")
        self._models["kidney"] = self._safe_load(Config.KIDNEY_MODEL_PATH, "Kidney Model")
        self._models["hm"] = self._safe_load(Config.HM_MODEL_PATH, "HM Model")

        self._scalers["heart"] = self._safe_load(Config.HEART_SCALER_PATH, "Heart Scaler")
        self._scalers["diabetes"] = self._safe_load(Config.DIABETES_SCALER_PATH, "Diabetes Scaler")
        self._scalers["kidney"] = self._safe_load(Config.KIDNEY_SCALER_PATH, "Kidney Scaler")
        self._scalers["hm"] = self._safe_load(Config.HM_SCALER_PATH, "HM Scaler")

        self._classes["hm"] = self._safe_load(Config.HM_CLASSES_PATH, "HM Classes")
        
        hm_feat = self._safe_load(Config.HM_FEATURES_PATH, "HM Features")
        self._features["hm"] = hm_feat if hm_feat is not None else self.HM_FEATURES

        kidney_feat = self._safe_load(Config.KIDNEY_FEATURES_PATH, "Kidney Features")
        if kidney_feat is not None:
            self.logger.info(f"Loaded kidney features from pkl: {kidney_feat}")
            self._features["kidney"] = kidney_feat
        else:
            self._features["kidney"] = self._KIDNEY_FEATURES_DEFAULT
            self.logger.warning(f"kidney_features.pkl not found; using hardcoded list "
                                f"({len(self._features['kidney'])} features). Re-run preprocess.py to fix.")

        self._features["heart"] = self.HEART_FEATURES
        self._features["diabetes"] = self.DIABETES_FEATURES

        duration_ms = (time.time() - start_time) * 1000
        self.logger.info(f"Model loading sequence completed in {duration_ms:.0f} ms")

        self._loaded = True

    def get_model(self, name: str):
        self.load_all()
        return self._models.get(name)

    def get_scaler(self, name: str):
        self.load_all()
        return self._scalers.get(name)

    def get_features(self, name: str) -> list:
        self.load_all()
        return self._features.get(name, [])

    def get_classes(self, name: str):
        self.load_all()
        return self._classes.get(name)

model_loader = ModelLoader()
