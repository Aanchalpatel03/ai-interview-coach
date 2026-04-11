import base64
import json
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return round(max(low, min(high, value)), 1)


def decode_frame(frame: str) -> Image.Image:
    encoded = frame.split(",", 1)[1] if "," in frame else frame
    return Image.open(BytesIO(base64.b64decode(encoded))).convert("L")


def load_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


class EmotionEngine:
    def __init__(self, artifact_path: Path | None = None) -> None:
        self.artifact_path = artifact_path or Path(__file__).with_name("artifacts").joinpath("emotion-calibration.json")
        self.artifact = load_artifact(self.artifact_path)
        self.local_model_loaded = False

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "artifact_loaded": bool(self.artifact),
            "model_loaded": self.local_model_loaded,
        }

    def analyze(self, frame: str) -> dict[str, Any]:
        image = decode_frame(frame)
        stat = ImageStat.Stat(image)
        brightness = stat.mean[0]
        variance = stat.var[0]

        confidence_score = clamp(55 + variance / 4.5 + brightness * 0.08)
        nervousness_score = clamp(100 - confidence_score)
        engagement_score = clamp(48 + variance / 5.0)
        smile_score = clamp(45 + max(0.0, brightness - 90) * 0.4)
        eye_contact_score = clamp(60 + min(20.0, variance / 8.0))

        if confidence_score >= 75:
            emotion = "confident"
        elif nervousness_score >= 55:
            emotion = "nervous"
        else:
            emotion = "engaged"

        suggestions = []
        if confidence_score < 70:
            suggestions.append("Pause before answering so your delivery feels more controlled.")
        if nervousness_score > 55:
            suggestions.append("Relax your jaw and shoulders to reduce visible tension.")
        if engagement_score < 65:
            suggestions.append("Keep your face directed toward the camera to look more engaged.")
        if not suggestions:
            suggestions.append("Facial expression looks steady and engaged.")

        return {
            "emotion": emotion,
            "confidence_score": confidence_score,
            "nervousness_score": nervousness_score,
            "engagement_score": engagement_score,
            "smile_score": smile_score,
            "eye_contact_score": eye_contact_score,
            "suggestions": suggestions,
        }
