from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


manager = ConnectionManager()


@app.websocket("/ws/customer")
async def websocket_customer(websocket: WebSocket):
    await manager.connect_customer(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_to_support(f"Customer: {data}")
    except WebSocketDisconnect:
        manager.disconnect_customer()
        await manager.send_to_support("A customer has left the chat")


@app.websocket("/ws/support")
async def websocket_support(websocket: WebSocket):
    await manager.connect_support(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_to_customer(f"Support: {data}")
    except WebSocketDisconnect:
        manager.disconnect_support()
        await manager.send_to_customer("Support has left the chat")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
