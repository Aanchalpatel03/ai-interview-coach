from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from inference import EmotionEngine

app = FastAPI(title="ML Emotion Service")
engine = EmotionEngine()


class FrameRequest(BaseModel):
    frame: str


@app.get("/health")
async def health():
    return engine.health()


@app.post("/ml/emotion/analyze")
async def analyze_emotion(payload: FrameRequest):
    return engine.analyze(payload.frame)


@app.post("/analyze-emotion")
async def analyze_emotion_legacy(payload: FrameRequest):
    return engine.analyze(payload.frame)


@app.websocket("/ws/ml/emotion")
async def emotion_socket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            await websocket.send_json(engine.analyze(payload["frame"]))
    except WebSocketDisconnect:
        return
