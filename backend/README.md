# Copy Management Backend

Python FastAPI backend for the Copy Management System.

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Initialize Database

```bash
python init_db.py
```

This will create the SQLite database and an admin user with default credentials:
- Username: `admin`
- Password: `changeme`

### Change Password

```bash
python change_password.py
```

Follow the prompts to change the admin password.

## Running the Server

### Development

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:4223/docs
- ReDoc: http://localhost:4223/redoc

## Configuration

### Secret Key

The JWT secret key is defined in `auth.py`. For production, change this to a secure random value:

```python
SECRET_KEY = "your-secure-random-secret-key-here"
```

You can generate a secure key using:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Base Paths

The mount points for the drives are defined in `main.py`:

```python
ZURG_BASE = "/mnt/zurg"
HARDDRIVE_BASE = "/mnt/16tb"
```

Adjust these paths according to your system configuration.

## Background Worker

The copy worker runs as a background thread and automatically starts when the application starts. It:

1. Polls the database for queued jobs
2. Processes jobs one at a time
3. Updates progress in real-time via WebSocket
4. Handles errors and updates job status

## WebSocket

The WebSocket endpoint at `/ws/progress` broadcasts real-time progress updates to all connected clients. Message format:

```json
{
  "job_id": 1,
  "status": "processing",
  "progress_percent": 45,
  "copied_size_bytes": 1073741824,
  "total_size_bytes": 2147483648
}
```

## Database

The application uses SQLite with SQLAlchemy ORM. The database file `copypaste.db` is created in the application directory.

### Tables

- **users**: Stores user credentials
- **copy_jobs**: Stores copy job information and history

## Security

- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Path validation to prevent directory traversal attacks
- Read-only access to source drive (recommended in production)

## Testing

### Test Authentication

```bash
curl -X POST "http://localhost:4223/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'
```

### Test File Browsing

```bash
curl -X GET "http://localhost:4223/api/browse?source=zurg&path=" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test Copy Operation

```bash
curl -X POST "http://localhost:4223/api/copy/start" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"source_path":"folder1","destination_path":"backup/folder1"}'
```

