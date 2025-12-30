<div align="center">

![CopyCat Logo](https://s.2ya.me/api/shares/lVlUQ6CB/files/8776d8e1-9a61-42b8-80ea-eb80d03977b8)
![Docker](https://img.shields.io/badge/Docker-Ready-8b5cf6?style=for-the-badge&labelColor=6b21a8&logo=docker&logoColor=white)
![Nuxt](https://img.shields.io/badge/Nuxt-3.0-8b5cf6?style=for-the-badge&labelColor=6b21a8&logo=nuxtdotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-8b5cf6?style=for-the-badge&labelColor=6b21a8&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11%2B-8b5cf6?style=for-the-badge&labelColor=6b21a8&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-8b5cf6?style=for-the-badge&labelColor=6b21a8)

</div>

---

## 😸 What is CopyCat? 

**CopyCat** is the ultimate self-hosted manager for your digital library. It is built to bridge the gap between your **Cloud Storage** (using tools like Zurg, Rclone, or Real-Debrid mounts) and your **Local Storage** (HDD/NAS).

Instead of dealing with command-line tools or generic file managers, CopyCat provides a **premium, Netflix-like interface** to scan, organize, and copy media files.

### Key Features
- **Smart Parsing**: Automatically detects Movies vs TV Shows, Seasons, and Episodes from raw filenames.
- **Metadata Enrichment**: Integrates with **Trakt** to pull posters, ratings, and plot summaries for your files.
- **Supercharged Copying**: Custom-built queue manager handles massive file transfers reliably in the background.
- **Glass UI**: A stunning, responsive "Aurora Glass" interface that feels like a native desktop app.

<div align="center">

[![Documentation](https://img.shields.io/badge/🐱_Deployment_Guide-8b5cf6?style=for-the-badge&labelColor=6b21a8)](docs/deployment.md)
[![Configuration](https://img.shields.io/badge/🐱_Configuration-8b5cf6?style=for-the-badge&labelColor=6b21a8)](docs/configuration.md)
[![Developer Guide](https://img.shields.io/badge/🐱_Developer_Guide-8b5cf6?style=for-the-badge&labelColor=6b21a8)](docs/development.md)

</div>

---

## 😻 The Experience

<div align="center">
  <img src="https://s.2ya.me/api/shares/9PH2j0tk/files/f9a74261-ffc9-486a-bcd7-baa4f71a1b60" alt="CopyCat Dashboard" width="100%" style="border-radius: 10px; border: 1px solid #60cdff;">
</div>

<br>

<details>
<summary><strong>📸 View More Screenshots</strong></summary>

### Media Library
Browse your content in a rich, Overseerr-inspired interface. Filter by movies or TV shows, view metadata, and select items to transfer with a single click. Be "wowed" by the seamless integration of your local and cloud libraries.

<div align="center">
  <img src="https://s.2ya.me/api/shares/9PH2j0tk/files/08a45da9-716d-4c76-83d4-38361f797a3b" alt="Media Library" width="100%" style="border-radius: 10px; border: 1px solid #8b5cf6;">
  <p><em>Rich Media Library</em></p>
</div>

### Copy Wizard
Prefer a traditional view? The Copy Wizard offers a familiar file explorer interface, allowing you to manually navigate directory structures and define precise destinations for your transfers.

<div align="center">
  <img src="https://s.2ya.me/api/shares/9PH2j0tk/files/8c1b8ba2-c695-4e46-87b0-2e3b1044271d" alt="Copy Wizard" width="100%" style="border-radius: 10px; border: 1px solid #8b5cf6;">
  <p><em>File Explorer & Copy Wizard</em></p>
</div>

### Transfer Queue
Monitor active transfers in real-time. View detailed progress, transfer speeds, and manage your queue with priority controls to ensure your most important media is ready when you are.

<div align="center">
  <img src="https://s.2ya.me/api/shares/9PH2j0tk/files/47720500-3a77-4e7c-8bc0-4674c50c8b3a" alt="Transfer Queue" width="100%" style="border-radius: 10px; border: 1px solid #8b5cf6;">
  <p><em>Live Transfer Queue</em></p>
</div>

</details>

### 😺 Smart Browsing
Navigate your messy cloud mounts as a clean, organized library. CopyCat filters out "junk" files (samples, txt, nfo) and presents only the media you care about.

### 😼 Intelligent Queue
Don't worry about network interruptions. The queue manager handles retries, progress tracking, and ensures your downloads finishes, even if you close the browser.

---

## 😺 Quick Start (One-Command)
Try CopyCat instantly with this single Docker command:

```bash
docker run -d --name copycat \
  -p 4223:4223 \
  -v copycat-data:/app/data \
  -e SOURCE_PATH=/mnt/zurg \
  -e DESTINATION_PATH=/mnt/local/media \
  -e JWT_SECRET_KEY=super_strong_secret_here \
  ghcr.io/woahai321/copy-cat:main
```

Open `http://localhost:4223` and login with **admin** / **changeme**.

## 😽 Deployment

<details>
<summary><strong>Full instructions</strong></summary>

CopyCat is designed to be deployed in minutes using Docker.

### 1. Requirements
- A machine running Docker & Docker Compose.
- A **Source Path** (e.g., `/mnt/zurg` or any folder with media).
- A **Destination Path** (e.g., `/mnt/media` where you want files to go).

### 2. Setup
Clone the repo and configure your environment:

```bash
git clone https://github.com/woahai321/copy-cat.git
cd copy-cat
cp .env.example .env
```

### 3. Configure
Edit `.env` to match your paths:

```ini
# Where your media is getting READ from (ReadOnly recommended)
SOURCE_PATH=/mnt/zurg

# Where you want your media COPIED to
DESTINATION_PATH=/mnt/local/media

# Security: Set a strong random password!
JWT_SECRET_KEY=change_me_to_something_secure
```

### 4. Launch
```bash
docker-compose up -d
```

### 5. Login
Go to `http://localhost:4223`.
- **User**: `admin`
- **Password**: `changeme`

> **Need more help?** Check out the [Deployment Guide](docs/deployment.md) or [Configuration Reference](docs/configuration.md).

</details>


## 🙀 How It Works

1.  **Scanner**: The scanner reads your `SOURCE_PATH` and identifies media files. It uses regex to strip "garbage" (release groups, quality tags) and extracts a clean Title and Year.
2.  **Enricher**: If you configure a **Trakt Client ID**, CopyCat matches your files to Trakt to download high-quality posters and metadata. *Note: We cache images locally to respect API limits.*
3.  **Queue**: When you select files to copy, they are added to the background queue. The system performs a verifiable copy operation to your `DESTINATION_PATH`.

---
## 😺 Documentation
- [Deployment Guide](docs/deployment.md)
- [Configuration Reference](docs/configuration.md)
- [Developer Guide](docs/development.md)

---
## 😺 Support CopyCat's Development
If CopyCat saves you time, consider sponsoring:

➡️ [GitHub Sponsors](https://github.com/sponsors/woahai321)

Thank you! 🐱

---
## 🐱 Contributing
Welcome! See [Developer Guide](docs/development.md) for Nuxt + FastAPI setup.

---
## 🐱 License
[MIT License](LICENSE)

---
## Star History
<a href="https://star-history.com/#woahai321/copy-cat&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=woahai321/copy-cat&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=woahai321/copy-cat&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=woahai321/copy-cat&type=Date" />
  </picture>
</a>
