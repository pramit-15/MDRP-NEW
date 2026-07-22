import os, sys, joblib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from ml_pipeline.training.ensemble_model import build_ensemble
from backend.utils.logger import get_logger

logger = get_logger("train_models")

def train(path, target, out, multiclass=False):
    df = pd.read_csv(path)
    X  = df.drop(target, axis=1)
    y  = df[target]
    logger.info(f"Training on: {path} | samples={len(df)} | features={X.shape[1]} | classes={sorted(y.unique())}")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42,
        stratify=y if y.nunique() <= 20 else None,
    )
    model = build_ensemble(multiclass=multiclass)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    logger.info(f"Hold-out accuracy: {accuracy_score(y_test, preds):.4f}")
    logger.info(f"Classification report:\n{classification_report(y_test, preds, zero_division=0)}")
    joblib.dump(model, out)
    logger.info(f"Model saved → {out}")

if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    for path, target, out, mc in [
        ("data/processed/heart_processed.csv",    "target",          "models/heart_model.pkl",    False),
        ("data/processed/diabetes_processed.csv", "outcome",         "models/diabetes_model.pkl", False),
        ("data/processed/kidney_processed.csv",   "classification",  "models/kidney_model.pkl",   False),
        ("data/processed/hm_processed.csv",       "condition_label", "models/hm_model.pkl",       True),
    ]:
        if os.path.exists(path):
            train(path, target, out, mc)
        else:
            logger.warning(f"SKIPPED — {path} not found")
    logger.info("All models trained")
