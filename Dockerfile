FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --no-install-project --no-dev

# Copy the rest of the application code
COPY src/ src/
COPY config/ config/
COPY .planning/ .planning/
COPY README.md ./

# Ensure the app code is installed
RUN uv sync --no-dev

# Expose port (internal)
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
