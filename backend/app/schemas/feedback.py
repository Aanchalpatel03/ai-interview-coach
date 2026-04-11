from pydantic import BaseModel


class FeedbackResponse(BaseModel):
    interview_id: str
    posture_score: float
    confidence_score: float
    communication_score: float
    eye_contact_score: float
    hand_movement_score: float = 0
    overall_score: float = 0
    session_xp: int = 0
    improvement_delta: float = 0
    summary: str | None
    suggestions: list[str]
