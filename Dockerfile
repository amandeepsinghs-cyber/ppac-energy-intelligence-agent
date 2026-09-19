# =============================================================================
# PPAC Energy Intelligence Agent Container
# Target: Vertex AI Agent Runtime / Cloud Run
# Protocol: ADK :streamQuery & A2A JSON-RPC 1.0
# =============================================================================

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install --no-cache-dir uv>=0.12.0

# Copy dependency specifications and lockfile
COPY pyproject.toml README.md uv.lock* ./
RUN uv sync --frozen

# Copy application source code and fixtures
COPY app/ ./app/
COPY fixtures/ ./fixtures/

# Ensure output artifacts directory exists
RUN mkdir -p output_artifacts

EXPOSE 8080

# Run ADK FastAPI server mounting Reasoning Engine and A2A routes
CMD ["uv", "run", "uvicorn", "app.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]
