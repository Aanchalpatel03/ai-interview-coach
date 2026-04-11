from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from inference import VisionEngine

app = FastAPI(title="ML Vision Service")
engine = VisionEngine()


class FrameRequest(BaseModel):
    frame: str


@app.get("/health")
async def health():
    return engine.health()


@app.post("/ml/vision/analyze-frame")
async def analyze_frame(payload: FrameRequest):
    return engine.analyze(payload.frame)


@app.post("/analyze-frame")
async def analyze_frame_legacy(payload: FrameRequest):
    return engine.analyze(payload.frame)


@app.websocket("/ws/ml/vision")
async def vision_socket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            await websocket.send_json(engine.analyze(payload["frame"]))
    except WebSocketDisconnect:
        return
