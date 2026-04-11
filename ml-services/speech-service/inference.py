import base64
import json
import wave
from io import BytesIO
from pathlib import Path
from typing import Any


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return round(max(low, min(high, value)), 1)


def load_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


class SpeechEngine:
    def __init__(self, artifact_path: Path | None = None) -> None:
        self.artifact_path = artifact_path or Path(__file__).with_name("artifacts").joinpath("speech-calibration.json")
        self.artifact = load_artifact(self.artifact_path)
        self.transcriber_loaded = False

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "artifact_loaded": bool(self.artifact),
            "transcriber_loaded": self.transcriber_loaded,
        }

    def analyze(self, transcript: str | None, audio_base64: str | None, duration_seconds: float | None) -> dict[str, Any]:
        transcript = (transcript or "").strip() or None
        duration_seconds = duration_seconds or self._estimate_duration(audio_base64) or 60.0
        words = transcript.lower().split() if transcript else []
        filler_terms = {"um", "uh", "like", "actually", "basically", "literally"}
        filler_words = [word.strip(",.!?") for word in words if word.strip(",.!?") in filler_terms]
        speaking_rate_wpm = round((len(words) / max(duration_seconds, 1.0)) * 60, 1) if words else 110.0

        clarity_score = 84.0
        if len(filler_words) > 3:
            clarity_score -= min(24.0, len(filler_words) * 2.5)
        if speaking_rate_wpm > 170 or speaking_rate_wpm < 95:
            clarity_score -= 10.0

        tone = "balanced"
        if transcript:
            lower = transcript.lower()
            if any(phrase in lower for phrase in ("maybe", "i think", "probably")):
                tone = "hesitant"
            elif transcript.endswith("!") or transcript.count("!") > 1:
                tone = "energetic"

        confidence_score = clamp(clarity_score + (6 if tone == "balanced" else 0))
        speech_score = clamp(clarity_score * 0.7 + confidence_score * 0.3)

        suggestions = []
        if len(filler_words) > 3:
            suggestions.append("Reduce filler words by pausing instead of restarting phrases.")
        if speaking_rate_wpm > 165:
            suggestions.append("Slow the pace slightly so key ideas sound more deliberate.")
        elif speaking_rate_wpm < 95:
            suggestions.append("Increase the pace slightly to sound more decisive.")
        if tone == "hesitant":
            suggestions.append("Replace hedge phrases with direct statements about your decisions and outcomes.")
        if not suggestions:
            suggestions.append("Speech delivery is clear and steady.")

        return {
            "speech_score": speech_score,
            "clarity_score": clamp(clarity_score),
            "filler_word_count": len(filler_words),
            "filler_words": sorted(set(filler_words)),
            "speaking_rate_wpm": speaking_rate_wpm,
            "tone": tone,
            "confidence_score": confidence_score,
            "suggestions": suggestions,
            "transcript": transcript,
        }

    def _estimate_duration(self, audio_base64: str | None) -> float | None:
        if not audio_base64:
            return None
        try:
            encoded = audio_base64.split(",", 1)[1] if "," in audio_base64 else audio_base64
            audio_bytes = BytesIO(base64.b64decode(encoded))
        except Exception:
            return None
        try:
            with wave.open(audio_bytes, "rb") as handle:
                sample_rate = handle.getframerate() or 1
                return handle.getnframes() / sample_rate
        except Exception:
            return None
