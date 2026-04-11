from pydantic import BaseModel, Field


class VideoFrameRequest(BaseModel):
    interview_id: str
    frame: str = Field(description="Base64 encoded image")


class VideoFeedbackResponse(BaseModel):
    posture_score: float
    confidence_score: float
    eye_contact_score: float
    hand_movement_score: float
    status: str
    posture: str
    eye_contact: str
    confidence: float
    suggestions: list[str]
    overall_score: float
