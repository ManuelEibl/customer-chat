from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from services.backend.connection_manager import ConnectionManager

app = FastAPI()

# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
