from pydantic import BaseModel


class PerformancePointResponse(BaseModel):
    interview_id: str
    date: str
    confidence: float
    posture: float
    communication: float
    eye_contact: float
    overall_score: float


class PerformanceHistoryResponse(BaseModel):
    history: list[PerformancePointResponse]


class PerformanceAnalyticsResponse(BaseModel):
    averages: dict[str, float]
    strengths: list[str]
    weaknesses: list[str]
    improvement_score: float
    consistency_score: float
