from pydantic import BaseModel


class LeaderboardEntryResponse(BaseModel):
    user_id: str
    name: str
    total_score: float
    rank: int
    level: str
    xp_points: int
    badges: list[str]
    streak_count: int
    improvement_score: float


class LeaderboardResponse(BaseModel):
    leaders: list[LeaderboardEntryResponse]
    current_user: LeaderboardEntryResponse | None = None


class LeaderboardUpdateResponse(BaseModel):
    status: str
    entry: LeaderboardEntryResponse
