# ⚙️ Configuration Guide

CopyCat is configured primarily via Environment Variables. These can be set in a `.env` file or directly in your Docker container settings.

## Core Settings

| Variable | Description | Default | Required |
| :--- | :--- | :--- | :--- |
| `SOURCE_PATH` | Host path to the source directory (e.g., Zurg mount). | `/mnt/zurg` | Yes |
| `DESTINATION_PATH` | Host path to the destination directory. | `/mnt/16tb` | Yes |
| `JWT_SECRET_KEY` | Secret key for signing session tokens. **Must be changed in production.** | *unsafe default* | Yes |
| `TZ` | Timezone for logs and scheduled tasks. | `UTC` | No |

## Application Paths (Internal)

These are used inside the container. You typically do not need to change these unless you are modifying the `Dockerfile`.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `SOURCE_MOUNT` | Internal container path where `SOURCE_PATH` is mounted. | `/mnt/source` |
| `DESTINATION_MOUNT` | Internal container path where `DESTINATION_PATH` is mounted. | `/mnt/destination` |
| `DATABASE_DIR` | Internal path where the DB is stored. | `/data` |

## Advanced Settings (Database)

Some settings can be configured via the **Web UI > Settings** page, stored in the database:

-   **Discord Webhook**: URL for sending notifications.
-   **Trakt Client ID**: Integrates metadata fetching from Trakt.
-   **Scan Interval**: How often the system scans the source directory (in seconds).
-   **Default Paths**: Default subfolders for Movies and TV Shows.

## 🔐 Security Best Practices

1.  **JWT Secret**: Never use the default secret. Generate a long random string.
2.  **Reverse Proxy**: Do not expose port 4223 directly to the internet. Use Nginx, Caddy, or Traefik with SSL/TLS termination.
3.  **Firewall**: Restrict access to the application port if not using a reverse proxy.
