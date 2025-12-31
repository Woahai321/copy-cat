# Stage 1: Build Frontend
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
# Generate static output (Nuxt 3)
RUN npm run generate

# Stage 2: Build Backend & Serve
# Stage 2: Build Backend & Serve
FROM python:3.11-slim AS backend-build

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies
COPY --from=backend-build /install /usr/local

# Copy backend code
COPY backend/ ./backend
# Copy static frontend build to backend/static
COPY --from=frontend-build /app/frontend/.output/public ./backend/static

# Set working directory to backend
WORKDIR /app/backend

# Expose port (FastAPI default)
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_DIR=/data
ENV STATIC_DIR=static

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Run command using entrypoint script (ensure it is executable)
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
