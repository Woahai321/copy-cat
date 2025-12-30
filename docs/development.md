# 🧑‍💻 Developer Guide

This guide helps you set up a local development environment to contribute to CopyCat.

## Architecture

CopyCat consists of two main parts:
1.  **Frontend**: Nuxt 3 (Vue 3) SPA handled in `/frontend`.
2.  **Backend**: FastAPI (Python) server handling API, database, and file operations in `/backend`.

## Prerequisites

-   Node.js 18+
-   Python 3.11+
-   Docker (optional, for testing)

## Local Setup

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Run the backend:**
```bash
uvicorn main:app --reload --port 4223
```
The API is now available at `http://localhost:4223`.

### 2. Frontend Setup

```bash
cd frontend
npm install
```

**Run the frontend dev server:**
```bash
npm run dev
```
The UI is available at `http://localhost:3000`. It configures a proxy to talk to the backend on port 4223.

## Project Structure

```
├── backend/
│   ├── main.py             # Entry point
│   ├── models.py           # Database models (SQLAlchemy)
│   ├── file_operations.py  # Core copying logic
│   └── ...
├── frontend/
│   ├── app/
│   │   ├── pages/          # Vue Pages
│   │   ├── components/     # Vue Components
│   │   └── ...
│   └── nuxt.config.ts
├── docs/                   # Documentation
└── docker-compose.yml
```

## Running Tests

(Add testing instructions here once test suite is established)

## Contribution Workflow

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes.
4.  Push to the branch.
5.  Open a Pull Request.
