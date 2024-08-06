from typing import Optional
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.customer_connection: Optional[WebSocket] = None
        self.support_connection: Optional[WebSocket] = None

    async def connect_customer(self, connection: WebSocket):
        await connection.accept()
        self.customer_connection = connection

    async def connect_support(self, connection: WebSocket):
        await connection.accept()
        self.support_connection = connection

    def disconnect_customer(self):
        self.customer_connection = None

    def disconnect_support(self):
        self.support_connection = None

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_to_support(self, message: str):
        if self.support_connection:
            await self.support_connection.send_text(message)

    async def send_to_customer(self, message: str):
        if self.customer_connection:
            await self.customer_connection.send_text(message)
