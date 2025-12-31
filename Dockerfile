# Stage 1: Build Frontend (Nuxt SSR)
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
# Build for server mode
RUN npm run build

# Stage 2: Build Backend Dependencies
FROM python:3.11-slim AS backend-build
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 3: Final Runtime Image
FROM python:3.11-slim
WORKDIR /app

# Install Node.js (for Nuxt server) and system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies
COPY --from=backend-build /install /usr/local

# Copy backend code
COPY backend/ ./backend

# Copy frontend server output
COPY --from=frontend-build /app/frontend/.output ./frontend/.output

# Set working directory to backend for entrypoint
WORKDIR /app/backend

# Expose ports: 8000 (API), 3000 (Frontend)
EXPOSE 8000 3000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_DIR=/data
ENV STATIC_DIR=static

# Healthcheck (Checks API)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Run command using entrypoint script
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
