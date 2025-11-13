from fastapi import WebSocket
from typing import List
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Acepta una nueva conexión WebSocket y la agrega a la lista activa.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 Cliente conectado ({len(self.active_connections)} conectados)")

    def disconnect(self, websocket: WebSocket):
        """
        Elimina la conexión de la lista activa.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"❌ Cliente desconectado ({len(self.active_connections)} restantes)")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Envía un mensaje JSON a un cliente específico.
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"⚠️ Error enviando mensaje individual: {e}")

    async def broadcast(self, message: dict):
        """
        Envía un mensaje JSON a todos los clientes conectados.
        """
        if not self.active_connections:
            return

        coros = []
        for conn in list(self.active_connections):
            try:
                coros.append(conn.send_json(message))
            except Exception as e:
                print(f"⚠️ Error al enviar a una conexión: {e}")

        if coros:
            await asyncio.gather(*coros, return_exceptions=True)

# Instancia global del administrador
manager = ConnectionManager()
