# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.11-slim as builder

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system build dependencies required for ML packages (e.g., scikit-learn, xgboost)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
# Copy only requirements to cache them in docker layer
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.11-slim as runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the default port, can be overridden at runtime
ENV PORT=5000

# Install runtime dependencies ONLY
# libgomp1 is required by LightGBM / XGBoost / scikit-learn on some slim environments
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the app
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy the built virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set PATH to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY . .

# Change ownership of the application directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the application port
EXPOSE $PORT

# Define Healthcheck using Python built-in urllib
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request, os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\", 5000)}/api/v1/health')" || exit 1

# Start the application using Gunicorn
# Using 1 worker and 4 threads to optimize for I/O bounds while keeping memory low for ML models
CMD ["gunicorn", "api:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "120"]
