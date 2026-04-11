from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from inference import SpeechEngine

app = FastAPI(title="ML Speech Service")
engine = SpeechEngine()


class SpeechRequest(BaseModel):
    transcript: str | None = None
    audio_base64: str | None = None
    duration_seconds: float | None = Field(default=None, ge=0)


@app.get("/health")
async def health():
    return engine.health()


@app.post("/ml/speech/analyze")
async def analyze_speech(payload: SpeechRequest):
    return engine.analyze(payload.transcript, payload.audio_base64, payload.duration_seconds)


@app.websocket("/ws/ml/speech")
async def speech_socket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            await websocket.send_json(
                engine.analyze(
                    payload.get("transcript"),
                    payload.get("audio_base64"),
                    payload.get("duration_seconds"),
                )
            )
    except WebSocketDisconnect:
        return
