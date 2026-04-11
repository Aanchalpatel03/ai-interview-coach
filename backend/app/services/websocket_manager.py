from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[str, dict[str, list[WebSocket]]] = defaultdict(lambda: defaultdict(list))
        self.latest_feedback: dict[str, dict] = {}
        self.modality_state: dict[str, dict[str, dict]] = defaultdict(dict)

    async def connect(self, interview_id: str, websocket: WebSocket, channel: str = "video") -> None:
        await websocket.accept()
        self.connections[interview_id][channel].append(websocket)

    def disconnect(self, interview_id: str, websocket: WebSocket, channel: str = "video") -> None:
        if websocket in self.connections[interview_id][channel]:
            self.connections[interview_id][channel].remove(websocket)

    async def broadcast(self, interview_id: str, payload: dict) -> dict:
        return await self.update_feedback(interview_id, "video", payload)

    async def update_feedback(self, interview_id: str, source: str, payload: dict) -> dict:
        self.modality_state[interview_id][source] = payload
        aggregate = self._compose_feedback(self.modality_state[interview_id])
        self.latest_feedback[interview_id] = aggregate
        for channel in ("video", "ml"):
            for connection in list(self.connections[interview_id][channel]):
                await connection.send_json(aggregate)
        return aggregate

    def _compose_feedback(self, state: dict[str, dict]) -> dict:
        video = state.get("video", {})
        speech = state.get("speech", {})
        nlp = state.get("nlp", {})

        suggestions = []
        for source_payload in (video, speech, nlp):
            for suggestion in source_payload.get("suggestions", []):
                if suggestion not in suggestions:
                    suggestions.append(suggestion)

        posture_score = float(video.get("posture_score", 0))
        confidence_score = float(video.get("confidence_score", 0))
        eye_contact_score = float(video.get("eye_contact_score", 0))
        speech_score = float(speech.get("speech_score", 0))
        answer_score = float(nlp.get("score", 0))
        scored_values = [score for score in (posture_score, confidence_score, eye_contact_score, speech_score, answer_score) if score > 0]
        overall_score = round(sum(scored_values) / len(scored_values), 1) if scored_values else 0.0

        if overall_score >= 75:
            status = "green"
        elif overall_score >= 50:
            status = "yellow"
        else:
            status = "red"

        return {
            "posture_score": posture_score,
            "confidence_score": confidence_score,
            "eye_contact_score": eye_contact_score,
            "hand_movement_score": float(video.get("hand_movement_score", 0)),
            "speech_score": speech_score,
            "answer_score": answer_score,
            "posture": video.get("posture", "unknown"),
            "head_position": video.get("head_position", "unknown"),
            "eye_contact": video.get("eye_contact", "unknown"),
            "eye_alignment": video.get("eye_alignment", video.get("eye_contact", "unknown")),
            "hand_movement": video.get("hand_movement", "unknown"),
            "emotion": video.get("emotion", "neutral"),
            "speech_tone": speech.get("tone", "neutral"),
            "status": status,
            "suggestions": suggestions[:5],
            "overall_score": overall_score,
            "sources": sorted(state.keys()),
        }


manager = ConnectionManager()
