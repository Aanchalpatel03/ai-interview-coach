from pydantic import BaseModel, Field


class MLNlpEvaluationRequest(BaseModel):
    interview_id: str | None = None
    question: str
    answer: str = Field(min_length=1)
    interview_type: str = "hr"


class MLFrameRequest(BaseModel):
    interview_id: str
    frame: str = Field(description="Base64 encoded image")


class MLSpeechAnalysisRequest(BaseModel):
    interview_id: str
    transcript: str | None = None
    audio_base64: str | None = None
    duration_seconds: float | None = Field(default=None, ge=0)


class MLSpeechAnalysisResponse(BaseModel):
    speech_score: float
    clarity_score: float
    filler_word_count: int
    filler_words: list[str]
    speaking_rate_wpm: float
    tone: str
    confidence_score: float
    suggestions: list[str]
    transcript: str | None = None


class MLRealtimeFeedbackResponse(BaseModel):
    posture_score: float = 0
    confidence_score: float = 0
    eye_contact_score: float = 0
    hand_movement_score: float = 0
    speech_score: float = 0
    answer_score: float = 0
    posture: str = "unknown"
    head_position: str = "unknown"
    eye_contact: str = "unknown"
    eye_alignment: str = "unknown"
    hand_movement: str = "unknown"
    emotion: str = "neutral"
    speech_tone: str = "neutral"
    status: str = "yellow"
    suggestions: list[str] = Field(default_factory=list)
    overall_score: float = 0
    sources: list[str] = Field(default_factory=list)
