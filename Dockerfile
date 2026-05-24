# ─────────────────────────────────────────────
# Stage 1: Builder — install dependencies
# ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Prevent .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies in an isolated layer (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ─────────────────────────────────────────────
# Stage 2: Runtime — lean final image
# ─────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy only the files the app needs at runtime
COPY app.py          .
COPY models/         ./models/

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Start the API server
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
