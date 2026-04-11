from datetime import datetime

from pydantic import BaseModel, Field


class InterviewStartRequest(BaseModel):
    type: str = Field(default="hr")
    target_role: str | None = None
    difficulty: str = "mid"


class InterviewResponse(BaseModel):
    id: str
    type: str
    status: str
    start_time: datetime
    target_role: str | None
    difficulty: str


class QuestionResponse(BaseModel):
    question: str
    category: str


class AnswerRequest(BaseModel):
    interview_id: str
    question: str
    answer: str = Field(min_length=1)


class AnswerEvaluationResponse(BaseModel):
    response_id: str
    score: float
    communication_score: float
    structure_score: float
    relevance_score: float
    specificity_score: float
    verdict: str
    strengths: list[str]
    improvements: list[str]
    feedback: str


class EndInterviewRequest(BaseModel):
    interview_id: str


class DashboardMetric(BaseModel):
    label: str
    value: float


class DashboardInterview(BaseModel):
    id: str
    type: str
    status: str
    date: datetime
    confidence_score: float
    posture_score: float
    communication_score: float


class DashboardResponse(BaseModel):
    metrics: list[DashboardMetric]
    progress: list[dict]
    interviews: list[DashboardInterview]
    gamification: dict
    challenge_summary: dict
