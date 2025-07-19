# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    NAUTOBOT_VERSION=1.6.0

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq-dev \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
COPY service_now_groups/ ./service_now_groups/
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_NAUTOBOT_SERVICENOW_GROUPS=1.0.0
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "nautobot==${NAUTOBOT_VERSION}" \
    && pip install --no-cache-dir -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash nautobot

# Create necessary directories and set permissions
RUN mkdir -p /opt/nautobot /home/nautobot/.nautobot \
    && chown -R nautobot:nautobot /opt/nautobot /home/nautobot/.nautobot /app

# Switch to nautobot user
USER nautobot

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health/ || exit 1

# Default command
CMD ["nautobot-server", "runserver", "0.0.0.0:8080"] 