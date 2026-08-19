from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression

def build_ensemble(multiclass=False, xgb_params=None, rf_params=None, meta_params=None, estimators=None):
    """
    Builds a StackingClassifier ensemble combining XGBoost and Random Forest with Logistic Regression meta-learner.
    Preserves named_estimators_ ['xgb', 'rf'] for full compatibility with explainability_service (SHAP TreeExplainer).
    """
    if estimators is not None:
        xgb_est, rf_est = estimators
    else:
        default_xgb = {
            "n_estimators": 200,
            "max_depth": 4,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "eval_metric": "mlogloss" if multiclass else "logloss",
            "random_state": 42,
            "verbosity": 0,
            "n_jobs": 1,
        }
        if xgb_params:
            default_xgb.update(xgb_params)
        xgb_est = XGBClassifier(**default_xgb)

        default_rf = {
            "n_estimators": 200,
            "max_depth": 8,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "class_weight": "balanced" if not multiclass else None,
            "random_state": 42,
            "n_jobs": 1,
        }
        if rf_params:
            default_rf.update(rf_params)
        rf_est = RandomForestClassifier(**default_rf)

    default_meta = {
        "max_iter": 1000,
        "C": 1.0,
        "solver": "lbfgs",
        "random_state": 42,
    }
    if meta_params:
        default_meta.update(meta_params)
    meta = LogisticRegression(**default_meta)

    return StackingClassifier(
        estimators=[("xgb", xgb_est), ("rf", rf_est)],
        final_estimator=meta,
        cv=5,
        stack_method="predict_proba",
        passthrough=False,
        n_jobs=-1,
    )
