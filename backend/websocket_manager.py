from typing import Set
from fastapi import WebSocket
import json
import asyncio


class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._loop = None
    
    def set_event_loop(self, loop):
        """Set the event loop for thread-safe async operations."""
        self._loop = loop
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast_progress(self, data: dict):
        """Broadcast progress update to all connected clients."""
        message = json.dumps(data)
        disconnected = set()
        
        if not self.active_connections:
            print(f"Warning: No active WebSocket connections to broadcast progress for job {data.get('job_id')}")
            return
        
        success_count = 0
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                success_count += 1
            except Exception as e:
                print(f"Error sending to websocket: {e}")
                disconnected.add(connection)
        
        if success_count > 0:
            print(f"Broadcast progress to {success_count} client(s): Job {data.get('job_id')} - {data.get('progress_percent')}%")
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()

