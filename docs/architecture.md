# MDRP Architecture

## Overview
The Multi-Disease Risk Prediction (MDRP) platform uses a Flask-based REST API to provide clinical risk assessments for cardiovascular disease, diabetes, and kidney disease.

## Key Components

### 1. Application Factory (`backend/app/factory.py`)
Flask app is initialized here. Responsible for wiring up configurations, extensions (CORS, Limiter, Talisman, Swagger), and registering blueprints.

### 2. Services (`backend/services/`)
- `prediction_service.py`: Orchestrates model inference and clinical scoring.
- `explainability_service.py`: Computes SHAP feature attributions.
- `history_service.py`: Manages prediction persistence and history retrieval.
- `model_loader.py`: Efficient singleton loader for Scikit-Learn/XGBoost models.
- `clinical_risk.py`: Stateless clinical score calculators based on ACC/AHA, ADA, and KDIGO guidelines.

### 3. API Layer (`backend/api/`)
- `routes.py`: Defines REST endpoints. Uses Clerk middleware for Auth and centralized validation.

### 4. Data Layer (`backend/database/` and `backend/repositories/`)
- SQLAlchemy ORM models map to PostgreSQL.
- Repositories abstract all database access, ensuring services remain agnostic to SQL logic.

### 5. ML Pipeline (`ml_pipeline/`)
- Contains training, preprocessing, and feature engineering scripts used to produce the models stored in `models/`.

## Data Flow
1. Client requests `/api/v1/predict` with patient data.
2. `routes.py` validates inputs using `backend/utils/validators.py`.
3. `routes.py` calls `prediction_service.predict_all()`.
4. `predict_all` fetches models via `model_loader`, executes inference, and requests explanations from `explainability_service`.
5. `predict_all` also requests clinical scores from `clinical_risk.py`.
6. Final results are returned to the API layer, which persists them via `history_service` and responds to the client.
