# 🚀 Deployment Guide

This guide details how to deploy CopyCat in various environments.

## 🐳 Docker Compose (Recommended)

The easiest way to run CopyCat is using Docker Compose.

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- A source directory (e.g., Zurg mount)
- A destination directory (e.g., local hard drive)

### Step-by-Step

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/copycat.git
    cd copycat
    ```

2.  **Configure Environment**
    Copy the example file and edit it:
    ```bash
    cp .env.example .env
    nano .env
    ```

    **Key Variables:**
    - `SOURCE_PATH`: The absolute path to your source media (read-only recommended).
    - `DESTINATION_PATH`: The absolute path to where you want to copy files.
    - `JWT_SECRET_KEY`: A secure random string for session security.

3.  **Start the Stack**
    ```bash
    docker-compose up -d
    ```

4.  **Access the Application**
    - URL: `http://localhost:4223`
    - Default Credentials: `admin` / `changeme`

### Data Persistence
- **Database**: The SQLite database and user data are stored in the `./data` directory on the host machine.
- **Backups**: To backup your instance, simply archive the `./data` directory.
- **Updates**: To update, pull the latest changes/image and restart:
    ```bash
    git pull
    docker-compose down
    docker-compose up -d --build
    ```

## 🪟 Windows Deployment

For Windows users, use the `docker-compose.windows.yml` file which is optimized for Windows path handling.

```powershell
docker-compose -f docker-compose.windows.yml up -d
```

Ensure your `.env` paths use forward slashes `/` or double backslashes `\\` to avoid parsing errors.

## 🔧 Manual Migration

If you need to move CopyCat to a new server:
1.  Stop the docker container.
2.  Copy the entire `copycat` folder (containing `data/`, `.env`, and `docker-compose.yml`) to the new server.
3.  Run `docker-compose up -d` on the new server.
