# Copy Management Frontend

Nuxt 3 frontend for the Copy Management System.

## Setup

### Install Dependencies

```bash
npm install
```

## Development

### Start Development Server

```bash
npm run dev
```

The application will be available at http://localhost:4222

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Configuration

### API Base URL

The backend API URL is configured in `nuxt.config.ts`:

```typescript
runtimeConfig: {
  public: {
    apiBase: process.env.API_BASE_URL || 'http://localhost:4223'
  }
}
```

You can override this with an environment variable:

```bash
API_BASE_URL=http://your-backend-url npm run dev
```

## Project Structure

```
app/
├── components/          # Vue components
│   ├── FileExplorer.vue
│   └── CopyJobCard.vue
├── composables/         # Composable functions
│   ├── useAuth.ts
│   ├── useApi.ts
│   └── useWebSocket.ts
├── layouts/             # Layout components
│   └── default.vue
├── middleware/          # Route middleware
│   └── auth.ts
├── pages/              # Application pages
│   ├── index.vue       # Dashboard
│   ├── login.vue       # Login page
│   ├── browse.vue      # Browse & copy
│   ├── queue.vue       # Active queue
│   └── history.vue     # Copy history
└── app.vue             # Root component
```

## Features

### Authentication

The app uses JWT tokens stored in localStorage. The `useAuth` composable provides:

- `login(username, password)` - Login and store token
- `logout()` - Clear token and redirect
- `isAuthenticated` - Check if user is logged in
- `getAuthHeaders()` - Get headers for API requests

### File Browsing

The `FileExplorer` component provides:

- Recursive directory navigation
- File and folder size display
- Folder selection for copy operations
- Back navigation

### Real-time Progress

The `useWebSocket` composable:

- Connects to the backend WebSocket
- Receives real-time progress updates
- Auto-reconnects on disconnect
- Provides job-specific progress data

### Copy Operations

The browse page allows:

- Select source folder from Zurg
- Select destination folder on 16TB
- Optional custom folder naming
- Start copy operation

### Queue Management

The queue page shows:

- Active copy operations
- Real-time progress bars
- Cancel queued jobs
- Auto-refresh every 5 seconds

### History

The history page provides:

- Complete copy history
- Filter by status
- Retry failed operations
- Pagination support

## Styling

The app uses:

- **Nuxt UI**: Pre-built components
- **Tailwind CSS**: Utility-first CSS
- **Dark Mode**: Automatic dark mode support

## Auto-imports

Nuxt 3 provides auto-imports for:

- Vue functions (ref, computed, watch, etc.)
- Nuxt composables (useState, useRouter, etc.)
- Component imports

No need to manually import these!

## Building for Docker

The Dockerfile builds a production-ready image:

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

## Environment Variables

- `API_BASE_URL` - Backend API URL (default: http://localhost:4223)
- `NODE_ENV` - Node environment (development/production)

## Troubleshooting

### Module not found errors

Clear the Nuxt cache and reinstall:

```bash
rm -rf .nuxt .output node_modules
npm install
```

### API connection errors

1. Check backend is running: `curl http://localhost:4223`
2. Verify API_BASE_URL is correct
3. Check browser console for CORS errors

### WebSocket disconnects

The app automatically reconnects after 3 seconds. Check:

- Backend WebSocket endpoint is accessible
- Network connection is stable
- Backend logs for WebSocket errors
