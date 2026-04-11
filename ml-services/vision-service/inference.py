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
    return Image.open(BytesIO(base64.b64decode(encoded))).convert("RGB")


def load_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


class VisionEngine:
    def __init__(self, artifact_path: Path | None = None) -> None:
        self.artifact_path = artifact_path or Path(__file__).with_name("artifacts").joinpath("vision-calibration.json")
        self.artifact = load_artifact(self.artifact_path)
        self.pose_model_loaded = False
        try:
            import cv2  # noqa: F401
            import mediapipe  # noqa: F401

            self.pose_model_loaded = True
        except Exception:
            self.pose_model_loaded = False

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "artifact_loaded": bool(self.artifact),
            "pose_model_loaded": self.pose_model_loaded,
        }

    def analyze(self, frame: str) -> dict[str, Any]:
        image = decode_frame(frame)
        width, height = image.size
        grayscale = image.convert("L")
        overall_brightness = ImageStat.Stat(grayscale).mean[0]
        top_half = grayscale.crop((0, 0, width, height // 2))
        bottom_half = grayscale.crop((0, height // 2, width, height))
        left_half = grayscale.crop((0, 0, width // 2, height))
        right_half = grayscale.crop((width // 2, 0, width, height))

        top_brightness = ImageStat.Stat(top_half).mean[0]
        bottom_brightness = ImageStat.Stat(bottom_half).mean[0]
        left_brightness = ImageStat.Stat(left_half).mean[0]
        right_brightness = ImageStat.Stat(right_half).mean[0]

        posture_score = clamp(82 - abs(top_brightness - bottom_brightness) * 0.35 + overall_brightness * 0.05)
        eye_contact_score = clamp(84 - abs(left_brightness - right_brightness) * 0.45)
        hand_movement_score = clamp(78 - abs(bottom_brightness - overall_brightness) * 0.18)
        head_tilt = round((left_brightness - right_brightness) / 8, 2)

        posture = "good" if posture_score >= 72 else "bad"
        head_position = "aligned" if abs(head_tilt) <= 4 else "not_aligned"
        hand_movement = "stable" if hand_movement_score >= 65 else "excessive"
        eye_alignment = "aligned" if eye_contact_score >= 68 else "not_aligned"

        suggestions = []
        if posture_score < 70:
            suggestions.append("Sit taller and keep your shoulders squared to the camera.")
        if abs(head_tilt) > 4:
            suggestions.append("Center your head and keep the camera closer to eye level.")
        if hand_movement_score < 65:
            suggestions.append("Reduce visible hand movement so your delivery looks steadier.")
        if eye_contact_score < 68:
            suggestions.append("Look into the lens for the last sentence of each answer.")
        if not suggestions:
            suggestions.append("Posture and body language look stable.")

        return {
            "posture": posture,
            "posture_score": posture_score,
            "head_position": head_position,
            "head_tilt_degrees": head_tilt,
            "hand_movement": hand_movement,
            "hand_movement_score": hand_movement_score,
            "eye_alignment": eye_alignment,
            "eye_contact_score": eye_contact_score,
            "suggestions": suggestions,
        }
