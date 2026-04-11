from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.challenge import CompleteChallengeRequest, CompleteChallengeResponse, TodayChallengesResponse
from app.services.challenge_service import complete_challenge, get_today_challenges

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.get("/today", response_model=TodayChallengesResponse)
async def today_challenges(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_today_challenges(db, current_user.id)


@router.post("/complete", response_model=CompleteChallengeResponse)
async def complete(payload: CompleteChallengeRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return complete_challenge(db, current_user.id, payload.challenge_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
