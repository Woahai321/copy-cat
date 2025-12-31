# Stage 1: Build Frontend
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
# Generate static output (Nuxt 3)
RUN npm run generate

# Stage 2: Build Backend & Serve
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (e.g. for potential DB drivers or build tools)
# sqlite3 is usually included, but basic tools help debugging
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend
# Copy static frontend build to backend/static
COPY --from=frontend-build /app/frontend/.output/public ./backend/static

# Set working directory to backend so relative imports work usually
WORKDIR /app/backend

# Expose port (FastAPI default)
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_DIR=/data
ENV STATIC_DIR=static

# Run command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
