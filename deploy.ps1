# Copy Management System - Deployment Script (PowerShell)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Copy Management System - Deployment" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
} catch {
    Write-Host "Error: Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/"
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose --version | Out-Null
} catch {
    try {
        docker compose version | Out-Null
    } catch {
        Write-Host "Error: Docker Compose is not available!" -ForegroundColor Red
        exit 1
    }
}

# Check if mount points exist (adjust for Windows paths if needed)
Write-Host "Checking mount points..."
if (-not (Test-Path "/mnt/zurg" -ErrorAction SilentlyContinue)) {
    Write-Host "Warning: /mnt/zurg does not exist!" -ForegroundColor Yellow
    Write-Host "Please ensure your Zurg mount is at /mnt/zurg or update docker-compose.yml" -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}

if (-not (Test-Path "/mnt/16tb" -ErrorAction SilentlyContinue)) {
    Write-Host "Warning: /mnt/16tb does not exist!" -ForegroundColor Yellow
    Write-Host "Please ensure your hard drive is mounted at /mnt/16tb or update docker-compose.yml" -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}

Write-Host ""
Write-Host "Building and starting containers..." -ForegroundColor Cyan
Write-Host ""

# Build and start containers
docker-compose up -d --build

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Application is now running:"
Write-Host "  - Frontend: http://localhost:4222" -ForegroundColor Cyan
Write-Host "  - Backend:  http://localhost:4223" -ForegroundColor Cyan
Write-Host "  - API Docs: http://localhost:4223/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Default credentials:"
Write-Host "  Username: admin"
Write-Host "  Password: changeme"
Write-Host ""
Write-Host "⚠️  IMPORTANT: Change the default password after first login!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Useful commands:"
Write-Host "  - View logs:        docker-compose logs -f"
Write-Host "  - Stop:             docker-compose down"
Write-Host "  - Restart:          docker-compose restart"
Write-Host "  - Change password:  docker exec -it copypaste-backend python change_password.py"
Write-Host ""

