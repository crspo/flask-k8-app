FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install common build tools and native libraries required to build wheels
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

WORKDIR /wheels

CMD ["bash"]
