#!/bin/bash

# Copy Management System - Deployment Script

set -e

echo "======================================"
echo "Copy Management System - Deployment"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed!"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed!"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if mount points exist
echo "Checking mount points..."
if [ ! -d "/mnt/zurg" ]; then
    echo "Warning: /mnt/zurg does not exist!"
    echo "Please ensure your Zurg mount is at /mnt/zurg or update docker-compose.yml"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if [ ! -d "/mnt/16tb" ]; then
    echo "Warning: /mnt/16tb does not exist!"
    echo "Please ensure your hard drive is mounted at /mnt/16tb or update docker-compose.yml"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Building and starting containers..."
echo ""

# Build and start containers
docker-compose up -d --build

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "Application is now running:"
echo "  - Frontend: http://localhost:4222"
echo "  - Backend:  http://localhost:4223"
echo "  - API Docs: http://localhost:4223/docs"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: changeme"
echo ""
echo "⚠️  IMPORTANT: Change the default password after first login!"
echo ""
echo "Useful commands:"
echo "  - View logs:     docker-compose logs -f"
echo "  - Stop:          docker-compose down"
echo "  - Restart:       docker-compose restart"
echo "  - Change password: docker exec -it copypaste-backend python change_password.py"
echo ""

