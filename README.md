---
license: mit
title: MDRP
sdk: docker
emoji: 🚀
colorFrom: blue
colorTo: green
pinned: false
short_description: Multi-disease risk prediction from lab values and blood repo
---

# Multi-Disease Risk Prediction System

A full-stack Flask web application that predicts risk for cardiovascular disease, type 2 diabetes, and chronic kidney disease from standard blood test PDF reports. Combines ensemble machine learning with evidence-based clinical scoring for interpretable, clinically-grounded risk assessment.

## Features
- **Multi-Disease Predictions**: Simultaneous risk assessment for cardiovascular disease, type 2 diabetes, and chronic kidney disease.
- **PDF-Based Input**: Extracts blood test data directly from PDF reports using Gemini 2.0 Flash with robust regex fallback.
- **Hybrid Scoring**: Weighted ensemble combining 40% stacking ensemble ML + 60% clinical scoring based on ACC/AHA 2019, ADA 2024, and KDIGO 2022 guidelines.
- **Explainable AI (SHAP)**: Provides model explainability to understand the feature impact for each prediction.
- **Clerk Authentication**: Secure endpoints using robust session management and JWT authentication through Clerk.
- **Vanilla Frontend**: Lightweight JavaScript interface without framework overhead.

## Architecture Overview
- **Backend Framework**: Flask REST API using Application Factory pattern.
- **ML Stack**: scikit-learn, XGBoost, pandas 2.x.
- **PDF Extraction**: Google Generative AI (Gemini 2.0 Flash) with regex fallback.
- **Authentication**: Clerk backend integration for securing endpoints.
- **Logging & Monitoring**: Centralized structured logging for debugging and tracking request IDs.
- **Explainability**: SHAP (SHapley Additive exPlanations) for human-readable output feature impact.

## Repository Structure
```text
app/                 # Application factory, blueprints, and services
data/                # Raw and processed datasets
models/              # Trained machine learning model artifacts
logs/                # Centralized application logs
templates/           # HTML templates for the frontend
tests/               # Pytest suite (unit and integration tests)
README.md            # Project documentation
requirements.txt     # Python dependencies
Dockerfile           # Docker container configuration
runtime.txt          # Python runtime specification
.env.example         # Example environment variables template
.gitignore           # Git ignore rules
api.py               # Main application entry point
predict.py           # CLI Prediction script
pytest.ini           # Pytest configuration
artifacts/           # Extra scripts and generated artifacts
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js (optional, for frontend build tasks if any)
- Google Cloud API credentials (Gemini 2.0 Flash)
- Clerk API keys

### Setup
```bash
# Clone repository
git clone https://github.com/pramit1506/mdrp.git
cd mdrp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and supply required values
```

## Environment Variables
The application requires several environment variables for API keys and configuration. Refer to `.env.example`:

- `FLASK_ENV`: Deployment environment (`development` or `production`)
- `PORT`: Port for the application (default 5000)
- `GOOGLE_API_KEY`: API key for Gemini 2.0 Flash PDF extraction
- `CLERK_SECRET_KEY`: Backend secret key from Clerk dashboard
- `CLERK_PUBLISHABLE_KEY`: Publishable key from Clerk dashboard
- `CLERK_JWT_ISSUER`: Clerk JWT Issuer URL
- `CLERK_FRONTEND_API`: Clerk Frontend API endpoint
- `LOG_LEVEL`: Application logging level (`DEBUG`, `INFO`, `WARNING`, etc.)
- `MDRP_DEBUG`: Set to `1` for debug mode, `0` for production.

## Authentication Setup
This project uses **Clerk** for authentication. To set it up:
1. Create an application in the [Clerk Dashboard](https://dashboard.clerk.dev/).
2. Retrieve your **Secret Key**, **Publishable Key**, and **Issuer URL**.
3. Add these credentials to your `.env` file.
4. The backend verifies Clerk-issued JWTs in the `Authorization: Bearer <token>` header for protected endpoints.

## API Documentation
The API documentation is accessible via Swagger UI when running locally.

### Start the Server
```bash
python api.py
# Server runs on http://localhost:5000
```
Navigate to `http://localhost:5000/apidocs` (if configured) to view the Swagger UI.

### Extract Lab Values
```bash
POST /api/v1/parse-pdf
Authorization: Bearer <clerk_jwt_token>
Content-Type: multipart/form-data

Parameters:
  - file: Blood test PDF report

Response:
{
  "success": true,
  "extracted": { ... },
  "method": "gemini_ai"
}
```

### Risk Prediction
```bash
POST /api/v1/predict
Authorization: Bearer <clerk_jwt_token>
Content-Type: application/json

Parameters (JSON Body):
  - age, sex, bmi, ...

Response:
{
  "success": true,
  "heart": { "risk_score": 0.35, "risk_category": "Low", ... },
  "diabetes": { ... },
  "kidney": { ... },
  "explainability": { ... }
}
```

## Running Tests
The project uses `pytest` for automated testing.
```bash
# Run the entire test suite
pytest

# Run tests with verbosity
pytest -v

# Run specific integration tests
pytest tests/integration/
```

## Docker Containerization
The application is fully containerized using a multi-stage Docker build, optimized for production environments like Railway or Render.

### Local Docker Commands
The easiest way to run the entire stack (Database, Backend, Frontend) locally is using Docker Compose:

```bash
# Start the full stack in detached mode
docker-compose up -d --build

# View logs for all services
docker-compose logs -f

# Stop the stack
docker-compose down
```
The Docker images utilize Next.js standalone mode for the frontend and Gunicorn with thread optimizations (`--workers 1 --threads 4`) for the backend API.

## End-to-End Testing (Playwright)
We use Playwright for end-to-end testing of the Next.js frontend.
```bash
cd frontend
# Install Playwright dependencies
npx playwright install --with-deps

# Run E2E tests
npx playwright test

# View test report
npx playwright show-report
```
The Docker image utilizes Gunicorn as the WSGI server with thread optimizations (`--workers 1 --threads 4`) to minimize memory usage for ML models while maintaining concurrency. A native `/api/v1/health` health check is included.

## Deployment Prerequisites
Before deploying to production:
1. Ensure all environment variables (including Clerk and Google API keys) are configured in the deployment environment.
2. The application relies entirely on environment variables; no local `.env` is copied into the production container.
3. Keep `FLASK_ENV=production` and `MDRP_DEBUG=0`.
4. Ensure `logs/` directory permissions allow write access if logging to file system.

## Clinical Disclaimer
This tool is intended for **educational and research purposes only**. It does not replace professional medical judgment. Predictions should not be used for clinical decision-making without validation by a qualified healthcare provider. Always consult a physician for diagnosis and treatment recommendations.

## Contact
**Project Author**: Pramit Shrivastav
**Email**: pramitshrivastav15@gmail.com
**LinkedIn**: https://www.linkedin.com/in/pramit1506/
**GitHub**: https://github.com/pramit1506