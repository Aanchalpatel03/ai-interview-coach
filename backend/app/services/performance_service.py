from statistics import fmean

from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.services.leaderboard_service import update_leaderboard_for_user


def build_performance_history(db: Session, user_id: str) -> dict:
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == user_id, Interview.status == "completed")
        .order_by(Interview.start_time.asc())
        .all()
    )
    history = []
    for interview in interviews:
        feedback = interview.feedback
        if not feedback:
            continue
        history.append(
            {
                "interview_id": interview.id,
                "date": interview.start_time.isoformat(),
                "confidence": feedback.confidence_score,
                "posture": feedback.posture_score,
                "communication": feedback.communication_score,
                "eye_contact": feedback.eye_contact_score,
                "overall_score": feedback.overall_score,
            }
        )
    return {"history": history}


def build_performance_analytics(db: Session, user_id: str) -> dict:
    history = build_performance_history(db, user_id)["history"]
    if not history:
        return {
            "averages": {"confidence": 0, "posture": 0, "communication": 0, "eye_contact": 0, "overall_score": 0},
            "strengths": ["Complete a session to unlock analytics."],
            "weaknesses": ["No interview data yet."],
            "improvement_score": 0,
            "consistency_score": 0,
        }

    averages = {
        metric: round(fmean([item[metric] for item in history]), 1)
        for metric in ["confidence", "posture", "communication", "eye_contact", "overall_score"]
    }
    strongest = max(averages, key=averages.get)
    weakest = min(averages, key=averages.get)
    leaderboard_entry = update_leaderboard_for_user(db, user_id)
    return {
        "averages": averages,
        "strengths": [_metric_copy(strongest, "strong"), "You are sustaining visible progress over time."],
        "weaknesses": [_metric_copy(weakest, "weak"), "Turn repeated feedback into one concrete practice goal each week."],
        "improvement_score": round(leaderboard_entry.improvement_score, 1),
        "consistency_score": round(min(100, leaderboard_entry.total_score), 1),
    }


def _metric_copy(metric: str, tone: str) -> str:
    labels = {
        "confidence": "Confidence is becoming a reliable strength in live sessions.",
        "posture": "Posture control is one of your strongest visual signals.",
        "communication": "Communication clarity is trending well across recent interviews.",
        "eye_contact": "Eye contact is reinforcing your delivery and presence.",
        "overall_score": "Your overall interview performance is trending upward.",
    }
    weakness_labels = {
        "confidence": "Confidence dips are still hurting the authority of some answers.",
        "posture": "Posture consistency needs more attention during longer answers.",
        "communication": "Communication structure still needs tighter, clearer answers.",
        "eye_contact": "Eye contact is the biggest opportunity in your live delivery.",
        "overall_score": "Your overall scoring is improving, but not consistently enough yet.",
    }
    return labels[metric] if tone == "strong" else weakness_labels[metric]
