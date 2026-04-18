# This Dockerfile is placed at the root specifically for Hugging Face Spaces.
# Hugging Face Spaces requires the Dockerfile to be in the root directory.
# It builds the backend component of this monorepo.

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (to leverage Docker layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Hugging Face Spaces requires running as a non-root user
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/app

# Copy the backend files from the monorepo backend folder and set ownership
COPY --chown=user backend/ /app/

# Expose default port (7860 is Hugging Face Spaces default)
EXPOSE 7860

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120", "app:app"]
