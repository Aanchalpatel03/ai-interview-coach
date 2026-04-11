from datetime import date, datetime

from pydantic import BaseModel


class DailyChallengeResponse(BaseModel):
    id: str
    date: date
    question: str
    type: str
    xp_reward: int
    completed: bool
    completed_at: datetime | None = None


class ChallengeSummaryResponse(BaseModel):
    streak_count: int
    xp_boost: int
    completion_rate: float


class TodayChallengesResponse(BaseModel):
    date: date
    challenges: list[DailyChallengeResponse]
    summary: ChallengeSummaryResponse


class CompleteChallengeRequest(BaseModel):
    challenge_id: str


class CompleteChallengeResponse(BaseModel):
    status: str
    xp_awarded: int
    streak_count: int
