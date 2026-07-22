# Deployment Guide

The MDRP backend is designed to run in Docker, optimized for lightweight instances.

## Environment Variables
- `FLASK_ENV`: Set to `production`
- `MDRP_DEBUG`: Set to `0`
- `PORT`: Exposed port (default 5000)
- `DATABASE_URL`: Connection string for PostgreSQL
- `GOOGLE_API_KEY`: For Gemini 2.0 Flash PDF Extraction
- Clerk keys: `CLERK_SECRET_KEY`, `CLERK_PUBLISHABLE_KEY`, `CLERK_JWT_ISSUER`, `CLERK_FRONTEND_API`

## Running via Docker
Use the provided `Dockerfile` to build the application:

```bash
docker build -t mdrp-backend .
docker run -p 5000:5000 \
    -e FLASK_ENV=production \
    -e MDRP_DEBUG=0 \
    -e DATABASE_URL=... \
    ... \
    mdrp-backend
```

## Gunicorn Configuration
The Dockerfile runs Gunicorn. For ML model memory optimization, the recommended flags are:
`gunicorn --workers 1 --threads 4 api:app`

This ensures that the large ML models are loaded exactly once in the single worker process, while allowing multiple threads to handle concurrent I/O (like DB requests and PDF extraction API calls).

## Infrastructure Recommendations
- **Database**: PostgreSQL 14+
- **Compute**: Minimum 1GB RAM recommended due to Scikit-Learn/XGBoost models.
- **Reverse Proxy**: Use Nginx or similar to handle HTTPS and static file caching if serving `index.html` from the backend.
