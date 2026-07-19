# =============================================================================
# AI-MOS Backend — Production Dockerfile
# =============================================================================

FROM python:3.12-slim

# System env variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/Backend

# Create non-root system group and user
RUN groupadd -g 10001 aimos && \
    useradd -u 10001 -g aimos -m -s /bin/bash aimos

WORKDIR /app

# Ensure correct permissions
RUN chown aimos:aimos /app

# Copy dependency definition
COPY --chown=aimos:aimos Backend/requirements.txt /app/Backend/requirements.txt

# Install dependencies as root, then we drop privileges
RUN pip install --no-cache-dir -r /app/Backend/requirements.txt

# Copy curriculum folder (parallel to Backend, needed by KnowledgeBaseService)
COPY --chown=aimos:aimos curriculum /app/curriculum

# Copy backend source code and config files
COPY --chown=aimos:aimos Backend /app/Backend

# Switch working directory to Backend root to run uvicorn
WORKDIR /app/Backend

# Expose backend port
EXPOSE 8000

# Switch to non-privileged user
USER aimos

# Run under Uvicorn with 4 concurrent worker processes for production scaling
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
