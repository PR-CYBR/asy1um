# Dockerfile - Main application container using optimized base image
#
# This Dockerfile builds upon the pre-built base image containing heavy ML
# dependencies, significantly reducing build time and CI/CD costs.
#
# Build strategy:
# 1. Use ghcr.io/folkvarlabs/project-asylum:base-ml as the base
# 2. Copy only application-specific code
# 3. Install any additional lightweight dependencies
# 4. Configure the application runtime
#
# The base image is rebuilt only when core dependencies change,
# while this image rebuilds quickly for code changes.
#
# Build command:
#   docker build -t ghcr.io/folkvarlabs/project-asylum:ai .
#
# Performance optimization notes:
# - Base image contains TensorFlow, PyTorch, and other heavy dependencies
# - Only application code changes trigger rebuilds of this image
# - Docker layer caching further optimizes repeated builds
# - Typical rebuild time: < 2 minutes (vs 15-20 minutes with full build)

FROM ghcr.io/folkvarlabs/project-asylum:base-ml

# Set working directory
WORKDIR /app

# Copy application code
# Note: Use .dockerignore to exclude unnecessary files
COPY . /app

# Install any additional application-specific dependencies
# that are not in the base image
RUN if [ -f requirements-app.txt ]; then \
        pip install --no-cache-dir -r requirements-app.txt; \
    fi

# Create necessary directories for the application
RUN mkdir -p /app/logs /app/data /app/models

# Set permissions
RUN chmod -R 755 /app

# Expose ports for the application
# Adjust these based on your application needs
EXPOSE 8000 8080

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - runs the main application entry point
# The main.py file initializes the AI/ML infrastructure management system
CMD ["python", "main.py"]
