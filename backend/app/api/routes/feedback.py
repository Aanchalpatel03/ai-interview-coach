from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.interview import Interview
from app.schemas.feedback import FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("/{interview_id}", response_model=FeedbackResponse)
async def get_feedback(interview_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview or not interview.feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    suggestions = interview.feedback.suggestions.split(". ") if interview.feedback.suggestions else []
    return FeedbackResponse(
        interview_id=interview.id,
        posture_score=interview.feedback.posture_score,
        confidence_score=interview.feedback.confidence_score,
        communication_score=interview.feedback.communication_score,
        eye_contact_score=interview.feedback.eye_contact_score,
        hand_movement_score=interview.feedback.hand_movement_score,
        overall_score=interview.feedback.overall_score,
        session_xp=interview.feedback.session_xp,
        improvement_delta=interview.feedback.improvement_delta,
        summary=interview.feedback.summary,
        suggestions=[item.strip().rstrip(".") for item in suggestions if item.strip()],
    )
