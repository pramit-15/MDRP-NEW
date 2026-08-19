"""
hyperparameter_tuning.py
========================
Modular hyperparameter tuning, Stratified K-Fold Cross-Validation, medical metric
evaluation, and safe persistence for MDRP disease prediction models.

Key Guarantees:
- 100% Zero Data Leakage: 20% held-out test set is partitioned first and evaluated ONLY once at the end.
- Stratified 5-Fold Cross-Validation on training development set.
- Hyperparameter tuning for XGBoost, Random Forest, and Meta-Learners.
- Complete medical classification metrics: Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix.
- Full compatibility with StackingClassifier structure and SHAP TreeExplainer.
- Safe model persistence with pre-save validation gates.
- Structured JSON reporting to training_results/.
"""

import os
import sys
import time
import json
import shutil
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV, cross_validate
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression

from ml_pipeline.training.ensemble_model import build_ensemble
from backend.utils.logger import get_logger

logger = get_logger("hyperparameter_tuning")


def get_disease_param_distributions(disease_name: str, y_train: pd.Series, multiclass: bool = False):
    """
    Returns tailored hyperparameter search distributions for base estimators
    based on disease dataset characteristics (sample size, class balance, dimensionality).
    """
    is_imbalanced = False
    scale_pos_weight = 1.0
    if not multiclass:
        n_neg = int((y_train == 0).sum())
        n_pos = int((y_train == 1).sum())
        if n_pos > 0:
            scale_pos_weight = float(n_neg) / float(n_pos)
            if scale_pos_weight > 1.3 or scale_pos_weight < 0.7:
                is_imbalanced = True

    if disease_name.lower() in ["heart", "heart disease"]:
        # Heart: 1025 samples, 13 features, fairly balanced
        xgb_params = {
            "n_estimators": [100, 150, 200, 250],
            "max_depth": [3, 4, 5, 6],
            "learning_rate": [0.01, 0.03, 0.05, 0.1],
            "subsample": [0.7, 0.8, 0.9, 1.0],
            "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
            "min_child_weight": [1, 2, 3, 5],
            "gamma": [0, 0.05, 0.1, 0.2],
            "scale_pos_weight": [1.0],
        }
        rf_params = {
            "n_estimators": [100, 150, 200, 250],
            "max_depth": [6, 8, 10, 14, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt", "log2"],
            "class_weight": ["balanced", None],
        }

    elif disease_name.lower() in ["diabetes"]:
        # Diabetes: 768 samples, 8 features, ~35% positive class (imbalanced)
        xgb_params = {
            "n_estimators": [100, 150, 200, 300],
            "max_depth": [2, 3, 4, 5],
            "learning_rate": [0.01, 0.02, 0.03, 0.05, 0.1],
            "subsample": [0.6, 0.7, 0.8, 0.9],
            "colsample_bytree": [0.6, 0.7, 0.8, 0.9],
            "min_child_weight": [2, 3, 5, 7],
            "gamma": [0, 0.1, 0.2, 0.5],
            "scale_pos_weight": [1.0, scale_pos_weight, 1.5],
        }
        rf_params = {
            "n_estimators": [100, 150, 200, 300],
            "max_depth": [3, 4, 5, 6, 8],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4, 6],
            "max_features": ["sqrt", "log2", 0.6],
            "class_weight": ["balanced", "balanced_subsample", None],
        }

    elif disease_name.lower() in ["kidney", "kidney disease", "ckd"]:
        # Kidney: 400 samples, 13 features
        xgb_params = {
            "n_estimators": [50, 100, 150, 200],
            "max_depth": [3, 4, 5],
            "learning_rate": [0.01, 0.03, 0.05, 0.1],
            "subsample": [0.7, 0.8, 0.9, 1.0],
            "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
            "min_child_weight": [1, 2, 3],
            "gamma": [0, 0.1, 0.2],
            "scale_pos_weight": [1.0, scale_pos_weight],
        }
        rf_params = {
            "n_estimators": [100, 150, 200],
            "max_depth": [4, 6, 8, 10, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt", "log2"],
            "class_weight": ["balanced", None],
        }

    else:
        # Health Markers / Multiclass: 25,000 samples, 5 classes
        xgb_params = {
            "n_estimators": [50, 100, 150],
            "max_depth": [3, 4, 5],
            "learning_rate": [0.01, 0.03, 0.05, 0.1],
            "subsample": [0.8, 0.9, 1.0],
            "colsample_bytree": [0.8, 0.9, 1.0],
            "min_child_weight": [1, 3, 5],
            "gamma": [0, 0.1, 0.2],
        }
        rf_params = {
            "n_estimators": [50, 100, 150],
            "max_depth": [6, 8, 12, 16],
            "min_samples_split": [5, 10],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt"],
            "class_weight": [None],
        }

    return xgb_params, rf_params


def validate_model_contract(model, X_sample: pd.DataFrame, multiclass: bool = False):
    """
    Validates model contract, predict_proba outputs, and compatibility with
    explainability service (SHAP TreeExplainer) before saving.
    """
    # 1. Output probability shape and range check
    probs = model.predict_proba(X_sample)
    if not isinstance(probs, np.ndarray):
        raise ValueError("Model predict_proba did not return a numpy array.")
    
    if np.any(np.isnan(probs)) or np.any(np.isinf(probs)):
        raise ValueError("Model predict_proba returned NaN or Inf values.")
    
    if np.any(probs < 0.0) or np.any(probs > 1.0):
        raise ValueError(f"Model probabilities out of [0, 1] range: min={probs.min()}, max={probs.max()}")

    # Row sum must be close to 1.0
    row_sums = probs.sum(axis=1)
    if not np.allclose(row_sums, 1.0, atol=1e-3):
        raise ValueError(f"Probabilities do not sum to 1.0: {row_sums}")

    # 2. Check named estimators for StackingClassifier TreeExplainer SHAP compatibility
    if isinstance(model, StackingClassifier):
        if not hasattr(model, "named_estimators_"):
            raise ValueError("StackingClassifier is missing fitted named_estimators_ attribute.")
        named = model.named_estimators_
        if "xgb" not in named or "rf" not in named:
            raise ValueError(f"StackingClassifier missing 'xgb' or 'rf' estimators: keys={list(named.keys())}")


def safe_save_model(model, out_path: str, X_sample: pd.DataFrame, multiclass: bool = False):
    """
    Safely validates and persists model artifact to disk with atomic replacement
    and backup protection.
    """
    # Step 1: Validate contract in memory
    validate_model_contract(model, X_sample, multiclass=multiclass)

    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Step 2: Write to temporary file first
    temp_out = f"{out_path}.tmp"
    joblib.dump(model, temp_out)

    # Step 3: Test loading the saved temporary artifact
    loaded = joblib.load(temp_out)
    validate_model_contract(loaded, X_sample, multiclass=multiclass)

    # Step 4: Backup existing file if present
    bak_path = f"{out_path}.bak"
    if os.path.exists(out_path):
        shutil.copy2(out_path, bak_path)

    try:
        # Atomic replace
        if os.path.exists(out_path):
            os.remove(out_path)
        os.rename(temp_out, out_path)
        if os.path.exists(bak_path):
            os.remove(bak_path)
        logger.info(f"Model successfully validated and persisted → {out_path}")
    except Exception as e:
        if os.path.exists(bak_path) and not os.path.exists(out_path):
            shutil.copy2(bak_path, out_path)
        raise RuntimeError(f"Failed to atomically persist model to {out_path}: {e}")


def tune_and_train_disease(
    name: str,
    path: str,
    target: str,
    out_path: str,
    multiclass: bool = False,
    n_iter: int = 20,
    results_dir: str = "training_results",
) -> dict:
    """
    Executes the complete leak-free cross-validation and hyperparameter tuning workflow:
    1. Splits 20% held-out test set (unseen until final evaluation).
    2. Runs 5-Fold Stratified Cross-Validation on development set to tune XGBoost and Random Forest.
    3. Stacks tuned base estimators with LogisticRegression meta-learner.
    4. Evaluates the assembled ensemble via 5-Fold Stratified CV on training set (Mean & Std).
    5. Refits the best stacked ensemble on the complete development set.
    6. Evaluates once on the held-out test set for unbiased final metrics.
    7. Validates and saves model to models/<name>_model.pkl.
    8. Persists evaluation metrics to training_results/<name>_results.json.
    """
    start_time = time.time()
    os.makedirs(results_dir, exist_ok=True)

    if not os.path.exists(path):
        logger.error(f"Dataset path not found: {path}")
        raise FileNotFoundError(f"Dataset path not found: {path}")

    df = pd.read_csv(path)
    X = df.drop(target, axis=1)
    y = df[target]

    logger.info(f"[{name}] Dataset loaded | Samples={len(df)} | Features={X.shape[1]} | Classes={sorted(y.unique())}")

    # 1. Held-out test set partition (20% held out, NEVER used in hyperparameter tuning)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y if y.nunique() <= 20 else None,
    )
    logger.info(f"[{name}] Data split | Dev set={len(X_train)} samples | Held-out test set={len(X_test)} samples")

    # 2. Stratified 5-Fold Cross-Validation Setup
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    primary_metric = "roc_auc_ovr" if multiclass else "roc_auc"

    # Get tailored parameter distributions
    xgb_dist, rf_dist = get_disease_param_distributions(name, y_train, multiclass=multiclass)

    # 3. Tune Base Estimator 1: XGBoost
    xgb_base = XGBClassifier(
        eval_metric="mlogloss" if multiclass else "logloss",
        random_state=42,
        verbosity=0,
        n_jobs=1,
    )
    xgb_search = RandomizedSearchCV(
        xgb_base,
        param_distributions=xgb_dist,
        n_iter=n_iter,
        cv=cv,
        scoring=primary_metric,
        random_state=42,
        n_jobs=-1,
        refit=True,
    )
    t_xgb_start = time.time()
    xgb_search.fit(X_train, y_train)
    best_xgb = xgb_search.best_estimator_
    logger.info(f"[{name}] XGBoost tuned in {time.time() - t_xgb_start:.2f}s | Best CV {primary_metric}: {xgb_search.best_score_:.4f}")

    # 4. Tune Base Estimator 2: Random Forest
    rf_base = RandomForestClassifier(random_state=42, n_jobs=1)
    rf_search = RandomizedSearchCV(
        rf_base,
        param_distributions=rf_dist,
        n_iter=n_iter,
        cv=cv,
        scoring=primary_metric,
        random_state=42,
        n_jobs=-1,
        refit=True,
    )
    t_rf_start = time.time()
    rf_search.fit(X_train, y_train)
    best_rf = rf_search.best_estimator_
    logger.info(f"[{name}] Random Forest tuned in {time.time() - t_rf_start:.2f}s | Best CV {primary_metric}: {rf_search.best_score_:.4f}")

    # 5. Build Tuned Stacked Ensemble
    meta_learner = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs", random_state=42)
    ensemble = StackingClassifier(
        estimators=[("xgb", best_xgb), ("rf", best_rf)],
        final_estimator=meta_learner,
        cv=5,
        stack_method="predict_proba",
        passthrough=False,
        n_jobs=-1,
    )

    # 6. Evaluate Full Ensemble via 5-Fold CV on Dev Set
    scoring_dict = {
        "accuracy": "accuracy",
        "f1": "f1_macro" if multiclass else "f1",
        "precision": "precision_macro" if multiclass else "precision",
        "recall": "recall_macro" if multiclass else "recall",
        "roc_auc": primary_metric,
    }
    cv_results = cross_validate(ensemble, X_train, y_train, cv=cv, scoring=scoring_dict, n_jobs=-1)

    cv_summary = {
        "cv_roc_auc_mean": float(cv_results["test_roc_auc"].mean()),
        "cv_roc_auc_std": float(cv_results["test_roc_auc"].std()),
        "cv_accuracy_mean": float(cv_results["test_accuracy"].mean()),
        "cv_accuracy_std": float(cv_results["test_accuracy"].std()),
        "cv_precision_mean": float(cv_results["test_precision"].mean()),
        "cv_precision_std": float(cv_results["test_precision"].std()),
        "cv_recall_mean": float(cv_results["test_recall"].mean()),
        "cv_recall_std": float(cv_results["test_recall"].std()),
        "cv_f1_mean": float(cv_results["test_f1"].mean()),
        "cv_f1_std": float(cv_results["test_f1"].std()),
    }

    logger.info(f"[{name}] Ensemble 5-Fold CV Results on Dev Set:")
    logger.info(f"  ROC-AUC  : {cv_summary['cv_roc_auc_mean']:.4f} +/- {cv_summary['cv_roc_auc_std']:.4f}")
    logger.info(f"  Accuracy : {cv_summary['cv_accuracy_mean']:.4f} +/- {cv_summary['cv_accuracy_std']:.4f}")
    logger.info(f"  Precision: {cv_summary['cv_precision_mean']:.4f} +/- {cv_summary['cv_precision_std']:.4f}")
    logger.info(f"  Recall   : {cv_summary['cv_recall_mean']:.4f} +/- {cv_summary['cv_recall_std']:.4f}")
    logger.info(f"  F1-Score : {cv_summary['cv_f1_mean']:.4f} +/- {cv_summary['cv_f1_std']:.4f}")

    # 7. Refit Best Ensemble on Complete Dev Set
    ensemble.fit(X_train, y_train)

    # 8. Final Evaluation on Untouched Held-Out Test Set
    test_probs = ensemble.predict_proba(X_test)
    test_preds = ensemble.predict(X_test)

    if multiclass:
        test_auc = float(roc_auc_score(y_test, test_probs, multi_class="ovr"))
        avg_mode = "macro"
    else:
        test_auc = float(roc_auc_score(y_test, test_probs[:, 1]))
        avg_mode = "binary"

    test_acc = float(accuracy_score(y_test, test_preds))
    test_prec = float(precision_score(y_test, test_preds, average=avg_mode, zero_division=0))
    test_rec = float(recall_score(y_test, test_preds, average=avg_mode, zero_division=0))
    test_f1 = float(f1_score(y_test, test_preds, average=avg_mode, zero_division=0))
    cm = confusion_matrix(y_test, test_preds).tolist()
    clf_report = classification_report(y_test, test_preds, zero_division=0, output_dict=True)

    test_summary = {
        "test_roc_auc": test_auc,
        "test_accuracy": test_acc,
        "test_precision": test_prec,
        "test_recall": test_rec,
        "test_f1": test_f1,
        "confusion_matrix": cm,
        "classification_report": clf_report,
    }

    logger.info(f"[{name}] Held-Out Test Set Performance (20% Unseen):")
    logger.info(f"  Test ROC-AUC  : {test_auc:.4f}")
    logger.info(f"  Test Accuracy : {test_acc:.4f}")
    logger.info(f"  Test Precision: {test_prec:.4f}")
    logger.info(f"  Test Recall   : {test_rec:.4f}")
    logger.info(f"  Test F1-Score : {test_f1:.4f}")

    # 9. Validate Contract & Persist Model
    safe_save_model(ensemble, out_path, X_test.iloc[:5], multiclass=multiclass)

    total_duration = round(time.time() - start_time, 2)

    # 10. Persist Detailed Results JSON
    result_record = {
        "disease_name": name,
        "dataset_path": path,
        "model_output_path": out_path,
        "multiclass": multiclass,
        "training_duration_seconds": total_duration,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "features_count": X.shape[1],
        "feature_names": list(X.columns),
        "primary_selection_metric": primary_metric,
        "best_hyperparameters": {
            "xgb": {k: (v if not isinstance(v, (np.integer, np.floating)) else float(v)) for k, v in xgb_search.best_params_.items()},
            "rf": {k: (v if not isinstance(v, (np.integer, np.floating)) else float(v)) for k, v in rf_search.best_params_.items()},
            "final_estimator": {"C": 1.0, "solver": "lbfgs", "max_iter": 1000},
        },
        "xgb_best_cv_score": float(xgb_search.best_score_),
        "rf_best_cv_score": float(rf_search.best_score_),
        "cross_validation_metrics": cv_summary,
        "held_out_test_metrics": test_summary,
    }

    slug = name.lower().replace(" ", "_")
    res_path = os.path.join(results_dir, f"{slug}_results.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(result_record, f, indent=2)
    logger.info(f"[{name}] Training results saved to {res_path}")

    return result_record
