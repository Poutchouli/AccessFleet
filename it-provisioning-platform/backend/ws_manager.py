"""
WebSocket Connection Manager for Real-Time Admin Dashboard

This module handles WebSocket connections for the admin dashboard,
allowing real-time updates when new requests are submitted or 
request statuses are changed.
"""

from fastapi import WebSocket

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        """Initialize the connection manager with an empty connections list."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection and add it to active connections.
        
        Args:
            websocket: The WebSocket connection to accept
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from active connections.
        
        Args:
            websocket: The WebSocket connection to remove
        """
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        """
        Broadcast data to all active WebSocket connections.
        
        Args:
            data: Dictionary containing the data to broadcast
        """
        for connection in self.active_connections:
            await connection.send_json(data)

# Global connection manager instance
manager = ConnectionManager()
