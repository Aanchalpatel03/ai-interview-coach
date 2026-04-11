from statistics import fmean

from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.services.challenge_service import get_today_challenges
from app.services.leaderboard_service import ensure_leaderboard_entry, serialize_entry, update_leaderboard_for_user


def build_dashboard(db: Session, user_id: str) -> dict:
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == user_id)
        .order_by(Interview.start_time.desc())
        .limit(8)
        .all()
    )
    feedback_rows = [interview.feedback for interview in interviews if interview.feedback]
    metrics = {
        "Confidence": round(fmean([item.confidence_score for item in feedback_rows]), 1) if feedback_rows else 0,
        "Communication": round(fmean([item.communication_score for item in feedback_rows]), 1) if feedback_rows else 0,
        "Posture": round(fmean([item.posture_score for item in feedback_rows]), 1) if feedback_rows else 0,
    }

    progress = [
        {
            "name": interview.start_time.strftime("%b %d"),
            "confidence": interview.feedback.confidence_score if interview.feedback else 0,
            "communication": interview.feedback.communication_score if interview.feedback else 0,
            "posture": interview.feedback.posture_score if interview.feedback else 0,
        }
        for interview in reversed(interviews)
    ]

    challenge_summary = get_today_challenges(db, user_id)["summary"]
    leaderboard_entry = update_leaderboard_for_user(db, user_id)

    return {
        "metrics": [{"label": key, "value": value} for key, value in metrics.items()],
        "progress": progress,
        "interviews": [
            {
                "id": interview.id,
                "type": interview.type,
                "status": interview.status,
                "date": interview.start_time,
                "confidence_score": interview.feedback.confidence_score if interview.feedback else 0,
                "posture_score": interview.feedback.posture_score if interview.feedback else 0,
                "communication_score": interview.feedback.communication_score if interview.feedback else 0,
            }
            for interview in interviews
        ],
        "gamification": serialize_entry(leaderboard_entry) or serialize_entry(ensure_leaderboard_entry(db, user_id)),
        "challenge_summary": challenge_summary,
    }
