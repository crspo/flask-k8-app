# --- Stage 1: Builder ---
ARG BUILDER_BASE=python:3.13-slim
FROM ${BUILDER_BASE} AS builder

# Set work directory
WORKDIR /app

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install build tools and CairoSVG system dependencies so wheels (Pillow, cairosvg) can be built
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        make \
        pkg-config \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        libjpeg-dev \
        zlib1g-dev \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip dependencies into virtual environment
COPY requirements.txt .
# Build wheels in builder stage so the runtime image can install from them
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip wheel --wheel-dir /wheels -r requirements.txt

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
FROM python:3.13-slim

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

# Copy built wheels from the builder and install into a fresh venv at runtime
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt ./requirements.txt
RUN python -m venv /venv \
    && /venv/bin/python -m pip install --upgrade pip setuptools wheel \
    && /venv/bin/pip install --no-index --find-links /wheels -r requirements.txt \
    && rm -rf /wheels
ENV PATH="/venv/bin:$PATH"

# Copy only runtime application files to keep the image small
COPY backend /app/backend
COPY wsgi.py /app/wsgi.py

COPY --from=node-builder /src/static ./backend/static
COPY frontend/public ./backend/static/public
COPY --from=node-builder /src/templates ./backend/templates

# Clean up __pycache__
RUN rm -rf /venv/lib/python*/site-packages/__pycache__ \
    && find . -type d -name '__pycache__' -exec rm -r {} +

ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
EXPOSE 5000
# Use gunicorn in the runtime image for production WSGI serving
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]

