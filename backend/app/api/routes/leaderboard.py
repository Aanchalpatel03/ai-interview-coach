from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.leaderboard import LeaderboardResponse, LeaderboardUpdateResponse
from app.services.leaderboard_service import get_leaderboard, serialize_entry, update_leaderboard_for_user

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def leaderboard(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    leaders, current_entry = get_leaderboard(db, current_user.id)
    return {
        "leaders": [serialize_entry(entry) for entry in leaders],
        "current_user": serialize_entry(current_entry),
    }


@router.post("/update", response_model=LeaderboardUpdateResponse)
async def update_leaderboard(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    entry = update_leaderboard_for_user(db, current_user.id)
    return {"status": "updated", "entry": serialize_entry(entry)}
