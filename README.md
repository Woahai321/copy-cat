<div align="center">

![CopyCat Logo](https://s.2ya.me/api/shares/lVlUQ6CB/files/8776d8e1-9a61-42b8-80ea-eb80d03977b8)
![Nuxt](https://img.shields.io/badge/Nuxt-3.0-8b5cf6?style=flat-square&logo=nuxtdotjs&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-8b5cf6?style=flat-square&logo=fastapi&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-Ready-8b5cf6?style=flat-square&logo=docker&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3.0-8b5cf6?style=flat-square&logo=vuedotjs&logoColor=white) ![Python](https://img.shields.io/badge/Python-3.11%2B-8b5cf6?style=flat-square&logo=python&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-8b5cf6?style=flat-square&logo=githubactions&logoColor=white)

</div>
<div align="center">

[![What is it?](https://img.shields.io/badge/🐱_About-8b5cf6?style=for-the-badge&labelColor=6b21a8)](#what-is-copycat)
[![Interface](https://img.shields.io/badge/😻_Interface-8b5cf6?style=for-the-badge&labelColor=6b21a8)](#interface-overview)
[![Quick Start](https://img.shields.io/badge/⚡_Quick_Start-8b5cf6?style=for-the-badge&labelColor=6b21a8)](#quick-start-docker-command)
[![Deployment](https://img.shields.io/badge/🚀_Deployment-8b5cf6?style=for-the-badge&labelColor=6b21a8)](docs/deployment.md)
[![Configuration](https://img.shields.io/badge/⚙️_Settings-8b5cf6?style=for-the-badge&labelColor=6b21a8)](docs/configuration.md)
[![Technical](https://img.shields.io/badge/🙀_Technical-8b5cf6?style=for-the-badge&labelColor=6b21a8)](#technical-overview)
[![Roadmap](https://img.shields.io/badge/😼_Roadmap-8b5cf6?style=for-the-badge&labelColor=6b21a8)](#roadmap)
[![Support](https://img.shields.io/badge/☕_Support-8b5cf6?style=for-the-badge&labelColor=6b21a8)](#support-copycats-development)

</div>

---

## 😸 What is CopyCat? 

**CopyCat** is a self-hosted media management tool for digital libraries. It bridges the gap between **Cloud Storage** (such as Zurg or Rclone mounts) and **Local Storage** (HDD/NAS).

CopyCat provides a web interface to scan, organize, and copy media files across different storage locations.

## 😻 Interface Overview

<p align="center">
  <img src="https://s.2ya.me/api/shares/9PH2j0tk/files/f9a74261-ffc9-486a-bcd7-baa4f71a1b60" alt="CopyCat Dashboard" width="100%">
</p>

<br>

<details>
<summary><strong>📸 View More Screenshots</strong></summary>

### Media Library
Browse content through a categorized interface. Filter by movies or TV shows, view metadata, and select items for transfer. 

<div align="center">
  <img src="https://s.2ya.me/api/shares/9PH2j0tk/files/08a45da9-716d-4c76-83d4-38361f797a3b" alt="Media Library" width="100%">
  <p><em>Media Library View</em></p>
</div>

### Copy Wizard
Prefer a traditional view? The Copy Wizard offers a familiar file explorer interface, allowing you to manually navigate directory structures and define precise destinations for your transfers.

<div align="center">
  <img src="https://s.2ya.me/api/shares/9PH2j0tk/files/8c1b8ba2-c695-4e46-87b0-2e3b1044271d" alt="Copy Wizard" width="100%">
  <p><em>File Explorer & Copy Wizard</em></p>
</div>

### Transfer Queue
Monitor active transfers in real-time. View detailed progress, transfer speeds, and manage your queue with priority controls to ensure your most important media is ready when you are.

<div align="center">
  <img src="https://s.2ya.me/api/shares/9PH2j0tk/files/47720500-3a77-4e7c-8bc0-4674c50c8b3a" alt="Transfer Queue" width="100%">
  <p><em>Live Transfer Queue</em></p>
</div>

</details>

### 😺 File Scanning
Navigate mounts as an organized library. CopyCat identifies media files and filters out secondary files like samples and metadata documents.

### 😼 Transfer Queue
Monitor and manage file transfers. The queue manager handles process tracking and ensures operations continue even after the browser is closed.

### 😼 Roadmap
- [x] Nuxt 3 + FastAPI Core
- [x] Multi-stage Docker Builds & Healthchecks
- [x] Metadata Enrichment (Trakt)
- [x] Multi-user login / Permissions
- [ ] tbd
- [ ] tbd

---

## 😸 Quick Start (Docker Command)
Run CopyCat with this single Docker command:

```bash
docker run -d --name copycat -p 4222:3000 -p 4223:8000 -v "$(pwd)/data":/data -v /path/to/source:/mnt/source:ro -v /path/to/destination:/mnt/destination -e JWT_SECRET_KEY=change_this_to_secure_random_string ghcr.io/woahai321/copy-cat:main
```

> [!TIP]
> **Access the App**: The Web Interface is at `http://localhost:4222` and the API at `http://localhost:4223`. Login with <kbd>admin</kbd> / <kbd>changeme</kbd>.

---

## 😽 Deployment

<details>
<summary><strong>Deployment Instructions</strong></summary>

CopyCat is deployed using Docker.

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

> [!CAUTION]
> **Production Security**: Ensure the `JWT_SECRET_KEY` is a unique, randomly generated string. Do not use the default value in public deployments.


### 4. Launch
```bash
docker-compose up -d
```

### 5. Login
- **Web Interface**: `http://localhost:4222`
- **Backend API**: `http://localhost:4223/api/docs`
- **User**: `admin`
- **Password**: `changeme`

> **Need more help?** Check out the [Deployment Guide](docs/deployment.md) or [Configuration Reference](docs/configuration.md).

</details>


## 🙀 Technical Overview

```mermaid
graph LR
    A[Source Mount] --> B(Scanner)
    B --> C{Enricher}
    C -->|Match| D[Trakt API]
    C -->|Cache| E[Local DB]
    E --> F(Queue Manager)
    F --> G[Destination Storage]
    
    style B fill:#8b5cf6,stroke:#fff,color:#fff
    style C fill:#8b5cf6,stroke:#fff,color:#fff
    style F fill:#8b5cf6,stroke:#fff,color:#fff
```

1.  **Scanner**: Reads the `SOURCE_PATH` and identifies media files. It uses regex to remove unnecessary tags and extracts titles and dates.
2.  **Enricher**: If a **Trakt Client ID** is configured, CopyCat retrieves posters and metadata from Trakt. Images are cached locally to minimize API requests.
3.  **Queue**: Selected files are added to a background queue for transfer to the `DESTINATION_PATH`.


## 😺 Documentation
- [Deployment Guide](docs/deployment.md)
- [Configuration Reference](docs/configuration.md)
- [Developer Guide](docs/development.md)


## 😺 Support CopyCat's Development
If CopyCat saves you time, consider sponsoring:

➡️ [GitHub Sponsors](https://github.com/sponsors/woahai321)

Thank you.


## 🐱 Contributing
Welcome! See [Developer Guide](docs/development.md) for Nuxt + FastAPI setup.


## 🐱 License
[MIT License](LICENSE)


## Star History
<a href="https://star-history.com/#woahai321/copy-cat&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=woahai321/copy-cat&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=woahai321/copy-cat&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=woahai321/copy-cat&type=Date" />
  </picture>
</a>
