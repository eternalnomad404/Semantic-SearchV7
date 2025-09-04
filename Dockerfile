# Multi-stage Dockerfile for Semantic Search Application
FROM python:3.11-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies in user space for better caching
# Use pip cache and install in parallel
RUN pip install --no-cache-dir --user --no-warn-script-location \
    --timeout 1000 --retries 3 -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/app/.local

# Set working directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=app:app . .

# Ensure the data and vectorstore directories exist with proper permissions
RUN mkdir -p /app/vectorstore /app/data \
    && chown -R app:app /app

# Make sure scripts in .local are usable
ENV PATH=/home/app/.local/bin:$PATH
ENV PYTHONPATH=/app

# Switch to non-root user
USER app

# Expose ports for both API and Streamlit
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command runs the API server
# Can be overridden to run Streamlit: docker run -p 8501:8501 <image> streamlit run app_main.py --server.port=8501 --server.address=0.0.0.0
CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "8000"]
