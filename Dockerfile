FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libdmtx0b \
    libdmtx-dev \
    shared-mime-info \
    libfontconfig1 \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Patch pylibdmtx to remove distutils
RUN sed -i 's/from distutils.version import LooseVersion/from packaging.version import Version/' /usr/local/lib/python3.12/site-packages/pylibdmtx/wrapper.py \
 && sed -i 's/LooseVersion/Version/g' /usr/local/lib/python3.12/site-packages/pylibdmtx/wrapper.py

# Copy application code
COPY . .

# Clean up __pycache__
RUN find . -type d -name '__pycache__' -exec rm -r {} +

EXPOSE 5000
CMD ["python", "app.py"]

