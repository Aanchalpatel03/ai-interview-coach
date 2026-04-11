import base64
from io import BytesIO

from fastapi import FastAPI
from PIL import Image, ImageStat
from pydantic import BaseModel

app = FastAPI(title="Vision Service")


class FrameRequest(BaseModel):
    frame: str


def decode_frame(frame: str) -> Image.Image:
    _, encoded = frame.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    return Image.open(BytesIO(image_bytes)).convert("RGB")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze-frame")
async def analyze_frame(payload: FrameRequest):
    frame = decode_frame(payload.frame)
    brightness = ImageStat.Stat(frame.convert("L")).mean[0] if frame is not None else 120.0
    posture_score = max(35.0, min(95.0, brightness / 255 * 100))
    eye_contact_score = max(40.0, min(92.0, 100 - abs(brightness - 128) / 2))
    hand_movement_score = max(45.0, min(90.0, posture_score - 5))
    return {
        "posture_score": round(posture_score, 1),
        "eye_contact_score": round(eye_contact_score, 1),
        "hand_movement_score": round(hand_movement_score, 1),
        "head_tilt": round((128 - brightness) / 20, 2),
    }
