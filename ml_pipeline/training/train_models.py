import os, sys, json, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ml_pipeline.training.hyperparameter_tuning import tune_and_train_disease
from backend.utils.logger import get_logger

logger = get_logger("train_models")


def train_all_models():
    """
    Trains and tunes all MDRP disease models using Stratified 5-Fold Cross-Validation,
    unbiased held-out test evaluation, and safe atomic model persistence.
    """
    os.makedirs("models", exist_ok=True)
    os.makedirs("training_results", exist_ok=True)

    models_config = [
        {
            "name": "Heart Disease",
            "path": "data/processed/heart_processed.csv",
            "target": "target",
            "out_path": "models/heart_model.pkl",
            "multiclass": False,
            "n_iter": 20,
        },
        {
            "name": "Diabetes",
            "path": "data/processed/diabetes_processed.csv",
            "target": "outcome",
            "out_path": "models/diabetes_model.pkl",
            "multiclass": False,
            "n_iter": 25,
        },
        {
            "name": "Kidney Disease",
            "path": "data/processed/kidney_processed.csv",
            "target": "classification",
            "out_path": "models/kidney_model.pkl",
            "multiclass": False,
            "n_iter": 20,
        },
        {
            "name": "Health Markers",
            "path": "data/processed/hm_processed.csv",
            "target": "condition_label",
            "out_path": "models/hm_model.pkl",
            "multiclass": True,
            "n_iter": 10,
        },
    ]

    results_summary = {}
    total_start = time.time()

    for config in models_config:
        path = config["path"]
        name = config["name"]
        if os.path.exists(path):
            logger.info(f"{'='*60}")
            logger.info(f"Starting CV & Hyperparameter Tuning for: {name}")
            logger.info(f"{'='*60}")
            result = tune_and_train_disease(
                name=name,
                path=path,
                target=config["target"],
                out_path=config["out_path"],
                multiclass=config["multiclass"],
                n_iter=config["n_iter"],
                results_dir="training_results",
            )
            results_summary[name] = result
        else:
            logger.warning(f"SKIPPED — Dataset {path} not found")

    total_time = round(time.time() - total_start, 2)
    summary_path = os.path.join("training_results", "all_models_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_duration_seconds": total_time,
            "models": results_summary
        }, f, indent=2)

    logger.info(f"{'='*60}")
    logger.info(f"All models trained and tuned successfully in {total_time:.2f}s.")
    logger.info(f"Summary metrics saved → {summary_path}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    train_all_models()
