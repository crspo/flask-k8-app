# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

# Set work directory
WORKDIR /app

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install CairoSVG system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-xlib-2.0-0 \
        shared-mime-info \
        fonts-dejavu-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip dependencies into virtual environment
COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

# --- Stage: Frontend build ---
FROM node:18-bullseye AS node-builder
# Build inside /src/frontend so package.json, lockfile and source all live in the
# same folder when npm runs. This avoids path-related failures during the
# containerized build.
WORKDIR /src/frontend
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ ./
# Ensure the server-side `templates/` directory is available in the node build
# stage so `scripts/copy-index.js` can write the built `index.html` into
# `/src/templates/index.html` inside the container.
COPY templates/ /src/templates/
# Prefer reproducible install; fall back to npm install if npm ci fails
RUN if [ -f package-lock.json ]; then npm ci --legacy-peer-deps; else npm install; fi
RUN npm run build

# --- Stage 2: Runtime ---
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
        shared-mime-info \
        libfontconfig1 \
        fonts-dejavu-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy app code
COPY . .

COPY --from=node-builder /src/static ./static
COPY frontend/public ./static/public

# Clean up __pycache__
RUN rm -rf /venv/lib/python*/site-packages/__pycache__ \
    && find . -type d -name '__pycache__' -exec rm -r {} +

EXPOSE 5000
CMD ["python", "app.py"]

