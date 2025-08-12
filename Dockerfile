# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

# Set work directory
WORKDIR /app

# Install CairoSVG system dependencies
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libdmtx0b \
    libdmtx-dev \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip dependencies into virtual environment
COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.12-slim

# Set work directory
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libdmtx0b \
    libdmtx-dev \
    shared-mime-info \
    libfontconfig1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy app code
COPY . .

# Clean up __pycache__
RUN rm -rf /venv/lib/python*/site-packages/__pycache__ \
    && find . -type d -name '__pycache__' -exec rm -r {} +

EXPOSE 5000
CMD ["python", "app.py"]

