from datetime import datetime
from statistics import fmean

from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.models.interview import Interview
from app.models.response import Response
from app.services.leaderboard_service import award_xp, update_leaderboard_for_user


def create_interview(db: Session, user_id: str, interview_type: str, target_role: str | None, difficulty: str) -> Interview:
    interview = Interview(user_id=user_id, type=interview_type, target_role=target_role, difficulty=difficulty)
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def store_answer(
    db: Session,
    interview_id: str,
    question: str,
    answer: str,
    score: float,
    communication_score: float,
    feedback: str,
) -> Response:
    response = Response(
        interview_id=interview_id,
        question=question,
        answer=answer,
        score=score,
        communication_score=communication_score,
        answer_feedback=feedback,
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    return response


def finalize_interview(db: Session, interview: Interview, latest_video_feedback: dict | None) -> Feedback:
    interview.status = "completed"
    interview.end_time = datetime.utcnow()
    response_scores = [response.communication_score for response in interview.responses]
    communication_score = round(fmean(response_scores), 1) if response_scores else 0
    answer_quality = round(fmean([response.score for response in interview.responses]), 1) if interview.responses else 0
    speech_score = latest_video_feedback.get("speech_score", communication_score) if latest_video_feedback else communication_score

    feedback = interview.feedback or Feedback(interview_id=interview.id)
    feedback.communication_score = communication_score
    feedback.posture_score = latest_video_feedback.get("posture_score", 0) if latest_video_feedback else 0
    feedback.confidence_score = latest_video_feedback.get("confidence_score", 0) if latest_video_feedback else 0
    feedback.eye_contact_score = latest_video_feedback.get("eye_contact_score", 0) if latest_video_feedback else 0
    feedback.hand_movement_score = latest_video_feedback.get("hand_movement_score", 0) if latest_video_feedback else 0
    feedback.overall_score = round(
        (
            communication_score * 0.25
            + speech_score * 0.2
            + feedback.confidence_score * 0.2
            + feedback.posture_score * 0.15
            + feedback.eye_contact_score * 0.1
            + answer_quality * 0.1
        ),
        1,
    )
    previous_feedback = [
        row.overall_score
        for row in db.query(Feedback)
        .join(Interview, Interview.id == Feedback.interview_id)
        .filter(Interview.user_id == interview.user_id, Interview.id != interview.id)
        .all()
    ]
    baseline = round(fmean(previous_feedback), 1) if previous_feedback else feedback.overall_score
    feedback.improvement_delta = round(feedback.overall_score - baseline, 1)
    feedback.session_xp = max(40, int(round(feedback.overall_score + max(feedback.improvement_delta, 0))))
    feedback.summary = _build_summary(communication_score, speech_score, feedback.confidence_score, feedback.posture_score)
    feedback.suggestions = ". ".join(_build_suggestions(latest_video_feedback, communication_score)) + "."
    db.add(feedback)
    db.add(interview)
    db.commit()
    db.refresh(feedback)
    award_xp(db, interview.user_id, feedback.session_xp)
    update_leaderboard_for_user(db, interview.user_id)
    return feedback


def _build_summary(communication_score: float, speech_score: float, confidence_score: float, posture_score: float) -> str:
    summary_parts = []
    summary_parts.append("Your answer quality stayed strongest when you used structured, outcome-driven examples.")
    if speech_score >= 70:
        summary_parts.append("Speech delivery was clear and interviewer-friendly.")
    else:
        summary_parts.append("Speech clarity still needs tightening to land points more cleanly.")
    if confidence_score >= 70 and posture_score >= 70:
        summary_parts.append("Non-verbal presence looked steady on camera.")
    else:
        summary_parts.append("Body language dipped during harder moments, which lowered overall presence.")
    if communication_score >= 75:
        summary_parts.append("You are close to a strong mock interview baseline.")
    else:
        summary_parts.append("You need more concise phrasing and better pacing to become interview-ready.")
    return " ".join(summary_parts)


def _build_suggestions(latest_feedback: dict | None, communication_score: float) -> list[str]:
    suggestions = list((latest_feedback or {}).get("suggestions", []))
    if communication_score < 70:
        suggestions.append("Shorten each answer to the decision, action, and result that matters most.")
    if not suggestions:
        suggestions.append("Keep the current pacing and maintain the same on-camera presence.")
    return list(dict.fromkeys(suggestions))[:5]
