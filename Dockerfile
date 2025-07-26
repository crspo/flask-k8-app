# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

# Set work directory
WORKDIR /app

# Install pip dependencies into virtual environment
COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy app code
COPY . .

# Remove cache and __pycache__ if needed
RUN rm -rf /venv/lib/python*/site-packages/__pycache__ \
    && find . -type d -name '__pycache__' -exec rm -r {} +

EXPOSE 5000
CMD ["python", "app.py"]


