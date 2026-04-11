import base64
from io import BytesIO

from fastapi import FastAPI
from PIL import Image, ImageStat
from pydantic import BaseModel

app = FastAPI(title="Emotion Service")


class FrameRequest(BaseModel):
    frame: str


def decode_frame(frame: str) -> Image.Image:
    _, encoded = frame.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    return Image.open(BytesIO(image_bytes)).convert("L")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze-emotion")
async def analyze_emotion(payload: FrameRequest):
    frame = decode_frame(payload.frame)
    variance = ImageStat.Stat(frame).var[0] if frame is not None else 900.0
    confidence_score = max(42.0, min(94.0, 55 + variance / 120))
    nervousness_score = max(8.0, min(65.0, 100 - confidence_score))
    dominant_emotion = "confident" if confidence_score >= 72 else "neutral"
    return {
        "confidence_score": round(confidence_score, 1),
        "nervousness_score": round(nervousness_score, 1),
        "dominant_emotion": dominant_emotion,
    }
